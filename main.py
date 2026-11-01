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
