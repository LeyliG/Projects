"""
Author: Aya Garryyeva

This script processes GitHub repository data from multiple CSV files, filters the data based on specific criteria, 
and extracts the top 50th percentile of repositories based on stargazers count. The final filtered data is saved 
to a CSV file.

Steps:
1. Load GitHub repository data from CSV files into pandas DataFrames.
2. Merge all the datasets into a single DataFrame.
3. Filter the data based on various conditions such as homepage URL, repository status, creation and last commit dates, 
    repository name, default branch, and number of contributors.
4. Identify the top 50th percentile of repositories based on stargazers count for each programming language.
5. Remove redundant features that have a single unique value across all rows.
6. Save the final filtered data to a CSV file.

Output:
- A CSV file named 'gh_popular_repo_data.csv' containing the filtered repository data.
"""

import pandas as pd
# Load ghs data files into pandas dataframes
c_plus_data = pd.read_csv('./data_files/ghs_c_plus_plus.csv').set_index('id')
c_sharp_data = pd.read_csv('./data_files/ghs_c_sharp.csv').set_index('id')
go_data = pd.read_csv('./data_files/ghs_go.csv').set_index('id')
java_data = pd.read_csv('./data_files/ghs_java.csv').set_index('id')
python_data = pd.read_csv('./data_files/ghs_python.csv').set_index('id')
ruby_data = pd.read_csv('./data_files/ghs_ruby.csv').set_index('id')
typescript_data = pd.read_csv('./data_files/ghs_typescript.csv').set_index('id')
javascript_data = pd.read_csv('./data_files/ghs_javascript.csv').set_index('id')

# Merge all the datasets into one dataset
all_data = pd.concat([c_plus_data, c_sharp_data, go_data, java_data, 
                      python_data, ruby_data, typescript_data, javascript_data])

# print the number of rows in the dataset
print("Total number of repositories in the original GHS data: ", all_data.shape[0])

#  Filter data based on selected criteria
#valid_licenses = {'Apache License 2.0', 'MIT License', 'Other'}
comp_names = {'microsoft', 
              'github', #'github-education-resources', 'githubtraining',
              'google',  'gemini-testing', #'GoogleChromeLabs' #'google-ai-edge', 'google-research',
              'facebook', 'langchain',
              'aws', 'amazon', #awslabs, amazonwebservices
              'jetbrains', 'vscode'              
              }
clean_data = all_data.copy()

# filter the data based on the following conditions
  # Filter for defaultBranch
clean_data = clean_data[
    #(clean_data['license'].isin(valid_licenses)) &  
    (~clean_data['homepage'].str.contains('youtube.com', na=False)) &  
    # Filter out instances where isArchived, isDisabled, or isLocked are True
    (~(clean_data['isArchived'] | clean_data['isDisabled'] | clean_data['isLocked'])) &
    (pd.to_datetime(clean_data['createdAt']) <= pd.to_datetime('2020-06-30')) &  
    (pd.to_datetime(clean_data['lastCommit']) >= pd.to_datetime('2022-07-31')) &      
    (~clean_data['name'].str.lower().str.startswith(tuple(comp_names), na=False))& 
    (clean_data['defaultBranch'].isin(['main', 'master']))  &
    (clean_data['contributors'] > 10)
] # 20569

print("Total number of repositories after filtering the data: " ,clean_data.shape[0])


# Identify top repo cutoff values based on watchers, stargazers, and forks for each language
top_n_percentile_repos = clean_data.groupby('mainLanguage').apply(
    lambda x: x[
        #(x['watchers'] >= x['watchers'].quantile(0.5)) &
        (x['stargazers'] >= x['stargazers'].quantile(0.5)) 
        #(x['forks'] >= x['forks'].quantile(0.5)) &
        #(x['totalPullRequests'] >= x['totalPullRequests'].quantile(0.5))
    ]
).reset_index(drop=True)

# Filter out the top 50% of repos: 
clean_data = clean_data[clean_data['name'].isin(top_n_percentile_repos['name'])]

# Remove redundant features that only have a single value across all rows
redundant_features = [col for col in clean_data.columns if clean_data[col].nunique() == 1]
clean_data = clean_data.drop(columns=redundant_features)


print("Total number of repositories after extracting top 50-th percentile: " ,clean_data.shape[0]) # 10290

# write full popular repo data to csv
clean_data.to_csv('./data_files/gh_popular_repo_data.csv', index=False)

























