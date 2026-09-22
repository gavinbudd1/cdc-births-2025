"""
visualizations.py
=================
Plotly visualization functions for the CDC 2025 Provisional Natality Dashboard.

Design Principles:
- Accessible, colorblind-friendly color palettes
- Zero-based quantitative axes to prevent misleading visual distortion (Rule 7 & 9)
- Formatted hover tooltips with commas for thousands
- Informative titles and subtitles reinforcing that values are counts, not rates
"""

from typing import List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Consistent accessible theme styling
THEME_FONT = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
COLOR_PRIMARY = "#2563EB"    # Slate Blue
COLOR_SECONDARY = "#0D9488"  # Teal
COLOR_FEMALE = "#7C3AED"     # Deep Purple / Violet
COLOR_MALE = "#0284C7"       # Ocean Blue
COLOR_ACCENT = "#D97706"     # Amber Accent


def empty_chart_placeholder(message: str = "No data available for the current filter selection.") -> go.Figure:
    """Returns an empty figure with an explanatory message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color="#64748B", family=THEME_FONT),
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=320,
    )
    return fig


def plot_monthly_trend(df: pd.DataFrame, breakdown_by_sex: bool = False) -> go.Figure:
    """
    Renders the chronological monthly birth trend for 2025.
    Axes enforce zero-baseline to prevent visual distortion.
    """
    if df.empty:
        return empty_chart_placeholder("No observations to display for monthly trend.")

    if breakdown_by_sex:
        trend_df = (
            df.groupby(["Month", "Month Code", "Sex of Infant"], observed=False, as_index=False)["Births"]
            .sum()
            .sort_values(by="Month Code")
        )
        fig = px.line(
            trend_df,
            x="Month",
            y="Births",
            color="Sex of Infant",
            markers=True,
            color_discrete_map={"Female": COLOR_FEMALE, "Male": COLOR_MALE},
            labels={"Births": "Birth Count", "Month": "Calendar Month", "Sex of Infant": "Infant Sex"},
            title="Monthly Birth Count Trend by Infant Sex (2025)",
        )
    else:
        trend_df = (
            df.groupby(["Month", "Month Code"], observed=False, as_index=False)["Births"]
            .sum()
            .sort_values(by="Month Code")
        )
        fig = px.line(
            trend_df,
            x="Month",
            y="Births",
            markers=True,
            color_discrete_sequence=[COLOR_PRIMARY],
            labels={"Births": "Birth Count", "Month": "Calendar Month"},
            title="Total Monthly Live Birth Count (2025)",
        )

    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Births: <b>%{y:,.0f}</b><extra></extra>",
        line=dict(width=3),
        marker=dict(size=8),
    )
    fig.update_layout(
        font=dict(family=THEME_FONT),
        yaxis=dict(
            rangemode="tozero",
            tickformat=",.0f",
            gridcolor="#E2E8F0",
            title="Live Birth Count",
        ),
        xaxis=dict(gridcolor="#F1F5F9", title="Calendar Month"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        hovermode="x unified",
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_sex_comparison(df: pd.DataFrame) -> go.Figure:
    """
    Renders comparison of Female and Male births across the selection.
    Displays both absolute counts and proportional share of selected births.
    """
    if df.empty:
        return empty_chart_placeholder("No observations to display for sex comparison.")

    sex_df = df.groupby("Sex of Infant", as_index=False)["Births"].sum()
    total_births = sex_df["Births"].sum()
    sex_df["Percentage"] = (sex_df["Births"] / total_births * 100) if total_births > 0 else 0

    fig = px.bar(
        sex_df,
        x="Sex of Infant",
        y="Births",
        color="Sex of Infant",
        color_discrete_map={"Female": COLOR_FEMALE, "Male": COLOR_MALE},
        text=sex_df.apply(lambda r: f"{r['Births']:,.0f}<br>({r['Percentage']:.1f}%)", axis=1),
        labels={"Births": "Total Live Births", "Sex of Infant": "Infant Sex"},
        title="Live Birth Counts & Proportion by Infant Sex",
    )

    fig.update_traces(
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Births: <b>%{y:,.0f}</b><extra></extra>",
        marker=dict(line=dict(width=1, color="#CBD5E1")),
    )
    # Add headroom for outside text labels
    max_val = sex_df["Births"].max() if not sex_df.empty else 100
    fig.update_layout(
        font=dict(family=THEME_FONT),
        yaxis=dict(
            range=[0, max_val * 1.18],
            tickformat=",.0f",
            gridcolor="#E2E8F0",
            title="Live Birth Count",
        ),
        xaxis=dict(title=""),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        showlegend=False,
        margin=dict(l=40, r=30, t=50, b=40),
    )
    return fig


def plot_state_ranking(df: pd.DataFrame, top_n: Optional[int] = None) -> go.Figure:
    """
    Horizontal bar chart ranking states by aggregate birth counts in selection.
    Sorted from largest to smallest, zero-based X-axis.
    """
    if df.empty:
        return empty_chart_placeholder("No observations to display for state ranking.")

    state_df = (
        df.groupby("State of Residence", as_index=False)["Births"]
        .sum()
        .sort_values(by="Births", ascending=True)
    )

    if top_n is not None and top_n > 0:
        state_df = state_df.tail(top_n)

    fig = px.bar(
        state_df,
        x="Births",
        y="State of Residence",
        orientation="h",
        color="Births",
        color_continuous_scale="Blues",
        labels={"Births": "Total Live Births", "State of Residence": "Geography"},
        title=f"State Ranking by Live Birth Count {'(Top ' + str(top_n) + ')' if top_n else '(All Selected)'}",
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Births: <b>%{x:,.0f}</b><extra></extra>",
    )
    fig.update_layout(
        font=dict(family=THEME_FONT),
        xaxis=dict(
            rangemode="tozero",
            tickformat=",.0f",
            gridcolor="#E2E8F0",
            title="Total Live Birth Count",
        ),
        yaxis=dict(title="", dtick=1),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        coloraxis_showscale=False,
        height=max(400, len(state_df) * 22 + 100),
        margin=dict(l=140, r=40, t=50, b=40),
    )
    return fig


def plot_choropleth_map(df: pd.DataFrame) -> go.Figure:
    """
    U.S. state choropleth map visualizing total birth volume by geography.
    Uses 2-letter postal abbreviations.
    """
    if df.empty:
        return empty_chart_placeholder("No observations to display for choropleth map.")

    map_df = (
        df.groupby(["State of Residence", "State Abbreviation"], as_index=False)["Births"]
        .sum()
    )
    total_selection_births = map_df["Births"].sum()
    map_df["Pct_Share"] = (map_df["Births"] / total_selection_births * 100) if total_selection_births > 0 else 0

    fig = go.Figure(
        data=go.Choropleth(
            locations=map_df["State Abbreviation"],
            z=map_df["Births"],
            locationmode="USA-states",
            colorscale="Viridis",
            marker_line_color="#CBD5E1",
            marker_line_width=1,
            colorbar=dict(
                title=dict(text="Births", font=dict(family=THEME_FONT, size=12)),
                tickformat=",.0f",
                thickness=15,
                len=0.75,
            ),
            customdata=map_df[["State of Residence", "Pct_Share"]],
            hovertemplate=(
                "<b>%{customdata[0]} (%{location})</b><br>"
                + "Live Birth Count: <b>%{z:,.0f}</b><br>"
                + "Share of Selection: <b>%{customdata[1]:.2f}%</b>"
                + "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text="Geographic Distribution of Provisional Live Birth Counts (2025)",
            font=dict(family=THEME_FONT, size=16),
        ),
        geo=dict(
            scope="usa",
            projection=dict(type="albers usa"),
            showlakes=True,
            lakecolor="#EFF6FF",
            bgcolor="rgba(0,0,0,0)",
        ),
        font=dict(family=THEME_FONT),
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=50, b=20),
        height=500,
    )
    return fig


def plot_state_month_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    2D interactive heatmap showing State on Y-axis and Month on X-axis.
    Reveals seasonal and geographic volume concentration.
    """
    if df.empty:
        return empty_chart_placeholder("No observations to display for heatmap.")

    pivot_df = (
        df.groupby(["State of Residence", "Month"], observed=False, as_index=False)["Births"]
        .sum()
        .pivot(index="State of Residence", columns="Month", values="Births")
        .fillna(0)
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns.tolist(),
            y=pivot_df.index.tolist(),
            colorscale="Tealgrn",
            colorbar=dict(
                title=dict(text="Births", font=dict(family=THEME_FONT, size=12)),
                tickformat=",.0f",
                thickness=15,
            ),
            hovertemplate="<b>State</b>: %{y}<br><b>Month</b>: %{x}<br><b>Births</b>: %{z:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text="State by Month Live Birth Heatmap (2025)",
            font=dict(family=THEME_FONT, size=16),
        ),
        xaxis=dict(title="Calendar Month", tickangle=-45),
        yaxis=dict(title="", dtick=1),
        font=dict(family=THEME_FONT),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=max(450, len(pivot_df) * 18 + 120),
        margin=dict(l=140, r=40, t=60, b=80),
    )
    return fig


def plot_top_bottom_comparison(df: pd.DataFrame, n: int = 5) -> go.Figure:
    """
    Side-by-side / grouped comparison of Top N vs Bottom N states by birth volume.
    Educational takeaway: Highlighting the magnitude difference due to population size.
    """
    if df.empty:
        return empty_chart_placeholder("No observations to display for top/bottom comparison.")

    state_totals = (
        df.groupby("State of Residence", as_index=False)["Births"]
        .sum()
        .sort_values(by="Births", ascending=False)
    )

    if len(state_totals) < n * 2:
        n = max(1, len(state_totals) // 2)

    top_states = state_totals.head(n).copy()
    top_states["Group"] = f"Top {n} Geographies"

    bottom_states = state_totals.tail(n).copy()
    bottom_states["Group"] = f"Bottom {n} Geographies"

    comp_df = pd.concat([top_states, bottom_states]).sort_values(by="Births", ascending=True)

    fig = px.bar(
        comp_df,
        x="Births",
        y="State of Residence",
        color="Group",
        orientation="h",
        color_discrete_map={
            f"Top {n} Geographies": COLOR_PRIMARY,
            f"Bottom {n} Geographies": COLOR_ACCENT,
        },
        labels={"Births": "Total Live Births", "State of Residence": "Geography", "Group": "Cohort"},
        title=f"Comparison: Top {n} vs. Bottom {n} Geographies by Birth Volume",
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b> (%{data.name})<br>Births: <b>%{x:,.0f}</b><extra></extra>",
    )
    fig.update_layout(
        font=dict(family=THEME_FONT),
        xaxis=dict(
            rangemode="tozero",
            tickformat=",.0f",
            gridcolor="#E2E8F0",
            title="Total Live Birth Count",
        ),
        yaxis=dict(title="", dtick=1),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=140, r=40, t=60, b=40),
        height=max(380, len(comp_df) * 32 + 100),
    )
    return fig
