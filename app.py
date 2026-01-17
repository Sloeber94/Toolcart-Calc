import streamlit as st
import pandas as pd
from cutlist_calculator import calculate_drawer, generate_cutlist

st.set_page_config(page_title="Drawer Calculator", layout="wide")

st.title("🔨 Drawer Box Cost & Cutlist Calculator")
st.markdown("Calculate costs and generate cutting lists for drawer cabinets.")

# MASTER CONFIG (change bounds here!)
CONFIG = {
    "dimensions": {
        "Wi": {"label": "Inner Width", "min": 50, "max": 2000, "def": 845, "step": 10},
        "Di": {"label": "Inner Depth", "min": 50, "max": 2000, "def": 450, "step": 10},
        "t": {"label": "Thickness", "min": 5, "max": 30, "def": 15, "step": 1},
        "td": {"label": "Dado", "min": 3, "max": 15, "def": 6, "step": 1}
    },
    "heights": {
        "hl": {"label": "Low Height", "min": 40, "max": 300, "def": 80, "step": 10},
        "hm": {"label": "Mid Height", "min": 40, "max": 300, "def": 150, "step": 10},
        "hh": {"label": "High Height", "min": 40, "max": 300, "def": 250, "step": 10}
    },
    "costs": {
        "Cp": {"label": "Panel Cost", "min": 5, "max": 100, "def": 30, "step": 1},
        "Cb": {"label": "Base Cost", "min": 2, "max": 50, "def": 10, "step": 1}
    },
    "quantities": {
        "nl": {"label": "# Low", "min": 0, "max": 10, "def": 1, "step": 1},
        "nm": {"label": "# Mid", "min": 0, "max": 10, "def": 2, "step": 1},
        "nh": {"label": "# High", "min": 0, "max": 10, "def": 1, "step": 1}
    }
}

# Sidebar: AUTO-GENERATED from CONFIG
with st.sidebar:
    st.header("📏 Configuration")
    
    vars = {}  # Store all values
    
    for section_name, section in CONFIG.items():
        st.subheader(section_name.title().replace("_", " "))
        
        for var_name, params in section.items():
            # Slider first
            slider_val = st.slider(
                params["label"], 
                params["min"], 
                params["max"], 
                params["def"], 
                step=params["step"]
            )
            
            # Editable number input below
            vars[var_name] = st.number_input(
                f"Edit {params['label']}", 
                value=slider_val,
                min_value=params["min"],
                max_value=params["max"],
                step=params["step"]
            )
    
    # Extract ALL variables (one line!)
    Wi, Di, t, td = vars["Wi"], vars["Di"], vars["t"], vars["td"]
    hl, hm, hh = vars["hl"], vars["hm"], vars["hh"]
    Cp, Cb = vars["Cp"], vars["Cb"]
    nl, nm, nh = vars["nl"], vars["nm"], vars["nh"]

# Main: Calculate
result = calculate_drawer(Wi, Di, hl, hm, hh, t, td, Cp, Cb)

# Display Dimensions
st.subheader("Cabinet Dimensions")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Inner Width", f"{result['dimensions']['Wi']} mm")
with col2:
    st.metric("Inner Depth", f"{result['dimensions']['Di']} mm")
with col3:
    st.metric("Outer Width", f"{result['dimensions']['Wo']} mm")
with col4:
    st.metric("Outer Depth", f"{result['dimensions']['Do']} mm")

# Price Summary
st.subheader("Cost Summary")
col1, col2, col3 = st.columns(3)
with col1:
    cost_l = result['low']['cost_total'] * nl
    st.metric("Low Height (×qty)", f"CHF {cost_l:.2f}")
with col2:
    cost_m = result['mid']['cost_total'] * nm
    st.metric("Mid Height (×qty)", f"CHF {cost_m:.2f}")
with col3:
    cost_h = result['high']['cost_total'] * nh
    st.metric("High Height (×qty)", f"CHF {cost_h:.2f}")

total_cost = cost_l + cost_m + cost_h
st.metric("**TOTAL COST**", f"**CHF {total_cost:.2f}**", delta=None)

# Detailed Price Breakdown
st.subheader("Price Breakdown (per drawer)")
tabs = st.tabs(["Low", "Mid", "High"])

for idx, (tab, key) in enumerate([(tabs[0], 'low'), (tabs[1], 'mid'), (tabs[2], 'high')]):
    with tab:
        data = result[key]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**Panels Area:** {data['A_panels_m2']:.4f} m²")
            st.write(f"**Cost:** CHF {data['cost_panels']:.2f}")
        with col2:
            st.write(f"**Base Area:** {data['A_base_m2']:.4f} m²")
            st.write(f"**Cost:** CHF {data['cost_base']:.2f}")
        with col3:
            st.write(f"**Height:** {data['height']} mm")
        with col4:
            st.write(f"**Total/unit:** CHF {data['cost_total']:.2f}")

# Cutlist Tables
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
        st.dataframe(df, use_container_width=True)
        
        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label=f"Download {key.upper()} Cutlist (CSV)",
            data=csv,
            file_name=f"cutlist_{key}.csv",
            mime="text/csv"
        )

st.markdown("---")
st.info("💡 Adjust parameters in the sidebar to explore cost variations.")
