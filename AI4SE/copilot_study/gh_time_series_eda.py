'''
Author: Leyli (Aya) Garryyeva

This code is for the EDA of the monthly commit data. 
'''

from gh_time_series_data_prep import preprocess_data
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import datetime as Dt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import statsmodels.formula.api as smf
from pymer4.models import Lmer
import researchpy as rp
import scipy.stats as stats

# Call the function and get the filtered data
filtered_data = preprocess_data()

features_to_plot = [#'total_commits', 
                    'merge_commits', 
                    'non_merge_commits',
                    'unique_authors', 
                    'mean_commit_churn',
                    'blank_lines', 
                    'code_lines', 
                    'comment_lines'
                    ]

# do eda on the number of name of the repo for each language
# Group by 'mainLanguage' and calculate the number of unique 'name' values
repo_count = filtered_df.groupby('mainLanguage')['repository'].nunique().reset_index()

# Plotting
plt.figure(figsize=(10, 6))
bars = plt.bar(repo_count['mainLanguage'], repo_count['repository'])

# Adding labels and title
plt.xlabel('Main Language')
plt.ylabel('Number of Repositories')
plt.title('Number of Repositories per Main Language')

# Adding the number on top of each bar
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height}', ha='center', va='bottom')

# Display the plot
plt.grid(False)
plt.show()


# lineplot for the features
plt.figure(figsize=(16, 12))
for i, feature in enumerate(features_to_plot, 1):
    plt.subplot(7, 2, i)
    sns.lineplot(data=filtered_df,
                 #df[(df['month_index'] >= -12) & (df['month_index'] <= 12)],
                  x='month_index', y=feature)
    plt.axvline(x=0, color='red', linestyle='--', label='Reference Date (2021-07-01)')
    plt.title(f"{feature} by Month Index")
    plt.xlabel("Month Index")
    plt.ylabel(feature)

plt.tight_layout()
plt.show()


###
rp.summary_cont(filtered_df.groupby(["mainLanguage", "copilot"])["total_commits"])

rp.summary_cont(filtered_df.groupby(["mainLanguage", "copilot"])["unique_authors"])

# plot the mean and confidence interval of unique_authors by mainLanguage and intervention
plt.figure(figsize=(12, 6))
sns.lineplot(data=filtered_df, x='mainLanguage', y='unique_authors', hue='copilot', marker='o')
plt.title("Mean Number of Authors by Main Language and Intervention")
plt.xlabel("Main Language")
plt.ylabel("Total Commits")
plt.grid()
#plt.show()


# plot the mean and confidence interval of merge_commits by mainLanguage and intervention
plt.figure(figsize=(12, 6))
sns.lineplot(data=filtered_df, x='mainLanguage', y='merge_commits', hue='copilot', marker='o')
plt.title("Mean Merge Commits by Main Language and Intervention")
plt.xlabel("Main Language")
plt.ylabel("Merge Commits")
plt.grid()
#plt.show()


# plot the mean and confidence interval of non_merge_commits by mainLanguage and intervention
plt.figure(figsize=(12, 6))
sns.lineplot(data=filtered_df, x='mainLanguage', y='non_merge_commits', hue='copilot', marker='o')
plt.title("Mean Non-Merge Commits by Main Language and Intervention")
plt.xlabel("Main Language")
plt.ylabel("Non-Merge Commits")
plt.grid()
#plt.show()

#mean_commit_churn
plt.figure(figsize=(12, 6))
sns.lineplot(data=filtered_df, x='mainLanguage', y='mean_commit_churn', hue='copilot', marker='o')
plt.title("Mean Commit Churn by Main Language and Intervention")
plt.xlabel("Main Language")
plt.ylabel("Mean Commit Churn")
plt.grid()
#plt.show()
# Create a 2x2 grid for the plots
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# Plot the mean and confidence interval of unique_authors by mainLanguage and intervention
sns.lineplot(data=filtered_df, x='mainLanguage', y='unique_authors', hue='copilot', marker='o', ax=axs[0, 0])
axs[0, 0].set_title("Mean Number of Authors by Main Language and Intervention")
axs[0, 0].set_xlabel("Main Language")
axs[0, 0].set_ylabel("Total Commits")
axs[0, 0].grid()

# Plot the mean and confidence interval of merge_commits by mainLanguage and intervention
sns.lineplot(data=filtered_df, x='mainLanguage', y='merge_commits', hue='copilot', marker='o', ax=axs[0, 1])
axs[0, 1].set_title("Mean Merge Commits by Main Language and Intervention")
axs[0, 1].set_xlabel("Main Language")
axs[0, 1].set_ylabel("Merge Commits")
axs[0, 1].grid()

# Plot the mean and confidence interval of non_merge_commits by mainLanguage and intervention
sns.lineplot(data=filtered_df, x='mainLanguage', y='non_merge_commits', hue='copilot', marker='o', ax=axs[1, 0])
axs[1, 0].set_title("Mean Non-Merge Commits by Main Language and Intervention")
axs[1, 0].set_xlabel("Main Language")
axs[1, 0].set_ylabel("Non-Merge Commits")
axs[1, 0].grid()

# Plot the mean and confidence interval of mean_commit_churn by mainLanguage and intervention
sns.lineplot(data=filtered_df, x='mainLanguage', y='mean_commit_churn', hue='copilot', marker='o', ax=axs[1, 1])
axs[1, 1].set_title("Mean Commit Churn by Main Language and Intervention")
axs[1, 1].set_xlabel("Main Language")
axs[1, 1].set_ylabel("Mean Commit Churn")
axs[1, 1].grid()

# Adjust layout
plt.tight_layout()
plt.show()









