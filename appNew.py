import os
import pandas as pd
import streamlit as st
from configNew import DEFAULTS, SLIDERS, SLIDES, get_slide_data
from cutlist_calculatorNew import (
    calculate_drawer, calculate_toolbox_frame, 
    generate_frame_parts, generate_drawer_cutlist
)

st.set_page_config(page_title="Tool Trolley Calculator", layout="wide")
st.title("🔨 Verschraubt.ch: Tool Trolley Project")

# ============ SIDEBAR CONFIGURATION ============
with st.sidebar:
    st.header("📏 Configuration")
    gf_mode = st.checkbox("Gridfinity Mode")
    uprights = st.radio("Uprights Profile", ["4040", "4080"], index=0)
    tabs = st.tabs(["Input", "Constants"])
# ============ INPUT TAB ============

    with tabs[0]:
        st.subheader("Drawer Dimensions")
        col1, col2 = st.columns(2)
        with col1:
            drwL = st.slider("Width", 100, 2000, DEFAULTS["drwL"], 50, format="%g mm")
        with col2:
            drwW = st.slider("Depth", 100, 1000, DEFAULTS["drwW"], 50, format="%g mm")
    
        st.subheader("Drawer Heights")
        col1, col2, col3 = st.columns(3)
        with col1:
            drwHt = st.slider("Top", 20, 300, DEFAULTS["drwHt"], 10, format="%.0f mm")
        with col2:
            drwHm = st.slider("Mid", 20, 300, DEFAULTS["drwHm"], 10, format="%.0f mm")
        with col3:
            drwHb = st.slider("Bottom", 20, 300, DEFAULTS["drwHb"], 10, format="%.0f mm")
        
        st.subheader("Drawer Quantities")
        col1, col2, col3 = st.columns(3)
        with col1:
            nDrwT = st.slider("Top", 1, 20, DEFAULTS["nDrwT"], 1, format="%d pcs")
        with col2:
            nDrwM = st.slider("Mid", 0, 20, DEFAULTS["nDrwM"], 1, format="%d pcs")
        with col3:
            nDrwB = st.slider("Bottom", 0, 20, DEFAULTS["nDrwB"], 1, format="%d pcs")

        st.subheader("Accessories")
        col1, col2 = st.columns(2)
        with col1:
            hCastors = st.slider("Castors Height", 0, 200, DEFAULTS["hCastors"], 10)
        with col2:
            tTabletop = st.slider("Tabletop Thickness", 15, 50, DEFAULTS["tTabletop"], 1)


    with tabs[1]:
# ============ PRICING TAB ============
        st.subheader("💰 Prices")
        col1, col2 = st.columns(2)
        with col1:
            cBox = st.number_input("Plywood CHF/m²", 1.0, 200.0, DEFAULTS["cBox"], 1.0)
        with col2:
            cBase = st.number_input("Base CHF/m²", 1.0, 200.0, DEFAULTS["cBase"], 1.0)

            st.subheader("Drawer Slides")
        col1, col2 = st.columns(2)
        with col1:
            slide_feature = st.selectbox("Features", ["Basic", "Bumper", "Soft-Close", "Push-to-Open"])
        with col2:
            slide_load = st.selectbox("Load Class", ["Light", "Medium", "Heavy"], index=1)

        tSlides, cSlides = get_slide_data(slide_feature, slide_load)

            # ============ MATERIAL THICKNESS ============
        st.subheader("Material Properties")
        col1, col2, col3 = st.columns(3)
        with col1:
            tBox = st.slider("Box Thickness", 5, 30, DEFAULTS["tBox"], 1, format="%.0f mm")
        with col2:
            tBase = st.slider("Base Thickness", 2, 20, DEFAULTS["tBase"], 1, format="%.0f mm")
        with col3:
            sDado = st.slider("Dado Depth", 2, 15, DEFAULTS["sDado"], 1, format="%.0f mm")

        # Frame rear clearance based on profile
        sRear = DEFAULTS["sRear40"] if uprights == "4040" else DEFAULTS["sRear80"]
        tUprights = DEFAULTS["w4040"] if uprights == "4040" else DEFAULTS["w4080"]

# ============ CALCULATIONS ============
nDrw = nDrwT + nDrwM + nDrwB
slides_cost = nDrw * cSlides

result = calculate_drawer(drwL, drwW, drwHt, drwHm, drwHb, tBox, sDado, cBox, cBase)

frame = calculate_toolbox_frame(
    result, tSlides, sRear, DEFAULTS["sFront"],
    nDrwT, nDrwM, nDrwB, nDrw, DEFAULTS["sDrw"], DEFAULTS["tBkt"]
)

frmHi, frmWi, frmDo, sDrwTot = frame['frmHi'], frame['frmWi'], frame['frmDo'], frame['sDrwTot']

# Outer dimensions
frmHo = frmHi + 2 * tUprights + hCastors + tTabletop
frmWo = frmWi + 2 * tUprights
frmDi = frmDo - 2 * tUprights
trlH = frmHo

# ============ DISPLAY RESULTS ============
st.subheader("🛠️ Frame Dimensions")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Outer Width", f"{frmWo:.0f} mm")
    st.metric("Inner Width", f"{frmWi:.0f} mm")
with col2:
    st.metric("Outer Depth", f"{frmDo:.0f} mm")
    st.metric("Inner Depth", f"{frmDi:.0f} mm")
with col3:
    st.metric("Outer Height", f"{frmHo:.0f} mm")
    st.metric("Inner Height", f"{frmHi:.0f} mm")

# ============ CUTLIST ============
st.subheader("📋 Cutlist")
drawer_parts = generate_drawer_cutlist(result, nDrwT, nDrwM, nDrwB)
frame_parts = generate_frame_parts(frmHo, frmWo, frmDo, tUprights)

all_parts = drawer_parts + frame_parts + [{
    "Type": "Plywood", "Component": "Tabletop", "L (mm)": frmWo + 50, "W (mm)": frmDi + 50, "Qty": 1
}]

df = pd.DataFrame(all_parts)
df_merged = df.groupby(["Type", "Component", "L (mm)", "W (mm)"], as_index=False).agg({"Qty": "sum"})
st.dataframe(df_merged, use_container_width=True)

csv = df_merged.to_csv(index=False)
st.download_button("📥 Download Cutlist CSV", csv, "cutlist.csv", "text/csv")

# ============ COST SUMMARY ============
st.subheader("💰 Cost Summary")

panels_area = result["low"]["A_panels_m2"] * nDrwT + result["mid"]["A_panels_m2"] * nDrwM + result["high"]["A_panels_m2"] * nDrwB
bases_area = result["low"]["A_base_m2"] * nDrwT + result["mid"]["A_base_m2"] * nDrwM + result["high"]["A_base_m2"] * nDrwB

cost_panels = panels_area * cBox
cost_bases = bases_area * cBase
cost_brackets = nDrw * 4 * DEFAULTS["cBracket"]
cost_total = cost_panels + cost_bases + slides_cost + cost_brackets

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🪵 Panels", f"CHF {cost_panels:.2f}")
with col2:
    st.metric("🪵 Bases", f"CHF {cost_bases:.2f}")
with col3:
    st.metric("🔩 Hardware", f"CHF {slides_cost + cost_brackets:.2f}")
with col4:
    st.metric("💰 TOTAL", f"CHF {cost_total:.2f}")
