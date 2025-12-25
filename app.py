import streamlit as st
import pandas as pd
import os
import glob
import altair as alt
import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="PSDnet.nl | Vaarstaten Archief",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- INJECT CUSTOM TOP BAR HTML ---
st.markdown("""
    <div class="custom-top-bar">
        <div class="bar-content">
            <a href="https://www.psdnet.nl" target="_self">← Terug naar PSDnet.nl</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- CONSTANTS ---
SOURCE_CITATION = "Data afkomstig uit Zeeuws Archief: 123 Provinciale Stoombootdiensten in Zeeland (PSD), 3.2.6 (917-920), 1952 ontbreekt in het archief."

# --- CSS STYLING & SVG PATTERNS ---
st.markdown(
    """
    <style>
    /* =============================================
       0. CUSTOM TOP BAR
       ============================================= */
    .custom-top-bar {
        position: fixed; top: 0; left: 0; width: 100%; height: 50px; 
        background-color: #e6c37d; border-top: 8px solid #181818; 
        z-index: 999999; display: flex; align-items: center; justify-content: center;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1); font-family: "Source Sans Pro", sans-serif;
    }
    .custom-top-bar a {
        color: #404348 !important; text-decoration: none; font-size: 0.95rem;
        font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
    }
    .custom-top-bar a:hover { color: #404348 !important; text-decoration: underline; }

    /* =============================================
       1. GLOBALE LAYOUT
       ============================================= */
    header[data-testid="stHeader"] { top: 50px !important; background: transparent !important; }
    div.block-container { padding-top: 6rem !important; padding-bottom: 1rem !important; }
    [data-testid="stElementToolbar"] { display: none !important; }
    
    h1 { padding-top: 0rem !important; margin-top: 0rem !important; padding-bottom: 0.5rem !important; }
    [data-testid="stSidebar"] h1 { margin-top: 0rem !important; }

    /* =============================================
       2. DESKTOP SPECIFIEK (> 768px)
       ============================================= */
    @media only screen and (min-width: 769px) {
        section[data-testid="stSidebar"] {
            top: 50px !important; height: calc(100vh - 50px) !important;
        }
        /* Verberg de toggle knop op desktop */
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    }

    /* =============================================
       3. MOBIEL SPECIFIEK (<= 768px)
       ============================================= */
    @media only screen and (max-width: 768px) {
        
        section[data-testid="stSidebar"] {
            top: 0px !important; height: 100vh !important; z-index: 1000020 !important;
        }
        
        /* Padding in sidebar op mobiel */
        section[data-testid="stSidebar"] > div > div:nth-child(2) {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 4rem !important;
        }

        /* MENU KNOP (> Icoon) */
        [data-testid="stSidebarCollapsedControl"] {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            position: fixed !important;
            top: 65px !important; 
            left: 10px !important;
            z-index: 1000003 !important;
            background-color: #263c52 !important;
            border: 2px solid #e6c37d !important;
            border-radius: 5px !important;
            width: auto !important;
            height: 35px !important;
            padding: 0 10px !important;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3) !important;
            color: transparent !important;
        }
        [data-testid="stSidebarCollapsedControl"] svg { display: none !important; }
        [data-testid="stSidebarCollapsedControl"]::after {
            content: "MENU"; color: #fff !important; font-weight: 700; font-size: 14px; letter-spacing: 1px;
            visibility: visible !important; display: block !important;
        }

        /* SLUIT KNOP (<< Icoon) */
        section[data-testid="stSidebar"] button[kind="header"] {
            background-color: #263c52 !important;
            border: 1px solid #e6c37d !important;
            color: white !important;
            margin-right: 1rem !important;
        }
        section[data-testid="stSidebar"] button[kind="header"] svg { fill: white !important; }

        div.block-container {
            padding-top: 8rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* Reset marge voor tekstlinks op mobiel (OVERAL) */
        div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) {
            margin-left: 0px !important; 
            margin-top: 5px !important;
        }
    }

    /* =============================================
       4. OVERIGE STYLING & JAARTALLEN FIX
       ============================================= */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.filter-box-marker) {
        background-color: #bbc2ba; padding: 0.8rem 1rem; border-radius: 10px; margin-bottom: 15px; border: 1px solid #9aa09a;
    }
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.filter-box-marker) p,
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.filter-box-marker) span {
        color: #1a2e1a; font-weight: 600; margin-bottom: 0px; display: flex; align-items: center; height: 100%;
    }
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.filter-box-marker) button {
        border-color: #1a2e1a; color: #1a2e1a; background-color: rgba(255,255,255,0.4);
    }
    
    /* --- STYLING VOOR TEKST-LINK KNOPPEN (JAARTALLEN) --- */
    div.year-link-marker { display: none; }
    
    /* STANDAARD (HOOFDINHOUD): Negatieve marge om tekst uit te lijnen */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) {
        display: flex; 
        flex-direction: row; 
        flex-wrap: wrap; 
        align-items: baseline; 
        gap: 0.4rem;
        margin-top: -10px; 
        margin-left: -23px; /* DESKTOP MARGIN */
    }
    
    /* UITZONDERING SIDEBAR: Hier moet de marge 0 zijn (anders valt het weg) */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) {
        margin-left: 0px !important;
    }
    
    /* Text styling */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) div[data-testid="stMarkdownContainer"] p {
        margin-bottom: 0px !important; 
        font-size: 0.85rem; 
        color: rgba(49, 51, 63, 0.7); 
        margin-right: 5px; 
        font-weight: 600;
    }

    /* Button styling */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) button {
        background-color: transparent !important; 
        border: none !important; 
        color: #003366 !important;
        text-decoration: underline; 
        padding: 0px !important; 
        margin: 0px !important; 
        height: auto !important;
        min-height: 0px !important; 
        line-height: 1.6 !important; 
        font-size: 0.85rem !important; 
        display: inline;
    }
    
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) button:hover {
        color: #FFCC00 !important; text-decoration: none;
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) div[data-testid="stElementContainer"] {
        width: auto !important; display: inline-flex !important;
    }
    
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) div[data-testid="stElementContainer"]:has(button):not(:last-child)::after {
        content: ","; color: rgba(49, 51, 63, 0.6); font-size: 0.8rem; margin-left: 0px; 
    }
    
    div.stButton > button { margin-top: 0px; }
    
    /* SVG Pattern */
    </style>
    <svg style="position: absolute; width: 0; height: 0; overflow: hidden;" aria-hidden="true">
      <defs>
        <pattern id="diagonal-stripe" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)">
          <rect width="8" height="8" fill="#f2f2f2"/> 
          <line x1="0" y1="0" x2="0" y2="8" stroke="#cccccc" stroke-width="2" />
        </pattern>
      </defs>
    </svg>
    """,
    unsafe_allow_html=True,
)

# --- HELPER: DUTCH DATE FORMATTING ---
def format_dutch_date(date_obj):
    if pd.isnull(date_obj):
        return ""
    months = {
        1: "januari", 2: "februari", 3: "maart", 4: "april",
        5: "mei", 6: "juni", 7: "juli", 8: "augustus",
        9: "september", 10: "oktober", 11: "november", 12: "december"
    }
    return f"{date_obj.day} {months[date_obj.month]} {date_obj.year}"

# --- HELPER: FORMAT NUMBER (No .0) ---
def format_ship_count(value):
    if value.is_integer():
        return f"{int(value)}"
    else:
        return f"{value:.1f}"

# --- HELPER: CALLBACKS ---
def update_date_range(new_range):
    st.session_state['date_range_picker'] = new_range

def reset_all_filters(full_range):
    st.session_state['date_range_picker'] = full_range
    st.session_state['pref_selected_ship'] = "Koningin Emma (1933)"
    st.session_state['pref_selected_route'] = "Vlissingen-Breskens"

# Nieuwe callbacks voor de dropdowns
def update_ship_pref():
    if 'widget_ship_selector' in st.session_state:
        st.session_state['pref_selected_ship'] = st.session_state['widget_ship_selector']

def update_route_pref():
    if 'widget_route_selector' in st.session_state:
        st.session_state['pref_selected_route'] = st.session_state['widget_route_selector']

# --- HELPER: CALCULATE METRICS ---
def calculate_metrics(df_subset):
    if df_subset.empty:
        return None
    
    min_date = df_subset['DateObj'].min()
    max_date = df_subset['DateObj'].max()
    total_days_range = (max_date - min_date).days + 1
    actual_days_present = df_subset['DateObj'].nunique()
    
    coverage_pct = 0
    if total_days_range > 0:
        coverage_pct = actual_days_present / total_days_range

    unique_years = sorted(df_subset['DateObj'].dt.year.unique())
    
    return {
        'min_date': min_date,
        'max_date': max_date,
        'total_days': total_days_range,
        'actual_days': actual_days_present,
        'coverage': coverage_pct,
        'years': unique_years
    }

# --- HELPER: DATA PREP FOR TIMELINE ---
def prepare_timeline_data(ship_df, ship_name):
    df = ship_df.copy()
    df = df.sort_values('DateObj')
    df['Status'] = df['Status'].fillna('Onbekend')
    
    df['grp_change'] = (df['Status'] != df['Status'].shift()) | (df['DateObj'].diff().dt.days > 1)
    df['grp_id'] = df['grp_change'].cumsum()
    
    intervals = df.groupby(['grp_id', 'Status']).agg(
        Start=('DateObj', 'min'),
        End=('DateObj', 'max')
    ).reset_index()
    
    intervals['End'] = intervals['End'] + pd.Timedelta(days=1)
    intervals['ShipLabel'] = ship_name
    return intervals

# --- HELPER: DISPLAY METRICS (MET DE JAARTALLEN ERONDER) ---
def display_coverage_metrics(metrics, current_start, current_end, min_global, max_global, show_years=True, extra_text=None):
    if not metrics:
        return

    # Datadekking is verwijderd. Alleen extra tekst tonen indien aanwezig (bijv. gemiddelde)
    if extra_text:
        st.caption(extra_text)
    
    is_filtered = (current_start != min_global) or (current_end != max_global)
    
    # Als jaren getoond moeten worden, zet ze er direct onder (CSS trekt ze omhoog en naar links)
    if not is_filtered and show_years and metrics['years']:
        with st.container():
            # De CSS class 'year-link-marker' zorgt voor styling en positionering
            st.markdown('<div class="year-link-marker"></div>', unsafe_allow_html=True)
            st.markdown("**Beschikbare jaren:**")
            
            for year in metrics['years']:
                start_y = datetime.date(year, 1, 1)
                end_y = datetime.date(year, 12, 31)
                start_y = max(start_y, min_global)
                end_y = min(end_y, max_global)
                
                st.button(
                    str(year), 
                    key=f"inline_year_{year}",
                    on_click=update_date_range,
                    args=((start_y, end_y),)
                )

# --- HELPER: RENDER PERIOD & RESET BUTTON ---
def render_period_header(start_date, end_date, min_global, max_global, key_suffix):
    is_custom_filter = (start_date != min_global) or (end_date != max_global)
    range_str = f"{format_dutch_date(start_date)} - {format_dutch_date(end_date)}"

    if is_custom_filter:
        with st.container():
            st.markdown('<div class="filter-box-marker"></div>', unsafe_allow_html=True)
            col_txt, col_btn = st.columns([0.85, 0.15])
            with col_txt:
                st.markdown(f"**Filter actief:** {range_str} *(Niet alle data zichtbaar)*")
            with col_btn:
                st.button(
                    "Reset", 
                    key=f"reset_main_{key_suffix}",
                    on_click=reset_all_filters,
                    args=((min_global, max_global),),
                    width='stretch'
                )
    else:
        st.markdown(f"##### Volledige Periode: {range_str}")


# --- DATA LOADING & CLEANING ---
@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_pattern = os.path.join(script_dir, "**", "*.csv")
    files = glob.glob(search_pattern, recursive=True)
    
    st.session_state['debug_search_path'] = script_dir
    st.session_state['debug_files_found'] = len(files)
    
    all_data = []
    debug_log = []
    
    if not files:
        return pd.DataFrame(), [], ["Geen bestanden gevonden in huidige map (en submappen)."]

    for file in files:
        try:
            df = pd.read_csv(file, sep=None, engine='python')
            
            if df.empty or len(df.columns) < 2:
                debug_log.append(f"❌ {os.path.basename(file)}: Te weinig kolommen ({len(df.columns)}).")
                continue

            raw_month_str = df.columns[0] 
            df.rename(columns={df.columns[0]: 'DateRaw'}, inplace=True)
            
            # --- ROBUUSTE DATUM PARSING ---
            df['DateObj'] = pd.to_datetime(df['DateRaw'], format='%d-%m-%Y', errors='coerce')
            
            if df['DateObj'].isna().any():
                clean_dates = df['DateRaw'].astype(str).str.split(' GMT').str[0]
                df['DateObj'] = df['DateObj'].fillna(pd.to_datetime(clean_dates, errors='coerce'))
            
            valid_dates = df['DateObj'].notna().sum()
            if valid_dates == 0:
                first_val = df['DateRaw'].iloc[0] if not df.empty else "Leeg"
                debug_log.append(f"❌ {os.path.basename(file)}: Datums niet herkend. Eerste waarde: '{first_val}'")
                continue
                
            df = df.dropna(subset=['DateObj'])
            df['Day'] = df['DateObj'].dt.day.astype(int)
            df['Source_File_Month'] = raw_month_str
            df['Month_Start_Date'] = df['DateObj'].dt.to_period('M').dt.to_timestamp()
            
            metadata_cols = ['DateRaw', 'DateObj', 'Day', 'Source_File_Month', 'Month_Start_Date']
            ship_cols = [c for c in df.columns if c not in metadata_cols]
            
            df_melted = df.melt(
                id_vars=metadata_cols, 
                value_vars=ship_cols, 
                var_name='Ship', 
                value_name='Status'
            )
            
            all_data.append(df_melted)
            debug_log.append(f"✅ {os.path.basename(file)}: {len(df)} rijen")
            
        except Exception as e:
            debug_log.append(f"⚠️ {os.path.basename(file)}: Error ({str(e)})")
    
    if all_data:
        full_df = pd.concat(all_data, ignore_index=True)
        return full_df, files, debug_log
    else:
        return pd.DataFrame(), files, debug_log

# --- LOAD RAW DATA ---
raw_df, found_files, debug_log = load_data()
global_metrics_raw = calculate_metrics(raw_df)

# --- GLOBAL COLOR SCALES (Consistent across all pages) ---
if not raw_df.empty:
    # 1. STATUS SCALE (Voor Schip Historie) - AANGEPAST MET CONTRASTRIJKE KLEUREN
    
    # De gewenste vaste kleuren
    custom_color_map = {
        # GRIJSTINTEN
        'Werf': '#A0A6A0',          
        'Werkplaats': '#788078',    
        'Binnen': '#555955',        
        
        # GROENEN
        'Vlissingen-Breskens': '#437C3E',        
        'Kruiningen-Perkpolder': '#2A4B27',      
        'Terneuzen-Hoedekenskerke': '#88B084',   
        
        # BLAUWEN
        'Zierikzee-Katseveer': '#36648B',        
        'Kortgene-Wolphaartsdijk': '#6CA0DC',    
        'Veere-Kamperland': '#1C3549',           
        
        # Variaties
        'Ligplaats Vlissingen': '#555955', 
        'Ligplaats Perkpolder': '#555955',
        'Ligplaats Zierikzee': '#555955',
        'Ligplaats Katseveer': '#555955'
    }
    
    # Een divers palet voor alle overige statussen
    fallback_palette = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
        "#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5",
        "#c49c94", "#f7b6d2", "#c7c7c7", "#dbdb8d", "#9edae5"
    ]
    
    all_statuses_in_data = sorted([str(s) for s in raw_df['Status'].unique() if pd.notna(s)])
    
    final_domain = []
    final_range = []
    palette_index = 0
    
    for status in all_statuses_in_data:
        final_domain.append(status)
        if status in custom_color_map:
            final_range.append(custom_color_map[status])
        else:
            color = fallback_palette[palette_index % len(fallback_palette)]
            final_range.append(color)
            palette_index += 1
            
    global_status_scale = alt.Scale(domain=final_domain, range=final_range)
    
    # 2. SHIP SCALE (Voor Dienst/Lijn Zoeker)
    all_ships = sorted([str(s) for s in raw_df['Ship'].unique() if pd.notna(s)])
    global_ship_scale = alt.Scale(domain=all_ships, scheme='category20') 
else:
    global_status_scale = alt.Scale(scheme='category20')
    global_ship_scale = alt.Scale(scheme='category20')

# --- INITIALIZE PREFERENCE STATE ---
if 'pref_selected_route' not in st.session_state:
    st.session_state['pref_selected_route'] = "Vlissingen-Breskens"

if 'pref_selected_ship' not in st.session_state:
    st.session_state['pref_selected_ship'] = "Koningin Emma (1933)"

# ==========================================
# SIDEBAR OPBOUW
# ==========================================

# VERVANG STANDAARD TITEL DOOR KLIKBARE LINK NAAR ROOT (RELOAD)
st.sidebar.markdown(
    """
    <a href="." target="_self" style="text-decoration: none; color: inherit;">
        <h1 style="margin-top: 0rem; margin-bottom: 0rem; padding-bottom: 1rem;">PSDnet.nl Vaarstaten</h1>
    </a>
    """,
    unsafe_allow_html=True
)

# 1. NAVIGATIE
st.sidebar.header("Inhoud website")
view_mode = st.sidebar.radio("Kies een weergave:", ["Vaarstaten per veerboot", "Vaarstaten per veerdienst", "Maandoverzicht"])

st.sidebar.markdown("---")

# 2. FILTER LOGICA
if not raw_df.empty:
    min_global_date = raw_df['DateObj'].min().date()
    max_global_date = raw_df['DateObj'].max().date()

    if 'date_range_picker' not in st.session_state:
        st.session_state['date_range_picker'] = (min_global_date, max_global_date)

    # A. SNELKIEZER JAREN (NU ALS TEXT LINKS, MET TITEL OP APARTE REGEL)
    st.sidebar.write("**Snelkiezer Jaren:**")
    
    # Marker voor CSS styling
    st.sidebar.markdown('<div class="year-link-marker"></div>', unsafe_allow_html=True)
    
    unique_years = sorted(raw_df['DateObj'].dt.year.unique())
    
    for year in unique_years:
        start_y = datetime.date(year, 1, 1)
        end_y = datetime.date(year, 12, 31)
        start_y = max(start_y, min_global_date)
        end_y = min(end_y, max_global_date)
        
        st.sidebar.button(
            str(year), 
            key=f"btn_year_{year}",
            on_click=update_date_range,
            args=((start_y, end_y),)
        )

    # B. RESET BUTTON (NU OOK ALS TEXT LINK GESTYLED VIA CSS)
    # We zetten hem ook in een year-link-marker container voor consistente styling
    st.sidebar.markdown('<div class="year-link-marker"></div>', unsafe_allow_html=True)
    st.sidebar.button(
        "Reset datumfilter", 
        key="reset_sidebar", 
        on_click=reset_all_filters,
        args=((min_global_date, max_global_date),)
    )

    # C. DATUM SELECTIE
    st.sidebar.markdown("<br>", unsafe_allow_html=True) # Beetje ruimte
    dates = st.sidebar.date_input(
        "Selecteer datumreeks:",
        min_value=min_global_date,
        max_value=max_global_date,
        key='date_range_picker'
    )

    # Filter Logic
    if len(dates) == 2:
        start_date, end_date = dates
        mask = (raw_df['DateObj'].dt.date >= start_date) & (raw_df['DateObj'].dt.date <= end_date)
        df = raw_df.loc[mask].copy()
    else:
        if len(dates) == 1:
            start_date = dates[0]
        else:
            start_date = min_global_date
        end_date = max_global_date
        df = raw_df.copy()

    # D. FOOTER INFO
    if len(found_files) == 0:
        st.sidebar.error("Geen bestanden gevonden")

else:
    df = pd.DataFrame()
    start_date = None
    end_date = None
    st.error("⚠️ Geen data gevonden!")
    st.warning("De app heeft gezocht naar CSV-bestanden, maar kon geen geldige data vinden.")
    with st.expander("🔍 Bekijk Import Logboek (Debug)", expanded=True):
        if not found_files:
            st.write("Geen bestanden gevonden met extensie .csv.")
        else:
            for line in debug_log:
                if "❌" in line:
                    st.error(line)
                elif "⚠️" in line:
                    st.warning(line)
                else:
                    st.success(line)


# ==========================================
# MAIN CONTENT
# ==========================================

if df.empty and raw_df.empty:
    pass 
elif df.empty:
    st.warning("Geen data gevonden in deze selectie. Reset het filter.")
else:

    # --- VIEW: SCHIP HISTORIE ---
    if view_mode == "Vaarstaten per veerboot":
        st.title("Vaarstaten per veerboot")
        
        ships = sorted(raw_df['Ship'].unique())
        
        if ships:
            # Defaults logic
            current_pref_ship = st.session_state.get('pref_selected_ship', ships[0])
            if current_pref_ship not in ships:
                if "Koningin Emma (1933)" in ships:
                    current_pref_ship = "Koningin Emma (1933)"
                else:
                    current_pref_ship = ships[0]
                st.session_state['pref_selected_ship'] = current_pref_ship
            
            try:
                ship_index = ships.index(current_pref_ship)
            except ValueError:
                ship_index = 0
            
            selected_ship = st.selectbox(
                "Selecteer Schip:", 
                ships, 
                index=ship_index,
                key='widget_ship_selector',
                on_change=update_ship_pref
            )
            
            ship_data = df[df['Ship'] == selected_ship].copy().sort_values(by='DateObj')
            
            st.subheader(f"Logboek: {selected_ship}")
            render_period_header(start_date, end_date, min_global_date, max_global_date, "schip")
            
            if not ship_data.empty:
                ship_metrics = calculate_metrics(ship_data)
                
                display_coverage_metrics(ship_metrics, start_date, end_date, min_global_date, max_global_date)
                
                # --- TOEVOEGING BRONVERMELDING NA BESCHIKBARE JAREN ---
                st.caption(SOURCE_CITATION)
                
                # --- GANTT / TIMELINE CHART ---
                st.markdown("### Tijdslijn Inzet")
                
                # STAP 1: DEFINIEER DE EXCLUSION LIST
                exclude_list = ["Overbrenging", "Speciale vaart", "Gestaakt", "Gevorderd door burgemeester Zierikzee"]
                
                # STAP 2: SPLITS DATA IN 'VISIBLE' (KLEUR) EN 'HIDDEN' (GRIJS)
                mask_visible = (~ship_data['Status'].isin(exclude_list)) & (~ship_data['Status'].astype(str).str.startswith("Ligplaats"))
                df_visible = ship_data[mask_visible].copy()
                
                mask_hidden = (ship_data['Status'].isin(exclude_list)) | (ship_data['Status'].astype(str).str.startswith("Ligplaats"))
                df_hidden = ship_data[mask_hidden].copy()
                
                # STAP 3: BEREID INTERVALS VOOR
                intervals_visible = pd.DataFrame(columns=['Start', 'End', 'ShipLabel', 'Status'])
                if not df_visible.empty:
                    intervals_visible = prepare_timeline_data(df_visible, selected_ship)
                    
                intervals_hidden = pd.DataFrame(columns=['Start', 'End', 'ShipLabel', 'Status'])
                if not df_hidden.empty:
                    intervals_hidden = prepare_timeline_data(df_hidden, selected_ship)

                # STAP 4: ACHTERGROND LAAG (HATCHING VOOR MISSING DATA)
                ts_start = pd.Timestamp(start_date)
                ts_end = pd.Timestamp(end_date) + pd.Timedelta(days=1)
                
                # FIX: Explicit conversion to python datetime for domain scale
                domain_start = ts_start.to_pydatetime()
                domain_end = ts_end.to_pydatetime()
                
                bg_data = pd.DataFrame([{
                    'Start': domain_start,
                    'End': domain_end,
                    'ShipLabel': selected_ship
                }])
                
                bg_chart = alt.Chart(bg_data).mark_bar(
                    height=30
                ).encode(
                    # FIX: labelAngle=0 forces horizontal labels
                    # FIX: Explicit ':T' type definition ensures temporal scale
                    x=alt.X('Start:T', 
                        title=None, 
                        axis=alt.Axis(format='%d-%m-%Y', labelAngle=0),
                        scale=alt.Scale(domain=[domain_start, domain_end])
                    ), 
                    x2='End:T',
                    y=alt.Y('ShipLabel:N', title=None, axis=None),
                    color=alt.value("url(#diagonal-stripe)") # Layer 1: Hatching
                )
                
                # STAP 5: HIDDEN LAAG (EFFEN GRIJS VOOR EXCLUDED/LIGPLAATS)
                # FIX: donkerder grijs en ondoorzichtig gemaakt om strepen te maskeren
                hidden_chart = alt.Chart(intervals_hidden).mark_bar(height=30, opacity=1.0).encode(
                    x=alt.X('Start:T'), # Forceer :T
                    x2='End:T',
                    y=alt.Y('ShipLabel:N', title=None, axis=None),
                    color=alt.value("#999999"), # Layer 2: Dark Gray
                    tooltip=['Status:N', alt.Tooltip('Start:T', format='%d-%m-%Y'), alt.Tooltip('End:T', format='%d-%m-%Y')]
                )
                
                # STAP 6: VISIBLE LAAG (GEKLEURD)
                visible_chart = alt.Chart(intervals_visible).mark_bar(height=30).encode(
                    x=alt.X('Start:T'), # Forceer :T
                    x2='End:T',
                    y=alt.Y('ShipLabel:N', title=None, axis=None),
                    color=alt.Color(
                        'Status:N', 
                        scale=global_status_scale,
                        legend=None 
                    ),
                    tooltip=['Status:N', alt.Tooltip('Start:T', format='%d-%m-%Y'), alt.Tooltip('End:T', format='%d-%m-%Y')]
                )
                
                # COMBINEER: BG (onder) + Hidden (midden) + Visible (boven)
                final_timeline = (bg_chart + hidden_chart + visible_chart).properties(height=120)

                st.altair_chart(final_timeline, width='stretch')
                
                # --- STATS BAR CHART ---
                st.caption("**Verdeling van statussen:**")
                status_counts = ship_data['Status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                dynamic_height_ship = 80 + (len(status_counts) * 35)
                
                chart = alt.Chart(status_counts).mark_bar().encode(
                    x=alt.X('Count:Q', title='Aantal Dagen', axis=alt.Axis(tickMinStep=1, format='d')),
                    y=alt.Y('Status:N', sort='-x', title='Status', axis=alt.Axis(labelLimit=500)), 
                    color=alt.Color('Status:N', scale=global_status_scale, legend=None), 
                    tooltip=['Status:N', 'Count:Q']
                ).properties(height=dynamic_height_ship)
                
                st.altair_chart(chart, width='stretch')
                
                # --- SAMENVATTINGSTABEL ---
                # STAP 1: Maak een schone lijst van ACTIEVE dagen (Alles behalve 'Ligplaats ...')
                summary_source = ship_data.dropna(subset=['Status']).copy()
                
                # STAP 2: Tel het aantal ECHTE dagen inzet (AANGEPAST: DREMPEL 366)
                if len(summary_source) < 366:
                    # Check filter status voor titel
                    is_filtered = (start_date != min_global_date) or (end_date != max_global_date)
                    title_suffix = ""
                    if is_filtered:
                        if start_date.year == end_date.year:
                            title_suffix = f" (Filter: {start_date.year})"
                        else:
                            title_suffix = f" (Filter: {start_date.year} - {end_date.year})"
                    
                    st.markdown(f"### Samenvatting inzet: {selected_ship}{title_suffix}")
                    
                    if not summary_source.empty:
                        # Sorteer en groepeer opeenvolgende periodes
                        summary_source = summary_source.sort_values('DateObj')
                        summary_source['grp_change'] = (summary_source['Status'] != summary_source['Status'].shift()) | (summary_source['DateObj'].diff().dt.days > 1)
                        summary_source['grp_id'] = summary_source['grp_change'].cumsum()
                        
                        summary_intervals = summary_source.groupby(['grp_id', 'Status']).agg(
                            Start=('DateObj', 'min'),
                            End=('DateObj', 'max')
                        ).reset_index().sort_values('Start')
                        
                        html_rows = ""
                        for _, row in summary_intervals.iterrows():
                            start_str = format_dutch_date(row['Start'])
                            end_str = format_dutch_date(row['End'])
                            status_val = row['Status']
                            
                            if row['Start'] == row['End']:
                                date_display = start_str
                            else:
                                date_display = f"{start_str} - {end_str}"
                                
                            html_rows += f"""<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;">{status_val}</td>
<td style="padding: 8px;">{date_display}</td>
</tr>"""
                        
                        full_html = f"""<table style="width:100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.95rem;">
<thead>
<tr style="border-bottom: 2px solid #ddd; background-color: #f9f9f9;">
<th style="padding: 8px; text-align: left;">Veerdienst / Status</th>
<th style="padding: 8px; text-align: left;">Periode</th>
</tr>
</thead>
<tbody>
{html_rows}
</tbody>
</table>"""
                        st.markdown(full_html, unsafe_allow_html=True)
                    else:
                        st.info("Geen actieve inzet gevonden in deze periode.")

                st.markdown("### Ruwe data")
                st.dataframe(ship_data[['DateRaw', 'Status']], width='stretch', height=500, hide_index=True)
            else:
                st.info(f"Geen data gevonden voor **{selected_ship}** in de periode {format_dutch_date(start_date)} t/m {format_dutch_date(end_date)}.")
        else:
            st.warning("Geen schepen gevonden in de database.")

    # --- VIEW: DIENST ZOEKER ---
    elif view_mode == "Vaarstaten per veerdienst":
        st.title("Vaarstaten per veerdienst")
        
        excluded_statuses = [
            "Aan de grond", "Binnen", "Defect", "Gestaakt", 
            "Gevorderd door burgemeester Zierikzee", 
            "Ligplaats Katseveer", "Ligplaats Perkpolder", 
            "Ligplaats Vlissingen", "Ligplaats Zierikzee", 
            "Overbrenging", "Reserve Vlissingen-Breskens", 
            "Speciale vaart", "Werf", "Werkplaats"
        ]
        
        all_statuses = raw_df['Status'].unique()
        
        routes = sorted([
            str(x) for x in all_statuses 
            if pd.notna(x) 
            and str(x) not in excluded_statuses
            and not str(x).startswith("Ligplaats")
            and not str(x).startswith("Reserve")
        ])
        
        current_pref_route = st.session_state.get('pref_selected_route', routes[0] if routes else "")
        if current_pref_route not in routes:
            if "Vlissingen-Breskens" in routes:
                current_pref_route = "Vlissingen-Breskens"
            elif routes:
                current_pref_route = routes[0]
            st.session_state['pref_selected_route'] = current_pref_route
        
        if routes:
            try:
                route_index = routes.index(current_pref_route)
            except ValueError:
                route_index = 0

            selected_route = st.selectbox(
                "Selecteer Dienst/Status:", 
                routes, 
                index=route_index,
                key='widget_route_selector',
                on_change=update_route_pref
            )
            
            route_data = df[df['Status'].astype(str) == selected_route].copy()
            route_data = route_data.sort_values(by='DateObj')
            
            st.subheader(f"Welke schepen voeren op: {selected_route}?")
            render_period_header(start_date, end_date, min_global_date, max_global_date, "dienst")
            
            if not route_data.empty:
                route_metrics = calculate_metrics(route_data)
                
                total_ship_entries = len(route_data)
                unique_days_active = route_data['DateObj'].nunique()
                avg_ships = 0
                if unique_days_active > 0:
                    avg_ships = total_ship_entries / unique_days_active
                
                formatted_avg = format_ship_count(avg_ships)

                ship_counts = route_data['Ship'].value_counts().reset_index()
                ship_counts.columns = ['Ship', 'Days']
                
                # AANGEPAST: BRONVERMELDING TOEVOEGEN
                avg_text = f"Gemiddeld waren er **{formatted_avg}** schepen per dag actief *(berekend over {unique_days_active} dagen)*. {SOURCE_CITATION}"
                
                display_coverage_metrics(route_metrics, start_date, end_date, min_global_date, max_global_date, extra_text=avg_text)
                
                dynamic_height = 80 + (len(ship_counts) * 35)
                
                bar_chart = alt.Chart(ship_counts).mark_bar().encode(
                    x=alt.X('Days:Q', title='Aantal dagen ingezet', axis=alt.Axis(tickMinStep=1, format='d')),
                    y=alt.Y('Ship:N', sort='-x', title='Schip', axis=alt.Axis(labelLimit=500)), 
                    color=alt.Color('Ship:N', scale=global_ship_scale, legend=None), 
                    tooltip=['Ship:N', 'Days:Q']
                ).properties(height=dynamic_height)
                
                st.altair_chart(bar_chart, width='stretch')
                
                st.markdown("### Ruwe data")
                st.dataframe(route_data[['DateRaw', 'Source_File_Month', 'Ship']], width='stretch', height=500, hide_index=True)
            else:
                st.info(f"Geen data gevonden voor **{selected_route}** in de periode {format_dutch_date(start_date)} t/m {format_dutch_date(end_date)}.")
        else:
            st.warning("Geen diensten gevonden in de geselecteerde periode.")

    # --- VIEW: MAANDOVERZICHT ---
    elif view_mode == "Maandoverzicht":
        st.title("Maandoverzichten")
        
        month_order_df = df[['Source_File_Month', 'Month_Start_Date']].drop_duplicates()
        month_order_df = month_order_df.sort_values('Month_Start_Date')
        
        month_order_df['Year'] = month_order_df['Month_Start_Date'].dt.year
        available_years = sorted(month_order_df['Year'].unique())
        
        if available_years:
            col_sel_1, col_sel_2 = st.columns(2)
            
            with col_sel_1:
                selected_year = st.selectbox("Selecteer Jaar:", available_years)
            
            months_in_year = month_order_df[month_order_df['Year'] == selected_year]
            
            with col_sel_2:
                selected_month = st.selectbox("Selecteer Maand:", months_in_year['Source_File_Month'])
            
            subset = df[df['Source_File_Month'] == selected_month].copy()
            
            st.subheader(f"Rooster: {selected_month}")
            render_period_header(start_date, end_date, min_global_date, max_global_date, "maand")
            
            # AANGEPAST: BRONVERMELDING TOEVOEGEN
            st.caption(SOURCE_CITATION)
            
            not_sailing_list = ['binnen', 'werkplaats', 'werf']
            def assign_category(status):
                if str(status).lower() in not_sailing_list:
                    return "Aan de kant"
                else:
                    return "In de vaart"
            
            subset['Category'] = subset['Status'].apply(assign_category)
            
            pie_data = subset['Category'].value_counts().reset_index()
            pie_data.columns = ['Category', 'Count']
            pie_data['Percent'] = pie_data['Count'] / pie_data['Count'].sum()
            
            val_vaart = pie_data.loc[pie_data['Category'] == 'In de vaart', 'Percent']
            val_kant = pie_data.loc[pie_data['Category'] == 'Aan de kant', 'Percent']
            
            pct_vaart = val_vaart.iloc[0] if not val_vaart.empty else 0
            pct_kant = val_kant.iloc[0] if not val_kant.empty else 0
            
            num_unique_ships = subset['Ship'].nunique()
            
            caption_str = f"🟢 **In de vaart:** {pct_vaart:.1%} &nbsp;&nbsp; | &nbsp;&nbsp; 🔴 **Aan de kant:** {pct_kant:.1%} &nbsp;&nbsp; | &nbsp;&nbsp; 🚢 **Totaal schepen:** {num_unique_ships}"

            subset_metrics = calculate_metrics(subset)
            display_coverage_metrics(subset_metrics, start_date, end_date, min_global_date, max_global_date, show_years=False)
            
            st.markdown(caption_str)
            
            matrix_view = subset.pivot(index='Day', columns='Ship', values='Status')
            st.dataframe(matrix_view, width='stretch', height=600)
            
        else:
            st.warning("Geen maanden beschikbaar in de geselecteerde periode.")

# --- FOOTER ---
st.markdown("---")
st.markdown(f"[PSDnet.nl](https://www.psdnet.nl) Archief vaarstaten")