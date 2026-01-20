<<<<<<< HEAD
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
=======
def calculate_toolbox_frame(drawers, slide_thickness=25, frame_clearance=50, nl=1, nm=2, nh=1):
    dims = drawers['dimensions']
    
    # Dynamic total height from quantities
    h_total = (drawers['low']['height'] * nl + 
               drawers['mid']['height'] * nm + 
               drawers['high']['height'] * nh)
    
    n_drawers = nl + nm + nh
    spacing_total = (n_drawers + 1) * 10
    
    frame_inner_h = h_total + spacing_total
    frame_inner_w = dims['Wo'] + 2 * slide_thickness
    frame_outer_d = dims['Do'] + frame_clearance
    
    return {
        'inner_height': frame_inner_h,
        'inner_width': frame_inner_w,
        'outer_depth': frame_outer_d,
        'spacing_used': spacing_total,
        'slides_width': 2 * slide_thickness,
        'n_drawers': n_drawers
    }

def calculate_drawer(Wi, Di, hl, hm, hh, t=15, td=6, Cp=30, Cb=10):
>>>>>>> c8b13b13627046af9a95b5223bbebc1f3e502cdf
    """
    Calculate cost and cutlist for drawer boxes.
    
    Args:
<<<<<<< HEAD
        drwL: drawer Length (Inner width)
        drwW: drawer Width (Inner depth)
        drwHt, drwHm, drwHb: Top, Mid, Bottom drawer heights
        tBox: Material thickness sides
        sDado: Dado thickness (mm, default 6)
        cBox: CHF per m² sides
        cBase: CHF per m² base
=======
        Wi: Inner width (mm)
        Di: Inner depth (mm)
        hl, hm, hh: Low, mid, high heights (mm)
        t: Material thickness sides (mm, default 15)
        td: Dado thickness (mm, default 6)
        Cp: Cost per m² panels (CHF)
        Cb: Cost per m² base (CHF)
>>>>>>> c8b13b13627046af9a95b5223bbebc1f3e502cdf
    
    Returns:
        dict with calculations for each height
    """
<<<<<<< HEAD
    Wi = drwL
    Di = drwW
    Wo = Wi + 2 * tBox
    Do = Di + 2 * tBox
    Wb = Wi + 2 * sDado
    Db = Di + 2 * sDado
=======
    
    Wo = Wi + 2 * t
    Do = Di + 2 * t
    Wb = Wo + 2 * td
    Db = Do + 2 * td
>>>>>>> c8b13b13627046af9a95b5223bbebc1f3e502cdf
    
    def cost_for_height(h):
        A_front = 2 * (Wi * h) * 1e-6
        A_sides = 2 * (Do * h) * 1e-6
        A_panels = A_front + A_sides
        A_base = (Wb * Db) * 1e-6
        
<<<<<<< HEAD
        y_panels = cBox * A_panels
        y_base = cBase * A_base
=======
        y_panels = Cp * A_panels
        y_base = Cb * A_base
>>>>>>> c8b13b13627046af9a95b5223bbebc1f3e502cdf
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
<<<<<<< HEAD
        'low': cost_for_height(drwHt),
        'mid': cost_for_height(drwHm),
        'high': cost_for_height(drwHb),
        'dimensions': {
            'drwL': drwL, 'drwW': drwW,
=======
        'low': cost_for_height(hl),
        'mid': cost_for_height(hm),
        'high': cost_for_height(hh),
        'dimensions': {
            'Wi': Wi, 'Di': Di,
>>>>>>> c8b13b13627046af9a95b5223bbebc1f3e502cdf
            'Wo': Wo, 'Do': Do,
            'Wb': Wb, 'Db': Db
        }
    }

<<<<<<< HEAD
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

=======
def generate_cutlist(Wi, Di, h, Wo, Do, Wb, Db, qty=1):
    """Generate cutlist table for one drawer height."""
    
    cutlist = [
        {
            'Part': 'Fronts',
            'Qty': 2 * qty,
            'Width (mm)': Wi,
            'Height (mm)': None,
            'Depth (mm)': '-'
        },
        {
            'Part': 'Sides',
            'Qty': 2 * qty,
            'Width (mm)': Do,
            'Height (mm)': None,
            'Depth (mm)': '-'
        },
        {
            'Part': 'Base',
            'Qty': 1 * qty,
            'Width (mm)': Wb,
            'Height (mm)': '-',
            'Depth (mm)': Db
        }
    ]
    
    return cutlist
>>>>>>> c8b13b13627046af9a95b5223bbebc1f3e502cdf
