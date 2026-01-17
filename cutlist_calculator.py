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
    """
    Calculate cost and cutlist for drawer boxes.
    
    Args:
        Wi: Inner width (mm)
        Di: Inner depth (mm)
        hl, hm, hh: Low, mid, high heights (mm)
        t: Material thickness sides (mm, default 15)
        td: Dado thickness (mm, default 6)
        Cp: Cost per m² panels (CHF)
        Cb: Cost per m² base (CHF)
    
    Returns:
        dict with calculations for each height
    """
    
    Wo = Wi + 2 * t
    Do = Di + 2 * t
    Wb = Wo + 2 * td
    Db = Do + 2 * td
    
    def cost_for_height(h):
        A_front = 2 * (Wi * h) * 1e-6
        A_sides = 2 * (Do * h) * 1e-6
        A_panels = A_front + A_sides
        A_base = (Wb * Db) * 1e-6
        
        y_panels = Cp * A_panels
        y_base = Cb * A_base
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
        'low': cost_for_height(hl),
        'mid': cost_for_height(hm),
        'high': cost_for_height(hh),
        'dimensions': {
            'Wi': Wi, 'Di': Di,
            'Wo': Wo, 'Do': Do,
            'Wb': Wb, 'Db': Db
        }
    }

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
