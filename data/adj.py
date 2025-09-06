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
            
            data_start_index = -1
            for i, line in enumerate(lines):
                if header_start_line in line:
                    data_start_index = i + 2
                    break
            
            if data_start_index == -1:
                raise ValueError("Could not find the start of the data in the file.")
                
            data_lines = "".join(lines[data_start_index:])
            df = pd.read_csv(StringIO(data_lines), sep=r'\s+', header=None)
            return df
            
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the input file is available.")
        raise
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        raise

def main():
    """Main function to perform point matching, correction, and generate the report with correction magnitude."""
    
    try:
        xpn_df_raw = read_data_robust("NOM/SEC_A4.XPN", "Point      User Co-ordinates")
        xpr_df_raw = read_data_robust("SEC_A4.XPR", "Point      User Co-ordinates")
    except (FileNotFoundError, ValueError, Exception) as e:
        print("Script halted due to a file reading error.")
        return

    # Assign column names and convert to numeric
    xpn_df = xpn_df_raw.copy()
    xpn_df.columns = ['Point#', 'X', 'Y', 'Z', 'I', 'J', 'K', 'HTol', 'LTol']
    xpn_df[['X', 'Y', 'Z', 'HTol', 'LTol']] = xpn_df[['X', 'Y', 'Z', 'HTol', 'LTol']].apply(pd.to_numeric, errors='coerce')
    xpn_df.dropna(subset=['X', 'Y', 'Z'], inplace=True)
    
    xpr_df = xpr_df_raw.copy()
    xpr_df.columns = ['Point#', 'X', 'Y', 'Z', 'I', 'J', 'K']
    xpr_df[['X', 'Y', 'Z']] = xpr_df[['X', 'Y', 'Z']].apply(pd.to_numeric, errors='coerce')
    xpr_df.dropna(subset=['X', 'Y', 'Z'], inplace=True)

    # Compute initial deviations
    xpn_coords = xpn_df[['X', 'Y', 'Z']].to_numpy()
    xpr_coords = xpr_df[['X', 'Y', 'Z']].to_numpy()
    dist_matrix = distance_matrix(xpn_coords, xpr_coords)
    min_deviations = dist_matrix.min(axis=1)
    closest_xpr_indices = dist_matrix.argmin(axis=1)

    # Store the corresponding original XPR coords and normals to apply corrections
    matched_xpr_coords = xpr_df.iloc[closest_xpr_indices][['X', 'Y', 'Z']].to_numpy()
    matched_xpr_normals = xpr_df.iloc[closest_xpr_indices][['I', 'J', 'K']].to_numpy()

    # Calculate corrected coordinates
    corrected_coords = np.zeros_like(xpn_coords)
    for i in range(len(xpn_coords)):
        dev = min_deviations[i]
        htol = xpn_df.loc[xpn_df.index[i], 'HTol']
        xpn_p = xpn_coords[i]
        xpr_p = matched_xpr_coords[i]

        if dev > htol and dev > 0:
            direction_vector = (xpr_p - xpn_p) / dev
            corrected_coords[i] = xpn_p + direction_vector * htol
        else:
            corrected_coords[i] = xpr_p
            
    # Calculate the magnitude of the correction
    correction_magnitudes = np.linalg.norm(corrected_coords - matched_xpr_coords, axis=1)

    # Create the new corrected XPR DataFrame, ensuring it's in order
    xpr_corrected_df = pd.DataFrame({
        'Point#': xpn_df['Point#'].to_numpy(),
        'X': corrected_coords[:, 0],
        'Y': corrected_coords[:, 1],
        'Z': corrected_coords[:, 2],
        'I': matched_xpr_normals[:, 0],
        'J': matched_xpr_normals[:, 1],
        'K': matched_xpr_normals[:, 2]
    })
    
    # Save the corrected XPR data to a new file, now correctly ordered
    corrected_xpr_filepath = Path("SEC_A4_corrected_sorted_with_correction_mag.XPR")
    with open(corrected_xpr_filepath, 'w') as f:
        f.write("Raw Scan Data Listing                             Units:MM\n")
        f.write("Data Seq:X,Y,Z,I,J,K\n")
        f.write("Point      User Co-ordinates\n")
        f.write("Number\n")
    xpr_corrected_df.to_csv(corrected_xpr_filepath, sep='\t', mode='a', index=False, header=False, float_format='%.4f')
    print(f"✅ Generated corrected and sorted XPR file at: {corrected_xpr_filepath.resolve()}")

    # Generate the final report using the corrected data
    final_report_df = xpn_df[['Point#', 'X', 'Y', 'Z', 'HTol']].copy()
    final_report_df.columns = ['Point# (XPN)', 'XPN X', 'XPN Y', 'XPN Z', 'HTol']
    
    final_report_df['XPR X'] = xpr_corrected_df['X'].to_numpy()
    final_report_df['XPR Y'] = xpr_corrected_df['Y'].to_numpy()
    final_report_df['XPR Z'] = xpr_corrected_df['Z'].to_numpy()
    
    final_deviations = np.linalg.norm(final_report_df[['XPN X', 'XPN Y', 'XPN Z']].to_numpy() - final_report_df[['XPR X', 'XPR Y', 'XPR Z']].to_numpy(), axis=1)
    final_report_df['Deviation'] = final_deviations
    final_report_df['Error'] = final_report_df['Deviation'] - final_report_df['HTol']
    final_report_df['Correction_Magnitude'] = correction_magnitudes
    final_report_df['Remarks'] = np.where(final_report_df['Deviation'] <= final_report_df['HTol'], 'Within tolerance', 'Out of spec')
    
    # Round numerical columns for a cleaner output
    final_report_df = final_report_df.round(3)

    # Save the final report to a CSV file
    output_filepath = Path("Point_Deviation_Toleranced_Sorted_Report_with_Correction.csv")
    final_report_df.to_csv(output_filepath, index=False)

    print(f"✅ Final toleranced and sorted report successfully saved to: {output_filepath.resolve()}")
    print(final_report_df.head())

if __name__ == "__main__":
    main()
