"""Tool Trolley Calculator — Central Config
All defaults, ranges, constants and slide data live here.
app.py imports from this file and contains only UI logic.
"""

# ---------------------------------------------------------------------------
# DEFAULTS (always in mm unless noted)
# ---------------------------------------------------------------------------
DEFAULTS = {
    # Drawer dimensions
    "drwW":    650,   # drawer width
    "drwD":    450,   # drawer depth
    "drwHt":    50,   # top drawer height
    "drwHm":   100,   # middle drawer height
    "drwHb":   175,   # bottom drawer height

    # Drawer quantities
    "nDrwT":     6,   # top drawer count
    "nDrwM":     3,   # middle drawer count
    "nDrwB":     2,   # bottom drawer count

    # Accessories
    "hCastors": 100,  # castor height
    "tTbl":      18,  # tabletop thickness

    # Wood dimensions
    "tBox":      15,  # plywood thickness
    "tBase":      5,  # base panel thickness
    "sDado":      7,  # dado depth

    # Clearances
    "sRear":     40,  # rear clearance
    "sFront":     5,  # front clearance
    "sDrw":       2,  # spacing per drawer

    # Prices (CHF)
    "cBox":    25.0,  # drawer panels per m²
    "cBase":   15.0,  # drawer base per m²
    "c4040":   15.0,  # 4040 profile per m
    "c4080":   20.0,  # 4080 profile per m

    # Gridfinity
    "gf_mode": False,
    "gf":        42,  # 1 gridfinity unit = 42 mm
}

# ---------------------------------------------------------------------------
# SLIDER RANGES  (min, max, step)  — all in mm
# ---------------------------------------------------------------------------
SLIDER_RANGES = {
    "drwW":    (0,    2000,   5),
    "drwD":    (0,    1000,  50),
    "drwHt":   (0,     500,   1),
    "drwHm":   (0,     500,   1),
    "drwHb":   (0,     500,   1),
    "nDrwT":   (0,      20,   1),
    "nDrwM":   (0,      20,   1),
    "nDrwB":   (0,      20,   1),
    "hCastors":(0,     200,   1),
    "tTbl":    (0,      50,   1),
    "tBox":    (0,      30,   1),
    "tBase":   (0,      30,   1),
    # dado depth max is computed dynamically as tBox // 2
}

# ---------------------------------------------------------------------------
# NUMBER INPUT RANGES  (min, max, step)
# ---------------------------------------------------------------------------
NUMBER_RANGES = {
    "sFront":  (0,   100,   1),
    "sRear":   (0,   100,   1),
    "cBox":    (0.0, 200.0, 1.0),
    "cBase":   (0.0, 200.0, 1.0),
    "c4040":   (0.0, 200.0, 1.0),
    "c4080":   (0.0, 200.0, 1.0),
}

# ---------------------------------------------------------------------------
# PRICE FIELDS  (label, session_state key, default)
# ---------------------------------------------------------------------------
PRICE_FIELDS = [
    ("Plywood per m²", "cBox",  25.0),
    ("Plywood base per m²",   "cBase", 15.0),
    ("4040 profiles per m",  "c4040", 15.0),
    ("4080 profiles per m",  "c4080", 20.0),
]

# ---------------------------------------------------------------------------
# DRAWER SLIDE DATA  {(feature, load_class): (price_chf, thickness_mm)}
# ---------------------------------------------------------------------------
SLIDE_DATA = {
    ("Basic",          "Light"):  ( 5, 12.0),
    ("Basic",          "Medium"): ( 8, 15.0),
    ("Basic",          "Heavy"):  (10, 19.0),
    ("Bumper",         "Light"):  ( 8, 15.0),
    ("Bumper",         "Medium"): (11, 19.0),
    ("Bumper",         "Heavy"):  (14, 22.0),
    ("Soft-Close",     "Light"):  (12, 19.0),
    ("Soft-Close",     "Medium"): (16, 22.0),
    ("Soft-Close",     "Heavy"):  (20, 25.0),
    ("Push-to-Open",   "Light"):  (15, 22.0),
    ("Push-to-Open",   "Medium"): (19, 25.0),
    ("Push-to-Open",   "Heavy"):  (24, 28.0),
}

SLIDE_FEATURES    = ["Basic", "Bumper", "Soft-Close", "Push-to-Open"]
SLIDE_LOAD_CLASSES = ["Light", "Medium", "Heavy"]

# ---------------------------------------------------------------------------
# PROFILE / FRAME CONSTANTS
# ---------------------------------------------------------------------------
PROFILE_WIDTHS = {
    "4040": 40,
    "4080": 80,
}

FRAME_CLEAR_DEFAULTS = {   # default rear clearance per profile type
    "4040": 10,
    "4080": 50,
}

# Fixed construction constants (not user-editable)
CONSTANTS = {
    "tBkt":    2,   # drawer slide bracket thickness
    "sRear40": 20,  # rear spacing for 4040 profile
    "sRear80": 35,  # rear spacing for 4080 profile
}

# ---------------------------------------------------------------------------
# GRIDFINITY
# ---------------------------------------------------------------------------
GRIDFINITY = {
    "unit":        42,   # width/depth step (mm)
    "half_unit":   21,   # height 0.5U
    "unit_height": 42,   # height 1U
    "clearance":  0.5,   # bin clearance
}
