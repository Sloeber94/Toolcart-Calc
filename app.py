import os
import pandas as pd
import streamlit as st
from typing import Dict, Any
from config import DEFAULTS, SLIDERS, NUMBER_RANGES
from cutlist_calculator import calculate_drawer, generate_cutlist, generate_drawer_cutlist, calculate_toolbox_frame


def load_css():
    css_path = "styles.css"
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

st.set_page_config(page_title="Drawer Calculator", layout="wide")

st.title('[Verschraubt.ch - Tool Trolley Project Calculator](https://verschraubt.ch)')
st.markdown(
    "Fully customizable by you, just enter your requirements and let it calculate your materials."
)

INIT_STATE = {
    "gf_mode": False,
    "gf": 42,
    "drwW": 650,
    "drwD": 450,
    "drwHt": 50,
    "drwHm": 100,
    "drwHb": 175,
    "nDrwT": 6,
    "nDrwM": 3,
    "nDrwB": 2,
    "hCastors": 100,
    "tTbl": 18,
    "tBox": 15,
    "tBase": 5,
    "sRear": 40,
    "sFront": 5,
    "sDrw": 2,
    "sDado": 7,
    "cBox": 25.0,
    "cBase": 15.0,
    "c4040": 15.0,
    "c4080": 20.0,
}

for k, v in INIT_STATE.items():
    st.session_state.setdefault(k, v)

def toDisp(val, gf_mode, gf):
    return val / gf if gf_mode else val


def toMm(val, gf_mode, gf):
    return val * gf if gf_mode else val


def lbl(gf_mode):
    return "u" if gf_mode else "mm"


def mmSlider(label, key, minVal, maxVal, defVal, stepVal, showMm=False, gf=True):
    gf_mode = st.session_state.gf_mode and gf
    gf_step = st.session_state.gf

    if key not in st.session_state:
        st.session_state[key] = defVal

    col1, col2 = st.columns([4, 1])

    with col1:
        new_disp = st.slider(
            label,
            min_value=float(toDisp(minVal, gf_mode, gf_step)),
            max_value=float(toDisp(maxVal, gf_mode, gf_step)),
            value=float(toDisp(st.session_state[key], gf_mode, gf_step)),
            step=float(toDisp(stepVal, gf_mode, gf_step)),
            format=f"%.1f {lbl(gf_mode)}",
            key=f"{key}_{'gf' if gf_mode else 'mm'}_{'usegf' if gf else 'fixedmm'}",
        )

    st.session_state[key] = toMm(new_disp, gf_mode, gf_step)

    with col2:
        if showMm and gf_mode:
            st.caption(f"{int(st.session_state[key])} mm")

    return st.session_state[key]


if "gf_mode" not in st.session_state:
    st.session_state.gf_mode = False

if "gf" not in st.session_state:
    st.session_state.gf = 42


# defaults, always in mm
defaults = {
    "drwW": 650,      # drawer width
    "drwD": 450,      # drawer depth
    "drwHt": 50,      # top drawer height
    "drwHm": 100,     # middle drawer height
    "drwHb": 175,     # bottom drawer height
    "nDrwT": 6,       # top drawer quantity
    "nDrwM": 3,       # middle drawer quantity
    "nDrwB": 2,       # bottom drawer quantity
    "hCastors": 100,  # height of castors
    "tTbl": 18,       # tabletop thickness
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Initialize other constants in session state (needed by CALCULATIONS)
if "tBox" not in st.session_state:
    st.session_state.tBox = 15

if "tBase" not in st.session_state:
    st.session_state.tBase = 5

if "sRear" not in st.session_state:
    st.session_state.sRear = 40

if "sFront" not in st.session_state:
    st.session_state.sFront = 5

if "sDrw" not in st.session_state:
    st.session_state.sDrw = 2


with st.sidebar:
    st.header("Configuration")

    st.checkbox("Gridfinity Mode", key="gf_mode")
    gf_mode = st.session_state.gf_mode
    gf = st.session_state.gf

    # constants (just for clarity; values are stored in st.session_state below)
    tBox = 15
    tBase = 5
    tBkt = 2
    sRear = 40
    sRear40 = 20
    sRear80 = 35
    sDrw = 2
    sDadoMax = tBox // 2
    sFront = 5
    w4040 = 40
    w4080 = 80

    # limits, always in mm
    drwWmin = 0
    drwWmax = 2000
    drwWdef = defaults["drwW"]
    drwWstep = 42 if gf_mode else 5

    drwDmin = 0
    drwDmax = 1000
    drwDdef = defaults["drwD"]
    drwDstep = 42 if gf_mode else 50

    drwHmin = 0
    drwHmax = 500
    drwHstep = 21 if gf_mode else 1

    nDrwMin = 0
    nDrwMax = 20

    tabs = st.tabs(["Input", "Constants"])


    with tabs[0]:
        drwW = mmSlider("Drawer Width", "drwW", drwWmin, drwWmax, drwWdef, drwWstep, True)
        drwD = mmSlider("Drawer Depth", "drwD", drwDmin, drwDmax, drwDdef, drwDstep, True)

        if drwW >= 2 * drwD:
            st.warning("It is recommended to keep drawer width less than twice the drawer depth, be advised!")

        st.subheader("Drawer Heights")

        for label, key, defVal in [
            ("Top", "drwHt", defaults["drwHt"]),
            ("Middle", "drwHm", defaults["drwHm"]),
            ("Bottom", "drwHb", defaults["drwHb"]),
        ]:
            mmSlider(label, key, drwHmin, drwHmax, defVal, drwHstep, True)

        drwHt = st.session_state.drwHt
        drwHm = st.session_state.drwHm
        drwHb = st.session_state.drwHb

        st.subheader("Drawer Quantities")

        for label, key, defVal in [
            ("Top", "nDrwT", defaults["nDrwT"]),
            ("Middle", "nDrwM", defaults["nDrwM"]),
            ("Bottom", "nDrwB", defaults["nDrwB"]),
        ]:
            st.session_state[key] = st.slider(
                label,
                min_value=nDrwMin,
                max_value=nDrwMax,
                value=st.session_state[key],
                step=1,
                format="%d pcs",
                key=f"{key}_qty"
            )

        nDrwT = st.session_state.nDrwT
        nDrwM = st.session_state.nDrwM
        nDrwB = st.session_state.nDrwB

        st.subheader("Accessoires")

        hCastors = mmSlider("Castors Height", "hCastors", 0, 200, defaults["hCastors"], 1, False, gf=False)
        tTbl = mmSlider("Tabletop thickness", "tTbl", 0, 50, defaults["tTbl"], 1, False, gf=False)


    with tabs[1]:
        st.subheader("Prices")

        priceFields = [
            ("Drawer panels per m²", "cBox", 25.0),
            ("Drawer base per m²", "cBase", 15.0),
            ("4040 profiles per m", "c4040", 15.0),
            ("4080 profiles per m", "c4080", 20.0),
        ]

        for i in range(0, len(priceFields), 2):
            col1, col2 = st.columns(2)
            for col, (label, key, defVal) in zip((col1, col2), priceFields[i:i+2]):
                with col:
                    if key not in st.session_state:
                        st.session_state[key] = defVal
                    st.session_state[key] = st.number_input(
                        label,
                        min_value=0.0,
                        max_value=200.0,
                        value=st.session_state[key],
                        step=1.0,
                        format="%.0f",
                        key=f"{key}_price"
                    )

        cBox = st.session_state.cBox
        cBase = st.session_state.cBase
        c4040 = st.session_state.c4040
        c4080 = st.session_state.c4080

        st.subheader("Drawer Slides")

        slideData = {
            ("Basic", "Light"): (5, 12.0),
            ("Basic", "Medium"): (8, 15.0),
            ("Basic", "Heavy"): (10, 19.0),
            ("Bumper", "Light"): (8, 15.0),
            ("Bumper", "Medium"): (11, 19.0),
            ("Bumper", "Heavy"): (14, 22.0),
            ("Soft-Close", "Light"): (12, 19.0),
            ("Soft-Close", "Medium"): (16, 22.0),
            ("Soft-Close", "Heavy"): (20, 25.0),
            ("Push-to-Open", "Light"): (15, 22.0),
            ("Push-to-Open", "Medium"): (19, 25.0),
            ("Push-to-Open", "Heavy"): (24, 28.0),
        }

        col1, col2 = st.columns(2)
        with col1:
            selectedFeature = st.selectbox(
                "Features",
                ["Basic", "Bumper", "Soft-Close", "Push-to-Open"],
                index=0
            )
        with col2:
            selectedLoad = st.selectbox(
                "Load Class",
                ["Light", "Medium", "Heavy"],
                index=1
            )

        cSlides, tSlides = slideData.get((selectedFeature, selectedLoad), (10, 19.0))
        st.caption(f"Price per pair: {cSlides} CHF", text_alignment="center")
        st.caption(f"Slide Thickness: {tSlides:.1f} mm", text_alignment="center")

        st.subheader("Dimensions")

        col1, col2 = st.columns([2, 3])

        with col1:
            uprights = st.radio("Uprights profile", ["4040", "4080"], index=0)

        tUprights = w4040 if uprights == "4040" else w4080
        frameClearDef = 10 if uprights == "4040" else 50

        with col2:
            sFront = st.number_input(
                "Front Clearance",
                value=st.session_state.sFront,
                min_value=0,
                max_value=100,
                step=1,
                help="Optional: change distance from drawer slides to front of frame or leave as is"
            )
            sRear = st.number_input(
                "Rear Clearance",
                value=st.session_state.sRear,
                min_value=0,
                max_value=100,
                step=1,
                help="Changes on profile selection, change only when required."
            )

            st.session_state.sRear = sRear
            st.session_state.sFront = sFront

        st.subheader("Wood Dimensions")

        col1, col2, col3 = st.columns(3)

        with col1:
            slab = st.slider(
                "Plywood thickness",
                0,
                30,
                st.session_state.tBox,
                1,
                format="%.0f mm"
            )
            st.session_state.tBox = slab

        with col2:
            slab = st.slider(
                "Base thickness",
                0,
                30,
                st.session_state.tBase,
                1,
                format="%.0f mm"
            )
            st.session_state.tBase = slab

        sDadoMax = max(int(st.session_state.tBox // 2), 3)
        sDadoDef = min(max(int(st.session_state.tBox // 2), 2), sDadoMax)

        with col3:
            sDado = st.slider(
                "Dado depth",
                min_value=2,
                max_value=sDadoMax,
                value=sDadoDef,
                step=1,
                format="%.0f mm",
                help="Default to <50% of Plywood thickness",
            )
            st.session_state.sDado = sDado

    """
    # TAB 3: FINE-TUNING
    with tabs[2]:
        st.title("🎯 Fine‑tuning")
        ...
    """


# CALCULATIONS
drwW = st.session_state.drwW
drwD = st.session_state.drwD
drwHt = st.session_state.drwHt
drwHm = st.session_state.drwHm
drwHb = st.session_state.drwHb
tBox = st.session_state.tBox
tBase = st.session_state.tBase
sDado = st.session_state.sDado
sDadoMax = tBox // 2
sRear = st.session_state.sRear
sFront = st.session_state.sFront
sDrw = st.session_state.sDrw

# prices
cBox = st.session_state.cBox
cBase = st.session_state.cBase
c4040 = st.session_state.c4040
c4080 = st.session_state.c4080
hCastors = st.session_state.hCastors
tTbl = st.session_state.tTbl

# quantities
nDrwT = st.session_state.nDrwT
nDrwM = st.session_state.nDrwM
nDrwB = st.session_state.nDrwB

# constants
tBkt = 2  # thickness of drawer slide bracket

result = calculate_drawer(
    drwW,   # drwL = drawer length ≈ drwW (frame width = drawer width)
    drwD,   # drwW = drawer depth (frame depth)
    drwHt,
    drwHm,
    drwHb,
    tBox,
    sDado,
    cBox,
    cBase,
)

nDrw = nDrwT + nDrwM + nDrwB  # total drawers
slides_cost = nDrw * cSlides  # cSlides is from tabs[1]; not in st.session_state

frame = calculate_toolbox_frame(
    result,     # calculate_drawer output
    tSlides,    # slide_thickness
    sRear,      # back spacing
    sFront,     # front spacing
    nDrwT,      # top drawer count
    nDrwM,      # middle drawer count
    nDrwB,      # bottom drawer count
    nDrw,       # total drawers
    sDrw,       # spacing per drawer
    tBkt        # thickness of drawer bracket
)

frmHi, frmWi, frmDo, sDrwTot = frame.values()
## intermediate calcs
frmHo = frmHi + 2 * w4040
frmWo = frmWi + 2 * w4040
frmDi = frmDo - 2 * tUprights
trlH = frmHo + hCastors + tTbl
trlW = frmWo
trlD = frmDo

# FRAME DISPLAY
st.subheader("Tool Trolley frame dimensions")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Frame outer Width", f"{frmWo:.0f} mm")
    st.metric("Frame inner Width", f"{frmWi:.0f} mm")
with col2:
    st.metric("Frame outer Depth", f"{frmDo:.0f} mm")
    st.metric("Frame inner Depth", f"{frmDi:.0f} mm")
with col3:
    st.metric("Frame outer Height", f"{frmHo:.0f} mm")
    st.metric("Frame inner Height", f"{frmHi:.0f} mm")

with st.expander("Frame Details"):
    st.info(f"Total spacing: {sDrwTot:.0f} mm")
    st.info(f"Tabletop working height: {trlH:.0f} mm")

# CUTLIST (MERGED)
st.subheader("Cutlist of Wood and Profiles")

drawer_parts = generate_drawer_cutlist(result, nDrwT, nDrwM, nDrwB)

profile_thick = tUprights

all_parts = drawer_parts + [
    {"Part": "Profile Verticals", "L (mm)": frmHo, "W (mm)": profile_thick, "Qty": 4},
    {"Part": "Profile Horizontals", "L (mm)": frmWo, "W (mm)": profile_thick, "Qty": 4},
    {"Part": "Plywood Tabletop", "L (mm)": frmWo + 50} ,]