"""
data_loader.py
==============
Data loading, validation, and feature preparation module for the CDC 2025 Provisional Natality Dashboard.

Designed for undergraduate business analytics students:
- Demonstrates cached data ingestion with Streamlit (@st.cache_data)
- Enforces strict data-quality assertions against expected benchmarks
- Standardizes categorical order and geographic identifiers
"""

from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
import streamlit as st

# Standard U.S. State and District of Columbia two-letter postal code mapping
STATE_TO_ABBREV: Dict[str, str] = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

# Chronological order of calendar months
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Benchmark constants for data-quality auditing
EXPECTED_ROWS = 1224
EXPECTED_GEOS = 51
EXPECTED_MONTHS = 12
EXPECTED_SEX_CATEGORIES = 2
EXPECTED_TOTAL_BIRTHS = 3604640


def validate_dataset(df: pd.DataFrame) -> Dict[str, bool]:
    """
    Validates the dataset against baseline ground truth benchmarks.
    
    Returns a dictionary of check names and boolean pass/fail flags.
    Raises ValueError if any critical check fails.
    """
    checks = {
        "Row count is 1,224": len(df) == EXPECTED_ROWS,
        "51 unique geographies": df["State of Residence"].nunique() == EXPECTED_GEOS,
        "12 calendar months": df["Month"].nunique() == EXPECTED_MONTHS,
        "2 infant-sex categories": df["Sex of Infant"].nunique() == EXPECTED_SEX_CATEGORIES,
        "Zero missing values": int(df.isnull().sum().sum()) == 0,
        "Zero duplicate rows": int(df.duplicated().sum()) == 0,
        "Total births equal 3,604,640": int(df["Births"].sum()) == EXPECTED_TOTAL_BIRTHS,
    }
    
    failed_checks = [name for name, passed in checks.items() if not passed]
    if failed_checks:
        raise ValueError(f"Data validation failed for: {', '.join(failed_checks)}")
        
    return checks


@st.cache_data(show_spinner="Loading CDC 2025 Provisional Natality data...")
def load_natality_data(data_path: str = None) -> pd.DataFrame:
    """
    Loads, validates, and enhances the CDC 2025 Provisional Natality dataset.
    
    1. Resolves path portably for both local execution and Streamlit Community Cloud.
    2. Reads the original workbook in read-only mode without modification.
    3. Runs automated data-quality validation.
    4. Adds standard postal state abbreviations for choropleth mapping.
    5. Sets Month as an ordered categorical variable to guarantee chronological sorting.
    """
    if data_path is None:
        # Resolve relative to project root
        base_dir = Path(__file__).resolve().parent.parent
        data_file = base_dir / "Data" / "Provisional_Natality_2025_CDC.xlsx"
    else:
        data_file = Path(data_path)

    if not data_file.exists():
        raise FileNotFoundError(f"Workbook not found at {data_file}")

    # Read the first worksheet
    df = pd.read_excel(data_file)

    # Perform automated audit check
    validate_dataset(df)

    # Add 2-letter state postal abbreviation
    df["State Abbreviation"] = df["State of Residence"].map(STATE_TO_ABBREV)

    # Ensure chronological order for Month
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)

    # Sort deterministically by State, Month Code, and Sex
    df = df.sort_values(by=["State of Residence", "Month Code", "Sex of Infant"]).reset_index(drop=True)

    return df
