import os
import pandas as pd
import streamlit as st
from config import DEFAULTS, SLIDER_RANGES, NUMBER_RANGES, PRICE_FIELDS, SLIDE_DATA, SLIDE_FEATURES, SLIDE_LOAD_CLASSES, PROFILE_WIDTHS, FRAME_CLEAR_DEFAULTS, CONSTANTS
from cutlist_calculator import calculate_drawer, generate_drawer_cutlist, generate_frame_cutlist, calculate_toolbox_frame, calculate_costs
from preview_3d import build_assembly, render_3d


def load_css():
    css_path = "styles.css"
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

st.set_page_config(page_title="Drawer Calculator", layout="wide")

st.title("Tool Cart Calculator")
st.markdown("Fully customizable by you, just enter your requirements and let it calculate your materials.")

# ---------------------------------------------------------------------------
# SESSION STATE — initialise once from DEFAULTS
# ---------------------------------------------------------------------------
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def toDisp(val, gf_mode, gf):
    return val / gf if gf_mode else val


def toMm(val, gf_mode, gf):
    return val * gf if gf_mode else val


def lbl(gf_mode):
    return "u" if gf_mode else "mm"


def mmSlider(label, key, minVal, maxVal, stepVal, showMm=False, gf=True):
    """Slider that works in mm or Gridfinity units."""
    gf_mode = st.session_state.gf_mode and gf
    gf_step = st.session_state.gf

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


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image("assets/banner.png", width='stretch')

    st.header("Configuration")

    st.checkbox("Gridfinity Mode", key="gf_mode")
    gf_mode = st.session_state.gf_mode

    # Gridfinity step sizes
    drwWstep = 42 if gf_mode else 5
    drwDstep = 42 if gf_mode else 50
    drwHstep = 21 if gf_mode else 1

    tabs = st.tabs(["Input", "Constants"])

    # ── TAB 0: INPUT ────────────────────────────────────────────────────────
    with tabs[0]:
        mmSlider("Drawer Width",  "drwW", *SLIDER_RANGES["drwW"][:2],  drwWstep, showMm=True)
        mmSlider("Drawer Depth",  "drwD", *SLIDER_RANGES["drwD"][:2],  drwDstep, showMm=True)

        if st.session_state.drwW >= 2 * st.session_state.drwD:
            st.warning("Drawer width is more than twice the depth — stability may be affected.")

        st.subheader("Drawer Heights")
        for label, key in [("Top", "drwHt"), ("Middle", "drwHm"), ("Bottom", "drwHb")]:
            mmSlider(label, key, *SLIDER_RANGES[key][:2], drwHstep, showMm=True)

        st.subheader("Drawer Quantities")
        for label, key in [("Top", "nDrwT"), ("Middle", "nDrwM"), ("Bottom", "nDrwB")]:
            mn, mx, step = SLIDER_RANGES[key]
            st.session_state[key] = st.slider(
                label,
                min_value=int(mn), max_value=int(mx),
                value=st.session_state[key],
                step=int(step),
                format="%d pcs",
                key=f"{key}_qty",
            )



    # ── TAB 1: CONSTANTS ────────────────────────────────────────────────────
    with tabs[1]:
        st.subheader("Prices")
        for i in range(0, len(PRICE_FIELDS), 2):
            col1, col2 = st.columns(2)
            for col, (label, key, defVal) in zip((col1, col2), PRICE_FIELDS[i:i+2]):
                mn, mx, step = NUMBER_RANGES[key]
                with col:
                    st.session_state[key] = st.number_input(
                        label,
                        min_value=float(mn), max_value=float(mx),
                        value=float(st.session_state[key]),
                        step=float(step),
                        format="%.0f",
                        key=f"{key}_price",
                    )

        st.subheader("Accessories")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state["hCastors"] = st.number_input(
                "Castors Height (mm)",
                min_value=0, max_value=200, step=1,
                value=st.session_state["hCastors"],
                key="hCastors_input",
            )
        with col2:
            st.session_state["tTbl"] = st.number_input(
                "Tabletop thickness (mm)",
                min_value=0, max_value=50, step=1,
                value=st.session_state["tTbl"],
                key="tTbl_input",
            )

        col1, col2 = st.columns(2)
        with col1:
            selectedFeature = st.selectbox("Drawer Slide", SLIDE_FEATURES,    index=0)
        with col2:
            selectedLoad    = st.selectbox("Load Class",   SLIDE_LOAD_CLASSES, index=1)

        cSlides, tSlides = SLIDE_DATA.get((selectedFeature, selectedLoad), (10, 19.0))
        cTbl    = st.session_state.cTbl
        cCastor = st.session_state.cCastor


        st.subheader("Dimensions")
        col1, col2 = st.columns([2, 3])
        with col1:
            uprights = st.radio("Uprights profile", list(PROFILE_WIDTHS.keys()), index=0)

        tUprights = PROFILE_WIDTHS[uprights]

        with col2:
            mn, mx, step = NUMBER_RANGES["sFront"]
            st.session_state["sFront"] = st.number_input(
                "Front Clearance",
                min_value=mn, max_value=mx, step=step,
                value=st.session_state["sFront"],
                help="Optional: distance from drawer slides to front of frame",
            )
            mn, mx, step = NUMBER_RANGES["sRear"]
            st.session_state["sRear"] = st.number_input(
                "Rear Clearance",
                min_value=mn, max_value=mx, step=step,
                value=st.session_state["sRear"],
                help="Changes on profile selection — only adjust if needed.",
            )

        st.subheader("Wood Dimensions")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.session_state["tBox"] = st.number_input(
                "Drawer thickness (mm)",
                min_value=0, max_value=30, step=1,
                value=st.session_state["tBox"],
                key="tBox_input",
            )
        with col2:
            st.session_state["tBase"] = st.number_input(
                "Base thickness (mm)",
                min_value=0, max_value=30, step=1,
                value=st.session_state["tBase"],
                key="tBase_input",
            )
        with col3:
            sDadoMax = max(int(st.session_state["tBox"] // 2), 3)
            if st.session_state["sDado"] > sDadoMax:
                st.session_state["sDado"] = sDadoMax
            st.session_state["sDado"] = st.number_input(
                "Dado depth (mm)",
                min_value=2, max_value=sDadoMax, step=1,
                value=st.session_state["sDado"],
                key="sDado_input",
                help="Default: <50% of plywood thickness",
            )

# ---------------------------------------------------------------------------
# READ ALL VALUES FROM SESSION STATE
# ---------------------------------------------------------------------------
drwW     = st.session_state.drwW
drwD     = st.session_state.drwD
drwHt    = st.session_state.drwHt
drwHm    = st.session_state.drwHm
drwHb    = st.session_state.drwHb
tBox     = st.session_state.tBox
tBase    = st.session_state.tBase
sDado    = st.session_state.sDado
sRear    = st.session_state.sRear
sFront   = st.session_state.sFront
sDrw     = st.session_state.sDrw
cBox     = st.session_state.cBox
cBase    = st.session_state.cBase
c4040    = st.session_state.c4040
c4080    = st.session_state.c4080
cTbl     = st.session_state.cTbl
cCastor  = st.session_state.cCastor
hCastors = st.session_state.hCastors
tTbl     = st.session_state.tTbl
nDrwT    = st.session_state.nDrwT
nDrwM    = st.session_state.nDrwM
nDrwB    = st.session_state.nDrwB
tBkt     = CONSTANTS["tBkt"]
w4040    = PROFILE_WIDTHS["4040"]
w4080    = PROFILE_WIDTHS["4080"]

# ---------------------------------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------------------------------
result = calculate_drawer(drwW, drwD, drwHt, drwHm, drwHb, tBox, sDado, cBox, cBase)

dims         = result['dimensions']
drwIW        = dims['drwL']
drwID        = dims['drwW']

nDrw        = nDrwT + nDrwM + nDrwB
slides_cost = nDrw * cSlides

frame = calculate_toolbox_frame(
    result, tSlides, sRear, sFront,
    nDrwT, nDrwM, nDrwB, nDrw, sDrw, tBkt,
)

frmHi, frmWi, frmDo, sDrwTot = frame.values()
frmHo = frmHi + 2 * w4040
frmWo = frmWi + 2 * w4040
frmDi = frmDo - 2 * tUprights
trlH  = frmHo + hCastors + tTbl
trlW  = frmWo
trlD  = frmDo

total_area   = drwIW * drwID * nDrw
total_volume = drwIW * drwID * (drwHt * nDrwT + drwHm * nDrwM + drwHb * nDrwB)

# ---------------------------------------------------------------------------
# FRAME DISPLAY
# ---------------------------------------------------------------------------
st.subheader("Tool Trolley Frame Dimensions")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Width",  f"{frmWo:.0f} mm")
with col2:
    st.metric("Depth",  f"{frmDo:.0f} mm")
with col3:
    st.metric("Height", f"{trlH:.0f} mm")

with st.expander("Details"):
    st.subheader("Frame")
    col1, col2, col3 = st.columns(3)
    col1.caption("Inner Width");  col1.write(f"**{frmWi:.0f} mm**")
    col2.caption("Inner Depth");  col2.write(f"**{frmDi:.0f} mm**")
    col3.caption("Inner Height"); col3.write(f"**{frmHi:.0f} mm**")

    st.subheader("Drawers")
    col1, col2, col3, col4 = st.columns(4)
    col1.caption("Inner Width");       col1.write(f"**{drwIW:.0f} mm**")
    col2.caption("Inner Depth");       col2.write(f"**{drwID:.0f} mm**")
    col3.caption("Total Area");        col3.write(f"**{total_area / 1e6:.1f} m²**")
    col4.caption("Total Volume");      col4.write(f"**{total_volume / 1e6:.1f} dm³**")

    st.subheader("Assembly")
    col1, col2 = st.columns(2)
    col1.caption("Drawer Spacing");       col1.write(f"**{sDrwTot:.0f} mm**")
    col2.caption("Tabletop Work Height"); col2.write(f"**{trlH:.0f} mm**")

# ---------------------------------------------------------------------------
# CUTLIST
# ---------------------------------------------------------------------------
st.subheader("Cutlist of Wood and Profiles")

drawer_parts = generate_drawer_cutlist(result, nDrwT, nDrwM, nDrwB)
frame_parts  = generate_frame_cutlist(frmHo, frmWo, frmDo, tUprights, uprights)

all_parts = drawer_parts + frame_parts

df = pd.DataFrame(all_parts)[["Belongs To", "Part", "Material", "L (mm)", "W (mm)", "Qty"]]

st.dataframe(
    df,
    hide_index=True,
    width="content",
    height="content",
    column_config={
        "Belongs To": st.column_config.TextColumn("Belongs To", width="medium"),
        "Part":       st.column_config.TextColumn("Part",       width="small"),
        "Material":   st.column_config.TextColumn("Material",   width="medium"),
        "L (mm)":     st.column_config.NumberColumn("L (mm)",   width="small"),
        "W (mm)":     st.column_config.Column("W (mm)",         width="small"),
        "Qty":        st.column_config.NumberColumn("Qty",      width="small"),
    }
)

# ---------------------------------------------------------------------------
# COST BREAKDOWN
# ---------------------------------------------------------------------------
st.subheader("Cost Breakdown")

costs = calculate_costs(
    result=result,
    frame_parts=frame_parts,
    nDrwT=nDrwT, nDrwM=nDrwM, nDrwB=nDrwB,
    nDrw=nDrw,
    cSlides=cSlides,
    c4040=c4040, c4080=c4080,
    cTbl=cTbl, cCastor=cCastor,
    frmWo=frmWo, frmDo=frmDo, tTbl=tTbl,
)

# Derived quantities from already-computed values
tbl_area_m2    = ((frmWo + 50) * frmDo) * 1e-6
panels_area_m2 = sum(result[t]['A_panels_m2'] * q for t, q in [('low', nDrwT), ('mid', nDrwM), ('high', nDrwB)])
base_area_m2   = sum(result[t]['A_base_m2']   * q for t, q in [('low', nDrwT), ('mid', nDrwM), ('high', nDrwB)])
len_4040_m     = sum(p['Qty'] * p['L (mm)'] / 1000 for p in frame_parts if p['Material'] == '4040')
len_uprights_m = sum(p['Qty'] * p['L (mm)'] / 1000 for p in frame_parts if p['Material'] == uprights and uprights != '4040')

cost_df = pd.DataFrame([
    {
        "Category": "Frame",
        "Description": "4040 Profiles",
        "Qty": f"{len_4040_m:.2f} m",
        "Cost (CHF)": c4040 * len_4040_m,
    },
    *([{
        "Category": "Frame",
        "Description": f"{uprights} Profiles",
        "Qty": f"{len_uprights_m:.2f} m",
        "Cost (CHF)": c4080 * len_uprights_m,
    }] if uprights != '4040' else []),
    {
        "Category": "Wood",
        "Description": "Panel wood",
        "Qty": f"{panels_area_m2:.2f} m²",
        "Cost (CHF)": cBox * panels_area_m2,
    },
    {
        "Category": "Wood",
        "Description": "Base wood",
        "Qty": f"{base_area_m2:.2f} m²",
        "Cost (CHF)": cBase * base_area_m2,
    },
    {
        "Category": "Accessories",
        "Description": "Drawer Slides",
        "Qty": f"{nDrw} pairs",
        "Cost (CHF)": cSlides * nDrw,
    },
    {
        "Category": "Accessories",
        "Description": "Tabletop",
        "Qty": f"{tbl_area_m2:.2f} m²",
        "Cost (CHF)": cTbl * tbl_area_m2,
    },
    {
        "Category": "Accessories",
        "Description": "Wheels",
        "Qty": "4 pcs",
        "Cost (CHF)": cCastor * 4,
    },
])

st.dataframe(
    cost_df,
    hide_index=True,
    width="content",
    height="content",
    column_config={
        "Category":    st.column_config.TextColumn("Category",    width="content"),
        "Description": st.column_config.TextColumn("Description", width="content"),
        "Qty":         st.column_config.TextColumn("Qty",         width="content"),
        "Cost (CHF)":  st.column_config.NumberColumn("Cost (CHF)",  width="content", format="%.2f"),
    }
)

st.metric("Total Estimated Cost", f"CHF {costs['total']:.2f}")
st.caption(f"Slides per pair:   {cSlides} CHF",     text_alignment="center")
st.caption(f"Tabletop per m²:   {cTbl:.0f} CHF",   text_alignment="center")
st.caption(f"Wheels per piece:  {cCastor:.0f} CHF", text_alignment="center")
    
# ---------------------------------------------------------------------------
# 3D PREVIEW
# ---------------------------------------------------------------------------
st.subheader("3D Preview")

parts = build_assembly(
    frmWo=frmWo, frmHo=frmHo, frmDo=frmDo,
    frmWi=frmWi, frmHi=frmHi, frmDi=frmDi,
    tUprights=tUprights, uprights=uprights,
    tTbl=tTbl, hCastors=hCastors,
    nDrwT=nDrwT, nDrwM=nDrwM, nDrwB=nDrwB,
    drwW=drwW, drwD=drwD,
    drwHt=drwHt, drwHm=drwHm, drwHb=drwHb,
    tBox=tBox, sDrw=sDrw,
    w4040=w4040, sRear=sRear, sFront=sFront,
)

render_3d(parts, height=650)