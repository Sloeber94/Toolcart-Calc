import streamlit as st
import pandas as pd
from cutlist_calculator import calculate_drawer, generate_cutlist, calculate_toolbox_frame

st.set_page_config(page_title="Drawer Calculator", layout="wide")
st.title("🔨 Drawer Box Cost & Cutlist Calculator")
st.markdown("Calculate costs and generate cutting lists for drawer cabinets.")

with st.sidebar:
    st.header("📏 Configuration")
    
    # TABS - FIXED INDENTATION
    tabs = st.tabs(["Variable", "Fixed"])
    
    with tabs[0]:
        st.subheader("Drawer Dimensions")
        
        col1, col2 = st.columns(2)
        with col1:
            Wi_slider = st.slider("Inner Width (mm)", 50, 1000, 845, 5, help="Drawer inside width")
            Wi = st.number_input("Edit Width", value=Wi_slider, min_value=50, max_value=2000, step=10)
        with col2:
            Di_slider = st.slider("Inner Depth (mm)", 50, 2000, 450, 10, help="Drawer inside depth")
            Di = st.number_input("Edit Depth", value=Di_slider, min_value=50, max_value=2000, step=10)
        
        st.subheader("Drawer Heights")
        col1, col2, col3 = st.columns(3)
        with col1:
            hl_slider = st.slider("Top (mm)", 40, 300, 80, 10, help="Top drawer")
            hl = st.number_input("Edit", value=hl_slider, min_value=40, max_value=300, step=10)
        with col2:
            hm_slider = st.slider("Middle (mm)", 40, 300, 150, 10, help="Middle drawer")
            hm = st.number_input("Edit", value=hm_slider, min_value=40, max_value=300, step=10)
        with col3:
            hh_slider = st.slider("Bottom (mm)", 40, 300, 250, 10, help="Bottom drawer")
            hh = st.number_input("Edit", value=hh_slider, min_value=40, max_value=300, step=10)
        
        st.subheader("Drawer Quantities")
        col1, col2, col3 = st.columns(3)
        with col1:
            nl_slider = st.slider("Top", 0, 10, 1, 1, help="Top drawer quantity")
            nl = nl_slider  # FIXED: assign slider value
        with col2:
            nm_slider = st.slider("Middle", 0, 10, 2, 1, help="Middle drawer quantity")
            nm = nm_slider  # FIXED: assign slider value
        with col3:
            nh_slider = st.slider("Bottom", 0, 10, 1, 1, help="Bottom drawer quantity")
            nh = nh_slider  # FIXED: assign slider value
    
with tabs[1]:
    st.subheader("Prices & Hardware")
    
    col1, col2 = st.columns(2)
    with col1:
        Cp = st.number_input("Panel Cost (CHF/m²)", value=30.0, min_value=5.0, max_value=100.0, step=1.0)
    with col2:
        Cb = st.number_input("Base Cost (CHF/m²)", value=10.0, min_value=2.0, max_value=50.0, step=1.0)
    
    st.subheader("Drawer Slides")
    col1, col2 = st.columns(2)
    with col1:
        slide_price_slider = st.slider("Price per Pair (CHF)", 5.0, 25.0, 15.0, 0.5, 
                                       help="B2B price range for telescopic/full-extension slides")
        slide_price = st.number_input("Edit Slide Price", value=slide_price_slider, 
                                      min_value=5.0, max_value=25.0, step=0.5)
    with col2:
        slide_thick_slider = st.slider("Slide Thickness (mm)", 10.0, 30.0, 25.0, 0.1, format="%.1f")
        slide_thick = st.number_input("Edit Thickness", value=slide_thick_slider, 
                                      min_value=10.0, max_value=30.0, step=0.1)
    
    frame_clear = st.number_input("Rear Clearance (mm)", value=50.0, min_value=30.0, max_value=100.0, step=5.0)
    td = st.number_input("Dado (mm)", value=6.0, min_value=3.0, max_value=15.0, step=0.1)
    t = st.number_input("Material (mm)", value=15.0, min_value=5.0, max_value=30.0, step=0.1)

# CALCULATIONS - FIXED ARGUMENTS
result = calculate_drawer(Wi, Di, hl, hm, hh, t, td, Cp, Cb)
total_drawers = nl + nm + nh
slides_cost = total_drawers * slide_price
frame = calculate_toolbox_frame(result, slide_thick, frame_clear, nl=nl, nm=nm, nh=nh)  # FIXED: nl/nm/nh not sliders

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
total_drawers = nl + nm + nh
slides_cost = total_drawers * slide_price

col1, col2, col3, col4 = st.columns(4)
cost_l = result['low']['cost_total'] * nl
cost_m = result['mid']['cost_total'] * nm
cost_h = result['high']['cost_total'] * nh
with col1: st.metric("Low", f"CHF {cost_l:.1f}")
with col2: st.metric("Mid", f"CHF {cost_m:.1f}")
with col3: st.metric("High", f"CHF {cost_h:.1f}")
with col4: st.metric("Slides", f"CHF {slides_cost:.1f}", 
                     delta=f"({total_drawers} prs)")

total_cost = cost_l + cost_m + cost_h + slides_cost
st.metric("**GRAND TOTAL**", f"**CHF {total_cost:.1f}**")




#Cutlist

# COMBINED CUTLIST WITH MERGED IDENTICAL PIECES
st.subheader("📋 Complete Cutlist (Merged Identical Pieces)")

all_parts = []

for drawer_type, height_key, qty in [('Top', 'low', nl), ('Middle', 'mid', nm), ('Bottom', 'high', nh)]:
    data = result[height_key]
    h = data['height']
    
    # Fronts
    all_parts.append({
        'Drawer': drawer_type,
        'Part': 'Fronts', 
        'Length (mm)': Wi,
        'Width (mm)': h,
        'Qty': 2 * qty
    })
    
    # Sides  
    all_parts.append({
        'Drawer': drawer_type,
        'Part': 'Sides',
        'Length (mm)': result['dimensions']['Do'],
        'Width (mm)': h,
        'Qty': 2 * qty
    })
    
    # Base
    all_parts.append({
        'Drawer': drawer_type, 
        'Part': 'Base',
        'Length (mm)': result['dimensions']['Wb'],
        'Width (mm)': result['dimensions']['Db'],
        'Qty': qty
    })

df_raw = pd.DataFrame(all_parts)

# MERGE IDENTICAL DIMENSIONS ACROSS DRAWERS
df_merged = df_raw.groupby(['Part', 'Length (mm)', 'Width (mm)']).agg({
    'Qty': 'sum',
    'Drawer': lambda x: ', '.join(sorted(set(x)))  # "Top, Middle"
}).reset_index()

df_merged = df_merged[['Part', 'Length (mm)', 'Width (mm)', 'Qty', 'Drawer']]

st.dataframe(df_merged.round(1), width="stretch")

csv_merged = df_merged.round(1).to_csv(index=False)
st.download_button(
    label="📥 Download Merged Cutlist (CSV)",
    data=csv_merged,
    file_name="merged_cutlist.csv", 
    mime="text/csv"
)