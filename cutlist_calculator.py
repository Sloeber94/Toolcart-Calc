from typing import Dict, List, Any


def calculate_toolbox_frame(drawers: Dict[str, Any], tSlides: float, sRear: float, sFront: float, nDrwT: int, nDrwM: int, nDrwB: int, nDrw: int, sDrw: float, tBkt: float) -> Dict[str, float]:
    """
    Calculate toolbox frame dimensions around drawer stack.

    Args:
        drawers: result dict from calculate_drawer()
        tSlides: Drawer slide thickness (mm)
        sRear: Rear clearance behind drawers (mm)
        sFront: Front clearance (mm)
        nDrwT: Number of top drawers
        nDrwM: Number of mid drawers
        nDrwB: Number of bottom drawers
        nDrw: Total drawers
        sDrw: Spacing between drawers (mm)
        tBkt: Thickness drawer bracket

    Returns:
        dict with frame dimensions and spacing info
    """
    dims = drawers['dimensions']

    h_total = (
        drawers['low']['height']  * nDrwT +
        drawers['mid']['height']  * nDrwM +
        drawers['high']['height'] * nDrwB
    )

    sDrwTot = (nDrw + 1) * sDrw
    if sDrwTot == 0:
        raise ValueError("Spacing cannot be zero")

    frmHi = h_total + sDrwTot
    frmWi = dims['Wo'] + 2 * (tSlides + tBkt)
    frmDo = dims['Do'] + sRear + sFront

    return {
        'frmHi':   frmHi,
        'frmWi':   frmWi,
        'frmDo':   frmDo,
        'sDrwTot': sDrwTot,
    }


def calculate_drawer(drwL: float, drwW: float, drwHt: float, drwHm: float, drwHb: float, tBox: float, sDado: float, cBox: float, cBase: float) -> Dict[str, Any]:
    """
    Calculate cost and cutlist dimensions for drawer boxes.

    Args:
        drwL: Drawer inner width (mm)
        drwW: Drawer inner depth (mm)
        drwHt, drwHm, drwHb: Top, Mid, Bottom drawer heights (mm)
        tBox: Panel material thickness (mm)
        sDado: Dado depth (mm)
        cBox: Price per m² for panel wood (CHF)
        cBase: Price per m² for base wood (CHF)

    Returns:
        dict with cost calculations and dimensions for each drawer size
    """
    Wi = drwL
    Di = drwW
    Wo = Wi + 2 * tBox
    Do = Di + 2 * tBox
    Wb = Wi + 2 * sDado
    Db = Di + 2 * sDado

    def cost_for_height(h):
        A_front  = 2 * (Wi * h) * 1e-6
        A_sides  = 2 * (Do * h) * 1e-6
        A_panels = A_front + A_sides
        A_base   = (Wb * Db) * 1e-6 if Wb > 0 and Db > 0 else 0

        return {
            'height':      h,
            'A_front_m2':  A_front,
            'A_sides_m2':  A_sides,
            'A_panels_m2': A_panels,
            'A_base_m2':   A_base,
            'cost_panels': cBox  * A_panels,
            'cost_base':   cBase * A_base,
            'cost_total':  cBox  * A_panels + cBase * A_base,
        }

    return {
        'low':  cost_for_height(drwHt),
        'mid':  cost_for_height(drwHm),
        'high': cost_for_height(drwHb),
        'dimensions': {
            'drwL': drwL, 'drwW': drwW,
            'Wo': Wo, 'Do': Do,
            'Wb': Wb, 'Db': Db,
        }
    }


def generate_drawer_cutlist(result: Dict[str, Any], nDrwT: int, nDrwM: int, nDrwB: int, tBox: int, tBase: int) -> List[Dict]:
    """Generate drawer cutlist with dynamic material labels."""
    all_parts = []
    dims = result['dimensions']

    for belongs_to, height_key, qty in [
        ("Top Drawer",    "low",  nDrwT),
        ("Middle Drawer", "mid",  nDrwM),
        ("Bottom Drawer", "high", nDrwB),
    ]:
        h = result[height_key]['height']
        parts = [
            {'Part': 'Fronts', 'Qty': 2 * qty, 'L (mm)': dims['drwL'], 'W (mm)': h,          'Material': f"Box wood {int(tBox)} mm",  'Belongs To': belongs_to},
            {'Part': 'Sides',  'Qty': 2 * qty, 'L (mm)': dims['Do'],   'W (mm)': h,          'Material': f"Box wood {int(tBox)} mm",  'Belongs To': belongs_to},
            {'Part': 'Base',   'Qty': qty,     'L (mm)': dims['Wb'],   'W (mm)': dims['Db'], 'Material': f"Base wood {int(tBase)} mm", 'Belongs To': belongs_to},
        ]
        all_parts.extend(parts)

    return all_parts


def generate_frame_cutlist(frmHo, frmWo, frmDo, tUprights, uprights_profile, tTbl:int):
    # Depth horizontals sit between uprights → subtract 2x upright width
    hDepthL = frmDo - 2 * tUprights

    return [
        {'Part': 'Uprights',         'Qty': 4, 'L (mm)': frmHo,      'W (mm)': '',    'Material': 
        f"{uprights_profile} Profile",    'Belongs To': 'Frame'},
        {'Part': 'Horizontals Width', 'Qty': 4, 'L (mm)': frmWo,      'W (mm)': '',    'Material': '4040 Profile',              'Belongs To': 'Frame'},
        {'Part': 'Horizontals Depth', 'Qty': 4, 'L (mm)': hDepthL,    'W (mm)': '',    'Material': '4040 Profile',    'Belongs To': 'Frame'},
        {'Part': 'Tabletop',          'Qty': 1, 'L (mm)': frmWo + 50, 'W (mm)': frmDo, 'Material':
        f"Tabletop wood {int(tTbl)} mm", 'Belongs To': 'Frame'},
    ]
