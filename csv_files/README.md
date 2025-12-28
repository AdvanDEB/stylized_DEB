# DEB Stylized Facts - CSV Extraction

This directory contains CSV files extracted from the LaTeX document `Material_2.tex`, which contains 1200 DEB (Dynamic Energy Budget) stylized facts organized into 12 thematic sections.

## Generated CSV Files

Each CSV file contains 100 stylized facts from a specific section:

1. **universal_laws_of_biological_organization.csv** (Facts 1-100)
   - Universal Laws of Biological Organization

2. **ecological_physiological_proportions_and_relationships.csv** (Facts 101-200)
   - Ecological-Physiological Proportions and Relationships

3. **temporal_characteristics_of_development_and_growth.csv** (Facts 201-300)
   - Temporal Characteristics of Development and Growth

4. **reproductive_strategy.csv** (Facts 301-400)
   - Reproductive Strategy

5. **metabolism_and_environment.csv** (Facts 401-500)
   - Metabolism and Environment

6. **biological_experiments_and_data_patterns.csv** (Facts 501-600)
   - Biological Experiments and Data Patterns

7. **dynamic_properties_and_equilibrium_states.csv** (Facts 601-700)
   - Dynamic Properties and Equilibrium States

8. **molecular_and_cellular_foundations.csv** (Facts 701-800)
   - Molecular and Cellular Foundations

9. **microbiological_and_parasitological_aspects.csv** (Facts 801-900)
   - Microbiological and Parasitological Aspects

10. **thermoregulation_and_biophysical_constraints.csv** (Facts 901-1000)
    - Thermoregulation and Biophysical Constraints

11. **integrative_aspects_and_emergent_properties.csv** (Facts 1001-1100)
    - Integrative Aspects and Emergent Properties

12. **toxicology_and_ecotoxicology.csv** (Facts 1101-1200)
    - Toxicology and Ecotoxicology

## CSV File Structure

Each CSV file has the following columns:

- **Number**: The unique identifier for each stylized fact (1-1200)
- **DEB Stylized Fact**: The text description of the stylized fact
- **Accuracy**: Empty column for rating accuracy (1-5 scale)
- **I have an explanation**: Empty column for indicating if an explanation can be provided
- **Importance**: Empty column for rating importance (1-5 scale)

## Usage

The empty columns (Accuracy, I have an explanation, Importance) are intended to be filled in by experts evaluating each stylized fact according to the instructions provided in the original LaTeX document:

- **Accuracy**: 1 to 5 scale (1 = completely inaccurate, 5 = completely accurate, 0 = no opinion)
- **I have an explanation**: Yes/No/Empty (Yes = can explain, No = cannot explain, Empty = don't know enough)
- **Importance**: 1 to 5 scale (1 = least important, 5 = most important for understanding DEB theory)

## Extraction Script

The Python script `extract_stylized_facts.py` was used to extract the data from the LaTeX file and generate these CSV files.

## Statistics

- Total sections: 12
- Total stylized facts: 1,200
- Facts per section: 100
- Total CSV lines: 1,212 (including headers)
