'''
Author Mostafa Ahmed
'''
import requests
import csv
import os
import base64
import time
from datetime import datetime

GITHUB_TOKEN = '##'
GITHUB_REPO_CONTENT_URL = "https://api.github.com/repos/{owner}/{repo}/readme"
RATE_LIMIT_URL = "https://api.github.com/rate_limit"

class DownloadStats:
    def __init__(self):
        self.total_repos = 0
        self.downloaded = 0
        self.skipped_existing = 0
        self.failed = 0
        self.start_time = time.time()

    def print_progress(self):
        elapsed_time = time.time() - self.start_time
        print(f"\nProgress Report:")
        print(f"Total repositories processed: {self.total_repos}")
        print(f"Successfully downloaded: {self.downloaded}")
        print(f"Skipped (already existing): {self.skipped_existing}")
        print(f"Failed downloads: {self.failed}")
        print(f"Time elapsed: {elapsed_time:.2f} seconds")
        
        if self.total_repos > 0:
            completion_percentage = (self.total_repos / self.total_repos_count) * 100
            print(f"Overall progress: {completion_percentage:.2f}%")

def check_rate_limit():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else None,
    }
    try:
        response = requests.get(RATE_LIMIT_URL, headers=headers)
        if response.status_code == 200:
            rate_data = response.json()['rate']
            remaining = rate_data['remaining']
            reset_time = rate_data['reset']
            
            print(f"API Rate Limit Status:")
            print(f"Remaining requests: {remaining}")
            print(f"Reset time: {datetime.fromtimestamp(reset_time)}")
            
            return remaining, reset_time
        else:
            print(f"Failed to check rate limit. Status code: {response.status_code}")
            return 0, None
    except requests.exceptions.RequestException as e:
        print(f"Error checking rate limit: {e}")
        return 0, None

def download_readme(owner, repo):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else None,
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        url = GITHUB_REPO_CONTENT_URL.format(owner=owner, repo=repo)
        response = requests.get(url, headers=headers)
        
        if response.status_code == 404:
            print(f"README not found for {owner}/{repo}")
            return None
        elif response.status_code == 403:
            print(f"Rate limit exceeded or authentication required for {owner}/{repo}")
            return None
        elif response.status_code != 200:
            print(f"Error downloading README for {owner}/{repo}. Status code: {response.status_code}")
            return None
            
        readme_data = response.json()
        if 'content' in readme_data:
            return base64.b64decode(readme_data['content']).decode('utf-8')
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error downloading README for {owner}/{repo}: {e}")
        return None
    except UnicodeDecodeError as e:
        print(f"Error decoding README content for {owner}/{repo}: {e}")
        return None

def save_readme_to_file(repo_full_name, readme_content):
    os.makedirs('readmes', exist_ok=True)
    filename = f"readmes/{repo_full_name.replace('/', '_')}_README.md"
    
    try:
        if os.path.exists(filename):
            return False
            
        with open(filename, 'w', encoding='utf-8') as readme_file:
            readme_file.write(readme_content)
        return True
    except IOError as e:
        print(f"Error saving README for {repo_full_name}: {e}")
        return False

def download_readmes_from_csv():
    stats = DownloadStats()
    
    try:
        # Count total repositories first
        with open('repos.csv', 'r') as csvfile:
            stats.total_repos_count = sum(1 for row in csv.DictReader(csvfile))
        
        with open('repos.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                repo_full_name = row['name']
                owner, repo = repo_full_name.split('/')
                stats.total_repos += 1
                
                print(f"\nProcessing {stats.total_repos}/{stats.total_repos_count}: {repo_full_name}")
                
                remaining_requests, reset_time = check_rate_limit()
                if remaining_requests < 1:
                    sleep_duration = reset_time - int(time.time())
                    print(f"Rate limit exceeded. Sleeping for {sleep_duration} seconds...")
                    time.sleep(max(0, sleep_duration + 1))  # Add 1 second buffer
                    continue
                
                readme_content = download_readme(owner, repo)
                if readme_content:
                    if save_readme_to_file(repo_full_name, readme_content):
                        stats.downloaded += 1
                        print(f"Successfully downloaded README for {repo_full_name}")
                    else:
                        stats.skipped_existing += 1
                        print(f"Skipped {repo_full_name} (README already exists)")
                else:
                    stats.failed += 1
                
                # Print progress every 100 repositories
                if stats.total_repos % 100 == 0:
                    stats.print_progress()
                
                time.sleep(0.5)  # Pause between requests
                
    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        stats.print_progress()
        print("\nDownload process completed.")

if __name__ == "__main__":
    download_readmes_from_csv()