from typing import Dict, List, Any


def calculate_toolbox_frame(
    drawers: Dict[str, Any],
    tSlides: float,
    sRear: float,
    sFront: float,
    nDrwT: int,
    nDrwM: int,
    nDrwB: int,
    nDrw: int,
    sDrw: float,
    tBkt: float,
) -> Dict[str, float]:
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


def calculate_drawer(
    drwL: float,
    drwW: float,
    drwHt: float,
    drwHm: float,
    drwHb: float,
    tBox: float,
    sDado: float,
    cBox: float,
    cBase: float,
) -> Dict[str, Any]:
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


def generate_drawer_cutlist(
    result: Dict[str, Any],
    nDrwT: int,
    nDrwM: int,
    nDrwB: int,
    tBox: int,
    tBase: int,
) -> List[Dict]:
    all_parts = []
    dims = result['dimensions']

    for belongs_to, height_key, qty in [
        ("Top Drawer",    "low",  nDrwT),
        ("Middle Drawer", "mid",  nDrwM),
        ("Bottom Drawer", "high", nDrwB),
    ]:
        h = result[height_key]['height']
        parts = [
            {'Part': 'Fronts', 'Qty': 2 * qty, 'L (mm)': dims['drwL'], 'W (mm)': h,          'Material': f'{tBox}mm Wood',  'Belongs To': belongs_to},
            {'Part': 'Sides',  'Qty': 2 * qty, 'L (mm)': dims['Do'],   'W (mm)': h,          'Material': f'{tBox}mm Wood',  'Belongs To': belongs_to},
            {'Part': 'Base',   'Qty': qty,     'L (mm)': dims['Wb'],   'W (mm)': dims['Db'], 'Material': f'{tBase}mm Wood', 'Belongs To': belongs_to},
        ]
        all_parts.extend(parts)

    return all_parts


def generate_frame_cutlist(
    frmHo: float,
    frmWo: float,
    frmDo: float,
    tUprights: int,
    uprights_profile: str,
    tTbl: float,
) -> List[Dict]:
    hw_len = frmWo - 2 * 40
    hd_len = frmDo - 2 * tUprights

    parts = [
        {'Part': 'Verticals',       'Qty': 4, 'L (mm)': frmHo,  'W (mm)': '', 'Material': uprights_profile, 'Belongs To': 'Frame'},
        {'Part': 'Horizontals (W)', 'Qty': 4, 'L (mm)': hw_len, 'W (mm)': '', 'Material': '4040',           'Belongs To': 'Frame'},
        {'Part': 'Horizontals (D)', 'Qty': 4, 'L (mm)': hd_len, 'W (mm)': '', 'Material': '4040',           'Belongs To': 'Frame'},
    ]
    if tTbl > 0:
        parts.append({'Part': 'Tabletop', 'Qty': 1, 'L (mm)': frmWo, 'W (mm)': frmDo, 'Material': f'{tTbl}mm Wood', 'Belongs To': 'Frame'})
    return parts


def calculate_costs(
    result: Dict[str, Any],
    frame_parts: List[Dict],
    nDrwT: int,
    nDrwM: int,
    nDrwB: int,
    nDrw: int,
    cSlides: float,
    c4040: float,
    c4080: float,
    cTbl: float,
    cCastor: float,
    frmWo: float,
    frmDo: float,
    tTbl: float,
    hCastors: float,
    uprights: str,
) -> Dict[str, Any]:
    cost_slides = nDrw * cSlides

    cost_frame = 0.0
    for part in frame_parts:
        mat = part['Material']
        if mat not in ('4040', '4080'):
            continue
        price_per_m = c4040 if mat == '4040' else c4080
        length_m = part['L (mm)'] / 1000.0
        cost_frame += part['Qty'] * length_m * price_per_m

    cost_drawers = 0.0
    for tier_key, qty in [('low', nDrwT), ('mid', nDrwM), ('high', nDrwB)]:
        tier = result[tier_key]
        cost_drawers += (tier['cost_panels'] + tier['cost_base']) * qty

    tbl_area_m2   = (frmWo * frmDo) * 1e-6 if tTbl > 0 else 0.0
    cost_tabletop = tbl_area_m2 * cTbl

    cost_castors     = (4 * cCastor) if hCastors > 0 else 0.0
    cost_accessories = cost_tabletop + cost_castors

    total = cost_slides + cost_frame + cost_drawers + cost_accessories

    panels_area_m2 = sum(
        result[t]['A_panels_m2'] * q
        for t, q in [('low', nDrwT), ('mid', nDrwM), ('high', nDrwB)]
    )
    base_area_m2 = sum(
        result[t]['A_base_m2'] * q
        for t, q in [('low', nDrwT), ('mid', nDrwM), ('high', nDrwB)]
    )
    len_4040_m = sum(
        p['Qty'] * p['L (mm)'] / 1000.0
        for p in frame_parts if p['Material'] == '4040'
    )
    len_uprights_m = sum(
        p['Qty'] * p['L (mm)'] / 1000.0
        for p in frame_parts if p['Material'] == uprights and uprights != '4040'
    )

    return {
        'cost_slides':      cost_slides,
        'cost_frame':       cost_frame,
        'cost_drawers':     cost_drawers,
        'cost_tabletop':    cost_tabletop,
        'cost_castors':     cost_castors,
        'cost_accessories': cost_accessories,
        'total':            total,
        'tbl_area_m2':      tbl_area_m2,
        'panels_area_m2':   panels_area_m2,
        'base_area_m2':     base_area_m2,
        'len_4040_m':       len_4040_m,
        'len_uprights_m':   len_uprights_m,
    }