
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
    page_icon="📊",
    layout="wide"
)

DATA_DIR = Path(__file__).parent / "processed_data"

# =========================================================
# 2. LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    poverty = pd.read_csv(DATA_DIR / "poverty_processed.csv")
    population = pd.read_csv(DATA_DIR / "population_total.csv")
    ethnicity = pd.read_csv(DATA_DIR / "population_ethnicity.csv")
    age = pd.read_csv(DATA_DIR / "population_age.csv")
    teachers = pd.read_csv(DATA_DIR / "teachers_processed.csv")
    integrated = pd.read_csv(DATA_DIR / "integrated_2024.csv")
    education = pd.read_csv(DATA_DIR / "education_features.csv")

    datasets = [
        poverty, population, ethnicity, age,
        teachers, integrated, education
    ]

    for df in datasets:
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        if "year" not in df.columns and "date" in df.columns:
            df["year"] = df["date"].dt.year

    return (
        poverty, population, ethnicity, age,
        teachers, integrated, education
    )


try:
    (
        poverty, population, ethnicity, age,
        teachers, integrated, education
    ) = load_data()

except Exception as e:
    st.error(f"Unable to load datasets: {e}")
    st.info(
        "Please ensure all seven CSV files are inside "
        "the processed_data folder."
    )
    st.stop()


# =========================================================
# 3. GENERAL SETTINGS
# =========================================================

st.title("Malaysian District Data Visualisation")
st.caption(
    "Exploring Household Poverty, Population Distribution "
    "and Teacher Availability Across Malaysian Districts"
)

st.markdown("---")

# Sidebar navigation
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Research Objective",
    [
        "1. Household Poverty Patterns",
        "2. Population Distribution",
        "3. Poverty & Teacher Availability"
    ]
)

# State filter
available_states = sorted(
    integrated["state"].dropna().unique().tolist()
)

selected_states = st.sidebar.multiselect(
    "Filter by State",
    available_states,
    default=available_states
)


def filter_states(df):
    if "state" in df.columns and selected_states:
        return df[df["state"].isin(selected_states)].copy()
    return df.iloc[0:0].copy()


# =========================================================
# 4. PAGE 1: HOUSEHOLD POVERTY PATTERNS
# =========================================================

if page == "1. Household Poverty Patterns":

    st.header("Objective 1: Analyse Household Poverty Patterns")

    st.markdown(
        """
        This objective examines household poverty patterns across
        Malaysian districts by comparing absolute and relative
        poverty rates and identifying districts with higher
        poverty levels.
        """
    )

    poverty_filtered = filter_states(poverty)

    poverty_2024 = poverty_filtered[
        poverty_filtered["year"] == 2024
    ].copy()

    if poverty_2024.empty:
        st.warning("No 2024 poverty data available for the selected states.")
        st.stop()

    # Summary box
    avg_absolute = poverty_2024["poverty_absolute"].mean()
    avg_relative = poverty_2024["poverty_relative"].mean()

    st.info(
        f"""
        **Summary of Household Poverty (2024)**

        - Average absolute poverty: **{avg_absolute:.2f}%**
        - Average relative poverty: **{avg_relative:.2f}%**
        - Districts analysed: **{poverty_2024['district'].nunique()}**
        """
    )

    # -----------------------------------------------------
    # VISUALISATION 1: POVERTY TREND
    # -----------------------------------------------------

    st.subheader("1. Household Poverty Trend (2019–2024)")

    # Use only districts with records in all three years
    years_required = {2019, 2022, 2024}

    trend_data = poverty_filtered[
        poverty_filtered["year"].isin(years_required)
    ].copy()

    common_districts = (
        trend_data.groupby("district")["year"]
        .nunique()
    )

    common_districts = common_districts[
        common_districts == len(years_required)
    ].index

    trend_data = trend_data[
        trend_data["district"].isin(common_districts)
    ]

    trend_summary = (
        trend_data.groupby("year")[
            ["poverty_absolute", "poverty_relative"]
        ]
        .mean()
        .reset_index()
        .melt(
            id_vars="year",
            var_name="Poverty Type",
            value_name="Average Rate (%)"
        )
    )

    trend_summary["Poverty Type"] = (
        trend_summary["Poverty Type"]
        .map({
            "poverty_absolute": "Absolute Poverty",
            "poverty_relative": "Relative Poverty"
        })
    )

    fig1 = px.line(
        trend_summary,
        x="year",
        y="Average Rate (%)",
        color="Poverty Type",
        markers=True,
        title="Average Poverty Rate Across Consistently Matched Districts",
        labels={
            "year": "Year",
            "Average Rate (%)": "Average Poverty Rate (%)"
        }
    )

    fig1.update_layout(hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown(
        """
        **Interpretation:**

        This line chart compares changes in average absolute and
        relative poverty rates over time. Using districts with
        records in all three years helps reduce the effect of
        changing district coverage on the comparison.
        """
    )

    # -----------------------------------------------------
    # VISUALISATION 2: TOP 10 POVERTY DISTRICTS
    # -----------------------------------------------------

    st.subheader("2. Top 10 Districts by Absolute Poverty (2024)")

    top_poverty = (
        poverty_2024.nlargest(10, "poverty_absolute")
        .sort_values("poverty_absolute", ascending=True)
    )

    fig2 = px.bar(
        top_poverty,
        x="poverty_absolute",
        y="district",
        orientation="h",
        color="poverty_absolute",
        color_continuous_scale="Reds",
        text="poverty_absolute",
        title="Top 10 Districts with Highest Absolute Poverty Rates",
        labels={
            "poverty_absolute": "Absolute Poverty Rate (%)",
            "district": "District"
        }
    )

    fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig2.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        """
        **Interpretation:**

        This ranking highlights the ten districts with the highest
        absolute poverty rates in 2024. Districts at the top of the
        ranking may warrant further investigation into local
        socioeconomic conditions.
        """
    )

    # -----------------------------------------------------
    # VISUALISATION 3: ABSOLUTE VS RELATIVE POVERTY
    # -----------------------------------------------------

    st.subheader("3. Absolute vs Relative Poverty (2024)")

    fig3 = px.scatter(
        poverty_2024,
        x="poverty_absolute",
        y="poverty_relative",
        hover_name="district",
        color="state",
        size="poverty_absolute",
        size_max=18,
        title="Relationship Between Absolute and Relative Poverty",
        labels={
            "poverty_absolute": "Absolute Poverty Rate (%)",
            "poverty_relative": "Relative Poverty Rate (%)"
        }
    )

    fig3.update_layout(legend_title="State")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(
        """
        **Interpretation:**

        The scatter plot compares absolute and relative poverty
        rates across districts. Points further towards the upper
        right indicate districts with higher values for both
        poverty measures. The chart helps identify patterns and
        unusual observations.
        """
    )


# =========================================================
# 5. PAGE 2: POPULATION DISTRIBUTION
# =========================================================

elif page == "2. Population Distribution":

    st.header("Objective 2: Examine Population Distribution")

    st.markdown(
        """
        This objective examines population trends and demographic
        characteristics across Malaysian districts, focusing on
        population size, ethnic composition and age distribution.
        """
    )

    population_filtered = filter_states(population)
    ethnicity_filtered = filter_states(ethnicity)
    age_filtered = filter_states(age)

    population_2024 = population_filtered[
        population_filtered["year"] == 2024
    ]

    ethnicity_2024 = ethnicity_filtered[
        ethnicity_filtered["year"] == 2024
    ]

    age_2024 = age_filtered[
        age_filtered["year"] == 2024
    ]

    if population_2024.empty:
        st.warning("No 2024 population data available for the selected states.")
        st.stop()

    total_population = population_2024["population"].sum()

    st.info(
        f"""
        **Summary of Population Distribution (2024)**

        - Total reported population: **{total_population:,.1f}**
        - Districts analysed: **{population_2024['district'].nunique()}**
        - Ethnicity categories: **{ethnicity_2024['ethnicity'].nunique()}**
        - Age groups: **{age_2024['age'].nunique()}**

        *Population values are displayed in the source dataset's
        reported unit.*
        """
    )

    # -----------------------------------------------------
    # VISUALISATION 4: POPULATION TREND
    # -----------------------------------------------------

    st.subheader("1. Population Trend (2020–2026)")

    population_trend = (
        population_filtered.groupby("year")
        .agg(
            total_population=("population", "sum"),
            district_count=("district", "nunique")
        )
        .reset_index()
        .sort_values("year")
    )

    fig4 = px.line(
        population_trend,
        x="year",
        y="total_population",
        markers=True,
        title="Total Reported Population by Year",
        labels={
            "year": "Year",
            "total_population": "Total Population (Source Unit)"
        }
    )

    fig4.update_traces(
        hovertemplate="Year: %{x}<br>Population: %{y:,.1f}<extra></extra>"
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.caption(
        "Note: The number of districts covered changes between some "
        "years. Refer to the district coverage when interpreting the trend."
    )

    st.markdown(
        """
        **Interpretation:**

        This line chart illustrates changes in the total reported
        population from 2020 to 2026. Changes in district coverage
        should also be considered when comparing yearly totals.
        """
    )

    # -----------------------------------------------------
    # VISUALISATION 5: ETHNICITY DISTRIBUTION
    # -----------------------------------------------------

    st.subheader("2. Population by Ethnicity (2024)")

    ethnicity_summary = (
        ethnicity_2024.groupby("ethnicity")["population"]
        .sum()
        .reset_index()
        .sort_values("population", ascending=True)
    )

    ethnicity_summary["percentage"] = (
        ethnicity_summary["population"]
        / ethnicity_summary["population"].sum()
        * 100
    )

    fig5 = px.bar(
        ethnicity_summary,
        x="population",
        y="ethnicity",
        orientation="h",
        color="population",
        color_continuous_scale="Teal",
        text="percentage",
        title="Population Distribution by Ethnic Group",
        labels={
            "population": "Population (Source Unit)",
            "ethnicity": "Ethnic Group"
        }
    )

    fig5.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig5.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig5, use_container_width=True)

    st.markdown(
        """
        **Interpretation:**

        This horizontal bar chart compares the population size
        of each ethnic group. The percentage labels show each
        group's contribution to the total represented in the
        selected districts.
        """
    )

    # -----------------------------------------------------
    # VISUALISATION 6: AGE DISTRIBUTION
    # -----------------------------------------------------

    st.subheader("3. Population by Age Group (2024)")

    age_summary = (
        age_2024.groupby("age")["population"]
        .sum()
        .reset_index()
    )

    age_order = [
        "0-4", "5-9", "10-14", "15-19", "20-24",
        "25-29", "30-34", "35-39", "40-44", "45-49",
        "50-54", "55-59", "60-64", "65-69", "70-74",
        "75-79", "80-84", "85+"
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
        color="population",
        color_continuous_scale="Blues",
        title="Population Distribution Across Age Groups",
        labels={
            "age": "Age Group",
            "population": "Population (Source Unit)"
        }
    )

    fig6.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig6, use_container_width=True)

    st.markdown(
        """
        **Interpretation:**

        This column chart illustrates the distribution of
        population across different age groups. It helps identify
        age groups with larger population representation and
        provides insight into the demographic structure.
        """
    )


# =========================================================
# 6. PAGE 3: POVERTY AND TEACHER AVAILABILITY
# =========================================================

elif page == "3. Poverty & Teacher Availability":

    st.header("Objective 3: Identify Districts with Higher Poverty and Lower Teacher Availability")

    st.markdown(
        """
        This objective explores districts with higher poverty rates
        and comparatively lower teacher availability. It compares
        poverty indicators with teacher availability to identify
        districts that may warrant further investigation.
        """
    )

    education_filtered = filter_states(education)

    education_2024 = education_filtered[
        education_filtered["year"] == 2024
    ].copy()

    if education_2024.empty:
        st.warning("No integrated 2024 data available for the selected states.")
        st.stop()

    avg_poverty = education_2024["poverty_absolute"].mean()
    avg_teacher = education_2024["teachers_per_1000"].mean()

    priority_count = len(
        education_2024[
            (education_2024["poverty_absolute"] > avg_poverty)
            & (education_2024["teachers_per_1000"] < avg_teacher)
        ]
    )

    st.info(
        f"""
        **Summary of Poverty and Teacher Availability (2024)**

        - Districts analysed: **{len(education_2024)}**
        - Average absolute poverty: **{avg_poverty:.2f}%**
        - Average teacher availability indicator: **{avg_teacher:.2f}**
        - Districts above average poverty and below average teacher
          availability: **{priority_count}**

        *Teacher availability values are provisional and depend on
        confirmation of the population measurement unit.*
        """
    )

    # -----------------------------------------------------
    # VISUALISATION 7: POVERTY VS TEACHER AVAILABILITY
    # -----------------------------------------------------

    st.subheader("1. Poverty vs Teacher Availability")

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
        title="Relationship Between Poverty and Teacher Availability",
        labels={
            "teachers_per_1000": "Teacher Availability Indicator (Provisional)",
            "poverty_absolute": "Absolute Poverty Rate (%)"
        }
    )

    fig7.add_hline(
        y=avg_poverty,
        line_dash="dash",
        annotation_text="Average Poverty"
    )

    fig7.add_vline(
        x=avg_teacher,
        line_dash="dash",
        annotation_text="Average Teacher Indicator"
    )

    st.plotly_chart(fig7, use_container_width=True)

    st.markdown(
        """
        **Interpretation:**

        Districts in the upper-left quadrant have above-average
        absolute poverty and below-average teacher availability
        indicators within the selected sample. These districts
        may deserve further investigation. The chart does not
        establish a causal relationship or prove a teacher shortage.
        """
    )

    # -----------------------------------------------------
    # VISUALISATION 8: LOWEST TEACHER AVAILABILITY
    # -----------------------------------------------------

    st.subheader("2. 10 Districts with Lowest Teacher Availability")

    lowest_teacher = (
        education_2024.nsmallest(10, "teachers_per_1000")
        .sort_values("teachers_per_1000", ascending=True)
    )

    fig8 = px.bar(
        lowest_teacher,
        x="teachers_per_1000",
        y="district",
        orientation="h",
        color="teachers_per_1000",
        color_continuous_scale="Oranges",
        text="teachers_per_1000",
        title="Districts with the Lowest Teacher Availability Indicator",
        labels={
            "teachers_per_1000": "Teacher Availability Indicator (Provisional)",
            "district": "District"
        }
    )

    fig8.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig8.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig8, use_container_width=True)

    st.markdown(
        """
        **Interpretation:**

        This ranking identifies districts with the lowest calculated
        teacher availability indicator. It provides a comparison
        across districts but should not be interpreted as a direct
        measure of teaching quality or staffing adequacy.
        """
    )

    # -----------------------------------------------------
    # VISUALISATION 9: DISTRICT PRIORITY QUADRANT
    # -----------------------------------------------------

    st.subheader("3. District Priority Quadrant Analysis")

    quadrant_data = education_2024.copy()

    quadrant_data["Priority Group"] = np.select(
        [
            (quadrant_data["poverty_absolute"] > avg_poverty)
            & (quadrant_data["teachers_per_1000"] < avg_teacher),

            (quadrant_data["poverty_absolute"] > avg_poverty)
            & (quadrant_data["teachers_per_1000"] >= avg_teacher),

            (quadrant_data["poverty_absolute"] <= avg_poverty)
            & (quadrant_data["teachers_per_1000"] < avg_teacher),

            (quadrant_data["poverty_absolute"] <= avg_poverty)
            & (quadrant_data["teachers_per_1000"] >= avg_teacher)
        ],
        [
            "Higher Poverty / Lower Teacher Indicator",
            "Higher Poverty / Higher Teacher Indicator",
            "Lower Poverty / Lower Teacher Indicator",
            "Lower Poverty / Higher Teacher Indicator"
        ],
        default="Unclassified"
    )

    fig9 = px.scatter(
        quadrant_data,
        x="teachers_per_1000",
        y="poverty_absolute",
        color="Priority Group",
        hover_name="district",
        hover_data=["state", "population"],
        title="District Classification by Poverty and Teacher Availability",
        labels={
            "teachers_per_1000": "Teacher Availability Indicator (Provisional)",
            "poverty_absolute": "Absolute Poverty Rate (%)"
        }
    )

    fig9.add_hline(
        y=avg_poverty,
        line_dash="dash",
        line_color="gray"
    )

    fig9.add_vline(
        x=avg_teacher,
        line_dash="dash",
        line_color="gray"
    )

    fig9.update_layout(
        legend_title="District Category"
    )

    st.plotly_chart(fig9, use_container_width=True)

    st.markdown(
        """
        **Interpretation:**

        The quadrant analysis classifies districts using the
        average absolute poverty rate and average teacher
        availability indicator as comparison thresholds.

        Districts in the higher-poverty/lower-teacher-indicator
        quadrant are potential priority areas for further
        investigation. The classification is relative to the
        districts included in the analysis.
        """
    )

    # Display priority district table
    st.subheader("Potential Priority Districts")

    priority_table = quadrant_data[
        quadrant_data["Priority Group"]
        == "Higher Poverty / Lower Teacher Indicator"
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
            "teachers_per_1000": "Teacher Indicator (Provisional)"
        }
    )

    st.dataframe(
        priority_table,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 7. FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "JIE42403 Scientific Visualisation Assignment | "
    "Household Poverty, Population Distribution and "
    "Teacher Availability Across Malaysian Districts"
)

st.caption(
    "Data interpretation should consider differences in "
    "dataset coverage, reporting dates and measurement units."
)
