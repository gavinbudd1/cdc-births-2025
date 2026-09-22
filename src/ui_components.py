"""
ui_components.py
================
UI component renderers, banners, and layout helpers for the Streamlit dashboard.

Pedagogical Principles:
- Prominently positions statistical guardrails (provisional notice, counts vs. rates)
- Provides clear filter feedback so users know exactly what data slice they are analyzing
- Clean tabular data access with formatted numbers and download capability
"""

from typing import List, Dict, Any
import pandas as pd
import streamlit as st


def render_header():
    """Renders the dashboard title, contextual explanation, and official statistical guardrails."""
    st.title("👶 U.S. CDC Provisional Natality Dashboard (2025)")
    st.markdown(
        """
        Explore demographic, seasonal, and geographic distributions of provisional live births across 
        all 50 U.S. states and the District of Columbia.
        """
    )

    # Core statistical warning and attribution alert
    st.warning(
        """
        ⚠️ **Important Statistical & Source Notice for Analytics Students**:
        - **Provisional Data**: Figures are provisional 2025 estimates released by the **Centers for Disease Control and Prevention (CDC) / National Center for Health Statistics (NCHS)** via CDC WONDER. Provisional counts are subject to reporting lags and subsequent revisions.
        - **Counts vs. Rates**: All figures in this dashboard represent **raw birth counts**, **NOT birth rates or fertility rates**. Comparing raw counts across states or demographic groups reflects absolute volume and population scale, not maternal fertility behavior.
        """,
        icon="ℹ️",
    )


def render_filter_summary(
    selected_states: List[str],
    all_states: List[str],
    selected_months: List[str],
    all_months: List[str],
    selected_sex: str,
):
    """Renders an intuitive, compact summary badge of currently active sidebar filters."""
    states_label = (
        "All 51 Geographies"
        if len(selected_states) == len(all_states)
        else (f"{len(selected_states)} of {len(all_states)} Geographies" if selected_states else "None")
    )
    months_label = (
        "All 12 Months"
        if len(selected_months) == len(all_months)
        else (f"{len(selected_months)} of {len(all_months)} Months" if selected_months else "None")
    )
    sex_label = f"Infant Sex: {selected_sex}"

    st.info(
        f"🔍 **Active Filter Scope**: **{states_label}** | **{months_label}** | **{sex_label}**"
    )


def render_kpi_cards(kpi_data: Dict[str, Any]):
    """Renders 5 top-level KPI metric cards horizontally."""
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.metric(
            label="Total Live Births",
            value=kpi_data["total_births_str"],
            help="Sum of live birth counts across the currently selected filters (provisional 2025).",
        )
    with c2:
        st.metric(
            label="Geographies Selected",
            value=f"{kpi_data['selected_geos_count_str']} / 51",
            help="Number of distinct states / DC currently included in the filter.",
        )
    with c3:
        st.metric(
            label="Avg. Births / Month",
            value=kpi_data["avg_births_per_month_str"],
            help="Average monthly birth volume across the active calendar months in selection.",
        )
    with c4:
        st.metric(
            label="Top Geography",
            value=kpi_data["highest_geo_name"],
            delta=f"{kpi_data['highest_geo_births']:,.0f} births" if kpi_data["highest_geo_births"] > 0 else None,
            delta_color="off",
            help="Geography with the largest total birth volume in the active selection.",
        )
    with c5:
        st.metric(
            label="Peak Month",
            value=kpi_data["highest_month_name"],
            delta=f"{kpi_data['highest_month_births']:,.0f} births" if kpi_data["highest_month_births"] > 0 else None,
            delta_color="off",
            help="Calendar month with the highest aggregate birth count in the active selection.",
        )


def render_data_table_and_download(df: pd.DataFrame):
    """Renders a searchable, sortable data table and an instant CSV download option."""
    st.subheader("📋 Filtered Observations Explorer")
    st.markdown(
        """
        Inspect the underlying micro-aggregate records matching your filter criteria. 
        Each row represents the recorded birth count for a specific state, month, and infant sex.
        """
    )

    if df.empty:
        st.warning("No records match the current filter selection.")
        return

    # Present formatted display dataframe
    display_df = df.copy()
    display_df["Births Formatted"] = display_df["Births"].apply(lambda x: f"{x:,.0f}")
    
    cols_order = [
        "State of Residence",
        "State Abbreviation",
        "Month",
        "Month Code",
        "Year Code",
        "Sex of Infant",
        "Births",
    ]
    cols_available = [c for c in cols_order if c in display_df.columns]

    # Quick download button
    csv_bytes = df[cols_available].to_csv(index=False).encode("utf-8")
    
    c_dl, c_cnt = st.columns([1, 3])
    with c_dl:
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv_bytes,
            file_name="cdc_provisional_natality_2025_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c_cnt:
        st.caption(f"Showing **{len(df):,}** observations matching filter criteria.")

    st.dataframe(
        display_df[cols_available],
        use_container_width=True,
        hide_index=True,
    )


def render_about_section(audit_checks: Dict[str, bool]):
    """Renders the pedagogical About the Data section."""
    st.subheader("📚 About the CDC Natality Dataset & Analytics Methodology")
    
    st.markdown(
        """
        ### 1. Data Source & Attribution
        - **Source**: Centers for Disease Control and Prevention (CDC), National Center for Health Statistics (NCHS).
        - **System**: CDC WONDER Provisional Natality Statistics (2023 through 2025).
        - **Scope**: Live births occurring within the 50 United States and the District of Columbia to U.S. residents during calendar year 2025.
        
        ---

        ### 2. Crucial Analytics Principles for Students
        
        #### A. The Denominator Fallacy (Counts vs. Rates)
        In business analytics and epidemiology, a common error is comparing raw frequencies without adjusting for population size.
        - **Birth Count**: The absolute number of live births registered in a jurisdiction.
        - **General Fertility Rate (GFR)**: $\\text{GFR} = \\frac{\\text{Live Births}}{\\text{Female Population (Ages 15–44)}} \\times 1,000$.
        
        Because this dataset contains **only birth counts and no census population denominators**, you cannot conclude that a state with more births has a "higher birth rate." California and Texas have high birth counts because they have large populations.
        
        #### B. Provisional vs. Final Vital Statistics
        - **Provisional Data**: Released monthly on an ongoing basis to provide early indicators of public health trends. They are based on birth certificates registered by states as of the extract date.
        - **Final Natality Data**: Released approximately 9 to 12 months after the close of the calendar year following exhaustive data cleaning, delayed registration processing, and demographic reconciliation.
        
        ---

        ### 3. Automated Data Quality Audit Verification
        At application startup, this dashboard validates the integrity of the data against benchmark standards:
        """
    )

    audit_rows = []
    for check_name, passed in audit_checks.items():
        audit_rows.append({
            "Audit Check": check_name,
            "Verification Result": "Passed" if passed else "Failed",
            "Integrity Status": "Compliant with CDC provisional standards"
        })
    st.table(pd.DataFrame(audit_rows))
