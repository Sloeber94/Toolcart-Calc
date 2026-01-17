import streamlit as st
import pandas as pd
from cutlist_calculator import calculate_drawer, generate_cutlist, calculate_toolbox_frame

st.set_page_config(page_title="Drawer Calculator", layout="wide")
st.title("🔨 Drawer Box Cost & Cutlist Calculator")
st.markdown("Calculate costs and generate cutting lists for drawer cabinets.")

with st.sidebar:
    st.header("📏 Configuration")
    
    # TABS
    tab1, tab2 = st.tabs(["Fixed", "Variable"])
    
    with tab1:
        st.subheader("Prices & Hardware")
        Cp = st.number_input("Panel Cost (CHF/m²)", 5, 100, 30)
        Cb = st.number_input("Base Cost (CHF/m²)", 2, 50, 10)
        slide_thick = st.number_input("Slide Thickness", 15, 40, 25)
        frame_clear = st.number_input("Rear Clearance", 30, 100, 50)
        td = st.number_input("Dado (mm)", 3, 15, 6)
        t = st.number_input("Material (mm)", 5, 30, 15)
    
    with tab2:
        st.subheader("Dimensions")
        Wi = st.number_input("Inner Width", 50, 2000, 845, step=10)
        Di = st.number_input("Inner Depth", 50, 2000, 450, step=10)
        hl = st.number_input("Low Height", 40, 300, 80, step=10)
        hm = st.number_input("Mid Height", 40, 300, 150, step=10)
        hh = st.number_input("High Height", 40, 300, 250, step=10)
    
    st.subheader("Quantities")
    col1, col2, col3 = st.columns(3)
    with col1: nl = st.number_input("# Low", 0, 10, 1)
    with col2: nm = st.number_input("# Mid", 0, 10, 2)
    with col3: nh = st.number_input("# High", 0, 10, 1)

# CALCULATIONS
result = calculate_drawer(Wi, Di, hl, hm, hh, t, td, Cp, Cb)
frame = calculate_toolbox_frame(result, slide_thick, frame_clear, nl=nl, nm=nm, nh=nh)

# FRAME DISPLAY
st.subheader("🛠️ Toolbox Frame Dimensions")
col1, col2, col3 = st.columns(3)
with col1: st.metric("Frame Inner Height", f"{frame['inner_height']:.0f} mm")
with col2: st.metric("Frame Inner Width", f"{frame['inner_width']:.0f} mm")
with col3: st.metric("Frame Outer Depth", f"{frame['outer_depth']:.0f} mm")

with st.expander("Frame Details"):
    st.info(f"Spacing: ({frame['n_drawers']}+1)×10mm = {frame['spacing_used']}mm")
    st.info(f"Slides: 2×{slide_thick}mm = {frame['slides_width']}mm")

# CABINET DIMENSIONS
st.subheader("Cabinet Dimensions")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Inner Width", f"{result['dimensions']['Wi']} mm")
with col2: st.metric("Inner Depth", f"{result['dimensions']['Di']} mm")
with col3: st.metric("Outer Width", f"{result['dimensions']['Wo']} mm")
with col4: st.metric("Outer Depth", f"{result['dimensions']['Do']} mm")

# PRICE SUMMARY
st.subheader("Cost Summary")
col1, col2, col3 = st.columns(3)
cost_l = result['low']['cost_total'] * nl
cost_m = result['mid']['cost_total'] * nm
cost_h = result['high']['cost_total'] * nh
with col1: st.metric("Low (×qty)", f"CHF {cost_l:.2f}")
with col2: st.metric("Mid (×qty)", f"CHF {cost_m:.2f}")
with col3: st.metric("High (×qty)", f"CHF {cost_h:.2f}")

total_cost = cost_l + cost_m + cost_h
st.metric("**TOTAL COST**", f"**CHF {total_cost:.2f}**")

# PRICE BREAKDOWN
st.subheader("Price Breakdown (per drawer)")
tabs = st.tabs(["Low", "Mid", "High"])

for idx, (tab, key) in enumerate([(tabs[0], 'low'), (tabs[1], 'mid'), (tabs[2], 'high')]):
    with tab:
        data = result[key]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**Panels:** {data['A_panels_m2']:.4f} m²")
            st.write(f"CHF {data['cost_panels']:.2f}")
        with col2:
            st.write(f"**Base:** {data['A_base_m2']:.4f} m²")
            st.write(f"CHF {data['cost_base']:.2f}")
        with col3: st.write(f"**Height:** {data['height']} mm")
        with col4: st.write(f"**Total/unit:** CHF {data['cost_total']:.2f}")

# CUTLIST TABLES
st.subheader("Cut Lists")
tabs_cutlist = st.tabs(["Low", "Mid", "High"])

for idx, (tab, (key, qty)) in enumerate([(tabs_cutlist[0], ('low', nl)), (tabs_cutlist[1], ('mid', nm)), (tabs_cutlist[2], ('high', nh))]):
    with tab:
        data = result[key]
        cutlist = generate_cutlist(Wi, Di, data['height'], 
                                  result['dimensions']['Wo'], 
                                  result['dimensions']['Do'],
                                  result['dimensions']['Wb'],
                                  result['dimensions']['Db'], qty)
        df = pd.DataFrame(cutlist)
        st.dataframe(df, width="stretch")
        
        csv = df.to_csv(index=False)
        st.download_button(
            label=f"Download {key.upper()} Cutlist (CSV)",
            data=csv,
            file_name=f"cutlist_{key}.csv",
            mime="text/csv"
        )

st.markdown("---")
st.info("💡 Adjust parameters in sidebar tabs.")
