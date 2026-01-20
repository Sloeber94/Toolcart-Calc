"""Drawer Calculator Defaults + Sliders"""

# Fixed Defaults
DEFAULTS = {
    # Dimensions
    "Wi": 20*42, "Di": 462,
    
    # Heights
    "hl": 80, "hm": 150, "hh": 250,
    
    # Quantities
    "nl": 7, "nm": 4, "nh": 2,
    
    # Prices & Hardware
    "Cp": 30.0, "Cb": 10.0,
    "slide_price": 15.0,
    "slide_thick": 25.0, 
    "frame_clear": 50.0,
    "td": 6.0, "t": 15.0,
}

# Slider Tuples: (min, max, default, step)
SLIDERS = {
    # Dimensions
    "Wi": (50, 2000, DEFAULTS["Wi"], 10),
    "Di": (50, 2000, DEFAULTS["Di"], 10),
    
    # Heights
    "hl": (40, 300, DEFAULTS["hl"], 10),
    "hm": (40, 300, DEFAULTS["hm"], 10),
    "hh": (40, 300, DEFAULTS["hh"], 10),
    
    # Quantities (int step=1)
    "nl": (0, 10, DEFAULTS["nl"], 1),
    "nm": (0, 10, DEFAULTS["nm"], 1),
    "nh": (0, 10, DEFAULTS["nh"], 1),
    
    # Slides
    "slide_price": (5.0, 25.0, DEFAULTS["slide_price"], 0.5),
    "slide_thick": (10.0, 30.0, DEFAULTS["slide_thick"], 0.1),
}

# Number Input Ranges (min, max, step)
NUMBER_RANGES = {
    "Cp": (5.0, 100.0, 1.0),
    "Cb": (2.0, 50.0, 1.0),
    "frame_clear": (30.0, 100.0, 5.0),
    "td": (3.0, 15.0, 0.1),
    "t": (5.0, 30.0, 0.1),
}

# Gridfinity (1U = 42mm width/depth, 7mm height → 0.5U=21mm, 1U=42mm)
GRIDFINITY = {
    "unit": 42,      # Width/depth step
    "half_unit": 21, # Height 0.5U
    "unit_height": 42,  # Height 1U (6x7mm)
    "clearance": 0.5,   # Optional bin clearance
}
