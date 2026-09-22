"""
kpis.py
=======
Calculates key performance indicators (KPIs) for the CDC 2025 Provisional Natality Dashboard.

Analytics principles for students:
- All KPIs are derived dynamically from the active user filter selection.
- Handled gracefully when selections are empty.
- Strict distinction between birth counts and birth rates:
  * "Total Births" is a raw volume measure.
  * "Average Births per Selected Month" is a temporal aggregation of counts, NOT a rate per capita.
"""

from typing import Dict, Any
import pandas as pd


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes all 5 required dashboard KPIs for the filtered DataFrame.

    Returns a dictionary with raw values and pre-formatted display strings.
    """
    if df.empty or len(df) == 0:
        return {
            "total_births": 0,
            "total_births_str": "0",
            "selected_geos_count": 0,
            "selected_geos_count_str": "0",
            "avg_births_per_month": 0,
            "avg_births_per_month_str": "0",
            "highest_geo_name": "None",
            "highest_geo_births": 0,
            "highest_geo_str": "N/A",
            "highest_month_name": "None",
            "highest_month_births": 0,
            "highest_month_str": "N/A",
        }

    # 1. Total births in the current selection
    total_births = int(df["Births"].sum())

    # 2. Number of selected geographies
    selected_geos = int(df["State of Residence"].nunique())

    # 3. Average births per selected month
    num_months = int(df["Month"].nunique())
    avg_per_month = total_births / num_months if num_months > 0 else 0

    # 4. Geography with the highest selected birth count
    geo_totals = df.groupby("State of Residence", as_index=False)["Births"].sum()
    if not geo_totals.empty:
        top_geo_row = geo_totals.sort_values(by="Births", ascending=False).iloc[0]
        highest_geo_name = str(top_geo_row["State of Residence"])
        highest_geo_births = int(top_geo_row["Births"])
        highest_geo_str = f"{highest_geo_name} ({highest_geo_births:,.0f})"
    else:
        highest_geo_name = "None"
        highest_geo_births = 0
        highest_geo_str = "N/A"

    # 5. Month with the highest selected birth count
    month_totals = df.groupby("Month", observed=False, as_index=False)["Births"].sum()
    if not month_totals.empty and month_totals["Births"].max() > 0:
        top_month_row = month_totals.sort_values(by="Births", ascending=False).iloc[0]
        highest_month_name = str(top_month_row["Month"])
        highest_month_births = int(top_month_row["Births"])
        highest_month_str = f"{highest_month_name} ({highest_month_births:,.0f})"
    else:
        highest_month_name = "None"
        highest_month_births = 0
        highest_month_str = "N/A"

    return {
        "total_births": total_births,
        "total_births_str": f"{total_births:,.0f}",
        "selected_geos_count": selected_geos,
        "selected_geos_count_str": f"{selected_geos}",
        "avg_births_per_month": avg_per_month,
        "avg_births_per_month_str": f"{avg_per_month:,.0f}",
        "highest_geo_name": highest_geo_name,
        "highest_geo_births": highest_geo_births,
        "highest_geo_str": highest_geo_str,
        "highest_month_name": highest_month_name,
        "highest_month_births": highest_month_births,
        "highest_month_str": highest_month_str,
    }
