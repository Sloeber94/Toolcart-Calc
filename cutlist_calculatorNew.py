"""Drawer & Frame Calculations - Pure Math, No UI"""

def calculate_drawer(drwL, drwW, drwHt, drwHm, drwHb, tBox, sDado, cBox, cBase):
    """
    Calculate drawer box dimensions, areas, and costs.
    
    Returns:
        dict with 'low', 'mid', 'high' keys containing heights, areas, costs
    """
    Wi, Di = drwL, drwW
    Wo = Wi + 2 * tBox
    Do = Di + 2 * tBox
    Wb = Wi + 2 * sDado
    Db = Di + 2 * sDado
    
    def cost_for_height(h):
        A_front = 2 * (Wi * h) * 1e-6
        A_sides = 2 * (Do * h) * 1e-6
        A_panels = A_front + A_sides
        A_base = (Wb * Db) * 1e-6
        return {
            'height': h,
            'A_front_m2': A_front,
            'A_sides_m2': A_sides,
            'A_panels_m2': A_panels,
            'A_base_m2': A_base,
            'cost_panels': cBox * A_panels,
            'cost_base': cBase * A_base,
            'cost_total': cBox * A_panels + cBase * A_base
        }
    
    return {
        'low': cost_for_height(drwHt),
        'mid': cost_for_height(drwHm),
        'high': cost_for_height(drwHb),
        'dimensions': {
            'Wi': Wi, 'Di': Di,
            'Wo': Wo, 'Do': Do,
            'Wb': Wb, 'Db': Db
        }
    }


def calculate_toolbox_frame(result, tSlides, sRear, sFront, nDrwT, nDrwM, nDrwB, nDrw, sDrw, tBkt):
    """
    Calculate frame dimensions from drawer data.
    
    Returns:
        dict with frame inner/outer dimensions
    """
    dims = result['dimensions']
    
    h_total = (result['low']['height'] * nDrwT + 
               result['mid']['height'] * nDrwM + 
               result['high']['height'] * nDrwB)
    
    sDrwTot = (nDrw + 1) * sDrw
    
    return {
        'frmHi': h_total + sDrwTot,
        'frmWi': dims['Wo'] + 2 * (tSlides + tBkt),
        'frmDo': dims['Do'] + sRear + sFront,
        'sDrwTot': sDrwTot,
        'n_drawers': nDrw
    }


def generate_frame_parts(frmHo, frmWo, frmDo, profile_thick):
    """Generate frame profile cutlist parts."""
    return [
        {"Type": "Profile", "Component": "Verticals", "L (mm)": frmHo, "W (mm)": profile_thick, "Qty": 4},
        {"Type": "Profile", "Component": "Top Horizontals", "L (mm)": frmWo, "W (mm)": profile_thick, "Qty": 2},
        {"Type": "Profile", "Component": "Bottom Horizontals", "L (mm)": frmWo, "W (mm)": profile_thick, "Qty": 2},
        {"Type": "Profile", "Component": "Front Depths", "L (mm)": frmDo, "W (mm)": profile_thick, "Qty": 2},
        {"Type": "Profile", "Component": "Rear Depths", "L (mm)": frmDo, "W (mm)": profile_thick, "Qty": 2},
    ]


def generate_drawer_cutlist(result, nDrwT, nDrwM, nDrwB):
    """Generate drawer wood cutlist."""
    all_parts = []
    dims = result['dimensions']
    Wi, Do, Wb, Db = dims['Wi'], dims['Do'], dims['Wb'], dims['Db']
    
    for drawer_type, height_key, qty in [("Top", "low", nDrwT), ("Mid", "mid", nDrwM), ("Bottom", "high", nDrwB)]:
        h = result[height_key]['height']
        
        all_parts.extend([
            {"Type": "Wood", "Component": "Drawer Fronts", "Drawer": drawer_type, "L (mm)": Wi, "W (mm)": h, "Qty": 2 * qty},
            {"Type": "Wood", "Component": "Drawer Sides", "Drawer": drawer_type, "L (mm)": Do, "W (mm)": h, "Qty": 2 * qty},
            {"Type": "Wood", "Component": "Drawer Bases", "Drawer": drawer_type, "L (mm)": Wb, "W (mm)": Db, "Qty": qty},
        ])
    
    return all_parts
