import pandas as pd
import numpy as np
from scipy.spatial import distance_matrix
import logging

def compute_report(xpn_df_raw, xpr_df_raw):
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
    
    # Generate the final report using the corrected data
    final_report_df = xpn_df[['Point#', 'X', 'Y', 'Z', 'HTol', 'LTol']].copy()
    final_report_df.columns = ['Point# (XPN)', 'XPN X', 'XPN Y', 'XPN Z', 'HTol', 'LTol']
    
    final_report_df['XPR X'] = xpr_corrected_df['X'].to_numpy()
    final_report_df['XPR Y'] = xpr_corrected_df['Y'].to_numpy()
    final_report_df['XPR Z'] = xpr_corrected_df['Z'].to_numpy()
    final_report_df['I'] = xpr_corrected_df['I'].to_numpy()
    final_report_df['J'] = xpr_corrected_df['J'].to_numpy()
    final_report_df['K'] = xpr_corrected_df['K'].to_numpy()
    
    final_deviations = np.linalg.norm(final_report_df[['XPN X', 'XPN Y', 'XPN Z']].to_numpy() - final_report_df[['XPR X', 'XPR Y', 'XPR Z']].to_numpy(), axis=1)
    final_report_df['Deviation'] = final_deviations
    final_report_df['Error'] = final_report_df['Deviation'] - final_report_df['HTol']
    final_report_df['Correction_Magnitude'] = correction_magnitudes
    final_report_df['Remarks'] = np.where(final_report_df['Deviation'] <= final_report_df['HTol'], 'Within tolerance', 'Out of spec')
    
    # Round numerical columns for a cleaner output
    final_report_df = final_report_df.round(3)
    
    return final_report_df

def correct_deviation_batch(xpn_coords, xpr_coords, htol_array):
    """
    Vectorized correction for all points.
    Moves raw (XPR) points toward nominal (XPN) until within tolerance.
    """
    # Compute initial deviations
    deltas = xpn_coords - xpr_coords
    deviations = np.linalg.norm(deltas, axis=1)

    # Mask: points already within tolerance
    within_tol = deviations <= htol_array

    # Normalize direction vectors safely (avoid division by zero)
    direction_vectors = np.zeros_like(deltas)
    nonzero_mask = deviations > 0
    direction_vectors[nonzero_mask] = deltas[nonzero_mask] / deviations[nonzero_mask, None]

    # Distances to move = deviation - tolerance (only for out-of-spec points)
    correction_distances = np.maximum(deviations - htol_array, 0)

    # Apply correction
    corrected_xpr = xpr_coords + direction_vectors * correction_distances[:, None]

    # Final deviation after correction
    final_deviation = np.linalg.norm(xpn_coords - corrected_xpr, axis=1)

    # Actual correction magnitudes
    correction_magnitude = np.linalg.norm(corrected_xpr - xpr_coords, axis=1)

    # Remarks
    eps = 1e-6  # small margin for floating point errors
    remarks = np.where(final_deviation <= htol_array + eps,
                "Within tolerance", "Out of spec")


    # remarks = np.where(final_deviation <= htol_array, "Within tolerance", "Out of spec")

    return corrected_xpr, final_deviation, correction_magnitude, remarks

def apply_correction(report_df, logger=None):
    corrected_df = report_df.copy()
    out_of_spec_df = corrected_df[corrected_df['Remarks'] == 'Out of spec']
    
    if out_of_spec_df.empty:
        return corrected_df.round(3)

    xpn_coords = out_of_spec_df[['XPN X', 'XPN Y', 'XPN Z']].to_numpy()
    xpr_coords = out_of_spec_df[['XPR X', 'XPR Y', 'XPR Z']].to_numpy()
    htol_array = out_of_spec_df['HTol'].to_numpy()

    new_xpr_coords, final_deviation, correction_magnitude, remarks = correct_deviation_batch(xpn_coords, xpr_coords, htol_array)

    # Logging
    if logger:
        for i, index in enumerate(out_of_spec_df.index):
            if correction_magnitude[i] > 0:
                row = out_of_spec_df.loc[index]
                old_xpr = row[['XPR X', 'XPR Y', 'XPR Z']].to_numpy()
                old_deviation = np.linalg.norm(row[['XPN X', 'XPN Y', 'XPN Z']].to_numpy() - old_xpr)
                
                log_message = (f"Corrected Point# {row['Point# (XPN)']}: "
                               f"Old XPR=({old_xpr[0]:.3f}, {old_xpr[1]:.3f}, {old_xpr[2]:.3f}), "
                               f"New XPR=({new_xpr_coords[i, 0]:.3f}, {new_xpr_coords[i, 1]:.3f}, {new_xpr_coords[i, 2]:.3f}), "
                               f"Deviation changed from {old_deviation:.3f} to {final_deviation[i]:.3f}")
                logger.info(log_message)

    # Update the dataframe
    corrected_df.loc[out_of_spec_df.index, ['XPR X', 'XPR Y', 'XPR Z']] = new_xpr_coords
    corrected_df.loc[out_of_spec_df.index, 'Deviation'] = htol_array
    corrected_df.loc[out_of_spec_df.index, 'Correction_Magnitude'] = correction_magnitude
    corrected_df.loc[out_of_spec_df.index, 'Remarks'] = remarks
    corrected_df['Error'] = corrected_df['Deviation'] - corrected_df['HTol']
    
    return corrected_df.round(3)