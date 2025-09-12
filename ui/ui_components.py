import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import numpy as np
from utils.cmm_calculations import compute_max_thickness,compute_chord_length,compute_le_thickness,compute_te_thickness,compute_axis_alignment
from scipy.spatial import distance_matrix

def format_value(value, precision=3):
    if isinstance(value, (int, float)):
        return f"{value:.{precision}f}"
    return "N/A"

def display_dataframe(app, df, title, row):
    frame = ttk.LabelFrame(app.data_plot_frame, text=title, padding="10")
    frame.grid(row=row, column=0, padx=10, pady=5, sticky="nsew")
    
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)
    
    tree["columns"] = list(df.columns)
    tree["show"] = "headings"

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for index, row_data in df.iterrows():
        tree.insert("", "end", values=list(row_data))

    tree.pack(fill=tk.BOTH, expand=True)

def display_scatter_plot(app, df, title, row, x_key, y_key):
    frame = ttk.LabelFrame(app.data_plot_frame, text=title, padding="10")
    frame.grid(row=row, column=0, padx=10, pady=5, sticky="nsew")

    if len(df.columns) < 2:
        ttk.Label(frame, text="Data does not have enough columns for a scatter plot.").pack()
        return

    fig, ax = plt.subplots(figsize=(5, 4))
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    x_axis_var = tk.StringVar(value=df.columns[0])
    y_axis_var = tk.StringVar(value=df.columns[1])

    def update_plot(*args):
        ax.clear()
        ax.scatter(df[x_axis_var.get()], df[y_axis_var.get()])
        ax.set_xlabel(x_axis_var.get())
        ax.set_ylabel(y_axis_var.get())
        ax.set_title(title)
        canvas.draw()

    controls_frame = ttk.Frame(frame)
    controls_frame.pack(fill=tk.X)

    ttk.Label(controls_frame, text="X-axis:").pack(side=tk.LEFT, padx=5)
    x_axis_menu = ttk.Combobox(controls_frame, textvariable=x_axis_var, values=list(df.columns))
    x_axis_menu.pack(side=tk.LEFT, padx=5)

    ttk.Label(controls_frame, text="Y-axis:").pack(side=tk.LEFT, padx=5)
    y_axis_menu = ttk.Combobox(controls_frame, textvariable=y_axis_var, values=list(df.columns))
    y_axis_menu.pack(side=tk.LEFT, padx=5)

    x_axis_var.trace("w", update_plot)
    y_axis_var.trace("w", update_plot)

    update_plot()

def display_combined_plot_from_df(app, df, title, row, pdf_path=None):
    frame = ttk.LabelFrame(app.data_plot_frame, text=title, padding="10")
    frame.grid(row=row, column=0, padx=10, pady=5, sticky="nsew")

    xpn_df = df[['XPN X', 'XPN Y']].copy()
    xpn_df.columns = ['X', 'Y']
    xpn_df['source'] = 'Nominal'

    xpr_df = df[['XPR X', 'XPR Y']].copy()
    xpr_df.columns = ['X', 'Y']
    xpr_df['source'] = 'Actual'

    combined_df = pd.concat([xpn_df, xpr_df], ignore_index=True)

    fig, ax = plt.subplots(figsize=(5, 4))
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    if len(combined_df.columns) < 2:
        ttk.Label(frame, text="Data does not have enough columns for a scatter plot.").pack()
        return

    def update_plot(*args):
        ax.clear()
        colors = {'Nominal': 'b', 'Actual': 'r'}
        ax.scatter(combined_df['X'], combined_df['Y'], c=combined_df['source'].map(colors))
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(title)
        canvas.draw()

    update_plot()

    if pdf_path:
        fig.savefig(pdf_path, bbox_inches='tight')
        
def save_df_to_pdf(df, path, title="Data Report"):
    with PdfPages(path) as pp:
        # --- Page 1: Table ---
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.axis('tight')
        ax.axis('off')

        # Prepare column widths
        num_columns = len(df.columns)
        if num_columns > 0:
            # Set last column to be wider, e.g., 15% of table width
            width_last_col = 0.15
            
            if num_columns > 1:
                # Distribute the rest of the width among other columns
                width_other_cols = (1.0 - width_last_col) / (num_columns - 1)
                col_widths = [width_other_cols] * (num_columns - 1) + [width_last_col]
            else:
                # If only one column, it takes up the full width
                col_widths = [1.0]
            
            the_table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', colWidths=col_widths)
            if num_columns > 1:
                the_table.auto_set_column_width(col=list(range(num_columns - 1)))
        else:
            # Fallback for empty dataframe
            the_table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(8)
        the_table.scale(1.2, 1.2)

        plt.title(f"{title} - Table", fontsize=12, pad=20)
        pp.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # --- Page 2: Scatter Plot (Nominal vs Raw) ---
        fig, ax = plt.subplots(figsize=(6, 5))

        ax.scatter(df['Original X'], df['Original Y'], c='b', label='XPN - Nominal Data')
        ax.scatter(df['Actual X'], df['Actual Y'], c='r', label='XPR - Raw Data')

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(f"{title} - Scatter Plot")
        ax.legend(loc="best")

        pp.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # --- Page 3: Deviation heatmap scatter ---
        if "Deviation" in df.columns:
            fig, ax = plt.subplots(figsize=(6, 5))
            sc = ax.scatter(df['Original X'], df['Original Y'], c=df['Deviation'],
                            cmap='viridis', s=40, edgecolors='k')

            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_title(f"{title} - Deviation Map")

            # Add colorbar
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label("Deviation")

            pp.savefig(fig, bbox_inches='tight')
            plt.close(fig)

def get_diff_error(nominal, actual):
    if isinstance(nominal, (int, float)) and isinstance(actual, (int, float)):
        diff = actual - nominal
        error = abs(diff)
        return f"{diff:.3f}", f"{error:.3f}"
    return "N/A", "N/A"

def compute_geometric_features(report_df):
    actual_df = report_df[['XPR X', 'XPR Y', 'XPR Z', 'I', 'J', 'K']].copy()
    actual_df.columns = ['X', 'Y', 'Z', 'I', 'J', 'K']
    nominal_df = report_df[['XPN X', 'XPN Y', 'XPN Z']].copy()
    nominal_df.columns = ['X', 'Y', 'Z']

    points_xpn = report_df[['XPN X', 'XPN Y']].to_numpy()
    points_xpr = report_df[['XPR X', 'XPR Y']].to_numpy()

    #MAX. THICK - Cmax
    nominal_max_thickness = list(compute_max_thickness(points_xpn, section="N1").values())[0]
    actual_max_thickness = list(compute_max_thickness(points_xpr, section="N1").values())[0]

    # Chord length (X max - X min)
    actual_chord_length = actual_df['X'].max() - actual_df['X'].min()
    nominal_chord_length = nominal_df['X'].max() - nominal_df['X'].min()


    #LE CHORD LENGTH -B1
    nominal_le_chord_length_b1 = list(compute_chord_length(points_xpn, section="B1").values())[0]
    actual_le_chord_length_b1 = list(compute_chord_length(points_xpr, section="B1").values())[0]

    #TE CHORD LENGTH -B2
    nominal_te_chord_length_b2 = list(compute_chord_length(points_xpn, section="B2").values())[0]
    actual_te_chord_length_b2 = list(compute_chord_length(points_xpr, section="B2").values())[0]
    
    #LE THICKNESS- N1 @ 2 mm_C1
    nominal_le_thickness_C1 = list(compute_le_thickness(points_xpn, section="N1", offset_mm=2.0, tol=0.3).values())[0]
    actual_le_thickness_C1 = list(compute_le_thickness(points_xpr, section="N1", offset_mm=2.0, tol=0.3).values())[0]
    
    #TE THICKNESS- N1 @ 2 mm_C3
    nominal_te_thickness_C3 = list(compute_te_thickness(points_xpn, section="N1", offset_mm= (nominal_chord_length - 2.0), tol=0.3).values())[0]
    actual_te_thickness_C3 = list(compute_te_thickness(points_xpr, section="N1", offset_mm= (actual_chord_length - 2.0), tol=0.3).values())[0]

    # X AXIS ALIGNMENT, Y AXIS ALIGNMENT
    alignment = compute_axis_alignment(points_xpn, points_xpr, section="N1")
    x_align = alignment[f"X AXIS ALIGNMENT - N1"]
    y_align = alignment[f"Y AXIS ALIGNMENT - N1"]

    rot_align = np.degrees(np.arctan2(np.mean(actual_df["J"]), np.mean(actual_df["I"])))

    # Profile deviation from the main report
    max_deviation = report_df['Deviation'].max()
    min_deviation = report_df['Deviation'].min()
    max_dev_point_no = report_df.loc[report_df['Deviation'].idxmax(), 'Point# (XPN)']
    min_dev_point_no = report_df.loc[report_df['Deviation'].idxmin(), 'Point# (XPN)']

    return {
        "MAX. THICK - Cmax actual": actual_max_thickness,
        "MAX. THICK - Cmax nominal": nominal_max_thickness,
        "Chord Length Nominal": nominal_chord_length,
        "Chord Length Actual": actual_chord_length,
        "LE Chord Length B1 Nominal": nominal_le_chord_length_b1,
        "LE Chord Length B1 Actual": actual_le_chord_length_b1,
        "TE Chord Length B2 Nominal": nominal_te_chord_length_b2,
        "TE Chord Length B2 Actual": actual_te_chord_length_b2,
        "LE Thickness Nominal": nominal_le_thickness_C1,
        "LE Thickness Actual": actual_le_thickness_C1,
        "TE Thickness Nominal": nominal_te_thickness_C3,
        "TE Thickness Actual": actual_te_thickness_C3,
        "X Alignment": x_align,
        "Y Alignment": y_align,
        "Rotation Alignment": rot_align,
        "Max Profile Error": max_deviation,
        "Min Profile Error": min_deviation,
        "Max Profile Error Point No": max_dev_point_no,
        "Min Profile Error Point No": min_dev_point_no,
        "TETA": rot_align
    }

def generate_cmm_report(report_df, output_pdf, base_name, logger=None):
    features = compute_geometric_features(report_df)
    with PdfPages(output_pdf) as pp:
        fig, ax = plt.subplots(figsize=(16, 9))
        ax.axis("off")

        # ---------------- HEADER ----------------
        ax.text(0.01, 0.95, "[ENNEM EXCEL LOGO]", ha="left", fontsize=10)
        ax.text(0.5, 0.95, "ENNEM EXCEL ENGINEERING PRIVATE LIMITED",
                ha="center", fontsize=14, weight="bold")
        ax.text(0.5, 0.92, "E-7 & D-6, INDUSTRIAL ESTATE, PATANCHERU-502319", ha="center", fontsize=10)
        ax.text(0.5, 0.89, "SANGA REDDY DIST., TELANGANA STATE", ha="center", fontsize=10)
        ax.text(0.99, 0.95, "[Nikon LOGO]", ha="right", fontsize=10)

        # ---------------- TITLE ----------------
        ax.text(0.5, 0.82, "CMM INSPECTION REPORT", ha="center", fontsize=16, weight="bold")

        # ---------------- METADATA TABLE ----------------
        meta_top = [
            ["DRAWING NO", "", "REPORT NO", ""],
            ["DESCRIPITION", "", "DATE", ""],
            ["STAGE", "", "BLADE NO", ""]
        ]
        meta_bottom = [
            ["CUSTOMER NAME", ""],
            ["P.O NO/DC NO.", ""],
            ["PROJECT", ""]
        ]

        # Top metadata table
        meta_table_top = ax.table(
            cellText=meta_top,
            loc='center',
            cellLoc='left',
            bbox=[0.05, 0.70, 0.9, 0.10]
        )
        meta_table_top.auto_set_font_size(False)
        meta_table_top.set_fontsize(9)
        for row in range(len(meta_top)):
            for col in range(4):
                cell = meta_table_top[(row, col)]
                cell.set_linewidth(0.8)
                if col % 2 == 0:
                    cell.set_text_props(weight="bold")
                    cell.set_width(0.20)
                else:
                    cell.set_width(0.25)

        # Bottom metadata table
        meta_table_bottom = ax.table(
            cellText=meta_bottom,
            loc='center',
            cellLoc='left',
            bbox=[0.05, 0.62, 0.9, 0.06]
        )
        meta_table_bottom.auto_set_font_size(False)
        meta_table_bottom.set_fontsize(9)
        for row in range(len(meta_bottom)):
            for col in range(2):
                cell = meta_table_bottom[(row, col)]
                cell.set_linewidth(0.8)
                if col == 0:
                    cell.set_text_props(weight="bold")
                    cell.set_width(0.36)
                else:
                    cell.set_width(0.54)

        # ---------------- SECTION TITLE ----------------
        ax.text(0.5, 0.58, f"160.AEROFOIL SECTION # {base_name} @ 209mm",
                ha="center", fontsize=12, weight="bold")

        # ---------------- MAIN DATA TABLE ----------------
        col_labels = [
            'Sl.No', 'DESCRIPITION', 'NOMINAL', 'ACTUAL',
            'HIGH-TOL', 'LOW-TOL', 'DIFFERENCE', 'ERROR', 'REMARKS'
        ]

        # Sl.No and Description content from template (PDF)
        slno_values = [
            "114&193", "178", "168", "167", "176&195", "180&189", "68", "69", "",
            "107", "", "107", "", "166"
        ]
        desc_values = [
            "MAX. THICK - Cmax", "CHORD LENGTH - B", "LE  CHORD LENGTH -B1", "TE  CHORD LENGTH -B2",
            "LE THICKNESS- N1 @ 2 mm_C1", "TE THICKNESS- N1 @ 2 mm_C3", "X  AXIS ALIGNMENT",
            "Y  AXIS ALIGNMENT", "ROTATION AXIS ALIGNMENT - DEG",
            "PROF. FORM  MAX", "PROF. FORM  MAX OCCURS POINT NO.",
            "PROF. FORM  MIN", "PROF. FORM  MIN OCCURS POINT NO.",
            "TETA"
        ]

        nrows = len(slno_values)
        ncols = len(col_labels)

        # Fill only Sl.No + Description, keep others blank
        table_data = []
        for i in range(nrows):
            row_data = [""] * ncols
            row_data[0] = slno_values[i]
            row_data[1] = desc_values[i]
            table_data.append(row_data)

        main_table = ax.table(
            cellText=table_data,
            colLabels=col_labels,
            loc='center',
            cellLoc='center',
            bbox=[0.05, 0.05, 0.9, 0.5]
        )
        main_table.auto_set_font_size(False)
        main_table.set_fontsize(8)

        # Adjust column widths (Sl.No narrow, Description wide, others equal)
        total_width = 0.9
        slno_w = 0.07   # 7% width
        desc_w = 0.23   # 23% width
        other_w = (total_width - slno_w - desc_w) / (ncols - 2)

        for col in range(ncols):
            for row in range(nrows + 1):  # +1 header
                cell = main_table[(row, col)]
                cell.set_linewidth(0.8)
                if col == 0:
                    cell.set_width(slno_w)
                elif col == 1:
                    cell.set_width(desc_w)
                    cell.set_text_props(ha="left")  # left-align descriptions
                else:
                    cell.set_width(other_w)

                # Header row styling
                if row == 0:
                    cell.set_text_props(weight="bold", color="white")
                    cell.set_facecolor("#4F81BD")
                else:
                    if row % 2 == 0:
                        cell.set_facecolor("#F2F2F2")
                    else:
                        cell.set_facecolor("white")

        # ---------------- FOOTER ----------------
        ax.text(0.1, 0.02, "Inspected by:", ha="left", fontsize=10)
        ax.text(0.5, 0.02, "Reviewed by:", ha="center", fontsize=10)
        ax.text(0.9, 0.02, "Reviewed/Witnessed by:", ha="right", fontsize=10)

        # ---------------- SAVE ----------------
        pp.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    if logger:
        logger.info(f"Inspection report saved: {output_pdf}")
    else:
        print(f"✅ Inspection report saved: {output_pydf}")