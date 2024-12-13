'''
Author: Mostafa Ahmend
A Python script that searches GitHub repositories for 
issues and pull requests containing AI-related keywords ('copilot', 'chatgpt')
'''

import requests
import csv
import os
import time
import re
from datetime import datetime

GITHUB_TOKEN = '##'
GITHUB_API_URL = "https://api.github.com/search/issues"
REPOS_FILE = 'repos.csv'
RESULTS_FILE = 'github_search_results.csv'
ERROR_LOG_FILE = 'error_log.csv'
CONTEXT_CHARS = 100
INITIAL_DELAY = 2  # seconds
MAX_RETRIES = 3

def create_session():
    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    return session

def read_repos_from_csv():
    if not os.path.exists(REPOS_FILE):
        print(f"Error: {REPOS_FILE} not found.")
        return []
    repositories = []
    with open(REPOS_FILE, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'name' in row and row['name'].strip():
                repo = row['name'].strip()
                if repo.startswith('**'):
                    repo = repo.strip('*')
                if '/' in repo:
                    repositories.append(repo)
    return repositories

def extract_context(text, phrase):
    pattern = re.compile(f"(.{{0,{CONTEXT_CHARS}}}){re.escape(phrase)}(.{{0,{CONTEXT_CHARS}}})", re.IGNORECASE | re.DOTALL)
    match = pattern.search(text)
    if match:
        before, after = match.groups()
        return f"{before}{phrase}{after}"
    return ""

def search_repository(session, repo):
    query = f"copilot OR chatgpt repo:{repo}"
    params = {
        "q": query,
        "type": "issue",
        "sort": "created",
        "order": "asc",
        "per_page": 100
    }
    
    results = []
    seen_issues = set()
    page = 1
    total_requests = 0
    retry_count = 0
    delay = INITIAL_DELAY
    
    while True:
        try:
            response = session.get(GITHUB_API_URL, params=params)
            response.raise_for_status()
            total_requests += 1
            
            if response.status_code == 200:
                issues = response.json().get("items", [])
                for issue in issues:
                    if issue['id'] not in seen_issues:
                        seen_issues.add(issue['id'])
                        body = issue['body'] or ""
                        for phrase in ['copilot', 'chatgpt']:
                            context = extract_context(body, phrase)
                            if context:
                                results.append([
                                    phrase,
                                    issue['title'],
                                    issue['state'],
                                    repo,
                                    issue['html_url'],
                                    context
                                ])
                if 'Link' not in response.headers:
                    break
                page += 1
                params['page'] = page
            
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            print(f"Rate limit: {remaining} remaining, resets at {datetime.fromtimestamp(reset_time)}")
            
            if remaining < 5:
                sleep_time = max(reset_time - time.time(), 0) + 1
                print(f"Rate limit low. Sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
            else:
                time.sleep(delay)
            
            retry_count = 0
            delay = INITIAL_DELAY
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    print(f"Max retries reached for repo: {repo}. Skipping...")
                    with open(ERROR_LOG_FILE, 'a', newline='', encoding='utf-8') as error_file:
                        error_writer = csv.writer(error_file)
                        error_writer.writerow([repo, '403 Forbidden (Max Retries)', str(e)])
                    break
                print(f"403 Forbidden error for repo: {repo}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"HTTP error {e.response.status_code} for repo: {repo}")
                with open(ERROR_LOG_FILE, 'a', newline='', encoding='utf-8') as error_file:
                    error_writer = csv.writer(error_file)
                    error_writer.writerow([repo, f'HTTP error {e.response.status_code}', str(e)])
                break
        except requests.exceptions.RequestException as e:
            print(f"Error for query '{query}': {str(e)}")
            with open(ERROR_LOG_FILE, 'a', newline='', encoding='utf-8') as error_file:
                error_writer = csv.writer(error_file)
                error_writer.writerow([repo, 'Request Exception', str(e)])
            break
    
    return results, total_requests

def write_results(results):
    with open(RESULTS_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(results)

def search_github_issues(repos):
    with open(RESULTS_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Phrase', 'Issue/PR Title', 'State', 'Repository', 'URL', 'Context'])

    with open(ERROR_LOG_FILE, 'w', newline='', encoding='utf-8') as error_file:
        error_writer = csv.writer(error_file)
        error_writer.writerow(['Repository', 'Error Type', 'Error Details'])

    session = create_session()
    total_requests = 0
    for i, repo in enumerate(repos):
        print(f"Processing repository {i+1}/{len(repos)}: {repo}")
        results, requests = search_repository(session, repo)
        write_results(results)
        total_requests += requests
        print(f"Processed {repo}. Total API requests: {total_requests}")

    print(f"All results saved to '{RESULTS_FILE}'.")
    print(f"Error log saved to '{ERROR_LOG_FILE}'.")
    print(f"Total API requests made: {total_requests}")

if __name__ == "__main__":
    repos = read_repos_from_csv()
    if repos:
        search_github_issues(repos)
    else:
        print("No valid repositories found in the CSV file. Exiting.")
