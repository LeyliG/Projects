'''
Author: Leyli (Aya) Garryyeva

This code performs data pre-processing and feature engineering on GitHub repository data.
 It includes the following steps:
 1. Import necessary libraries.
 2. Load and clean the data.
 3. Remove duplicates and unnecessary columns.
 4. Impute missing months for each repository.
 5. Calculate repository age as of July 2021.
 6. Merge monthly commit data with repository data.
 7. Create time-related features.
 8. Filter data for a 24-month period around the intervention date.
 9. Remove top 1% of repositories by total commits.
 10. Print the total number of repositories left for model fitting.
 
'''

def preprocess_data():
    import pandas as pd 
    import numpy as np
    import datetime as Dt


    # load the data
    # popular repo data from github
    repo_data = pd.read_csv('data_files/gh_popular_repo_data.csv')
    
    # monthly commit data from github
    monthly_commits = pd.read_csv('data_files/gh_monthly_commit_data.csv')
    
    # remove duplicates from monthly_commits
    monthly_commits = monthly_commits.drop_duplicates()
    monthly_commits['month'] = pd.to_datetime(monthly_commits['month'], format='%Y-%m', errors='coerce')
    
    # remove blank_lines, code_lines, comment_lines columns
    monthly_commits = monthly_commits.drop(['blank_lines', 'code_lines', 'comment_lines'], axis=1)
    
    # impute the missing months per repository
    # get the min for all repositories 
    dates['min'] = monthly_commits['month'].min()
    
    # Get max from Frame
    dates['max'] = monthly_commits['month'].max()
    
    # Create MultiIndex with separate Date ranges per Group
    midx = pd.MultiIndex.from_frame(
        dates.apply(
            lambda x: pd.date_range(x['min'], x['max'], freq='MS'), axis=1
        ).explode().reset_index(name='month')[['month', 'repository']]
    )
    
    # Reindex
    monthly_commits = (
        monthly_commits.set_index(['month', 'repository'])
            .reindex(midx, fill_value=0)
            .reset_index()
    )
    
    # check for NA values in monthly_commits
    print("Checking for NAN values: ", monthly_commits.isna().sum())
    
    # get repo AGE as of July 2021  (in months)
    # rename name column to repository
    repo_data = repo_data.rename(columns={'name': 'repository'})
    
    # get the age (in months) of repos as of jun 2020 based on createdAt column
    # Convert the comparison date to a datetime object
    reference_date = pd.to_datetime('2021-07-01')
    
    # Ensure 'createdAt' is in datetime format
    repo_data['createdAt'] = pd.to_datetime(repo_data['createdAt'], errors='coerce')
    
    # Calculate year and month differences separately using direct access to year and month from the reference date
    year_diff = reference_date.year - repo_data['createdAt'].dt.year
    month_diff = reference_date.month - repo_data['createdAt'].dt.month
    
    # Combine the results to get the total difference in months
    repo_data['repo_age_2021'] = (year_diff * 12) + month_diff
    
    # Create TIME features
    # # merge monthly_commits and repo_data with selected columns by name
    df = monthly_commits.merge(
        repo_data[['repository', 'createdAt', 'repo_age_2021', 'mainLanguage', 'commits']], 
        on='repository') 
    
    # convert month from str to datetime
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m', errors='coerce')
    df['createdAt'] = pd.to_datetime(df['createdAt'], errors='coerce')
    
    # get difference between createdAt and month (observed) column in monthly_commits in months
    # Calculate year and month differences separately
    year_diff = df['month'].dt.year - df['createdAt'].dt.year 
    month_diff = df['month'].dt.month - df['createdAt'].dt.month
    
    # Combine the results to get the total difference in months
    df['age_months'] = (year_diff * 12) + month_diff
    
    # Reference dates for calculations
    # Reference date for indexing: Copilot was released on June 29, 2021
    ref_date_12 = pd.to_datetime('2020-07-01')  # Reference for time_12
    ref_date_24 = pd.to_datetime('2019-07-01')  # Reference for time_24
    intervention_date = pd.to_datetime('2021-07-01')  # Intervention date
    
    
    # get month index 
    # Calculate year and month differences separately using direct access to year and month from the reference date
    year_diff = df['month'].dt.year - intervention_date.year
    month_diff = df['month'].dt.month - intervention_date.month
    # Combine the results to get the total difference in months
    df['month_index'] = (year_diff * 12) + month_diff
    
    
    # Calculate time_12 (months since 2020-07-01)
    year_diff_12 = df['month'].dt.year - ref_date_12.year
    month_diff_12 = df['month'].dt.month - ref_date_12.month
    df['time_12'] = (year_diff_12 * 12) + month_diff_12
    
    # Calculate time_24 (months since 2019-07-01)
    year_diff_24 = df['month'].dt.year - ref_date_24.year
    month_diff_24 = df['month'].dt.month - ref_date_24.month
    df['time_24'] = (year_diff_24 * 12) + month_diff_24
    
    # Create intervention column (0 if before 2021-07-01, else 1)
    df['copilot'] = (df['month'] >= intervention_date).astype(int)
    
    # Create time_since_intervention (months since 2021-07-01)
    year_diff_intervention = df['month'].dt.year - intervention_date.year
    month_diff_intervention = df['month'].dt.month - intervention_date.month
    df['time_since_copilot'] = ((year_diff_intervention * 12) + month_diff_intervention).clip(lower=0)
    
    
    # data prep for EDA and modeling: leave only the data for 24 month-period
    filtered_df = df[(df['month_index'] >= -12) & (df['month_index'] <= 12)]
    
    # Remove top 1% of repositories by total commits
    # check which repository is in top 1% of total_commits
    # get the 1% of total_commits
    top_1_percent = filtered_df['total_commits'].quantile(0.99)
    
    # get the repository in top 1% of total_commits
    top_1_percent_repos = filtered_df[filtered_df['total_commits'] > top_1_percent]
    
    # get unique repository in top 1% of total_commits
    top_1_percent_repos['repository'].nunique()
    
    # remove the data for repositories in top_1_percent_repos
    filtered_df = filtered_df[~filtered_df['repository'].isin(top_1_percent_repos['repository'])]
    
    # get total number of repos left in the data
    print("Total projects for fitting the model: ",filtered_df['repository'].nunique())

    return filtered_df
    
    
    
    
    
    
