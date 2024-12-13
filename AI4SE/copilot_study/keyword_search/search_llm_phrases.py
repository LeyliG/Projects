'''
Author Mostafa Ahmed

This code snippet is from the script that searches for 
specific keywords in the README files of GitHub repositories. 
The script reads the content of the README files and searches 
for specific keywords. If the keywords are found, the script 
writes the repository name, matching keywords, keyword snippets, 
and the repository URL to a CSV file.
'''
import os
import csv
import re

readmes_dir = 'readmes'
keywords = ['chatgpt', 'copilot']

def search_keywords_in_readme(readme_content, keywords):
    found_keywords = []
    snippets = []
    for keyword in keywords:
        matches = re.finditer(re.escape(keyword), readme_content, re.IGNORECASE)
        for match in matches:
            found_keywords.append(keyword)
            start = max(0, match.start() - 30)
            end = min(len(readme_content), match.end() + 30)
            snippet = readme_content[start:end].replace('\n', ' ').strip()
            snippets.append(f"...{snippet}...")
    return found_keywords, snippets

def get_repo_name(filename):
    parts = filename.split('_')
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return filename

def search_in_readmes():
    with open('search_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(['Repository', 'Matching Keywords', 'Keyword Snippets', 'URL'])
        
        for readme_file in os.listdir(readmes_dir):
            owner_repo = get_repo_name(readme_file)
            file_path = os.path.join(readmes_dir, readme_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            matching_keywords, snippets = search_keywords_in_readme(readme_content, keywords)
            if matching_keywords:
                repo_url = f"https://github.com/{owner_repo}"
                writer.writerow([
                    owner_repo,
                    ', '.join(matching_keywords),
                    '\n'.join(snippets),
                    repo_url
                ])

if __name__ == "__main__":
    search_in_readmes()
