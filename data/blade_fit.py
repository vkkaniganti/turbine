import numpy as np
import pandas as pd

def load_points(filename):
    """Load XYZ coordinates only"""
    df = pd.read_csv(filename, sep=r'\s+', header=None)
    return df.values.astype(float)

def compute_rigid_transform(A, B):
    """Compute optimal rotation R and translation t using SVD"""
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    AA = A - centroid_A
    BB = B - centroid_B
    H = AA.T @ BB
    U, _, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T
    t = centroid_B - R @ centroid_A
    return R, t

def jacobian_icp(raw_points, nominal_points, max_iterations=50, tolerance=1e-6):
    """Iterative ICP using SVD-based alignment"""
    src = np.copy(raw_points)
    prev_error = float('inf')
    for iteration in range(max_iterations):
        distances = np.linalg.norm(src[:, None, :] - nominal_points[None, :, :], axis=2)
        indices = np.argmin(distances, axis=1)
        dst = nominal_points[indices]

        R, t = compute_rigid_transform(src, dst)
        src = (R @ src.T).T + t

        errors = np.linalg.norm(src - dst, axis=1)
        mean_error = np.mean(errors)

        if abs(prev_error - mean_error) < tolerance:
            break
        prev_error = mean_error

    distances = np.linalg.norm(src[:, None, :] - nominal_points[None, :, :], axis=2)
    final_indices = np.argmin(distances, axis=1)
    final_errors = distances[np.arange(len(src)), final_indices]

    return R, t, src, final_indices, final_errors

if __name__ == "__main__":
    # Load data
    raw_points = load_points("RawData.txt")
    nominal_points = load_points("NominalData.txt")

    # Hardcoded probe value
    probe_values = np.full(len(raw_points), 2.0)

    # Run ICP
    R, t, transformed, indices, errors = jacobian_icp(raw_points, nominal_points)

    # Filter: keep only the raw point with the minimum deviation for each nominal point
    best_indices = {}
    for i, nominal_idx in enumerate(indices):
        if nominal_idx not in best_indices or errors[i] < best_indices[nominal_idx][1]:
            best_indices[nominal_idx] = (i, errors[i])  # store raw point index and error

    # Prepare final output
    with open("output_best_matches.txt", "w") as f:
        f.write("Transformed_X,Transformed_Y,Transformed_Z,Nominal_X,Nominal_Y,Nominal_Z,Error,ProbeValue\n")
        for nominal_idx, (raw_idx, err) in best_indices.items():
            f.write(",".join(map(str, [
                transformed[raw_idx, 0], transformed[raw_idx, 1], transformed[raw_idx, 2],
                nominal_points[nominal_idx, 0], nominal_points[nominal_idx, 1], nominal_points[nominal_idx, 2],
                err,
                probe_values[raw_idx]
            ])) + "\n")

    print("✅ Filtered best-fit results with hardcoded probe value saved to output_best_matches.txt")