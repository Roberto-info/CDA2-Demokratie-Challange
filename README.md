# CDA2 Democracy Challange

This Repo contains the notebooks to visualize and document our
learnings and findings about the data we'd like to analyze

To work with this repo properly install poetry
https://python-poetry.org/docs/

or with brew: 
brew install poetry 

or with pip
pip install poetry

To set the directory of the venv
- poetry config virtualenvs.in-project true     

Then you are able to initialize:
- poetry init 
- poetry install

To use poetry with the notebooks use:
-  poetry add ipykernel 

To set poetry to be the kernel use:
- poetry run python -m ipykernel install --user --name=poetry-env --display-name "Python (Poetry)"

The Project starts with the eda.ipynb file, the following is contained in this file:
This notebook provides a broad exploratory analysis of all referenda conducted in Switzerland. The focus lies in gaining general insights and examining the dynamics of socially oriented votes in relation to other types of referenda.

1. Import Required Libraries
	•	Imported necessary Python packages to handle data, perform analysis, and create visualizations.
2. Load Dataset
	•	Loaded the complete dataset of Swiss referenda for exploration.
3. Dataset Overview
	•	Provided descriptive information about the dataset: number of votes, time range, types of issues, etc.
4. Prepare Data
	•	Cleaned and formatted the dataset for proper analysis (e.g., handling dates, missing values, or reformatting columns).
5. Basic Statistical Overview
	•	Calculated and visualized basic statistics to give a first impression of trends and distributions.
6. Identify Societally-Oriented Referenda
	•	Defined and detected which referenda were of societal importance using specific criteria or keyword searches.
7. Compare Approval Rates Over Time
	•	Compared how approval rates of societal vs. other referenda evolved across time.
8. Analyze Acceptance Trends for Societal Votes
	•	Investigated the overall trend in public support for socially oriented referenda across years.
9. Examine Cantonal Voting Differences
	•	Analyzed how voting behavior in societal referenda varied between cantons.
10. Relate Political Party Positions to Voting Results
	•	Explored how political party recommendations correlated with the public vote outcomes on these societal issues.

After the eda we did a detailed analysis which has been done in the detailed-eda.ipynb:
1. Import Required Libraries
	•	Imported necessary Python packages for data handling, analysis, and visualization.
2. Prepare Dataset
	•	Loaded and preprocessed the voting data for further analysis.
3. Extraction of Societally-Oriented Referenda
	•	Definition: Established criteria for identifying socially relevant referenda.
	•	Keywords: Used specific keywords to classify referenda as societal.
4. Ranking of Cantons by Liberalism/Conservatism
	•	Developed a ranking of Swiss cantons based on how liberally or conservatively they voted in the selected referenda.
5. Standardization of Dates
	•	Standardized date formats to allow consistent time-based analysis.
6. Subdivision into Periods
	•	Split the timeline into distinct periods to analyze temporal changes in voting behavior.
7. Identification of Yes-Percentages
	•	Extracted and processed the proportion of “Yes” votes for each referendum by canton.
8. Analysis of Changes in Cantonal Voting Over Time
	•	Investigated how cantons’ voting tendencies evolved over different periods.
9. Urban vs. Rural Canton Classification
	•	Differentiated between urban and rural cantons for deeper subgroup comparisons.
10. Contrast Between Liberal and Conservative Parties
	•	Analyzed the ideological contrast between political leanings in cantonal voting behavior.
11. Temporal Development of Polarization
	•	Examined how political or ideological polarization developed over time.
12. Regional Differences and Language Borders
	•	Studied spatial differences in voting, particularly along linguistic borders (German/French/Italian-speaking regions).

The Analyse_Einzelner_Abstimmungen notebook was used to break down and analyze individual votes considered socially relevant.
	•	Computed and compared the average approval rates of referenda in urban vs. rural cantons.
	•	Analyzed the distribution of votes (e.g., histograms, boxplots) to assess the spread and variability within each group.