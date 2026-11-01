
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Malaysian District Data Visualisation",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = Path(__file__).parent / "processed_data"


# =========================================================
# 2. COLOUR PALETTE
# =========================================================

COLORS = {
    "navy": "#174A7E",
    "blue": "#2166AC",
    "orange": "#E67E22",
    "red": "#C0392B",
    "green": "#218C74",
    "purple": "#7651A8",
    "teal": "#087E8B",
    "gold": "#C58B00",
    "dark": "#202A35",
    "grey": "#687385",
    "grid": "#D9E0E8",
    "white": "#FFFFFF"
}

CATEGORY_COLORS = [
    "#174A7E",
    "#E67E22",
    "#218C74",
    "#C0392B",
    "#7651A8",
    "#087E8B",
    "#A65D03",
    "#536878",
    "#B03A2E",
    "#4C6B3C"
]


# =========================================================
# 3. GLOBAL CHART STYLE
# =========================================================

def style_chart(fig, height=600):

    fig.update_layout(
        template="plotly_white",
        height=height,
        font=dict(
            family="Arial, sans-serif",
            size=13,
            color=COLORS["dark"]
        ),
        title=dict(
            font=dict(
                size=19,
                color=COLORS["dark"]
            ),
            x=0.02,
            xanchor="left"
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(
            l=75,
            r=65,
            t=90,
            b=75
        ),
        legend=dict(
            font=dict(
                size=12,
                color=COLORS["dark"]
            ),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#D9E0E8",
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#687385",
            font=dict(
                color="#202A35",
                size=13
            )
        ),
        hovermode="closest"
    )

    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor="#7B8794",
        showgrid=False,
        zeroline=False,
        tickfont=dict(
            size=12,
            color="#202A35"
        ),
        title_font=dict(
            size=13,
            color="#202A35"
        ),
        automargin=True
    )

    fig.update_yaxes(
        showline=False,
        showgrid=True,
        gridwidth=1,
        gridcolor=COLORS["grid"],
        zeroline=False,
        tickfont=dict(
            size=12,
            color="#202A35"
        ),
        title_font=dict(
            size=13,
            color="#202A35"
        ),
        automargin=True
    )

    return fig


# =========================================================
# 4. INTERACTIVE CHART DISPLAY
# =========================================================

def show_chart(fig, chart_key):

    fig = style_chart(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=chart_key,
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "scrollZoom": True,
            "doubleClick": "reset",
            "responsive": True,
            "modeBarButtonsToRemove": [
                "lasso2d",
                "select2d"
            ],
            "toImageButtonOptions": {
                "format": "png",
                "filename": chart_key,
                "height": 900,
                "width": 1600,
                "scale": 2
            }
        }
    )


# =========================================================
# 5. LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    poverty = pd.read_csv(
        DATA_DIR / "poverty_processed.csv"
    )

    population = pd.read_csv(
        DATA_DIR / "population_total.csv"
    )

    ethnicity = pd.read_csv(
        DATA_DIR / "population_ethnicity.csv"
    )

    age = pd.read_csv(
        DATA_DIR / "population_age.csv"
    )

    teachers = pd.read_csv(
        DATA_DIR / "teachers_processed.csv"
    )

    integrated = pd.read_csv(
        DATA_DIR / "integrated_2024.csv"
    )

    education = pd.read_csv(
        DATA_DIR / "education_features.csv"
    )

    datasets = [
        poverty,
        population,
        ethnicity,
        age,
        teachers,
        integrated,
        education
    ]

    for df in datasets:

        if "date" in df.columns:

            df["date"] = pd.to_datetime(
                df["date"],
                errors="coerce"
            )

        if "year" not in df.columns and "date" in df.columns:

            df["year"] = df["date"].dt.year

    return (
        poverty,
        population,
        ethnicity,
        age,
        teachers,
        integrated,
        education
    )


try:

    (
        poverty,
        population,
        ethnicity,
        age,
        teachers,
        integrated,
        education
    ) = load_data()

except Exception as e:

    st.error(f"Unable to load datasets: {e}")

    st.info(
        "Please ensure all seven CSV files are available "
        "inside the processed_data folder."
    )

    st.stop()


# =========================================================
# 6. MAIN HEADER
# =========================================================

st.title("Malaysian District Data Visualisation")

st.markdown(
    """
    Exploring Household Poverty, Population Distribution
    and Teacher Availability Across Malaysian Districts.
    """
)

st.markdown("---")


# =========================================================
# 7. SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("Dashboard Navigation")

page = st.sidebar.radio(
    "Select Research Objective",
    [
        "1. Household Poverty Patterns",
        "2. Population Distribution",
        "3. Poverty & Teacher Availability"
    ]
)

available_states = sorted(
    integrated["state"].dropna().unique().tolist()
)

selected_states = st.sidebar.multiselect(
    "Filter by State",
    available_states,
    default=available_states
)


def filter_states(df):

    if "state" not in df.columns:
        return df.copy()

    return df[
        df["state"].isin(selected_states)
    ].copy()


# =========================================================
# 8. PAGE 1: HOUSEHOLD POVERTY
# =========================================================

if page == "1. Household Poverty Patterns":

    st.header(
        "Objective 1: Household Poverty Patterns"
    )

    st.markdown(
        """
        **Objective:** Analyse household poverty patterns across
        Malaysian districts by examining absolute and relative
        poverty rates and identifying districts with higher
        poverty levels.
        """
    )

    poverty_filtered = filter_states(poverty)

    poverty_2024 = poverty_filtered[
        poverty_filtered["year"] == 2024
    ].copy()

    if poverty_2024.empty:

        st.warning(
            "No poverty data available for the selected states."
        )
        st.stop()

    avg_absolute = poverty_2024[
        "poverty_absolute"
    ].mean()

    avg_relative = poverty_2024[
        "poverty_relative"
    ].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Absolute Poverty",
        f"{avg_absolute:.2f}%"
    )

    col2.metric(
        "Average Relative Poverty",
        f"{avg_relative:.2f}%"
    )

    col3.metric(
        "Districts Analysed",
        f"{poverty_2024['district'].nunique()}"
    )

    st.markdown("---")

    # -----------------------------------------------------
    # CHART 1: POVERTY TREND
    # -----------------------------------------------------

    st.subheader(
        "1. Household Poverty Trend (2019–2024)"
    )

    years_required = {2019, 2022, 2024}

    trend_data = poverty_filtered[
        poverty_filtered["year"].isin(years_required)
    ].copy()

    trend_data["district_key"] = (
        trend_data["state"].astype(str)
        + " - "
        + trend_data["district"].astype(str)
    )

    common_districts = (
        trend_data.groupby("district_key")["year"]
        .nunique()
    )

    common_districts = common_districts[
        common_districts == 3
    ].index

    trend_data = trend_data[
        trend_data["district_key"].isin(common_districts)
    ]

    trend_summary = (
        trend_data.groupby("year")[
            [
                "poverty_absolute",
                "poverty_relative"
            ]
        ]
        .mean()
        .reset_index()
    )

    trend_summary = trend_summary.melt(
        id_vars="year",
        var_name="Poverty Type",
        value_name="Average Rate (%)"
    )

    trend_summary["Poverty Type"] = (
        trend_summary["Poverty Type"].map({
            "poverty_absolute": "Absolute Poverty",
            "poverty_relative": "Relative Poverty"
        })
    )

    trend_summary["year"] = (
        trend_summary["year"].astype(str)
    )

    fig1 = px.line(
        trend_summary,
        x="year",
        y="Average Rate (%)",
        color="Poverty Type",
        markers=True,
        color_discrete_map={
            "Absolute Poverty": COLORS["navy"],
            "Relative Poverty": COLORS["orange"]
        },
        title=(
            "Average Poverty Rate Across "
            "Consistently Matched Districts"
        )
    )

    fig1.update_traces(
        line=dict(width=4),
        marker=dict(
            size=12,
            line=dict(
                width=1.5,
                color="white"
            )
        ),
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Year: %{x}<br>"
            "Average Rate: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    fig1.update_layout(
        xaxis_title="Year",
        yaxis_title="Average Poverty Rate (%)",
        xaxis=dict(type="category"),
        hovermode="x unified"
    )

    show_chart(fig1, "chart_1_poverty_trend")

    st.markdown(
        """
        **Interpretation:**

        The line chart compares average absolute and relative
        poverty rates across districts with records in all three
        selected years. Consistent district coverage helps reduce
        the influence of changes in the number of districts.
        """
    )

    # -----------------------------------------------------
    # CHART 2: TOP 10 POVERTY DISTRICTS
    # -----------------------------------------------------

    st.subheader(
        "2. Top 10 Districts by Absolute Poverty (2024)"
    )

    top_poverty = (
        poverty_2024.nlargest(
            10,
            "poverty_absolute"
        )
        .sort_values(
            "poverty_absolute",
            ascending=True
        )
    )

    fig2 = px.bar(
        top_poverty,
        x="poverty_absolute",
        y="district",
        orientation="h",
        text="poverty_absolute",
        color_discrete_sequence=[
            COLORS["red"]
        ],
        title=(
            "Top 10 Districts with Highest "
            "Absolute Poverty Rates"
        ]
    )

    fig2.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        textfont=dict(
            size=13,
            color=COLORS["dark"]
        ),
        marker_line_color="#7D241C",
        marker_line_width=1,
        hovertemplate=(
            "District: %{y}<br>"
            "Absolute Poverty: %{x:.2f}%"
            "<extra></extra>"
        )
    )

    fig2.update_layout(
        xaxis_title="Absolute Poverty Rate (%)",
        yaxis_title="District",
        showlegend=False
    )

    fig2.update_xaxes(
        range=[
            0,
            top_poverty["poverty_absolute"].max() * 1.2
        ]
    )

    show_chart(fig2, "chart_2_top_poverty")

    st.markdown(
        """
        **Interpretation:**

        The ranking identifies districts with the highest
        absolute poverty rates in 2024. A concentration of
        high-poverty districts in particular states may indicate
        geographical differences in socioeconomic conditions.
        """
    )

    # -----------------------------------------------------
    # CHART 3: ABSOLUTE VS RELATIVE POVERTY
    # -----------------------------------------------------

    st.subheader(
        "3. Absolute vs Relative Poverty (2024)"
    )

    fig3 = px.scatter(
        poverty_2024,
        x="poverty_absolute",
        y="poverty_relative",
        color="state",
        hover_name="district",
        color_discrete_sequence=CATEGORY_COLORS,
        title=(
            "Relationship Between Absolute "
            "and Relative Poverty"
        )
    )

    fig3.update_traces(
        marker=dict(
            size=12,
            opacity=0.9,
            line=dict(
                width=1.2,
                color="#202A35"
            )
        ),
        hovertemplate=(
            "District: %{hovertext}<br>"
            "Absolute Poverty: %{x:.2f}%<br>"
            "Relative Poverty: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    fig3.update_layout(
        xaxis_title="Absolute Poverty Rate (%)",
        yaxis_title="Relative Poverty Rate (%)",
        legend_title="State"
    )

    show_chart(fig3, "chart_3_poverty_scatter")

    st.markdown(
        """
        **Interpretation:**

        The scatter plot compares absolute and relative poverty
        rates across districts. Points in the upper-right area
        represent districts with higher values for both measures.
        """
    )


# =========================================================
# 9. PAGE 2: POPULATION DISTRIBUTION
# =========================================================

elif page == "2. Population Distribution":

    st.header(
        "Objective 2: Population Distribution"
    )

    st.markdown(
        """
        **Objective:** Examine population distribution and
        demographic characteristics across Malaysian districts,
        focusing on population trends, ethnic composition
        and age distribution.
        """
    )

    population_filtered = filter_states(population)
    ethnicity_filtered = filter_states(ethnicity)
    age_filtered = filter_states(age)

    population_2024 = population_filtered[
        population_filtered["year"] == 2024
    ].copy()

    ethnicity_2024 = ethnicity_filtered[
        ethnicity_filtered["year"] == 2024
    ].copy()

    age_2024 = age_filtered[
        age_filtered["year"] == 2024
    ].copy()

    if population_2024.empty:

        st.warning(
            "No population data available for the selected states."
        )
        st.stop()

    total_population = population_2024[
        "population"
    ].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Population (2024)",
        f"{total_population:,.1f} thousand"
    )

    col2.metric(
        "Districts Analysed",
        f"{population_2024['district'].nunique()}"
    )

    col3.metric(
        "Age Groups",
        f"{age_2024['age'].nunique()}"
    )

    st.caption(
        "Population values are reported in thousands ('000), "
        "according to the source dataset."
    )

    st.markdown("---")

    # -----------------------------------------------------
    # CHART 4: POPULATION TREND
    # -----------------------------------------------------

    st.subheader(
        "1. Population Trend (2020–2026)"
    )

    population_trend = (
        population_filtered.groupby("year")
        .agg(
            total_population=("population", "sum"),
            district_count=("district", "nunique")
        )
        .reset_index()
        .sort_values("year")
    )

    population_trend["year"] = (
        population_trend["year"].astype(str)
    )

    fig4 = px.line(
        population_trend,
        x="year",
        y="total_population",
        markers=True,
        color_discrete_sequence=[
            COLORS["navy"]
        ],
        title="Total Reported Population by Year"
    )

    fig4.update_traces(
        line=dict(width=4),
        marker=dict(
            size=12,
            color=COLORS["orange"],
            line=dict(
                width=1.5,
                color=COLORS["navy"]
            )
        ),
        hovertemplate=(
            "Year: %{x}<br>"
            "Population: %{y:,.1f} thousand"
            "<extra></extra>"
        )
    )

    fig4.update_layout(
        xaxis_title="Year",
        yaxis_title="Total Population (Thousands)",
        xaxis=dict(type="category"),
        hovermode="x unified"
    )

    show_chart(fig4, "chart_4_population_trend")

    st.caption(
        "Note: District coverage varies between years. "
        "Yearly totals should be interpreted with this "
        "coverage difference in mind."
    )

    st.markdown(
        """
        **Interpretation:**

        The line chart illustrates changes in total reported
        population from 2020 to 2026. Changes in district
        coverage should be considered when comparing totals.
        """
    )

    # -----------------------------------------------------
    # CHART 5: POPULATION BY ETHNICITY
    # -----------------------------------------------------

    st.subheader(
        "2. Population by Ethnicity (2024)"
    )

    ethnicity_labels = {
        "bumi_malay": "Bumiputera Malay",
        "bumi_other": "Other Bumiputera",
        "chinese": "Chinese",
        "indian": "Indian",
        "other_citizen": "Other Citizens",
        "other_noncitizen": "Other Non-Citizens"
    }

    ethnicity_summary = (
        ethnicity_2024.groupby("ethnicity")[
            "population"
        ]
        .sum()
        .reset_index()
    )

    ethnicity_summary = ethnicity_summary[
        ethnicity_summary["ethnicity"] != "overall"
    ].copy()

    ethnicity_summary["Ethnic Group"] = (
        ethnicity_summary["ethnicity"]
        .map(ethnicity_labels)
        .fillna(ethnicity_summary["ethnicity"])
    )

    ethnicity_summary = ethnicity_summary.sort_values(
        "population",
        ascending=True
    )

    ethnicity_summary["percentage"] = (
        ethnicity_summary["population"]
        / ethnicity_summary["population"].sum()
        * 100
    )

    fig5 = px.bar(
        ethnicity_summary,
        x="population",
        y="Ethnic Group",
        orientation="h",
        text="percentage",
        color_discrete_sequence=[
            COLORS["teal"]
        ],
        title="Population Distribution by Ethnic Group"
    )

    fig5.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        textfont=dict(
            size=13,
            color=COLORS["dark"]
        ),
        marker_line_color="#07515A",
        marker_line_width=1,
        hovertemplate=(
            "Ethnic Group: %{y}<br>"
            "Population: %{x:,.1f} thousand"
            "<br>Share: %{text:.2f}%"
            "<extra></extra>"
        )
    )

    fig5.update_layout(
        xaxis_title="Population (Thousands)",
        yaxis_title="Ethnic Group",
        showlegend=False
    )

    fig5.update_xaxes(
        range=[
            0,
            ethnicity_summary["population"].max() * 1.3
        ]
    )

    show_chart(fig5, "chart_5_ethnicity")

    st.markdown(
        """
        **Interpretation:**

        The horizontal bar chart compares population sizes
        across ethnic groups. Percentage labels indicate
        each group's proportion within the selected districts.
        """
    )

    # -----------------------------------------------------
    # CHART 6: POPULATION BY AGE
    # -----------------------------------------------------

    st.subheader(
        "3. Population by Age Group (2024)"
    )

    age_summary = (
        age_2024.groupby("age")[
            "population"
        ]
        .sum()
        .reset_index()
    )

    age_order = [
        "0-4", "5-9", "10-14", "15-19",
        "20-24", "25-29", "30-34", "35-39",
        "40-44", "45-49", "50-54", "55-59",
        "60-64", "65-69", "70-74", "75-79",
        "80-84", "85+"
    ]

    age_summary["age"] = pd.Categorical(
        age_summary["age"],
        categories=age_order,
        ordered=True
    )

    age_summary = age_summary.sort_values("age")

    fig6 = px.bar(
        age_summary,
        x="age",
        y="population",
        color_discrete_sequence=[
            COLORS["blue"]
        ],
        title="Population Distribution Across Age Groups"
    )

    fig6.update_traces(
        marker_line_color="#123D68",
        marker_line_width=1,
        hovertemplate=(
            "Age Group: %{x}<br>"
            "Population: %{y:,.1f} thousand"
            "<extra></extra>"
        )
    )

    fig6.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Population (Thousands)"
    )

    show_chart(fig6, "chart_6_age_distribution")

    st.markdown(
        """
        **Interpretation:**

        The column chart shows how the population is distributed
        across different age groups. It helps identify age groups
        with larger population representation.
        """
    )


# =========================================================
# 10. PAGE 3: POVERTY & TEACHER AVAILABILITY
# =========================================================

elif page == "3. Poverty & Teacher Availability":

    st.header(
        "Objective 3: Poverty and Teacher Availability"
    )

    st.markdown(
        """
        **Objective:** Identify districts with higher poverty
        levels and comparatively lower teacher availability by
        examining the relationship between absolute poverty
        and the number of teachers per 1,000 residents.
        """
    )

    education_filtered = filter_states(education)

    education_2024 = education_filtered[
        education_filtered["year"] == 2024
    ].copy()

    if education_2024.empty:

        st.warning(
            "No integrated data available for the selected states."
        )
        st.stop()

    avg_poverty = education_2024[
        "poverty_absolute"
    ].mean()

    avg_teacher = education_2024[
        "teachers_per_1000"
    ].mean()

    priority_condition = (
        (education_2024["poverty_absolute"] > avg_poverty)
        & (
            education_2024["teachers_per_1000"]
            < avg_teacher
        )
    )

    priority_count = priority_condition.sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Absolute Poverty",
        f"{avg_poverty:.2f}%"
    )

    col2.metric(
        "Average Teachers per 1,000",
        f"{avg_teacher:.2f}"
    )

    col3.metric(
        "Potential Priority Districts",
        f"{priority_count}"
    )

    st.caption(
        "Teacher availability is calculated as total government-school "
        "teachers divided by population (reported in thousands)."
    )

    st.markdown("---")

    # -----------------------------------------------------
    # CHART 7: POVERTY VS TEACHER AVAILABILITY
    # -----------------------------------------------------

    st.subheader(
        "1. Poverty vs Teacher Availability"
    )

    fig7 = px.scatter(
        education_2024,
        x="teachers_per_1000",
        y="poverty_absolute",
        color="state",
        hover_name="district",
        hover_data={
            "teachers_per_1000": ":.2f",
            "poverty_absolute": ":.2f",
            "population": ":,.1f"
        },
        color_discrete_sequence=CATEGORY_COLORS,
        title=(
            "Relationship Between Poverty "
            "and Teacher Availability"
        )
    )

    fig7.update_traces(
        marker=dict(
            size=12,
            opacity=0.9,
            line=dict(
                width=1.2,
                color="#202A35"
            )
        )
    )

    fig7.add_hline(
        y=avg_poverty,
        line_dash="dash",
        line_width=2.5,
        line_color=COLORS["red"],
        annotation_text="Average Poverty",
        annotation_font_color=COLORS["red"]
    )

    fig7.add_vline(
        x=avg_teacher,
        line_dash="dash",
        line_width=2.5,
        line_color=COLORS["navy"],
        annotation_text="Average Teacher Availability",
        annotation_font_color=COLORS["navy"]
    )

    fig7.update_layout(
        xaxis_title="Teachers per 1,000 Residents",
        yaxis_title="Absolute Poverty Rate (%)",
        legend_title="State"
    )

    show_chart(fig7, "chart_7_poverty_teacher")

    st.markdown(
        """
        **Interpretation:**

        Districts in the upper-left quadrant have above-average
        poverty and below-average teacher availability within
        the selected sample. These districts may warrant further
        investigation. This comparison does not establish
        a causal relationship or prove a teacher shortage.
        """
    )

    # -----------------------------------------------------
    # CHART 8: LOWEST TEACHER AVAILABILITY
    # -----------------------------------------------------

    st.subheader(
        "2. Ten Districts with Lowest Teacher Availability"
    )

    lowest_teacher = (
        education_2024.nsmallest(
            10,
            "teachers_per_1000"
        )
        .sort_values(
            "teachers_per_1000",
            ascending=True
        )
    )

    fig8 = px.bar(
        lowest_teacher,
        x="teachers_per_1000",
        y="district",
        orientation="h",
        text="teachers_per_1000",
        color_discrete_sequence=[
            COLORS["orange"]
        ],
        title=(
            "Districts with the Lowest "
            "Teacher Availability"
        )
    )

    fig8.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
        textfont=dict(
            size=13,
            color=COLORS["dark"]
        ),
        marker_line_color="#9C4D08",
        marker_line_width=1
    )

    fig8.update_layout(
        xaxis_title="Teachers per 1,000 Residents",
        yaxis_title="District",
        showlegend=False
    )

    fig8.update_xaxes(
        range=[
            0,
            lowest_teacher["teachers_per_1000"].max() * 1.25
        ]
    )

    show_chart(fig8, "chart_8_lowest_teacher")

    st.markdown(
        """
        **Interpretation:**

        This ranking highlights the ten districts with the
        lowest calculated teacher availability per 1,000
        residents. It enables comparison between districts
        while accounting for differences in population size.
        """
    )

    # -----------------------------------------------------
    # CHART 9: DISTRICT PRIORITY QUADRANT
    # -----------------------------------------------------

    st.subheader(
        "3. District Priority Quadrant Analysis"
    )

    quadrant_data = education_2024.copy()

    quadrant_data["Priority Group"] = np.select(
        [
            (
                (quadrant_data["poverty_absolute"] > avg_poverty)
                & (
                    quadrant_data["teachers_per_1000"]
                    < avg_teacher
                )
            ),
            (
                (quadrant_data["poverty_absolute"] > avg_poverty)
                & (
                    quadrant_data["teachers_per_1000"]
                    >= avg_teacher
                )
            ),
            (
                (quadrant_data["poverty_absolute"] <= avg_poverty)
                & (
                    quadrant_data["teachers_per_1000"]
                    < avg_teacher
                )
            ),
            (
                (quadrant_data["poverty_absolute"] <= avg_poverty)
                & (
                    quadrant_data["teachers_per_1000"]
                    >= avg_teacher
                )
            )
        ],
        [
            "Higher Poverty / Lower Teacher Availability",
            "Higher Poverty / Higher Teacher Availability",
            "Lower Poverty / Lower Teacher Availability",
            "Lower Poverty / Higher Teacher Availability"
        ],
        default="Unclassified"
    )

    quadrant_colors = {
        "Higher Poverty / Lower Teacher Availability": "#C0392B",
        "Higher Poverty / Higher Teacher Availability": "#E67E22",
        "Lower Poverty / Lower Teacher Availability": "#2166AC",
        "Lower Poverty / Higher Teacher Availability": "#218C74"
    }

    fig9 = px.scatter(
        quadrant_data,
        x="teachers_per_1000",
        y="poverty_absolute",
        color="Priority Group",
        color_discrete_map=quadrant_colors,
        hover_name="district",
        hover_data={
            "state": True,
            "population": ":,.1f",
            "teachers_per_1000": ":.2f",
            "poverty_absolute": ":.2f"
        },
        title=(
            "District Classification by Poverty "
            "and Teacher Availability"
        )
    )

    fig9.update_traces(
        marker=dict(
            size=12,
            opacity=0.9,
            line=dict(
                width=1.2,
                color="#202A35"
            )
        )
    )

    fig9.add_hline(
        y=avg_poverty,
        line_dash="dash",
        line_width=2.5,
        line_color="#202A35",
        annotation_text="Average Poverty",
        annotation_font_color="#202A35"
    )

    fig9.add_vline(
        x=avg_teacher,
        line_dash="dash",
        line_width=2.5,
        line_color="#202A35",
        annotation_text="Average Teacher Availability",
        annotation_font_color="#202A35"
    )

    fig9.update_layout(
        xaxis_title="Teachers per 1,000 Residents",
        yaxis_title="Absolute Poverty Rate (%)",
        legend_title="District Classification"
    )

    show_chart(fig9, "chart_9_priority_quadrant")

    st.markdown(
        """
        **Interpretation:**

        The quadrant chart classifies districts using average
        poverty and teacher availability as thresholds.
        Districts in the higher-poverty/lower-teacher-availability
        group are potential priority areas for further investigation.
        The categories represent relative comparisons within
        the selected district sample.
        """
    )

    # -----------------------------------------------------
    # PRIORITY DISTRICT TABLE
    # -----------------------------------------------------

    st.subheader("Potential Priority Districts")

    priority_table = quadrant_data[
        quadrant_data["Priority Group"]
        == "Higher Poverty / Lower Teacher Availability"
    ][
        [
            "state",
            "district",
            "poverty_absolute",
            "teachers_per_1000"
        ]
    ].sort_values(
        "poverty_absolute",
        ascending=False
    )

    priority_table = priority_table.rename(
        columns={
            "state": "State",
            "district": "District",
            "poverty_absolute": "Absolute Poverty (%)",
            "teachers_per_1000": "Teachers per 1,000 Residents"
        }
    )

    st.dataframe(
        priority_table,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 11. FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "JIE42403 Scientific Visualisation Assignment"
)

st.caption(
    "Household Poverty, Population Distribution and "
    "Teacher Availability Across Malaysian Districts."
)

st.caption(
    "By Arissa Aida Kamilia Binti Aris (s23a0149)"
)

st.caption(
    "Data interpretation should consider differences in "
    "dataset coverage, reporting dates and measurement units."
)
