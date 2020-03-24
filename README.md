# GitHubData

To reproduce all the data processing, run these scripts in this order:

count_repos.py:
Counts the number of repos
Uses repos_count_scratch/urlfile and repos_count_scratch/urlfile2
Makes repos_count_scratch/repos_count.csv and repos_count_scratch/repos_all.data

scrape_wanted_repos.py:
Gets the data from github
Uses repos_count_scratch/repos_count.csv and repos_count_scratch/repos_all.data
Makes scraped_data/push_json_files.json and scraped_data/pull_json_files.json

filter_wanted_repos.py:
Filter out the wanted repos only, just make a list of them to filter out of the data
Uses repos_count_scratch/repos_count.csv
Makes final_pickles/wanted_repos.data

count_measures.py:
Gets a count of fork, watch, and issue events
Uses final_pickles/wanted_repos.data
Makes tons of files in wanted_measures

count_measures_per_repo.py:
Counts the number of measures per repo
Uses all the files in wanted_measures
Makes final_pickles/measures

get_measures_for_wanted_repos.py:
Gets the wanted files from Vader
Uses final_pickles/wanted_repos.data
Makes wanted_measures/wanted_measures

--

These scripts make the networks and visualize them, along with other plots

make_networks.py:
Makes 4 network pickles, nx graph objects
Uses scraped_data/push_json_files.json and scraped_data/pull_json_files.json
Makes network_pickles/networks1 through 4

plots_and_figures.py:
Visualized the networks and their measures
Uses network_pickles/networks1 through 4
Does not make any files, only shows the plots

--

This makes the df neeed for ML models

make_df.py:
Create df for data to feed into ML model of actions over time
Uses scraped_data files and network_pickles/network2
Makes scratch_pickles/df_rows and final_pickles/df_actions.pkl and final_pickles/components.pkl
