from data_reader.xpr_reader import XPRReader
from data_reader.xpn_reader import XPNReader
from visualizer.scatter_plot import plot_scatter
from utils.file_handler import validate_file

def main():
    # Example: Replace with input() or CLI args later
    xpr_file = "data/sample.xpr"
    xpn_file = "data/sample.xpn"

    # Validate files
    validate_file(xpr_file, [".xpr"])
    validate_file(xpn_file, [".xpn"])

    # Read data
    xpr_data = XPRReader(xpr_file).read()
    xpn_data = XPNReader(xpn_file).read()

    print("XPR Data:", xpr_data[:5])  # Preview first 5 rows
    print("XPN Data:", xpn_data[:5])

    # Example: Scatter plot (you can adapt x/y columns later)
    plot_scatter(xpr_data, x_col=0, y_col=1, title="XPR Data Scatter Plot")

if __name__ == "__main__":
    main()
