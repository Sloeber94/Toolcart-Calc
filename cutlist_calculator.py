def calculate_toolbox_frame(drawers, tSlides, sRear,sFront, nDrwT, nDrwM, nDrwB, nDrw, sDrw, tBkt):
    """
    Calculate toolbox frame dimensions around drawer stack.
    
    Args:
        drawers: result dict from calculate_drawer()
        tSlides: Drawer slide thickness (mm)
        sRear: Rear clearance behind drawers (mm) 
        sFront: 
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
    
    # Dynamic total height from quantities
    h_total = (drawers['low']['height'] * nDrwT + 
               drawers['mid']['height'] * nDrwM + 
               drawers['high']['height'] * nDrwB)
    
    sDrwTot = (nDrw + 1) * sDrw

   #Dimensions for: Length * Width * Height 
    #Drawers:       Width  * Depth * Height
    #Frame:         Width  * Depth * Height


    frmHi = h_total + sDrwTot
    frmWi = dims['Wo'] + 2 * (tSlides+tBkt)
    frmDo = dims['Do'] + sRear+sFront
    
    return {
        'frmHi': frmHi,
        'frmWi': frmWi,
        'frmDo': frmDo,
        'sDrwTot': sDrwTot,

    }

def calculate_drawer(drwL, drwW, drwHt, drwHm, drwHb, tBox, sDado, cBox, cBase):
    """
    Calculate cost and cutlist for drawer boxes.
    
    Args:
        drwL: drawer Length (Inner width)
        drwW: drawer Width (Inner depth)
        drwHt, drwHm, drwHb: Top, Mid, Bottom drawer heights
        tBox: Material thickness sides
        sDado: Dado thickness (mm, default 6)
        cBox: CHF per m² sides
        cBase: CHF per m² base
    
    Returns:
        dict with calculations for each height
    """
    Wi = drwL
    Di = drwW
    Wo = Wi + 2 * tBox
    Do = Di + 2 * tBox
    Wb = Wi + 2 * sDado
    Db = Di + 2 * sDado
    
    def cost_for_height(h):
        A_front = 2 * (Wi * h) * 1e-6
        A_sides = 2 * (Do * h) * 1e-6
        A_panels = A_front + A_sides
        A_base = (Wb * Db) * 1e-6
        
        y_panels = cBox * A_panels
        y_base = cBase * A_base
        y_total = y_panels + y_base
        
        return {
            'height': h,
            'A_front_m2': A_front,
            'A_sides_m2': A_sides,
            'A_panels_m2': A_panels,
            'A_base_m2': A_base,
            'cost_panels': y_panels,
            'cost_base': y_base,
            'cost_total': y_total
        }
    
    return {
        'low': cost_for_height(drwHt),
        'mid': cost_for_height(drwHm),
        'high': cost_for_height(drwHb),
        'dimensions': {
            'drwL': drwL, 'drwW': drwW,
            'Wo': Wo, 'Do': Do,
            'Wb': Wb, 'Db': Db
        }
    }

def generate_drawer_cutlist(result, nDrwT, nDrwM, nDrwB):
    """Generate complete drawer cutlist from result dict."""
    all_parts = []
    dims = result['dimensions']
    
    for drawer_type, height_key, qty in [
        ("Top", "low", nDrwT),
        ("Mid", "mid", nDrwM), 
        ("Bottom", "high", nDrwB)
    ]:
        h = result[height_key]['height']
        
        # Generate parts for this height
        parts = generate_cutlist_single(
            drwL=dims['drwL'], drwW=dims['drwW'], 
            h=h, Wo=dims['Wo'], Do=dims['Do'], 
            Wb=dims['Wb'], Db=dims['Db'], qty=qty
        )
        
        # Add drawer type
        for part in parts:
            part['Drawer'] = drawer_type
            
        all_parts.extend(parts)
    
    return all_parts

# Your existing single-drawer function (unchanged)
def generate_cutlist(drwL, drwW, h, Wo, Do, Wb, Db, qty=1):
    """Generate cutlist table for one drawer height."""
    return [  # Your existing code unchanged
        {'Part': 'Fronts', 'Qty': 2*qty, 'Width (mm)': drwL, 'Height (mm)': h, 'Depth (mm)': '-'},
        {'Part': 'Sides', 'Qty': 2*qty, 'Width (mm)': Do, 'Height (mm)': h, 'Depth (mm)': '-'},
        {'Part': 'Base', 'Qty': qty, 'Width (mm)': Wb, 'Height (mm)': '-', 'Depth (mm)': Db}
    ]

