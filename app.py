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
            <a href="https://www.psdnet.nl" target="_blank">← Terug naar PSDnet.nl</a>
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
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    }

    /* =============================================
       3. MOBIEL SPECIFIEK (<= 768px)
       ============================================= */
    @media only screen and (max-width: 768px) {
        
        section[data-testid="stSidebar"] {
            top: 0px !important; height: 100vh !important; z-index: 1000020 !important;
        }
        
        section[data-testid="stSidebar"] > div > div:nth-child(2) {
            padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 4rem !important;
        }

        /* MENU KNOP */
        [data-testid="stSidebarCollapsedControl"] {
            display: flex !important; align-items: center !important; justify-content: center !important;
            position: fixed !important; top: 65px !important; left: 10px !important; z-index: 1000003 !important;
            background-color: #263c52 !important; border: 2px solid #e6c37d !important;
            border-radius: 5px !important; width: auto !important; height: 35px !important;
            padding: 0 10px !important; box-shadow: 2px 2px 5px rgba(0,0,0,0.3) !important;
            color: transparent !important;
        }
        [data-testid="stSidebarCollapsedControl"] svg { display: none !important; }
        [data-testid="stSidebarCollapsedControl"]::after {
            content: "MENU"; color: #fff !important; font-weight: 700; font-size: 14px; letter-spacing: 1px;
            visibility: visible !important; display: block !important;
        }

        /* SLUIT KNOP */
        section[data-testid="stSidebar"] button[kind="header"] {
            background-color: #263c52 !important; border: 1px solid #e6c37d !important;
            color: white !important; margin-right: 1rem !important;
        }
        section[data-testid="stSidebar"] button[kind="header"] svg { fill: white !important; }

        div.block-container {
            padding-top: 8rem !important; padding-left: 1rem !important; padding-right: 1rem !important;
        }
        
        /* Reset marge voor tekstlinks op mobiel */
        div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) {
            margin-left: 0px !important; margin-top: 5px !important;
        }
    }

    /* =============================================
       4. OVERIGE STYLING
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
    
    /* JAARTALLEN STYLING */
    div.year-link-marker { display: none; }
    
    /* Desktop Marge */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) {
        display: flex; flex-direction: row; flex-wrap: wrap; align-items: baseline; gap: 0.4rem;
        margin-top: -10px; margin-left: -23px; 
    }
    
    /* Sidebar Reset */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) {
        margin-left: 0px !important;
    }
    
    /* Tekst */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) div[data-testid="stMarkdownContainer"] p {
        margin-bottom: 0px !important; font-size: 0.85rem; color: rgba(49, 51, 63, 0.7); margin-right: 5px; font-weight: 600;
    }

    /* Links */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.year-link-marker) button {
        background-color: transparent !important; border: none !important; color: #003366 !important;
        text-decoration: underline; padding: 0px !important; margin: 0px !important; height: auto !important;
        min-height: 0px !important; line-height: 1.6 !important; font-size: 0.85rem !important; display: inline;
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

# --- HELPER: FORMATTING ---
def format_dutch_date(date_obj):
    if pd.isnull(date_obj): return ""
    months = {1: "januari", 2: "februari", 3: "maart", 4: "april", 5: "mei", 6: "juni", 7: "juli", 8: "augustus", 9: "september", 10: "oktober", 11: "november", 12: "december"}
    return f"{date_obj.day} {months[date_obj.month]} {date_obj.year}"

def format_ship_count(value):
    return f"{int(value)}" if value.is_integer() else f"{value:.1f}"

# ==========================================
# DEEP LINKING & STATE LOGIC
# ==========================================

VIEW_OPTIONS = ["Vaarstaten per veerboot", "Vaarstaten per veerdienst", "Maandoverzicht"]
URL_KEYS = {"veerboot": 0, "veerdienst": 1, "maand": 2}
REVERSE_KEYS = {0: "veerboot", 1: "veerdienst", 2: "maand"}

def parse_date_param(param_value, default_date):
    try:
        return datetime.datetime.strptime(param_value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return default_date

# Functie om de URL te synchroniseren met de HUIDIGE sessie staat
def sync_url():
    # 1. Huidige View ophalen
    current_view = st.session_state.get('view_mode_selector', VIEW_OPTIONS[0])
    try:
        view_idx = VIEW_OPTIONS.index(current_view)
        view_code = REVERSE_KEYS[view_idx]
    except ValueError:
        view_code = "veerboot"

    new_params = {"view": view_code}

    # 2. Datums toevoegen
    if 'date_range_picker' in st.session_state:
        rng = st.session_state['date_range_picker']
        if len(rng) > 0: new_params["start"] = rng[0].strftime("%Y-%m-%d")
        if len(rng) > 1: new_params["end"] = rng[1].strftime("%Y-%m-%d")

    # 3. Context-specifieke parameters toevoegen
    if view_code == "veerboot":
        # Gebruik de widget waarde als die bestaat, anders de preference
        val = st.session_state.get('widget_ship_selector', st.session_state.get('pref_selected_ship'))
        if val: new_params["ship"] = val
            
    elif view_code == "veerdienst":
        val = st.session_state.get('widget_route_selector', st.session_state.get('pref_selected_route'))
        if val: new_params["route"] = val

    # 4. URL Overschrijven (Oude params worden gewist)
    st.query_params.clear()
    for key, value in new_params.items():
        st.query_params[key] = value

# Initialisatie bij laden pagina (Lees URL -> Sessie)
if 'init_done' not in st.session_state:
    qp = st.query_params
    
    # Defaults instellen als URL leeg is
    if "view" not in qp:
        st.session_state['view_mode_index'] = 0
        st.session_state['pref_selected_ship'] = "Koningin Emma (1933)"
        st.query_params["view"] = "veerboot"
        st.query_params["ship"] = "Koningin Emma (1933)"
    else:
        # URL parameters overnemen
        val = qp["view"]
        if val in URL_KEYS: st.session_state['view_mode_index'] = URL_KEYS[val]
        if "ship" in qp: st.session_state['pref_selected_ship'] = qp["ship"]
        if "route" in qp: st.session_state['pref_selected_route'] = qp["route"]
        if "start" in qp: st.session_state['url_start_date'] = qp["start"]
        if "end" in qp: st.session_state['url_end_date'] = qp["end"]
            
    st.session_state['init_done'] = True

# Callbacks voor widgets (Actie -> Update URL)
def on_view_change(): sync_url()
def on_ship_change(): 
    st.session_state['pref_selected_ship'] = st.session_state['widget_ship_selector']
    sync_url()
def on_route_change(): 
    st.session_state['pref_selected_route'] = st.session_state['widget_route_selector']
    sync_url()
def on_date_change(): sync_url()
def update_date_range_button(new_range):
    st.session_state['date_range_picker'] = new_range
    sync_url()
def reset_all_filters(full_range):
    st.session_state['date_range_picker'] = full_range
    st.session_state['pref_selected_ship'] = "Koningin Emma (1933)"
    st.session_state['pref_selected_route'] = "Vlissingen-Breskens"
    sync_url()

# --- HELPER: METRICS ---
def calculate_metrics(df_subset):
    if df_subset.empty: return None
    min_date = df_subset['DateObj'].min()
    max_date = df_subset['DateObj'].max()
    return {
        'min_date': min_date, 'max_date': max_date,
        'total_days': (max_date - min_date).days + 1,
        'actual_days': df_subset['DateObj'].nunique(),
        'years': sorted(df_subset['DateObj'].dt.year.unique())
    }

# --- HELPER: TIMELINE DATA ---
def prepare_timeline_data(ship_df, ship_name):
    df = ship_df.copy().sort_values('DateObj')
    df['Status'] = df['Status'].fillna('Onbekend')
    df['grp_change'] = (df['Status'] != df['Status'].shift()) | (df['DateObj'].diff().dt.days > 1)
    df['grp_id'] = df['grp_change'].cumsum()
    intervals = df.groupby(['grp_id', 'Status']).agg(Start=('DateObj', 'min'), End=('DateObj', 'max')).reset_index()
    intervals['End'] = intervals['End'] + pd.Timedelta(days=1)
    intervals['ShipLabel'] = ship_name
    return intervals

# --- HELPER: DISPLAY ---
def display_coverage_metrics(metrics, current_start, current_end, min_global, max_global, show_years=True, extra_text=None):
    if not metrics: return
    if extra_text: st.caption(extra_text)
    is_filtered = (current_start != min_global) or (current_end != max_global)
    if not is_filtered and show_years and metrics['years']:
        with st.container():
            st.markdown('<div class="year-link-marker"></div>', unsafe_allow_html=True)
            st.markdown("**Beschikbare jaren:**")
            for year in metrics['years']:
                start_y = datetime.date(year, 1, 1)
                end_y = datetime.date(year, 12, 31)
                start_y = max(start_y, min_global)
                end_y = min(end_y, max_global)
                st.button(str(year), key=f"inline_year_{year}", on_click=update_date_range_button, args=((start_y, end_y),))

def render_period_header(start_date, end_date, min_global, max_global, key_suffix):
    is_custom = (start_date != min_global) or (end_date != max_global)
    range_str = f"{format_dutch_date(start_date)} - {format_dutch_date(end_date)}"
    if is_custom:
        with st.container():
            st.markdown('<div class="filter-box-marker"></div>', unsafe_allow_html=True)
            col_txt, col_btn = st.columns([0.85, 0.15])
            with col_txt: st.markdown(f"**Filter actief:** {range_str} *(Niet alle data zichtbaar)*")
            with col_btn: st.button("Reset", key=f"reset_main_{key_suffix}", on_click=reset_all_filters, args=((min_global, max_global),), width='stretch')
    else:
        st.markdown(f"##### Volledige Periode: {range_str}")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    files = glob.glob(os.path.join(script_dir, "**", "*.csv"), recursive=True)
    all_data = []
    debug_log = []
    if not files: return pd.DataFrame(), [], ["Geen bestanden gevonden."]
    for file in files:
        try:
            df = pd.read_csv(file, sep=None, engine='python')
            if df.empty or len(df.columns) < 2: 
                debug_log.append(f"❌ {os.path.basename(file)}: Te weinig kolommen.")
                continue
            raw_month_str = df.columns[0]
            df.rename(columns={df.columns[0]: 'DateRaw'}, inplace=True)
            df['DateObj'] = pd.to_datetime(df['DateRaw'], format='%d-%m-%Y', errors='coerce')
            if df['DateObj'].isna().any():
                clean = df['DateRaw'].astype(str).str.split(' GMT').str[0]
                df['DateObj'] = df['DateObj'].fillna(pd.to_datetime(clean, errors='coerce'))
            df = df.dropna(subset=['DateObj'])
            if df.empty: continue
            df['Day'] = df['DateObj'].dt.day.astype(int)
            df['Source_File_Month'] = raw_month_str
            df['Month_Start_Date'] = df['DateObj'].dt.to_period('M').dt.to_timestamp()
            meta = ['DateRaw', 'DateObj', 'Day', 'Source_File_Month', 'Month_Start_Date']
            ship_cols = [c for c in df.columns if c not in meta]
            all_data.append(df.melt(id_vars=meta, value_vars=ship_cols, var_name='Ship', value_name='Status'))
            debug_log.append(f"✅ {os.path.basename(file)}")
        except Exception as e:
            debug_log.append(f"⚠️ {os.path.basename(file)}: {e}")
    if all_data: return pd.concat(all_data, ignore_index=True), files, debug_log
    return pd.DataFrame(), files, debug_log

raw_df, found_files, debug_log = load_data()

# --- COLORS ---
if not raw_df.empty:
    custom_color_map = {
        'Werf': '#A0A6A0', 'Werkplaats': '#788078', 'Binnen': '#555955',        
        'Vlissingen-Breskens': '#437C3E', 'Kruiningen-Perkpolder': '#2A4B27', 'Terneuzen-Hoedekenskerke': '#88B084',   
        'Zierikzee-Katseveer': '#36648B', 'Kortgene-Wolphaartsdijk': '#6CA0DC', 'Veere-Kamperland': '#1C3549',           
        'Ligplaats Vlissingen': '#555955', 'Ligplaats Perkpolder': '#555955',
        'Ligplaats Zierikzee': '#555955', 'Ligplaats Katseveer': '#555955'
    }
    fallback_palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5", "#c49c94", "#f7b6d2", "#c7c7c7", "#dbdb8d", "#9edae5"]
    all_stats = sorted([str(s) for s in raw_df['Status'].unique() if pd.notna(s)])
    final_range = [custom_color_map.get(s, fallback_palette[i % len(fallback_palette)]) for i, s in enumerate(all_stats)]
    global_status_scale = alt.Scale(domain=all_stats, range=final_range)
    global_ship_scale = alt.Scale(domain=sorted([str(s) for s in raw_df['Ship'].unique() if pd.notna(s)]), scheme='category20')
else:
    global_status_scale = alt.Scale(scheme='category20')
    global_ship_scale = alt.Scale(scheme='category20')

# --- APPLY URL DATES ---
if not raw_df.empty:
    min_glob = raw_df['DateObj'].min().date()
    max_glob = raw_df['DateObj'].max().date()
    cur_start = parse_date_param(st.session_state.get('url_start_date', ''), min_glob)
    cur_end = parse_date_param(st.session_state.get('url_end_date', ''), max_glob)
    # Clamp
    cur_start = max(min_glob, cur_start)
    cur_end = min(max_glob, cur_end)
    if 'date_range_picker' not in st.session_state:
        st.session_state['date_range_picker'] = (cur_start, cur_end)

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.markdown("""<a href="." target="_self" style="text-decoration: none; color: inherit;"><h1 style="margin-top: 0rem; margin-bottom: 0rem; padding-bottom: 1rem;">PSDnet.nl Vaarstaten</h1></a>""", unsafe_allow_html=True)
st.sidebar.header("Inhoud website")

idx = st.session_state.get('view_mode_index', 0)
view_mode = st.sidebar.radio("Kies een weergave:", VIEW_OPTIONS, index=idx, key='view_mode_selector', on_change=on_view_change)
st.sidebar.markdown("---")

if not raw_df.empty:
    st.sidebar.write("**Snelkiezer Jaren:**")
    st.sidebar.markdown('<div class="year-link-marker"></div>', unsafe_allow_html=True)
    years = sorted(raw_df['DateObj'].dt.year.unique())
    for y in years:
        sy = max(datetime.date(y, 1, 1), min_glob)
        ey = min(datetime.date(y, 12, 31), max_glob)
        st.sidebar.button(str(y), key=f"btn_year_{y}", on_click=update_date_range_button, args=((sy, ey),))
    
    st.sidebar.markdown('<div class="year-link-marker"></div>', unsafe_allow_html=True)
    st.sidebar.button("Reset datumfilter", key="reset_sidebar", on_click=reset_all_filters, args=((min_glob, max_glob),))
    st.sidebar.markdown("<br>", unsafe_allow_html=True) 
    
    dates = st.sidebar.date_input("Selecteer datumreeks:", min_value=min_glob, max_value=max_glob, key='date_range_picker', on_change=on_date_change)
    
    if len(dates) == 2:
        start_date, end_date = dates
        mask = (raw_df['DateObj'].dt.date >= start_date) & (raw_df['DateObj'].dt.date <= end_date)
        df = raw_df.loc[mask].copy()
    else:
        start_date, end_date = (dates[0], min_glob) if len(dates) == 1 else (min_glob, max_glob)
        df = raw_df.copy()

    if not found_files: st.sidebar.error("Geen bestanden gevonden")
else:
    df = pd.DataFrame()
    start_date, end_date = None, None
    st.error("⚠️ Geen data gevonden!")

# ==========================================
# MAIN CONTENT
# ==========================================
if not df.empty:
    if view_mode == "Vaarstaten per veerboot":
        st.title("Vaarstaten per veerboot")
        ships = sorted(raw_df['Ship'].unique())
        if ships:
            # Pre-select based on session state preference or url
            pref = st.session_state.get('pref_selected_ship', "Koningin Emma (1933)")
            if pref not in ships: pref = ships[0]
            try: s_idx = ships.index(pref)
            except: s_idx = 0
            
            sel_ship = st.selectbox("Selecteer Schip:", ships, index=s_idx, key='widget_ship_selector', on_change=on_ship_change)
            ship_data = df[df['Ship'] == sel_ship].sort_values('DateObj')
            
            st.subheader(f"Logboek: {sel_ship}")
            render_period_header(start_date, end_date, min_glob, max_glob, "schip")
            
            if not ship_data.empty:
                metrics = calculate_metrics(ship_data)
                display_coverage_metrics(metrics, start_date, end_date, min_glob, max_glob)
                st.caption(SOURCE_CITATION)
                
                st.markdown("### Tijdslijn Inzet")
                excl = ["Overbrenging", "Speciale vaart", "Gestaakt", "Gevorderd door burgemeester Zierikzee"]
                # Visible: Not in exclude AND NOT starting with Ligplaats
                vis = ship_data[(~ship_data['Status'].isin(excl)) & (~ship_data['Status'].astype(str).str.startswith("Ligplaats"))].copy()
                # Hidden: In exclude OR starting with Ligplaats
                hid = ship_data[(ship_data['Status'].isin(excl)) | (ship_data['Status'].astype(str).str.startswith("Ligplaats"))].copy()
                
                int_v = prepare_timeline_data(vis, sel_ship) if not vis.empty else pd.DataFrame(columns=['Start', 'End', 'ShipLabel', 'Status'])
                int_h = prepare_timeline_data(hid, sel_ship) if not hid.empty else pd.DataFrame(columns=['Start', 'End', 'ShipLabel', 'Status'])
                
                # Chart
                dom_s = pd.Timestamp(start_date).to_pydatetime()
                dom_e = (pd.Timestamp(end_date) + pd.Timedelta(days=1)).to_pydatetime()
                
                base = alt.Chart(pd.DataFrame([{'Start': dom_s, 'End': dom_e, 'ShipLabel': sel_ship}])).mark_bar(height=30).encode(
                    x=alt.X('Start:T', title=None, axis=alt.Axis(format='%d-%m-%Y', labelAngle=0), scale=alt.Scale(domain=[dom_s, dom_e])),
                    x2='End:T', y=alt.Y('ShipLabel:N', title=None, axis=None), color=alt.value("url(#diagonal-stripe)")
                )
                
                c_hid = alt.Chart(int_h).mark_bar(height=30, opacity=1).encode(
                    x='Start:T', x2='End:T', y=alt.Y('ShipLabel:N', title=None, axis=None), 
                    color=alt.value("#999999"), tooltip=['Status:N', alt.Tooltip('Start:T', format='%d-%m-%Y'), alt.Tooltip('End:T', format='%d-%m-%Y')]
                )
                c_vis = alt.Chart(int_v).mark_bar(height=30).encode(
                    x='Start:T', x2='End:T', y=alt.Y('ShipLabel:N', title=None, axis=None),
                    color=alt.Color('Status:N', scale=global_status_scale, legend=None),
                    tooltip=['Status:N', alt.Tooltip('Start:T', format='%d-%m-%Y'), alt.Tooltip('End:T', format='%d-%m-%Y')]
                )
                st.altair_chart((base + c_hid + c_vis).properties(height=120), width='stretch')
                
                # Stats
                st.caption("**Verdeling van statussen:**")
                cts = ship_data['Status'].value_counts().reset_index()
                cts.columns = ['Status', 'Count']
                st.altair_chart(alt.Chart(cts).mark_bar().encode(
                    x=alt.X('Count:Q', title='Aantal Dagen', axis=alt.Axis(tickMinStep=1, format='d')),
                    y=alt.Y('Status:N', sort='-x', title='Status', axis=alt.Axis(labelLimit=500)),
                    color=alt.Color('Status:N', scale=global_status_scale, legend=None), tooltip=['Status:N', 'Count:Q']
                ).properties(height=80 + len(cts)*35), width='stretch')
                
                # Table (ALL statuses, even Ligplaats)
                sum_src = ship_data.dropna(subset=['Status']).copy()
                if len(sum_src) < 366:
                    filt_txt = ""
                    if (start_date != min_glob) or (end_date != max_glob):
                        filt_txt = f" (Filter: {start_date.year})" if start_date.year == end_date.year else f" (Filter: {start_date.year} - {end_date.year})"
                    st.markdown(f"### Samenvatting inzet: {sel_ship}{filt_txt}")
                    if not sum_src.empty:
                        sum_src = sum_src.sort_values('DateObj')
                        sum_src['grp'] = (sum_src['Status'] != sum_src['Status'].shift()) | (sum_src['DateObj'].diff().dt.days > 1)
                        grps = sum_src.groupby([sum_src['grp'].cumsum(), 'Status']).agg(S=('DateObj', 'min'), E=('DateObj', 'max')).reset_index().sort_values('S')
                        rows = ""
                        for _, r in grps.iterrows():
                            d_str = format_dutch_date(r['S'])
                            if r['S'] != r['E']: d_str += f" - {format_dutch_date(r['E'])}"
                            rows += f"<tr style='border-bottom:1px solid #eee'><td style='padding:8px'>{r['Status']}</td><td style='padding:8px'>{d_str}</td></tr>"
                        st.markdown(f"<table style='width:100%; border-collapse:collapse'><thead><tr style='border-bottom:2px solid #ddd; background:#f9f9f9'><th style='padding:8px; text-align:left'>Veerdienst / Status</th><th style='padding:8px; text-align:left'>Periode</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
                
                st.markdown("### Ruwe data")
                st.dataframe(ship_data[['DateRaw', 'Status']], width='stretch', height=500, hide_index=True)
            else:
                st.info(f"Geen data gevonden voor {sel_ship} in deze periode.")

    elif view_mode == "Vaarstaten per veerdienst":
        st.title("Vaarstaten per veerdienst")
        excl = ["Aan de grond", "Binnen", "Defect", "Gestaakt", "Gevorderd door burgemeester Zierikzee", "Ligplaats Katseveer", "Ligplaats Perkpolder", "Ligplaats Vlissingen", "Ligplaats Zierikzee", "Overbrenging", "Reserve Vlissingen-Breskens", "Speciale vaart", "Werf", "Werkplaats"]
        routes = sorted([str(x) for x in raw_df['Status'].unique() if pd.notna(x) and str(x) not in excl and not str(x).startswith("Ligplaats") and not str(x).startswith("Reserve")])
        
        pref = st.session_state.get('pref_selected_route', routes[0] if routes else "")
        if pref not in routes and routes: pref = routes[0]
        try: r_idx = routes.index(pref)
        except: r_idx = 0
        
        sel_route = st.selectbox("Selecteer Dienst/Status:", routes, index=r_idx, key='widget_route_selector', on_change=on_route_change)
        route_data = df[df['Status'].astype(str) == sel_route].sort_values('DateObj')
        
        st.subheader(f"Welke schepen voeren op: {sel_route}?")
        render_period_header(start_date, end_date, min_glob, max_glob, "dienst")
        
        if not route_data.empty:
            met = calculate_metrics(route_data)
            days = route_data['DateObj'].nunique()
            avg = len(route_data)/days if days > 0 else 0
            display_coverage_metrics(met, start_date, end_date, min_glob, max_glob, extra_text=f"Gemiddeld waren er **{format_ship_count(avg)}** schepen per dag actief *(berekend over {days} dagen)*. {SOURCE_CITATION}")
            
            sc = route_data['Ship'].value_counts().reset_index()
            sc.columns = ['Ship', 'Days']
            st.altair_chart(alt.Chart(sc).mark_bar().encode(
                x=alt.X('Days:Q', title='Aantal dagen ingezet', axis=alt.Axis(tickMinStep=1, format='d')),
                y=alt.Y('Ship:N', sort='-x', title='Schip', axis=alt.Axis(labelLimit=500)),
                color=alt.Color('Ship:N', scale=global_ship_scale, legend=None), tooltip=['Ship:N', 'Days:Q']
            ).properties(height=80 + len(sc)*35), width='stretch')
            
            st.markdown("### Ruwe data")
            st.dataframe(route_data[['DateRaw', 'Source_File_Month', 'Ship']], width='stretch', height=500, hide_index=True)
        else:
            st.info(f"Geen data voor {sel_route} in deze periode.")

    elif view_mode == "Maandoverzicht":
        st.title("Maandoverzichten")
        # Simpele implementatie maandoverzicht (geen deep linking op maand/jaar niveau gevraagd, wel view)
        mo = df[['Source_File_Month', 'Month_Start_Date']].drop_duplicates().sort_values('Month_Start_Date')
        mo['Year'] = mo['Month_Start_Date'].dt.year
        avail_years = sorted(mo['Year'].unique())
        
        if avail_years:
            c1, c2 = st.columns(2)
            with c1: sy = st.selectbox("Selecteer Jaar:", avail_years)
            with c2: sm = st.selectbox("Selecteer Maand:", mo[mo['Year'] == sy]['Source_File_Month'])
            
            subset = df[df['Source_File_Month'] == sm].copy()
            st.subheader(f"Rooster: {sm}")
            render_period_header(start_date, end_date, min_glob, max_glob, "maand")
            st.caption(SOURCE_CITATION)
            
            # Pie logic
            not_sailing = ['binnen', 'werkplaats', 'werf']
            subset['Category'] = subset['Status'].apply(lambda x: "Aan de kant" if str(x).lower() in not_sailing else "In de vaart")
            pie = subset['Category'].value_counts(normalize=True)
            p_vaart = pie.get("In de vaart", 0)
            p_kant = pie.get("Aan de kant", 0)
            
            display_coverage_metrics(calculate_metrics(subset), start_date, end_date, min_glob, max_glob, show_years=False)
            st.markdown(f"🟢 **In de vaart:** {p_vaart:.1%} &nbsp;&nbsp; | &nbsp;&nbsp; 🔴 **Aan de kant:** {p_kant:.1%} &nbsp;&nbsp; | &nbsp;&nbsp; 🚢 **Totaal schepen:** {subset['Ship'].nunique()}")
            
            st.dataframe(subset.pivot(index='Day', columns='Ship', values='Status'), width='stretch', height=600)
        else:
            st.warning("Geen maanden beschikbaar.")

st.markdown("---")
st.markdown(f'<a href="https://www.psdnet.nl" target="_blank">PSDnet.nl</a> Archief vaarstaten', unsafe_allow_html=True)
