import pandas as pd
import numpy as np
from scipy.spatial import distance_matrix
from pathlib import Path
from io import StringIO

def read_data_robust(filepath, header_start_line):
    """
    Reads data from a file, skipping the header lines to avoid parsing errors.
    
    Args:
        filepath (str): The path to the file.
        header_start_line (str): A string that marks the start of the header section.
        
    Returns:
        pd.DataFrame: A DataFrame containing the parsed data.
    """
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
            # Find the line that marks the start of the data, after the header
            data_start_index = -1
            for i, line in enumerate(lines):
                if header_start_line in line:
                    # The data starts 2 lines after "Point      User Co-ordinates"
                    data_start_index = i + 2
                    break
            
            if data_start_index == -1:
                raise ValueError("Could not find the start of the data in the file.")
                
            # Create a string buffer with only the data lines
            data_lines = "".join(lines[data_start_index:])
            
            # Read the data into a DataFrame
            df = pd.read_csv(StringIO(data_lines), sep=r'\s+', header=None)
            return df
            
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the input file is available.")
        raise
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        raise

def main():
    """Main function to perform point matching and save the report."""
    
    # Read nominal and actual data using the robust function
    try:
        xpn_df_raw = read_data_robust("SEC_A4.XPN", "Point      User Co-ordinates")
        xpr_df_raw = read_data_robust("SEC_A4.XPR", "Point      User Co-ordinates")
    except (FileNotFoundError, ValueError, Exception) as e:
        print("Script halted due to a file reading error.")
        return

    # Manually assign column names
    xpn_df = xpn_df_raw.copy()
    xpn_df.columns = ['Point#', 'X', 'Y', 'Z', 'I', 'J', 'K', 'HTol', 'LTol']
    
    xpr_df = xpr_df_raw.copy()
    xpr_df.columns = ['Point#', 'X', 'Y', 'Z', 'I', 'J', 'K']

    # Convert relevant columns to numeric type
    xpn_df[['X', 'Y', 'Z', 'HTol', 'LTol']] = xpn_df[['X', 'Y', 'Z', 'HTol', 'LTol']].apply(pd.to_numeric, errors='coerce')
    xpr_df[['X', 'Y', 'Z']] = xpr_df[['X', 'Y', 'Z']].apply(pd.to_numeric, errors='coerce')

    # Drop any rows with NaN values
    xpn_df.dropna(subset=['X', 'Y', 'Z'], inplace=True)
    xpr_df.dropna(subset=['X', 'Y', 'Z'], inplace=True)

    # Extract X, Y, Z coordinates
    xpn_coords = xpn_df[['X', 'Y', 'Z']].to_numpy()
    xpr_coords = xpr_df[['X', 'Y', 'Z']].to_numpy()

    # Compute distance matrix and find minimum deviations
    dist_matrix = distance_matrix(xpn_coords, xpr_coords)
    min_deviations = dist_matrix.min(axis=1)
    closest_xpr_indices = dist_matrix.argmin(axis=1)

    # Create a new DataFrame for the report
    report_df = xpn_df[['Point#', 'X', 'Y', 'Z', 'HTol', 'LTol']].copy()
    report_df.columns = ['Point# (XPN)', 'XPN X', 'XPN Y', 'XPN Z', 'HTol', 'LTol']
    
    # Add the coordinates of the matched XPR points
    report_df['XPR X'] = xpr_df.iloc[closest_xpr_indices]['X'].to_numpy()
    report_df['XPR Y'] = xpr_df.iloc[closest_xpr_indices]['Y'].to_numpy()
    report_df['XPR Z'] = xpr_df.iloc[closest_xpr_indices]['Z'].to_numpy()
    report_df['Deviation'] = min_deviations

    # Calculate Error and Remarks
    report_df['Error'] = report_df['Deviation'] - report_df['HTol']
    report_df['Remarks'] = np.where(report_df['Deviation'] <= report_df['HTol'], 'Within tolerance', 'Out of spec')

    # Round numerical columns for a cleaner output
    report_df = report_df.round(3)

    # Save the DataFrame to a CSV file
    output_filepath = Path("Point_Deviation_Report_With_Tolerances.csv")
    report_df.to_csv(output_filepath, index=False)

    print(f"✅ Report successfully saved to: {output_filepath.resolve()}")

if __name__ == "__main__":
    main()
