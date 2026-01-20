"""Drawer Calculator Configuration - Single Source of Truth"""

# ============ DIMENSION DEFAULTS ============
DEFAULTS = {
    # Drawer dimensions (mm)
    "drwL": 400, "drwW": 500,
    "drwHt": 50, "drwHm": 75, "drwHb": 100,
    
    # Quantities
    "nDrwT": 7, "nDrwM": 4, "nDrwB": 2,
    
    # Material thickness (mm)
    "tBox": 15,      # Drawer box material
    "tBase": 5,      # Drawer base material  
    "tBkt": 2,       # Drawer bracket thickness
    "sDado": 6,      # Dado depth
    
    # Frame/spacing (mm)
    "sDrw": 10,      # Spacing between drawers
    "sFront": 5,     # Front clearance
    "sRear40": 20,   # Rear clearance 4040 profile
    "sRear80": 35,   # Rear clearance 4080 profile
    
    # Profiles (mm)
    "w4040": 40,
    "w4080": 80,
    
    # Accessories
    "hCastors": 125,
    "tTabletop": 20,
    
    # Prices (CHF)
    "cBox": 25.0,        # CHF/m² plywood panels
    "cBase": 15.0,       # CHF/m² plywood base
    "cBracket": 2.50,    # CHF per bracket
    "cProfile4040": 15,  # CHF/m
    "cProfile4080": 25,  # CHF/m
}

# ============ SLIDER CONFIGURATION ============
SLIDERS = {
    # (min, max, default, step, format)
    "drwL": (100, 2000, DEFAULTS["drwL"], 50, "%g mm"),
    "drwW": (100, 1000, DEFAULTS["drwW"], 50, "%g mm"),
    "drwHt": (20, 300, DEFAULTS["drwHt"], 10, "%.0f mm"),
    "drwHm": (20, 300, DEFAULTS["drwHm"], 10, "%.0f mm"),
    "drwHb": (20, 300, DEFAULTS["drwHb"], 10, "%.0f mm"),
    "nDrwT": (1, 20, DEFAULTS["nDrwT"], 1, "%d pcs"),
    "nDrwM": (0, 20, DEFAULTS["nDrwM"], 1, "%d pcs"),
    "nDrwB": (0, 20, DEFAULTS["nDrwB"], 1, "%d pcs"),
    "hCastors": (0, 200, DEFAULTS["hCastors"], 10, "%.0f mm"),
    "tTabletop": (15, 50, DEFAULTS["tTabletop"], 1, "%.0f mm"),
}

# ============ SLIDE MATRIX ============
SLIDES = [
    ["Basic", "Light", 5, 12.0],
    ["Basic", "Medium", 8, 15.0],
    ["Basic", "Heavy", 10, 19.0],
    ["Bumper", "Light", 8, 15.0],
    ["Bumper", "Medium", 11, 19.0],
    ["Bumper", "Heavy", 14, 22.0],
    ["Soft-Close", "Light", 12, 19.0],
    ["Soft-Close", "Medium", 16, 22.0],
    ["Soft-Close", "Heavy", 20, 25.0],
    ["Push-to-Open", "Light", 15, 22.0],
    ["Push-to-Open", "Medium", 19, 25.0],
    ["Push-to-Open", "Heavy", 24, 28.0],
]

def get_slide_data(feature, load_class):
    """Lookup slide thickness and cost."""
    for row in SLIDES:
        if row[0] == feature and row[1] == load_class:
            return row[2], row[3]
    return 10, 19.0  # Fallback

# ============ GRIDFINITY MODE ============
GRIDFINITY = {
    "unit": 42,          # 1U width/depth
    "half_unit": 21,     # 0.5U
    "unit_height": 42,   # 1U height
    "min": 1,
    "max": 40,
}
