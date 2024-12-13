'''
Author: Leyli (Aya) Garryyeva

 This code extracts the monthly commit data of the repositories and processes them to generate a CSV file with various metrics.
 It uses the pydriller library to traverse the commits and calculate metrics such as total commits, unique authors, merge commits,
 non-merge commits, mean commit churn, blank lines, code lines, and comment lines. 

 Note: Ensure you have a 'token.txt' file containing your GitHub token in the same directory.

 Output:
  - The results are saved in 'gh_monthly_commit_data.csv'.
'''

import pandas as pd
from pydriller import Repository
from datetime import datetime
import os
import csv
from tqdm import tqdm

# Load gh data files into pandas dataframes
copilot_pr_list = pd.read_excel('./data_files/copilot_repos_prs.xlsx')
copilot_commit_list = pd.read_excel('./data_files/copilot_repos_commits.xlsx')

# get the list of repositories
clean_data = pd.DataFrame(
    pd.concat([copilot_pr_list['Repository'], 
               copilot_commit_list['Repository']]).unique(),
    columns=['name'])

# test on two repos
#clean_data = clean_data.sample(2)

## functions for processing the repositories
def read_github_token(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def count_lines(file_content):
    lines = file_content.split('\n')
    blank_lines = sum(1 for line in lines if line.strip() == '')
    comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
    code_lines = len(lines) - blank_lines - comment_lines
    return blank_lines, code_lines, comment_lines

def process_repositories():
    token_file_path = 'token.txt'
    GITHUB_TOKEN = read_github_token(token_file_path)

    if GITHUB_TOKEN:
        print("GitHub token is set.")
    else:
        print("GitHub token not found. Set GITHUB_TOKEN environment variable.")
        return

    start_date = datetime(2019, 7, 1)
    end_date = datetime(2023, 7, 1)

    #clean_data = pd.read_csv('clean_data.csv')
    output_file = './data_files/gh_monthly_commit_data.csv'
    
    fieldnames = [
        "repository", "month", "total_commits", "unique_authors",
        "merge_commits", "non_merge_commits", "mean_commit_churn",
        "blank_lines", "code_lines", "comment_lines"
    ]

    # Create the CSV file and write the header
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    dataset = []
    row_count = 0

    for repo in tqdm(clean_data['name'], desc="Processing repositories"):
        repo_url = f"https://{GITHUB_TOKEN}:x-oauth-basic@github.com/{repo}.git"
        print(f"Processing {repo_url}")

        monthly_data = {}

        try:
            for commit in Repository(repo_url, since=start_date, to=end_date).traverse_commits():
                commit_month = commit.committer_date.strftime("%Y-%m")

                if commit_month not in monthly_data:
                    monthly_data[commit_month] = {
                        "total_commits": 0, "unique_authors": set(),
                        "merge_commits": 0, "non_merge_commits": 0,
                        "total_churn": 0, "commit_count": 0,
                        "blank_lines": 0, "code_lines": 0, "comment_lines": 0,
                    }

                monthly_data[commit_month]["total_commits"] += 1
                monthly_data[commit_month]["unique_authors"].add(commit.author.name)
                if len(commit.parents) > 1:
                    monthly_data[commit_month]["merge_commits"] += 1
                else:
                    monthly_data[commit_month]["non_merge_commits"] += 1
                
                churn = commit.insertions + commit.deletions
                monthly_data[commit_month]["total_churn"] += churn
                monthly_data[commit_month]["commit_count"] += 1

                for file in commit.modified_files:
                    if file.source_code is not None:
                        blank, code, comment = count_lines(file.source_code)
                        monthly_data[commit_month]["blank_lines"] += blank
                        monthly_data[commit_month]["code_lines"] += code
                        monthly_data[commit_month]["comment_lines"] += comment

        except Exception as e:
            print(f"Failed to process {repo_url}: {e}")
            continue

        for month, data in monthly_data.items():
            row = {
                "repository": repo,
                "month": month,
                "total_commits": data["total_commits"],
                "unique_authors": len(data["unique_authors"]),
                "merge_commits": data["merge_commits"],
                "non_merge_commits": data["non_merge_commits"],
                "mean_commit_churn": (data["total_churn"] / data["commit_count"]) if data["commit_count"] > 0 else 0,
                "blank_lines": data["blank_lines"],
                "code_lines": data["code_lines"],
                "comment_lines": data["comment_lines"],
            }
            dataset.append(row)
            row_count += 1

            if row_count >= 100:
                with open(output_file, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerows(dataset)
                dataset = []
                row_count = 0

    # Write any remaining rows
    if dataset:
        with open(output_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerows(dataset)

if __name__ == "__main__":
    process_repositories()


    
