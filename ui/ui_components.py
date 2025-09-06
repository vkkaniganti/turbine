import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

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
