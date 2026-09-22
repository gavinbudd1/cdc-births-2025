"""
app.py
======
Main Streamlit Application for the CDC 2025 Provisional Natality Dashboard.

Designed for undergraduate business analytics students to explore:
- Geographic variations
- Seasonal patterns
- Infant-sex differences in provisional live birth counts
"""

from pathlib import Path
import streamlit as st
import pandas as pd

from src.data_loader import (
    load_natality_data,
    validate_dataset,
    MONTH_ORDER,
)
from src.kpis import compute_kpis
from src.visualizations import (
    plot_monthly_trend,
    plot_sex_comparison,
    plot_state_ranking,
    plot_choropleth_map,
    plot_state_month_heatmap,
    plot_top_bottom_comparison,
)
from src.ui_components import (
    render_header,
    render_filter_summary,
    render_kpi_cards,
    render_data_table_and_download,
    render_about_section,
)

# Page configuration
st.set_page_config(
    page_title="U.S. CDC Provisional Natality 2025",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ingest and validate data
try:
    df_raw = load_natality_data()
    audit_results = validate_dataset(df_raw)
except Exception as e:
    st.error(f"Error loading or validating dataset: {e}")
    st.stop()

# Master filter lists
all_states = sorted(list(df_raw["State of Residence"].unique()))
all_months = [m for m in MONTH_ORDER if m in df_raw["Month"].unique()]
all_sexes = ["All", "Female", "Male"]

# Initialize session state for filter controls
if "filter_states" not in st.session_state:
    st.session_state.filter_states = all_states
if "filter_months" not in st.session_state:
    st.session_state.filter_months = all_months
if "filter_sex" not in st.session_state:
    st.session_state.filter_sex = "All"


# Callbacks for reset and select all buttons
def reset_filters():
    st.session_state.filter_states = all_states
    st.session_state.filter_months = all_months
    st.session_state.filter_sex = "All"


def select_all_states():
    st.session_state.filter_states = all_states


def select_all_months():
    st.session_state.filter_months = all_months


# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Dashboard Filters")
st.sidebar.markdown(
    "<small style='color: #64748B;'>Select dimensions to update all KPIs and visualizations dynamically.</small>",
    unsafe_allow_html=True,
)

# Reset Button
st.sidebar.button(
    "🔄 Reset All Filters",
    on_click=reset_filters,
    use_container_width=True,
    help="Reset all filters back to the full 2025 national dataset.",
)

st.sidebar.divider()

# Geography Filter
st.sidebar.subheader("1. Geography")
c_geo1, c_geo2 = st.sidebar.columns([1, 1])
with c_geo1:
    st.button("Select All", key="btn_all_geo", on_click=select_all_states, use_container_width=True)
with c_geo2:
    if st.button("Clear", key="btn_clr_geo", use_container_width=True):
        st.session_state.filter_states = []

selected_states = st.sidebar.multiselect(
    "States & DC:",
    options=all_states,
    key="filter_states",
    help="Select one or more states or District of Columbia.",
)

# Month Filter
st.sidebar.subheader("2. Calendar Month")
c_mo1, c_mo2 = st.sidebar.columns([1, 1])
with c_mo1:
    st.button("Select All", key="btn_all_mo", on_click=select_all_months, use_container_width=True)
with c_mo2:
    if st.button("Clear", key="btn_clr_mo", use_container_width=True):
        st.session_state.filter_months = []

selected_months = st.sidebar.multiselect(
    "Months (2025):",
    options=all_months,
    key="filter_months",
    help="Select one or more calendar months.",
)

# Infant Sex Filter
st.sidebar.subheader("3. Infant Sex")
selected_sex = st.sidebar.radio(
    "Select Demographic Slice:",
    options=all_sexes,
    key="filter_sex",
    horizontal=True,
    help="Filter by infant sex category or view combined totals.",
)

st.sidebar.divider()
st.sidebar.info(
    "💡 **Analytics Tip**: When comparing state totals, remember larger states naturally record more births. This reflects population volume, not higher birth rates."
)

# ---------------- DATA FILTERING ----------------
df_filtered = df_raw.copy()

if selected_states:
    df_filtered = df_filtered[df_filtered["State of Residence"].isin(selected_states)]
else:
    df_filtered = df_filtered.iloc[0:0]

if selected_months:
    df_filtered = df_filtered[df_filtered["Month"].isin(selected_months)]
else:
    df_filtered = df_filtered.iloc[0:0]

if selected_sex != "All":
    df_filtered = df_filtered[df_filtered["Sex of Infant"] == selected_sex]

# Compute dynamic KPIs
kpi_data = compute_kpis(df_filtered)

# ---------------- MAIN PAGE DISPLAY ----------------
render_header()

# Active Filter Badge
render_filter_summary(
    selected_states=selected_states,
    all_states=all_states,
    selected_months=selected_months,
    all_months=all_months,
    selected_sex=selected_sex,
)

# Top KPI row
render_kpi_cards(kpi_data)

st.markdown("<br>", unsafe_allow_html=True)

# Empty filter state guardrail
if df_filtered.empty:
    st.error(
        "⚠️ **No observations match your current filter settings.** Please select at least one geography and one month in the sidebar, or click **Reset All Filters**."
    )
    st.stop()

# ---------------- DASHBOARD TABS ----------------
tab_overview, tab_geo, tab_monthly_sex, tab_table, tab_about = st.tabs([
    "📊 Overview",
    "🗺️ Geographic Analysis",
    "📈 Monthly & Sex Analysis",
    "📋 Data Table & Download",
    "📚 About the Data",
])

# ----- TAB 1: OVERVIEW -----
with tab_overview:
    st.markdown("### 🎯 Executive Summary & Key Highlights")
    st.markdown(
        f"""
        During the selected period, **{kpi_data['total_births_str']}** live births were recorded across 
        **{kpi_data['selected_geos_count_str']}** geographies. The peak monthly volume occurred in 
        **{kpi_data['highest_month_name']}**, and the geography recording the highest birth volume was 
        **{kpi_data['highest_geo_name']}**.
        """
    )

    col_ov1, col_ov2 = st.columns([3, 2])
    with col_ov1:
        st.plotly_chart(
            plot_monthly_trend(df_filtered, breakdown_by_sex=False),
            use_container_width=True,
        )
    with col_ov2:
        st.plotly_chart(
            plot_sex_comparison(df_filtered),
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("#### ⚖️ Scale Disparity: Populous vs. Less Populous Geographies")
    st.plotly_chart(
        plot_top_bottom_comparison(df_filtered, n=5),
        use_container_width=True,
    )
    st.caption(
        "Note the massive volume difference between the largest states and smaller states. "
        "This demonstrates why business analysts must never compare raw counts as indicators of demographic fertility."
    )

# ----- TAB 2: GEOGRAPHIC ANALYSIS -----
with tab_geo:
    st.markdown("### 🗺️ Geographic Distribution & State Rankings")
    
    st.plotly_chart(
        plot_choropleth_map(df_filtered),
        use_container_width=True,
    )

    st.markdown("---")
    c_rank_ctrl, _ = st.columns([1, 2])
    with c_rank_ctrl:
        rank_view = st.selectbox(
            "Ranking Display Option:",
            options=["All Selected Geographies", "Top 10 Geographies", "Top 20 Geographies"],
            index=0,
        )
    
    top_n_val = None
    if rank_view == "Top 10 Geographies":
        top_n_val = 10
    elif rank_view == "Top 20 Geographies":
        top_n_val = 20

    st.plotly_chart(
        plot_state_ranking(df_filtered, top_n=top_n_val),
        use_container_width=True,
    )

# ----- TAB 3: MONTHLY & SEX ANALYSIS -----
with tab_monthly_sex:
    st.markdown("### 📈 Seasonal Trends and Infant-Sex Dynamics")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.plotly_chart(
            plot_monthly_trend(df_filtered, breakdown_by_sex=True),
            use_container_width=True,
        )
    with col_m2:
        st.plotly_chart(
            plot_sex_comparison(df_filtered),
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("#### 🌡️ Geographic-Seasonal Heatmap (State vs. Month)")
    st.markdown(
        "This matrix displays birth volume across each geography and month, highlighting seasonal variations."
    )
    st.plotly_chart(
        plot_state_month_heatmap(df_filtered),
        use_container_width=True,
    )

# ----- TAB 4: DATA TABLE & DOWNLOAD -----
with tab_table:
    render_data_table_and_download(df_filtered)

# ----- TAB 5: ABOUT THE DATA -----
with tab_about:
    render_about_section(audit_results)
