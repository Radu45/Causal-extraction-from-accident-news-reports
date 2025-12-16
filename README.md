# Evolution of road accident causes in the UK (1999–2025)

This repository contains the code and resources used for the project “Evolution of Car Accident Causes in the UK (1999–2025)”, which investigates how reported causes of road accidents have evolved over the last 26 years using unsupervised text mining applied to news articles.

The project combines unstructured news data from "The Guardian" with official structured statistics (STATS19) to study long-term trends in accident causation.

## Project motivation

Official accident statistics provide reliable aggregate information, but often lack contextual details such as weather conditions, behavioral descriptions, or narrative explanations.
News articles, on the other hand, contain rich descriptions but are unstructured and difficult to analyze at scale.

This project addresses the following question:
### How have the reported causal factors of road accidents in the UK evolved from 1999 to 2025, and what insights can be derived from long-term news reporting using unsupervised methods?

Because no labeled dataset exists across multiple decades, the entire pipeline is designed to be fully unsupervised, transparent, and reproducible.

## Methodology overview 

1) Data Collection : 
   - Articles are retrieved using The Guardian Content API
   - Queries are restricted to UK transport and accident-related reporting
   - Articles are collected month-by-month from 1999 to 2025
   - Articles published on the same day(YYYY-MM-DD) are stored in the same JSON files and these JSON files are stored in chronological order

2) Article classification (unsupervised) :
   - A rule-based scoring function assigns relevance scores to articles
   - Scores are computed using weighted phrase categories (e.g., accident descriptions, injuries, emergency response)
   - Articles above a threshold are classified as genuine accident reports
   - No training data or machine learning models are used

3) Causal phrase extraction and trend analysis
   - Accident causes are extracted using predefined phrase lists grouped into categories:
       - Driver-related (driver's fault)
       - Distraction-related
       - Impairment-related
       - Environmental
       - Mechanical causes 
       - Emerging causes
   - Cause frequencies are aggregated across time windows
   - Trends are visualized and analyzed longitudinally
  
## Validation of results
Results are validated against the STATS19 statistic published by the UK government (2015–2024). This comparision highlights:
- Areas of agreement (both statistics agree on the impairment trends)
- Differences between media framing and official reporting
- Strengths and limitations of news-based accident analysis

## Limitations 
- Literal phrase matching may miss semantically equivalent expressions
- Emerging causes, such as EV batteries on fire,  lack stable terminology
- News reporting may emphasize different aspects than official statistics
- Results should be interpreted as media-based trends, not absolute accident causation

# Reproducibility 
- All preprocessing steps are documented
- No randomness or training involved
- The pipeline can be rerun on different time windows or news sources
- Designed for transparency and interpretability
