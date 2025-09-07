import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import numpy as np

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

def display_combined_plot(app):
    frame = ttk.LabelFrame(app.data_plot_frame, text="Combined Scatter Plot", padding="10")
    frame.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")

    xpr_df_copy = app.xpr_df.copy()
    xpr_df_copy['source'] = 'Actual'
    xpn_df_copy = app.xpn_df.copy()
    xpn_df_copy['source'] = 'Original'

    combined_df = pd.concat([xpr_df_copy, xpn_df_copy], ignore_index=True)

    fig, ax = plt.subplots(figsize=(5, 4))
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    if len(combined_df.columns) < 2:
        ttk.Label(frame, text="Data does not have enough columns for a scatter plot.").pack()
        return

    x_axis_var = tk.StringVar(value=combined_df.columns[1])
    y_axis_var = tk.StringVar(value=combined_df.columns[2])

    def update_plot(*args):
        ax.clear()
        colors = {'Actual': 'r', 'Original': 'b'}
        ax.scatter(combined_df[x_axis_var.get()], combined_df[y_axis_var.get()], c=combined_df['source'].map(colors))
        ax.set_xlabel(x_axis_var.get())
        ax.set_ylabel(y_axis_var.get())
        ax.set_title("Combined Scatter Plot")
        canvas.draw()

    controls_frame = ttk.Frame(frame)
    controls_frame.pack(fill=tk.X)

    ttk.Label(controls_frame, text="X-axis:").pack(side=tk.LEFT, padx=5)
    x_axis_menu = ttk.Combobox(controls_frame, textvariable=x_axis_var, values=list(combined_df.columns))
    x_axis_menu.pack(side=tk.LEFT, padx=5)

    ttk.Label(controls_frame, text="Y-axis:").pack(side=tk.LEFT, padx=5)
    y_axis_menu = ttk.Combobox(controls_frame, textvariable=y_axis_var, values=list(combined_df.columns))
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
        the_table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(8)
        the_table.scale(1.2, 1.2)

        plt.title(f"{title} - Table", fontsize=12, pad=20)
        pp.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # --- Page 2: Scatter Plot (Nominal vs Raw) ---
        fig, ax = plt.subplots(figsize=(6, 5))

        ax.scatter(df['XPN X'], df['XPN Y'], c='b', label='XPN - Nominal Data')
        ax.scatter(df['XPR X'], df['XPR Y'], c='r', label='XPR - Raw Data')

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(f"{title} - Scatter Plot")
        ax.legend(loc="best")

        pp.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # --- Page 3: Deviation heatmap scatter ---
        if "Deviation" in df.columns:
            fig, ax = plt.subplots(figsize=(6, 5))
            sc = ax.scatter(df['XPN X'], df['XPN Y'], c=df['Deviation'],
                            cmap='viridis', s=40, edgecolors='k')

            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_title(f"{title} - Deviation Map")

            # Add colorbar
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label("Deviation")

            pp.savefig(fig, bbox_inches='tight')
            plt.close(fig)


    def generate_cmm_report(df, features, output_pdf, logger=None):
        with PdfPages(output_pdf) as pp:
            # Page 1: Cover & Summary
            fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape
            ax.axis("off")
            ax.text(0.5, 0.9, "CMM INSPECTION REPORT", ha="center", fontsize=20, weight="bold")

            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ax.text(0.5, 0.85, f"Generated: {now}", ha="center", fontsize=10)

            # Placeholders for customer info
            ax.text(0.05, 0.78, "Customer: ____________________", fontsize=11)
            ax.text(0.05, 0.74, "Project: _____________________", fontsize=11)
            ax.text(0.05, 0.70, "Drawing No: _________________", fontsize=11)
            ax.text(0.05, 0.66, "Report No: __________________", fontsize=11)

            # Features
            y = 0.58
            ax.text(0.05, y, "Geometric Features:", fontsize=12, weight="bold")
            for k, v in features.items():
                y -= 0.04
                ax.text(0.07, y, f"{k}: {v:.4f}" if isinstance(v, (int, float, np.floating)) else f"{k}: {v}", fontsize=10)

            pp.savefig(fig, bbox_inches="tight")
            plt.close(fig)

            # Page 2+: Data table
            df_print = df.round(4)
            max_rows = 35
            for start in range(0, len(df_print), max_rows):
                subset = df_print.iloc[start:start+max_rows]
                fig, ax = plt.subplots(figsize=(11.69, 8.27))
                ax.axis("off")
                table = ax.table(cellText=subset.values, colLabels=subset.columns, loc="center")
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                table.scale(1.1, 1.2)
                ax.set_title(f"Corrected Data Rows {start+1}-{min(start+max_rows, len(df_print))}", fontsize=11)
                pp.savefig(fig, bbox_inches="tight")
                plt.close(fig)

            # Scatter Plot (Nominal vs Raw)
            fig, ax = plt.subplots(figsize=(8,6))
            ax.scatter(df['XPN X'], df['XPN Y'], c='blue', label="XPN - Nominal Data")
            ax.scatter(df['XPR X'], df['XPR Y'], c='red', label="XPR - Corrected Raw Data")
            ax.set_xlabel("X"); ax.set_ylabel("Y")
            ax.set_title("Nominal vs Corrected Raw (Top view)")
            ax.legend()
            pp.savefig(fig, bbox_inches="tight"); plt.close(fig)

            # Deviation Heatmap
            if "Deviation" in df.columns:
                fig, ax = plt.subplots(figsize=(8,6))
                sc = ax.scatter(df['XPN X'], df['XPN Y'], c=df['Deviation'], cmap="plasma", s=40, edgecolors="k")
                plt.colorbar(sc, ax=ax, label="Deviation")
                ax.set_xlabel("X"); ax.set_ylabel("Y")
                ax.set_title("Deviation Map")
                pp.savefig(fig, bbox_inches="tight"); plt.close(fig)

            # Histogram
            if "Deviation" in df.columns:
                fig, ax = plt.subplots(figsize=(8,6))
                ax.hist(df['Deviation'], bins=40)
                ax.set_title("Deviation Distribution")
                ax.set_xlabel("Deviation"); ax.set_ylabel("Count")
                pp.savefig(fig, bbox_inches="tight"); plt.close(fig)

        if logger:
            logger.info(f"Inspection report saved: {output_pdf}")
        else:
            print(f"✅ Inspection report saved: {output_pdf}")