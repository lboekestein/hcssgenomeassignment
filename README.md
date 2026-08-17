# HCSS Datalab Technical Assignment GENOME
#### Luuk Boekestein | August 17, 2026

## Overview

This repository contains a short technical assignment, working with GENOME (Geopolitical Event News Observatory, Mapping, and Extraction) data from HCSS Datalab. 

The main output of the assignment is a dashboard with two examples of exploring the GENOME data on a "conflict episode" level, which is my proposed additional navigation layer for GENOME. The dashboard can be found publicly here: [link]. More elaborate replications instructions are given below.

## Table of contents
- [Chosen Domain Angle](#chosen-domain-angle)
- [Running Instructions](#running-instructions)
- [Overview of Repository](#overview-of-repository)
- [Challenges and Future Improvements](#challenges-and-future-improvements)


## Chosen Domain Angle

For me, the most interesting aspect of GENOME, as an explicitly actor-focused dataset, is the ability to do data analysis on an actor-to-actor level. Therefore, my immediate instinct was to propose "dyad" as an additional navigation layer for GENOME. However, since this functionality is already somewhat present in the dashboard itself, I decided to focus my attention a bit further, and explore specifically dyads that are part of a conflict.

Thus, my proposed domain angle is to explore the GENOME data on a "conflict episode" level. I think this is interesting especially in light of its promises for conflict prediction, since predicting on an actor-to-actor level has so far not been feasible due to a lack of relevant data, but GENOME could be a first step in this direction. In combination with the fact that GENOME also explicitly codes "lower intensity" events, this makes it a potentially viable dataset for early warning, since as also mentioned in the paper itself (p. 84), actual conflict is usually preceded by lower-intensity interactions, which could thus carry meaningful predictive signal about looming conflict onsets.

Since the GENOME data currently still spans a relatively short time period, training a fully-fledged predictive model was not feasible, but I instead did some basic exploratory data analysis on two specific conflict episodes, namely the 2026 US-Iran War and the 2024 Israeli War in Lebanon. Instead of training a predictive model, I made an attempt at extracting a potential predictive feature from the GENOME data, by aggregating the "intensity" variables of individual events into a proxy measure of "hostility" between two actors over time. I then visualized this measure for the two selected conflict episodes in a dashboard, to evaluate whether this variable carries predictive signal *prior* to the actual conflict onset.

I think this is an interesting question to explore for both methodological and substantive reasons. Methodologically, it is interesting to see whether the GENOME data can be used to construct a meaningful predictive feature for conflict onset. Substantively, it is interesting to see what patterns of hostility can be observed prior to the onset of the two conflict episodes, and whether these patterns are similar or different across the two cases.

## Running instructions

### Requirements

To run the code in this repository Python 3.11 is required.
Furthermore dependencies are listed in the [requirements.txt](requirements.txt) file, and can be installed using pip:

```bash
pip install -r requirements.txt
```

### Replication

The replication consists of two steps. 

The first step is to load, combine and preprocess the raw GENOME data stored in seperate CSV files in the [data/raw/](data/raw/) folder. This is done using the [src/preprocessing.py](src/preprocessing.py) script, which produces the [data/processed/processed_data.csv](data/processed/processed_data.csv) file. This file is also already uploaded to this repository, but to replicate this step run:

```bash
python src/preprocessing.py
```

The second step is to launch the dashboard in which the results are presented. The dashboard is written in the [dashboard.py](dashboard.py) script using Streamlit. It is currently deployed publicly on this link: [link], but can also be hosted locally by running:

```bash
streamlit run dashboard.py
```

## Overview of repository

This repository is structured as follows:

- The `src/` folder contains all scripts used for the assignment:
    - `preprocessing.py`: loading and preprocessing of GENOME data
    - `hostility.py`: script with function to compute the hostility index
    - `episodes.py`: definitions of two selected conflict episodes
    - `theme.py`: brief script to configure HCSS-style theme
- The `data/` folder contains both the raw CSV files (retrieved from the GENOME platform), and the processed data produced by the preprocessing script
- The `assets/` and `.streamlit/` folders contain some basic configurations for the dashboard
- The dashboard itself is written in the `dashboard.py` script
- Finally, requirements are listed in the `requirements.txt` file

## Challenges and future improvements

The biggest challenge when I came up with my idea to use GENOME for actor-to-actor conflict prediction was the limited scope of the current dataset. Applying proper machine learning in the temporal dimension would require a larger sample size, or extending the GENOME data backwards in time. 

Another limitation is the relatively noisy character of the data. Retrieving early warning signal from event data would require a more constant stream of events, as currently the data is heavily skewed towards highly-reported events, in addition to likely suffering from a bias towards Western media reporting, and therefore is too spiky to extract meaningful increases or decreases in a variable such as the hostility measure created here. A future improvement could be to spend more time smoothing the data, or to merge the GENOME data with other relevant data sources (e.g. ACLED or UCDP). 

Initially, my idea was to apply proper change-point techniques to the time series produced by the hostility measure (or to some of the other variables, such as the presence of each of the 4 PLOVER categories), but due to the slightly noisy data in addition to running out of time, I was not able to get this far. However, I think in the future it could be interesting to do more elaborate analysis to see if any informative change-points or distribution shifts can be identified prior to conflict onsets, since it did seem that the GENOME data contains more pre-onset signal that other datasets I have worked with. 

### Reflection on scalability

A few challenges arise when considering the scalability of this domain angle. The first issue is that it is not immediately clear how to define a "conflict episode". Therefore, scaling would require a better definition, or you could simply repeat the same analysis with all dyads that have any conflict-relevant events.

On a technical level, the data is currently retrieved manually by downloading CSV files from the GENOME platform (to avoid hitting API limits when scraping automatically), so scaling this domain angle would require proper data querying. However, this should be rather straightforward using the already present API filters.