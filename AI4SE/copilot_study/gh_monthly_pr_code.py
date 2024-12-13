"""
Author: Leyli (Aya) Garryyeva

This script processes GitHub repositories to collect monthly data on issues and pull requests.
It generates a CSV file containing the following information for each repository and month:
  - Number of issues opened
  - Number of issues closed
  - Number of pull requests (PRs) opened
  - Number of PRs closed
  - Mean latency for PRs
  - Mean latency for issues
  - Number of tests executed per build (placeholder values)

Note: Ensure you have a 'token.txt' file containing your GitHub token in the same directory.

Output:
- gh_monthly_pr_data_.csv

"""


import pandas as pd
from datetime import datetime, timezone
import csv
from tqdm import tqdm
from github import Github
from statistics import mean
import logging
import sys


# Load gh data files into pandas dataframes
copilot_pr_list = pd.read_excel('./data_files/copilot_repos_prs.xlsx')
copilot_commit_list = pd.read_excel('./data_files/copilot_repos_commits.xlsx')

# get the list of repositories
clean_data = pd.DataFrame(
    pd.concat([copilot_pr_list['Repository'], 
               copilot_commit_list['Repository']]).unique(),
    columns=['name'])

# test on two repos
#clean_data = clean_data.sample(21)


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_github_token(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        logging.error(f"Token file not found: {file_path}")
        return None

def process_repositories():
    token_file_path = 'token.txt'
    GITHUB_TOKEN = read_github_token(token_file_path)

    if GITHUB_TOKEN:
        print("GitHub token is set.")
    else:
        print("GitHub token not found. Set GITHUB_TOKEN environment variable.")
        return

    start_date = datetime(2019, 7, 1, tzinfo=timezone.utc)
    end_date = datetime(2023, 7, 1, tzinfo=timezone.utc)

    output_file = './data_files/gh_monthly_pr_data_.csv'
    
    fieldnames = [
        "repository", "month", "issues_opened", "issues_closed", 
        "prs_opened", "prs_closed", "mean_pr_latency", 
        "mean_issue_latency", "tests_per_build"
    ]

    # Create the CSV file and write the header
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    dataset = []
    row_count = 0

    g = Github(GITHUB_TOKEN)

    for repo in tqdm(clean_data['name'], desc="Processing repositories"):
        logging.info(f"Processing {repo}")

        monthly_data = {}

        try:
            github_repo = g.get_repo(repo)
            logging.info(f"Successfully accessed repo: {repo}")

            # Process issues and pull requests
            issues_count = 0
            for issue in github_repo.get_issues(state='all', since=start_date):
                issues_count += 1
                issue_created = issue.created_at.replace(tzinfo=timezone.utc)
                issue_month = issue_created.strftime("%Y-%m")
                if issue_month not in monthly_data:
                    monthly_data[issue_month] = {
                        "issues_opened": 0, "issues_closed": 0,
                        "prs_opened": 0, "prs_closed": 0,
                        "pr_latencies": [], "issue_latencies": [],
                        "tests_executed": 0, "build_count": 0
                    }

                monthly_data[issue_month]["issues_opened"] += 1
                if issue.closed_at:
                    issue_closed = issue.closed_at.replace(tzinfo=timezone.utc)
                    if issue_closed <= end_date:
                        closed_month = issue_closed.strftime("%Y-%m")
                        if closed_month not in monthly_data:
                            monthly_data[closed_month] = {
                                "issues_opened": 0, "issues_closed": 0,
                                "prs_opened": 0, "prs_closed": 0,
                                "pr_latencies": [], "issue_latencies": [],
                                "tests_executed": 0, "build_count": 0
                            }
                        monthly_data[closed_month]["issues_closed"] += 1
                        latency = (issue_closed - issue_created).days
                        monthly_data[closed_month]["issue_latencies"].append(latency)

                if issue.pull_request:
                    pr = issue.as_pull_request()
                    pr_created = pr.created_at.replace(tzinfo=timezone.utc)
                    pr_month = pr_created.strftime("%Y-%m")
                    monthly_data[pr_month]["prs_opened"] += 1
                    if pr.closed_at:
                        pr_closed = pr.closed_at.replace(tzinfo=timezone.utc)
                        if pr_closed <= end_date:
                            closed_month = pr_closed.strftime("%Y-%m")
                            if closed_month not in monthly_data:
                                monthly_data[closed_month] = {
                                    "issues_opened": 0, "issues_closed": 0,
                                    "prs_opened": 0, "prs_closed": 0,
                                    "pr_latencies": [], "issue_latencies": [],
                                    "tests_executed": 0, "build_count": 0
                                }
                            monthly_data[closed_month]["prs_closed"] += 1
                            latency = (pr_closed - pr_created).days
                            monthly_data[closed_month]["pr_latencies"].append(latency)

            logging.info(f"Processed {issues_count} issues for {repo}")

            # Process builds and tests (this is a placeholder, as actual build data might require additional API calls)
            for month in monthly_data:
                monthly_data[month]["tests_executed"] = 0  # Placeholder value
                monthly_data[month]["build_count"] = 0  # Placeholder value

            logging.info(f"Completed processing {repo}")

        except Exception as e:
            logging.error(f"Failed to process {repo}: {str(e)}")
            continue

        for month, data in monthly_data.items():
            row = {
                "repository": repo,
                "month": month,
                "issues_opened": data["issues_opened"],
                "issues_closed": data["issues_closed"],
                "prs_opened": data["prs_opened"],
                "prs_closed": data["prs_closed"],
                "mean_pr_latency": mean(data["pr_latencies"]) if data["pr_latencies"] else 0,
                "mean_issue_latency": mean(data["issue_latencies"]) if data["issue_latencies"] else 0,
                "tests_per_build": (data["tests_executed"] / data["build_count"]) if data["build_count"] > 0 else 0
            }
            dataset.append(row)
            row_count += 1

            if row_count >= 100:
                with open(output_file, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerows(dataset)
                logging.info(f"Wrote {row_count} rows to {output_file}")
                dataset = []
                row_count = 0

    # Write any remaining rows
    if dataset:
        with open(output_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerows(dataset)
        logging.info(f"Wrote final {len(dataset)} rows to {output_file}")

    logging.info("Script completed.")

if __name__ == "__main__":
    process_repositories()


    
