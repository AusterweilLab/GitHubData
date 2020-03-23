# GitHubData
This gathers the data from a server and:
1. Gets all the push/pull events from 2015
2. Filters the wanted repos by only looking at repos that have at least 2 push/pull events per month
3. Gets the push/pull urls from the files
3b. Also gets the watch/issue/fork events and counts them for the wanted repos as "measures of repo success/popularity"
4. Scrapes the GitHub website using those urls
5. Makes networks of the results between users and repos
6. Calculates network measures
7. Compare the watch/issue/fork events rates to network measures
8. Colorful plots!
