import tkinter as tk
from tkinter import ttk, messagebox
from data_reader.xpr_reader import XPRReader
from data_reader.xpn_reader import XPNReader
import os

from ui.file_operations import load_xpr_folder, load_xpn_folder, find_file_in_dir
from ui.data_processing import compute_report, apply_correction
from ui.ui_components import display_dataframe, display_combined_plot

class TurbineUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Turbine Data Visualizer")
        self.geometry("1200x800")

        self.xpr_df = None
        self.xpn_df = None
        self.xpr_folder_path = None
        self.xpn_folder_path = None

        # Create a canvas and a scrollbar
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack everything
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Content of the scrollable frame ---
        main_frame = self.scrollable_frame

        # File selection frame
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

        submit_button = ttk.Button(file_frame, text="Submit", command=self.process_files)
        submit_button.grid(row=2, column=0, pady=10)

        exit_button = ttk.Button(file_frame, text="Exit", command=self.destroy)
        exit_button.grid(row=2, column=1, pady=10)

        # Data display and plot frame
        self.data_plot_frame = ttk.Frame(main_frame)
        self.data_plot_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

    def process_files(self):
        if not self.xpr_folder_path:
            messagebox.showerror("Error", "Please select a RAW folder.")
            return

        if not self.xpn_folder_path:
            messagebox.showerror("Error", "Please select a NOM folder.")
            return

        xpr_file = find_file_in_dir(self.xpr_folder_path, ".xpr")

        if not xpr_file:
            messagebox.showerror("Error", "No .xpr file found in the selected RAW folder.")
            return

        base_name = os.path.basename(xpr_file).split('.')[0]
        xpn_file_name = base_name + ".XPN"
        xpn_file = os.path.join(self.xpn_folder_path, xpn_file_name)

        if not os.path.exists(xpn_file):
            messagebox.showerror("Error", f"Corresponding .xpn file not found at: {xpn_file}")
            return

        # Clear previous data
        for widget in self.data_plot_frame.winfo_children():
            widget.destroy()
        
        # Process XPR file
        reader_xpr = XPRReader(xpr_file)
        self.xpr_df = reader_xpr.read()

        # Process XPN file
        reader_xpn = XPNReader(xpn_file)
        self.xpn_df = reader_xpn.read()

        if self.xpr_df is not None and self.xpn_df is not None:
            display_combined_plot(self)
            
            self.original_report_df = compute_report(self.xpn_df, self.xpr_df)
            self.current_report_df = self.original_report_df.copy()
            
            # Display original report
            display_dataframe(self, self.original_report_df, "Original Deviation Report", 6)

            self.correction_row_counter = 7

            def setup_correction_ui(report_df):
                if 'Out of spec' in report_df['Remarks'].values:
                    out_of_spec_count = (report_df['Remarks'] == 'Out of spec').sum()
                    
                    correction_frame = ttk.LabelFrame(self.data_plot_frame, text="Apply Correction", padding="10")
                    correction_frame.grid(row=self.correction_row_counter, column=0, padx=10, pady=5, sticky="nsew")

                    count_label = ttk.Label(correction_frame, text=f"Out of spec count: {out_of_spec_count}")
                    count_label.pack(anchor='ne')

                    autocorrect_var = tk.BooleanVar()
                    autocorrect_check = ttk.Checkbutton(correction_frame, text="Autocorrection", variable=autocorrect_var)
                    autocorrect_check.pack(side=tk.LEFT, padx=5)

                    def apply_and_redisplay():
                        if not autocorrect_var.get():
                            messagebox.showinfo("Info", "Please check the 'Autocorrection' box to apply the correction.")
                            return

                        self.current_report_df = apply_correction(self.current_report_df.copy())
                        
                        # Destroy the current correction UI
                        correction_frame.destroy()
                        
                        # Display the new corrected report
                        display_dataframe(self, self.current_report_df, f"Corrected Report", self.correction_row_counter)
                        self.correction_row_counter += 1
                        
                        # Setup the next correction UI
                        setup_correction_ui(self.current_report_df)

                    correction_button = ttk.Button(correction_frame, text="Apply", command=apply_and_redisplay)
                    correction_button.pack(side=tk.LEFT, padx=5)

            setup_correction_ui(self.current_report_df)

if __name__ == "__main__":
    app = TurbineUI()
    app.mainloop()
