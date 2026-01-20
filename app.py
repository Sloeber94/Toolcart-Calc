<<<<<<< HEAD
import os
import pandas as pd
import streamlit as st
from config import DEFAULTS, SLIDERS, NUMBER_RANGES
from cutlist_calculator import calculate_drawer,generate_cutlist, generate_drawer_cutlist, calculate_toolbox_frame

def load_css():
    css_path = "styles.css"
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.set_page_config(page_title="Drawer Calculator", layout="wide")


st.title("🔨 Verschraubt.ch: Tool Trolley Project Calculator")
st.markdown(
    "Fully customizable by you, just enter your requirements and let it calculate your materials."
)
with st.sidebar:
    st.header("📏 Configuration")
    gf_mode = st.sidebar.checkbox("Gridfinity Mode")

    #gridfinity units
    ss = 0.5 if gf_mode else 1.0 #0.5u GF or 1 mm
    ms = 1 if gf_mode else 5 #1.0u GF or 5 mm
    gf = 42

    #drawer dimensions
    drwStep = ms if gf_mode else 50 #drawer slide stroke length in 50 mm or gf units with small under/overlap
    drwMin = 0
    drwMax = 40 if gf_mode else 2000 #max width
    drwWmax = 40 if gf_mode else 1000 #max depth
    drwDef = drwMax//2 #default slider value
    lblQt = "u" if gf_mode else "mm" #units in u (GF units) or mm
    gfStep = gf if gf_mode else 1 #conversion to mm step if GF chosen
    nMin = 0 #amount of drawers minimum value
    nMax = 20 #amount of drawers maximum value

    hMin = float(0) #min drawer height
    hMax = float(12 if gf_mode else 500) #max drawer height
    hDef = float(1 if gf_mode else 50) #default drawer height

    #design defaults
    tBox=15 #thickness drawer box material
    tBase=5 #thickness drawer base material
    tBkt=2 #thickness drawer bracket
    sRear = 40 #distance rear drawer slide to outer frame
    sRear40 = 20
    sRear80 = 35
    sDrw = 2 #drawer spacing
    sDadoMax =tBox//2 #dado depth in sides and fronts
    sFront = 5 #distance front drawer slide to outer frame
    w4040=40 #alu profile side 
    w4080=80 #alu profile side



    tabs = st.tabs(["Input", "Constants"])
    # TAB 0: INPUTS - Fixed formats
    with tabs[0]:
        # Width
        col1, col2 = st.columns([4, 1])
        with col1:
            drwLu = st.slider("Drawer Width", drwMin, drwMax, drwDef, ms, format=f"%g {lblQt}")
            drwL = drwLu * gfStep
        with col2:
            if gf_mode: 
                st.caption(f"{int(drwL)} mm", text_alignment="right")

        # Depth
        col1, col2 = st.columns([4, 1])
        with col1:
            drwWu = st.slider("Drawer Depth", drwMin, drwWmax, drwDef, drwStep, format=f"%g {lblQt}")
            drwW = drwWu * gfStep
        with col2:
            if gf_mode:
                st.caption(f"{int(drwW)} mm", text_alignment="right")

        st.subheader("Drawer Heights")
        # Top
        col1, col2 = st.columns([4, 1])
        with col1:
            drwHtu = st.slider("Top", hMin, hMax, hDef, ss, format=f"%.1f {lblQt}")
            drwHt = drwHtu * gfStep
        with col2:
            if gf_mode:
                st.caption(f"{int(drwHt)} mm", text_alignment="center")

        # Middle  
        col1, col2 = st.columns([4, 1])
        with col1:
            drwHmu = st.slider("Middle", hMin, hMax, hDef, ss, format=f"%.1f {lblQt}")
            drwHm = drwHmu * gfStep
        with col2:
            if gf_mode:
                st.caption(f"{int(drwHm)} mm", text_alignment="center")

        # Bottom
        col1, col2 = st.columns([4, 1])
        with col1:
            drwHbu = st.slider("Bottom", hMin, hMax, hDef, ss, format=f"%.1f {lblQt}")
            drwHb = drwHbu * gfStep
        with col2:
            if gf_mode:
                st.caption(f"{int(drwHb)} mm", text_alignment="center")

        st.subheader("Drawer Quantities")
        col1, col2 = st.columns([4, 1])
        with col1:
            nDrwT = st.slider("Top", nMin, nMax, 7, 1, format="%d pcs")
        with col2:
            pass
        col1, col2 = st.columns([4, 1])
        with col1:
            nDrwM = st.slider("Middle", nMin, nMax, 4, 1, format="%d pcs")
        with col2:
            pass
        col1, col2 = st.columns([4, 1])
        with col1:
            nDrwB = st.slider("Bottom", nMin, nMax, 2, 1, format="%d pcs")
        with col2:
            pass


        st.subheader("Accessoires")
        hCastors=st.slider("Castors Height", 0, 200, 125, 1, format="%.1d mm")
        tTbl=st.slider("Tabletop thickness", 0, 50, 20, 1, format="%.1d mm")

    # TAB 1: CONSTANTS - Fixed formats
    with tabs[1]:
        st.subheader("Prices")
        col1, col2 = st.columns(2)
        with col1:
            cBox = st.number_input("Plywood CHF/m²", value=25.0, min_value=0.0, max_value=200.0, step=1.0, format="%.0f")
        with col2:
            cBase = st.number_input("Base CHF/m² ", value=15.0, min_value=0.0, max_value=200.0, step=1.0, format="%.0f")
        st.subheader("Drawer Slides")

        # Slide matrix - background data only
        slide_data = [
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

        # Lookup function
        def get_slide_data(feature, load_class):
            for row in slide_data:
                if row[0] == feature and row[1] == load_class:
                    return row[2], row[3]
            return 10, 19.0  # default

        # SINGLE dropdown set - 2-column row
        col1, col2 = st.columns(2)
        with col1:
            selected_feature = st.selectbox("Features", ["Basic", "Bumper", "Soft-Close", "Push-to-Open"], index=0)
        with col2:
            selected_load = st.selectbox("Load Class", ["Light", "Medium", "Heavy"], index=1)

            # Extract and display values
        cSlides, tSlides = get_slide_data(selected_feature, selected_load)
        st.caption(f"Price per pair: {cSlides} CHF", text_alignment="center")
        st.caption(f"Slide Thickness: {tSlides:.1f} mm", text_alignment="center")

        st.subheader("Dimensions")
        col1, col2 = st.columns([2,3])
        with col1:
            uprights = st.radio("Uprights profile", ["4040", "4080"], index=0)
        if uprights == "4040":  # Fixed ==
            frame_clear = 10
            tUprights=w4040
        else:
            frame_clear = 50
            tUprights=w4080
        with col2:
            frame_clear_man = st.number_input("Rear Clearance", value=frame_clear, min_value=0, max_value=100, step=1, help="Changes on profile selection, change only when required.")
        sRear = frame_clear_man

        st.subheader("Wood Dimensions")
        col1, col2, col3 = st.columns([2,2,2])
        with col1:
            t_box = st.slider("Plywood thickness", 0, 30, tBox, 1, format="%.0f mm")
        with col2:
            t_base = st.slider("Base thickness", 0, 30, tBase, 1, format="%.0f mm")
        tBox = t_box
        tBase = t_base
        sDadoMax = tBox//2
        sDado_auto = tBox//2
        with col3:
            sDado = st.slider("Dado depth", min_value=2, max_value=sDadoMax, value=sDado_auto, step=1, format="%.0f mm",help="Default to <50% of Plywood thickness")



# CALCULATIONS
# -----------------------------
result = calculate_drawer(drwL,drwW,drwHt,drwHm,drwHb,tBox,sDado,cBox,cBase)

nDrw = nDrwT+nDrwM+nDrwB #total drawers
slides_cost = nDrw * cSlides

frame = calculate_toolbox_frame(
    result,           # calculate_drawer output
    tSlides,          # slide_thickness  
    sRear,            # Back Spacing (dist drawer slide to outer frame)
    sFront,           # Front spacing (dist drawer to outer frame)
    nDrwT,            # Top drawer count              
    nDrwM,            # Middle drawer count
    nDrwB,            # Bottom drawer count
    nDrw,             # total drawers
    sDrw,             # spacing per drawer
    tBkt              # Thickness Drawer Bracket    
)



frmHi, frmWi, frmDo, sDrwTot = frame.values()
##intermediate calcs
frmHo = frmHi+2*w4040
frmWo = frmWi+2*w4040
frmDi = frmDo-2*tUprights
trlH = frmHo+hCastors+tTbl
trlW=frmWo
trlD=frmDo
# -----------------------------
# FRAME DISPLAY
# -----------------------------
st.subheader("🛠️ Tool Trolley frame dimensions")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Frame outer Width", f"{frmWo:.0f} mm")
    st.metric("Frame inner Width",f"{frmWi:.0f} mm")
with col2:
    st.metric("Frame outer Depth", f"{frmDo:.0f} mm")
    st.metric("Frame inner Depth",f"{frmDi:.0f} mm")
with col3:
    st.metric("Frame outer Height",f"{frmHo:.0f} mm")
    st.metric("Frame inner Height",f"{frmHi:.0f} mm")

with st.expander("Frame Details"):
    st.info(f"Total spacing: {sDrwTot:.0f} mm")
    st.info(f"Tabletop working height: {trlH:.0f} mm")
   

# -----------------------------
# CABINET DIMENSIONS
# -----------------------------
# st.subheader("Cabinet Dimensions")
# col1, col2, col3, col4 = st.columns(4)
# with col1:
#     st.metric("Inner Width", f"{result['dimensions']['Wi']} mm")
# with col2:
#     st.metric("Inner Depth", f"{result['dimensions']['Di']} mm")
# with col3:
#     st.metric("Outer Width", f"{result['dimensions']['Wo']} mm")
# with col4:
#     st.metric("Outer Depth", f"{result['dimensions']['Do']} mm")

# -----------------------------

# -----------------------------
# CUTLIST (MERGED)
# -----------------------------
st.subheader("📋 Cutlist of Wood and Profiles")

# After result = calculate_drawer(...)
drawer_parts = generate_drawer_cutlist(result, nDrwT, nDrwM, nDrwB)

# Add frame/tabletop (keep in app.py - simple)
all_parts = drawer_parts + [
    {"Type": "Profile", "Component": "Verticals", "L (mm)": frmHo, "W (mm)": profile_thick, "Qty": 4},
    # ... other profiles
    {"Type": "Plywood", "Component": "Tabletop", "L (mm)": frmWo+50, "W (mm)": frmDi+50, "Qty": 1}
]

df_raw = pd.DataFrame(all_parts)
df_merged = df_raw.groupby(["Part", "L (mm)", "W (mm)"]).agg({"Qty": "sum"}).reset_index()
st.dataframe(df_merged)


# PRICE SUMMARY
# -----------------------------
st.subheader("💰 Cost Summary")

# Drawer costs (total wood area × price/m²)
drawers_area_panels = (result["low"]["A_panels_m2"] * nDrwT + 
                      result["mid"]["A_panels_m2"] * nDrwM + 
                      result["high"]["A_panels_m2"] * nDrwB)
drawers_area_bases = (result["low"]["A_base_m2"] * nDrwT + 
                     result["mid"]["A_base_m2"] * nDrwM + 
                     result["high"]["A_base_m2"] * nDrwB)

cost_drawers_panels = drawers_area_panels * cBox
cost_drawers_bases = drawers_area_bases * cBase
cost_drawers_total = cost_drawers_panels + cost_drawers_bases

# Slides + brackets (4 brackets/drawer = 2 brackets/slide × 2 slides/drawer)
cost_slides = slides_cost  # nDrw × cSlides (pairs)
cBracket = 2.50  # CHF per bracket (draft)
cost_brackets = nDrw * 4 * cBracket

# Hardware totals
cost_hardware = cost_slides + cost_brackets  # + castors + tabletop + fasteners later

# Frame (TODO)
# profile_length_m = (2*frmHo + 2*frmWo + 2*frmDo) / 1000  # Perimeter × height
# cProfile = 15  # CHF/m 4040 profile
# cost_frame = profile_length_m * cProfile

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🪵 Drawers Panels", f"CHF {cost_drawers_panels:.1f}")
with col2:
    st.metric("🪵 Drawers Bases", f"CHF {cost_drawers_bases:.1f}")
with col3:
    st.metric("🔩 Slides+Brackets", f"CHF {cost_hardware:.1f}")
with col4:
    st.metric("🏗️ Frame", "TBD")  # TODO: profile cutlist

# GRAND TOTAL
total_cost = cost_drawers_total + cost_hardware  # + cost_frame later
st.metric("**GRAND TOTAL**", f"**CHF {total_cost:.1f}**", 
          help=f"Drawers: {cost_drawers_total:.1f} + Hardware: {cost_hardware:.1f}")

with st.expander("Cost Breakdown"):
    st.info(f"**Drawers total area:** Panels {drawers_area_panels:.3f}m² × {cBox}CHF = {cost_drawers_panels:.1f}CHF")
    st.info(f"**Bases total area:** {drawers_area_bases:.3f}m² × {cBase}CHF = {cost_drawers_bases:.1f}CHF") 
    st.info(f"**Hardware:** {nDrw} slides ({slides_cost:.1f}CHF) + {nDrw*4} brackets ({cost_brackets:.1f}CHF)")

=======
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
>>>>>>> c8b13b13627046af9a95b5223bbebc1f3e502cdf
