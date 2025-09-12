import numpy as np

def compute_max_thickness(points, section="N1"):
    """
    Compute MAX. THICK - Cmax for an airfoil section.
    
    Parameters
    ----------
    points : np.ndarray
        Array of shape (N, 2) with columns [X, Y].
    section : str
        Section label (e.g. 'N1', 'B1').
    
    Returns
    -------
    dict
        { "MAX. THICK - {section} (Cmax)": value }
    """

    if points.shape[1] != 2:
        raise ValueError("points must be of shape (N, 2) with [X, Y] columns")

    # --- Leading & Trailing Edge (min/max X) ---
    le = points[np.argmin(points[:, 0])]   # Leading edge (min X)
    te = points[np.argmax(points[:, 0])]   # Trailing edge (max X)

    # --- Chord vector & unit direction ---
    chord_vec = te - le
    chord_unit = chord_vec / np.linalg.norm(chord_vec)

    # --- Normal vector (perpendicular to chord) ---
    normal_vec = np.array([-chord_unit[1], chord_unit[0]])

    # --- Project all points onto normal direction ---
    proj = points @ normal_vec

    # --- Max thickness (Cmax) ---
    cmax = proj.max() - proj.min()

    return {f"MAX. THICK - {section} (Cmax)": cmax}

def compute_chord_length(points, section="B1"):
    """
    Compute LE CHORD LENGTH - {section} from airfoil section points.
    
    Parameters
    ----------
    points : np.ndarray
        Array of shape (N, 2) with columns [X, Y].
    section : str
        Section label (e.g., 'B1', 'N1').
    
    Returns
    -------
    dict
        { "LE CHORD LENGTH - {section}": chord_length }
    """

    if points.shape[1] != 2:
        raise ValueError("points must be of shape (N, 2) with [X, Y] columns")

    # Leading edge (min X) and trailing edge (max X)
    x_le = np.min(points[:, 0])
    x_te = np.max(points[:, 0])

    # Chord length = trailing edge X - leading edge X
    chord_length = x_te - x_le

    return {f"LE CHORD LENGTH - {section}": chord_length}

def compute_te_thickness(points, section="N1", offset_mm=2.0, tol=0.3):
    """
    Compute TE THICKNESS - {section} @ {offset_mm} mm_C3.
    
    Parameters
    ----------
    points : np.ndarray
        Array of shape (N, 2) with columns [X, Y].
    section : str
        Section label (e.g., 'N1', 'B1').
    offset_mm : float
        Distance forward from Trailing Edge (mm).
    tol : float
        Tolerance window for selecting slice (default ±0.3 mm).
    
    Returns
    -------
    dict
        { "TE THICKNESS - {section} @ {offset_mm} mm_C3": thickness }
    """

    if points.shape[1] != 2:
        raise ValueError("points must be of shape (N, 2) with [X, Y]")

    # Trailing edge = max X
    te_x = np.max(points[:, 0])

    # Slice plane at TE - offset
    target_x = te_x - offset_mm
    mask = np.isclose(points[:, 0], target_x, atol=tol)
    slice_points = points[mask]

    if slice_points.shape[0] < 2:
        thickness = np.nan
    else:
        thickness = slice_points[:, 1].max() - slice_points[:, 1].min()

    return {f"TE THICKNESS - {section} @ {offset_mm} mm_C3": thickness}

def compute_le_thickness(points, section="N1", offset_mm=2.0, tol=0.3):
    """
    Compute LE THICKNESS - {section} @ {offset_mm} mm_C1.
    
    Parameters
    ----------
    points : np.ndarray
        Array of shape (N, 2) with columns [X, Y].
    section : str
        Section label (e.g., 'N1', 'B1').
    offset_mm : float
        Distance from Leading Edge (mm).
    tol : float
        Tolerance window for selecting slice (default ±0.3 mm).
    
    Returns
    -------
    dict
        { "LE THICKNESS - {section} @ {offset_mm} mm_C1": thickness }
    """

    if points.shape[1] != 2:
        raise ValueError("points must be of shape (N, 2) with [X, Y]")

    # Leading edge = min X
    le_x = np.min(points[:, 0])

    # Slice plane at LE + offset
    target_x = le_x + offset_mm
    mask = np.isclose(points[:, 0], target_x, atol=tol)
    slice_points = points[mask]

    if slice_points.shape[0] < 2:
        thickness = np.nan
    else:
        thickness = slice_points[:, 1].max() - slice_points[:, 1].min()

    return {f"LE THICKNESS - {section} @ {offset_mm} mm_C1": thickness}


def compute_axis_alignment(xpn_points, xpr_points, section="N1"):
    """
    Compute X and Y AXIS ALIGNMENT for a section.
    
    Parameters
    ----------
    xpn_points : np.ndarray
        Nominal profile points (N, 2) with [X, Y].
    xpr_points : np.ndarray
        Actual profile points (N, 2) with [X, Y].
    section : str
        Section label (e.g., 'N1', 'B1').
    
    Returns
    -------
    dict
        {
          "X AXIS ALIGNMENT - {section}": value,
          "Y AXIS ALIGNMENT - {section}": value
        }
    """

    if xpn_points.shape[0] != xpr_points.shape[0]:
        raise ValueError("Nominal and Actual must have the same number of points for direct comparison")

    x_align = np.mean(xpr_points[:, 0] - xpn_points[:, 0])
    y_align = np.mean(xpr_points[:, 1] - xpn_points[:, 1])

    return {
        f"X AXIS ALIGNMENT - {section}": x_align,
        f"Y AXIS ALIGNMENT - {section}": y_align
    }