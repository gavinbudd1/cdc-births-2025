# 👶 U.S. CDC Provisional Natality Dashboard (2025)

An interactive, educational business analytics dashboard built with **Streamlit**, **pandas**, and **Plotly** to explore provisional 2025 live birth counts across geographic, seasonal, and demographic dimensions.

Designed specifically for undergraduate business analytics students to practice descriptive analytics, visual design, and data-quality auditing.

---

## 📌 Project Overview & Educational Objectives

This project analyzes provisional live birth records from the **Centers for Disease Control and Prevention (CDC) / National Center for Health Statistics (NCHS)** for calendar year 2025.

### Key Analytical Takeaways for Students
1. **Counts vs. Rates (The Base-Rate Fallacy)**:
   - This dataset reports **raw counts of live births**, not demographic birth rates or general fertility rates.
   - Populous states (e.g., California with 393,111 births and Texas with 386,419 births) record high birth counts because they have large populations, not necessarily because maternal fertility is higher.
   - Comparing raw counts across groups of unequal size without a census population denominator can lead to misleading conclusions.
2. **Provisional Vital Statistics**:
   - Provisional data are released continuously to provide early indicators of public health trends. They represent early registrations and are subject to reporting delays and subsequent revisions before final annual data are certified.

---

## 📊 Dataset Specifications & Audit Benchmarks

The dashboard automatically audits the underlying dataset at startup against 7 ground truth benchmarks:

| Benchmark Criterion | Expected Value | Verification Status |
| :--- | :--- | :---: |
| **Total Observations** | 1,224 rows | Passed |
| **Geographic Coverage** | 51 jurisdictions (50 States + District of Columbia) | Passed |
| **Temporal Coverage** | 12 calendar months (January – December 2025) | Passed |
| **Demographic Slices** | 2 infant-sex categories (Female, Male) | Passed |
| **Missing Values (Nulls)** | 0 missing fields across all columns | Passed |
| **Duplicate Records** | 0 duplicate rows | Passed |
| **Total Live Birth Volume** | **3,604,640 births** | Passed |

---

## 🚀 Key Features

* **Real-Time Dynamic KPIs**:
  - **Total Live Births** in active filter selection
  - **Geographies Selected** ($N / 51$)
  - **Average Births per Selected Month**
  - **Top Geography** by birth volume with count
  - **Peak Month** by birth volume with count
* **Sidebar Controls**:
  - State / Geography multiselect with `Select All` and `Clear` shortcuts
  - Calendar Month multiselect with `Select All` and `Clear` shortcuts
  - Infant Sex filter (`All`, `Female`, `Male`)
  - `Reset All Filters` button to instantly restore full 50-state + DC scope
  - Dynamic active filter badge showing the active slice
* **Five Focused Analysis Tabs**:
  1. **📊 Overview**: Executive narrative summary, monthly volume line trend, female vs. male distribution, and Top 5 vs. Bottom 5 scale comparison.
  2. **🗺️ Geographic Analysis**: Interactive U.S. choropleth map using 2-letter state postal abbreviations and a customizable state ranking bar chart (All, Top 10, Top 20).
  3. **📈 Monthly & Sex Analysis**: Monthly birth trends broken down by sex and an interactive 2D State-by-Month matrix heatmap.
  4. **📋 Data Table & Download**: Searchable micro-aggregate record table with formatted numbers and an instant CSV download button (`st.download_button`).
  5. **📚 About the Data**: Full documentation of data provenance, public health principles, and live automated data audit verification.
* **Responsible Visual Design**:
  - Zero-based quantitative axes on all bar and line charts to prevent deceptive visual scaling.
  - Thousands separators (`:,`) on all numeric values and hover tooltips.
  - Fully responsive layout supporting both desktop screens and mobile viewports.

---

## 📁 Repository Structure

```
cdc-births-2025/
├── .streamlit/
│   └── config.toml               # Clean, accessible theme configuration
├── Data/
│   └── Provisional_Natality_2025_CDC.xlsx  # Read-only source workbook (unaltered)
├── src/
│   ├── __init__.py
│   ├── data_loader.py            # Cached loading, benchmark assertions, postal mapping
│   ├── kpis.py                   # Dynamic KPI calculations and thousands formatting
│   ├── visualizations.py         # Accessible Plotly figures with zero-based quantitative axes
│   └── ui_components.py          # Header, provisional alerts, badges, and table views
├── tests/
│   ├── test_dashboard_logic.py   # Unit test suite verifying logic, loading, & KPIs
│   └── run_browser_qa.py         # Selenium Edge 12-case end-to-end browser QA suite
├── app.py                        # Streamlit dashboard orchestrator
├── README.md                     # Project documentation & student guide
└── requirements.txt              # Project dependencies
```

---

## 🛠️ Setup & Running Locally

### 1. Prerequisites
- **Python**: 3.10, 3.11, or 3.12 installed.

### 2. Install Dependencies
Open your terminal in the project directory and install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Launch the Dashboard
Run the Streamlit local dev server:

```bash
streamlit run app.py
```

Open your browser to:
```
http://localhost:8501
```

---

## 🧪 Testing & Quality Assurance

### Automated Unit Tests
To verify data-loading integrity, KPI calculations, and chart generation:

```bash
python tests/test_dashboard_logic.py
```

### Browser-Based End-to-End QA
To run the automated 12-case Selenium browser test suite (verifying filter updates, tab transitions, map rendering, download buttons, and mobile layouts):

```bash
python tests/run_browser_qa.py
```

---

## 📜 Source Attribution & Disclaimer

- **Data Source**: Centers for Disease Control and Prevention (CDC) / National Center for Health Statistics (NCHS) via the CDC WONDER database.
- **Provisional Status**: All 2025 counts are provisional estimates subject to ongoing reporting lags and vital statistics revisions.
