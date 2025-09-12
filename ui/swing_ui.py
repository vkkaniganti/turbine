import tkinter as tk
from tkinter import ttk, messagebox
from data_reader.xpr_reader import XPRReader
from data_reader.xpn_reader import XPNReader
import os
import pandas as pd
import logging
import numpy as np
from scipy.spatial import distance_matrix
from ui.file_operations import load_xpr_folder, load_xpn_folder
from ui.data_processing import compute_report, apply_correction
from ui.ui_components import save_df_to_pdf,generate_cmm_report

def calculate_thickness_at(df, x_coord):
    points_around = df[np.isclose(df['X'], x_coord, atol=0.1)]
    if len(points_around) < 2:
        return np.nan
    
    y_values = points_around['Y'].values
    if len(y_values) < 2:
        return np.nan
        
    return np.max(y_values) - np.min(y_values)

class TurbineUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Turbine Data Processor")
        self.geometry("400x200")

        self.xpr_folder_path = None
        self.xpn_folder_path = None
        self.base_name = None
        self.xpr_header = ""

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        file_frame = ttk.LabelFrame(main_frame, text="Folder Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=5, padx=10)

        self.xpr_folder_label = ttk.Label(file_frame, text="No RAW folder selected")
        self.xpr_folder_label.grid(row=0, column=1, padx=10, sticky="w")
        xpr_button = ttk.Button(file_frame, text="Choose RAW folder", command=lambda: load_xpr_folder(self))
        xpr_button.grid(row=0, column=0, padx=10)

        self.xpn_folder_label = ttk.Label(file_frame, text="No NOM folder selected")
        self.xpn_folder_label.grid(row=1, column=1, padx=10, sticky="w")
        xpn_button = ttk.Button(file_frame, text="Choose NOM folder", command=lambda: load_xpn_folder(self))
        xpn_button.grid(row=1, column=0, padx=10)

        submit_button = ttk.Button(main_frame, text="Process Files", command=self.process_files)
        submit_button.pack(pady=10)

        exit_button = ttk.Button(main_frame, text="Exit", command=self.exit_app)
        exit_button.pack(pady=5)

    def exit_app(self):
        logging.shutdown()
        self.destroy()

    def process_files(self):
        if not self.xpr_folder_path or not self.xpn_folder_path:
            messagebox.showerror("Error", "Please select both RAW and NOM folders.")
            return

        os.makedirs("logs", exist_ok=True)
        
        xpr_files = [f for f in os.listdir(self.xpr_folder_path) if f.upper().endswith(".XPR")]

        if not xpr_files:
            messagebox.showerror("Error", "No .xpr files found in the selected RAW folder.")
            return

        for xpr_file in xpr_files:
            self.base_name = os.path.basename(xpr_file).split('.')[0]
            
            log_file = os.path.join("logs", f"{self.base_name}.log")
            logger = logging.getLogger(self.base_name)
            logger.setLevel(logging.INFO)
            if logger.hasHandlers():
                logger.handlers.clear()
            fh = logging.FileHandler(log_file, mode='w')
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(fh)

            xpr_file_path = os.path.join(self.xpr_folder_path, xpr_file)
            xpn_file_name = self.base_name + ".XPN"
            xpn_file_path = os.path.join(self.xpn_folder_path, xpn_file_name)

            if not os.path.exists(xpn_file_path):
                logger.error(f"Corresponding .xpn file not found at: {xpn_file_path}")
                continue

            with open(xpr_file_path, 'r') as f:
                self.xpr_header = "".join([next(f) for _ in range(4)])

            reader_xpr = XPRReader(xpr_file_path)
            self.xpr_df = reader_xpr.read()
            reader_xpn = XPNReader(xpn_file_path)
            self.xpn_df = reader_xpn.read()

            if self.xpr_df is None or self.xpn_df is None:
                logger.error("Failed to read XPR or XPN files.")
                continue

            self.original_report_df = compute_report(self.xpn_df, self.xpr_df)
            self.current_report_df = self.original_report_df.copy()
            
            reports_dir = "Reports"
            os.makedirs(reports_dir, exist_ok=True)
            original_output_path = os.path.join(reports_dir, f"{self.base_name}_original.csv")
            self.original_report_df.rename(columns={'Point# (XPN)': 'Point#', 'XPN X': 'Original X', 'XPN Y': 'Original Y', 'XPN Z': 'Original Z', 'XPR X': 'Actual X', 'XPR Y': 'Actual Y', 'XPR Z': 'Actual Z'}).to_csv(original_output_path, index=False)
            logger.info(f"Original report saved to {original_output_path}")
            
            self.handle_autocorrection(self.current_report_df, logger)
        
        messagebox.showinfo("Success", "Processing complete. Check logs for details.")

    def handle_autocorrection(self, report_df, logger):
        if 'Out of spec' in report_df['Remarks'].values:
            self.current_report_df = apply_correction(self.current_report_df.copy(), logger=logger)
            
            reports_dir = "Reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            corrected_csv_path = os.path.join(reports_dir, f"{self.base_name}_corrected.csv")
            renamed_df = self.current_report_df.rename(columns={'Point# (XPN)': 'Point#', 'XPN X': 'Original X', 'XPN Y': 'Original Y', 'XPN Z': 'Original Z', 'XPR X': 'Actual X', 'XPR Y': 'Actual Y', 'XPR Z': 'Actual Z'})
            renamed_df.to_csv(corrected_csv_path, index=False)
            logger.info(f"Corrected CSV report saved to {corrected_csv_path}")
            
            corrected_pdf_path = os.path.join(reports_dir, f"{self.base_name}_corrected.pdf")
            save_df_to_pdf(renamed_df.drop(columns=['I', 'J', 'K']), corrected_pdf_path)
            logger.info(f"Corrected PDF report saved to {corrected_pdf_path}")
            
            self.write_corrected_xpr(logger)
        else:
            logger.info("No 'Out of spec' remarks found. No correction applied.")

    def write_corrected_xpr(self, logger):
        reports_dir = "Reports"
        corrected_xpr_path = os.path.join(reports_dir, f"{self.base_name}_Correction.XPR")
        
     
        # generate_cmm_report(self.current_report_df,  os.path.join(reports_dir, f"{self.base_name}_CMM_Report.pdf"), self.base_name, logger=logger)

        corrected_xpr_df = self.current_report_df[['Point# (XPN)', 'XPR X', 'XPR Y', 'XPR Z', 'I', 'J', 'K']].copy()
        corrected_xpr_df.columns = ['Point#', 'X', 'Y', 'Z', 'I', 'J', 'K']
        with open(corrected_xpr_path, 'w') as f:
            f.write(self.xpr_header)
            corrected_xpr_df.to_csv(f, sep=' ', header=False, index=False, lineterminator='\n')
        logger.info(f"Corrected XPR file saved to {corrected_xpr_path}")

    

    

if __name__ == "__main__":
    app = TurbineUI()
    app.mainloop()
