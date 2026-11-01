# Scientific Visualisation: Household Poverty, Population Distribution and Teacher Availability Across Malaysian Districts

## Project Overview
This project explores household poverty, population distribution, and teacher availability across Malaysian districts using data visualisation techniques.

The project integrates three datasets to identify patterns, compare district-level characteristics, and explore the relationship between poverty levels and education resources.

## Research Objectives
1. Analyse household poverty patterns across Malaysian districts.
2. Examine population distribution and demographic characteristics across Malaysian districts.
3. Identify districts with higher poverty levels and comparatively lower teacher availability.

## Datasets
The project uses three complementary datasets:

- Household Poverty by District
- Population by District
- Teachers by District

The original datasets are retained in the repository root, while processed datasets are stored in the `processed_data/` folder.

## Data Processing
Data preprocessing and validation were conducted using Python in Google Colab. The process included:
- Data inspection and cleaning
- Date and category standardisation
- Dataset aggregation and transformation
- Integration of datasets using state and district
- Feature engineering
- Data validation and CSV export

## Repository Structure
```text
s23a0149_assignment_vs/
├── hh_poverty_district.csv
├── population_district.csv
├── teachers_district.csv
├── processed_data/
│   ├── poverty_processed.csv
│   ├── population_total.csv
│   ├── population_ethnicity.csv
│   ├── population_age.csv
│   ├── teachers_processed.csv
│   ├── integrated_2024.csv
│   └── education_features.csv
├── main.py
└── requirements.txt
```

## Tools and Technologies
- Python
- Pandas
- Google Colab
- GitHub
- Streamlit
- Data Visualisation Libraries

## Data Considerations
The integrated 2024 dataset contains 118 districts with matching records across the three datasets.

The poverty and population datasets use 1 January 2024 records, while the teacher dataset uses 30 June 2024 records. This difference in reporting dates should be considered when interpreting the findings.

The teacher availability indicator is based on the population unit in the source dataset and should be interpreted according to its documented measurement unit.

## Author
Scientific Visualisation Assignment — JIE42403
