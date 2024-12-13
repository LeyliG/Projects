'''
Author: Mostafa Ahmed
A Python script that analyzes GitHub repositories for 
commits containing specific keywords ('copilot', 'chatgpt')
'''

import requests
import csv
import os
import time
from datetime import datetime

GITHUB_TOKEN = '##'
REPOS_FILE = 'repos.csv'
RESULTS_FILE = 'github_commit_results.csv'
ERROR_LOG_FILE = 'commit_error_log.csv'
KEYWORDS = ['copilot', 'chatgpt']
MAX_PAGES = 5                      # Maximum number of pages to check per repository
COOLDOWN_PERIOD = 60    # 1 minute for 403 errors

#Sets up authenticated GitHub API session
def create_session():
    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    return session

#Reads repository list from CSV file
def read_repos_from_csv():
    if not os.path.exists(REPOS_FILE):
        print(f"Error: {REPOS_FILE} not found.")
        return []
    with open(REPOS_FILE, 'r', encoding='utf-8') as csvfile:
        return [row['name'].strip('*') for row in csv.DictReader(csvfile) if 'name' in row and '/' in row['name']]

#Logs errors to a CSV file
def log_error(repo, error_type, error_details):
    with open(ERROR_LOG_FILE, 'a', newline='', encoding='utf-8') as error_file:
        csv.writer(error_file).writerow([repo, error_type, error_details])

#Searches commits in a repository for specific keywords
def search_commits(session, repo):
    url = f"https://api.github.com/repos/{repo}/commits"
    params = {"per_page": 100}
    results = []
    total_requests = 0
    
    for page in range(MAX_PAGES):
        try:
            response = session.get(url, params=params)
            response.raise_for_status()
            total_requests += 1
            
            commits = response.json()
            for commit in commits:
                commit_message = commit['commit']['message'].lower()
                for keyword in KEYWORDS:
                    if keyword in commit_message:
                        results.append([
                            keyword,
                            commit['commit']['message'],
                            repo,
                            commit['html_url'],
                            commit['commit']['author']['date'],
                            commit['commit']['author']['name']
                        ])
                        break

            if 'next' not in response.links:
                break
            
            url = response.links['next']['url']
            
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining < 100:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                sleep_time = max(reset_time - time.time(), 0) + 1
                print(f"Rate limit low. Sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"403 Forbidden error for repo: {repo}. Cooling down...")
                time.sleep(COOLDOWN_PERIOD)
            else:
                print(f"HTTP error {e.response.status_code} for repo: {repo}")
                log_error(repo, f'HTTP error {e.response.status_code}', str(e))
            break
        except requests.exceptions.RequestException as e:
            print(f"Error for repo {repo}: {str(e)}")
            log_error(repo, 'Request Exception', str(e))
            break
    
    return results, total_requests

#Writes search results to a CSV file
def write_results(results):
    with open(RESULTS_FILE, 'a', newline='', encoding='utf-8') as file:
        csv.writer(file).writerows(results)

#Main function that searches commits in all repositories
def search_github_commits():
    repos = read_repos_from_csv()
    print(f"Found {len(repos)} repositories to process.")

    with open(RESULTS_FILE, 'w', newline='', encoding='utf-8') as file:
        csv.writer(file).writerow(['query', 'Commit Message', 'Repository', 'URL', 'Date', 'Author'])

    with open(ERROR_LOG_FILE, 'w', newline='', encoding='utf-8') as error_file:
        csv.writer(error_file).writerow(['Repository', 'Error Type', 'Error Details'])

    session = create_session()
    total_requests = 0
    processed_repos = 0

    for i, repo in enumerate(repos):
        print(f"Processing repository {i+1}/{len(repos)}: {repo}")
        results, requests = search_commits(session, repo)
        if results:
            write_results(results)
            processed_repos += 1
        total_requests += requests
        print(f"Processed {repo}. Total API requests: {total_requests}")

    print(f"Commit search results saved to '{RESULTS_FILE}'.")
    print(f"Error log saved to '{ERROR_LOG_FILE}'.")
    print(f"Total API requests made: {total_requests}")
    print(f"Total repositories processed successfully: {processed_repos}")
    print(f"Total repositories with errors: {len(repos) - processed_repos}")

if __name__ == "__main__":
    search_github_commits()
