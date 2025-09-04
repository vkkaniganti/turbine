import matplotlib.pyplot as plt

def plot_scatter(data, x_col=0, y_col=1, title="Scatter Plot"):
    x = [row[x_col] for row in data]
    y = [row[y_col] for row in data]

    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, alpha=0.7)
    plt.title(title)
    plt.xlabel(f"Column {x_col}")
    plt.ylabel(f"Column {y_col}")
    plt.grid(True)
    plt.show()
