import json
import os
from pathlib import Path
# merge data of category 1

def process_data():
    # Define paths
    repo_des_path = Path('out/api_repo/c1_repo_owner_des_less')
    keyword_path = Path('out/api_repo/c1_with_framework_keywords')
    output_dir = Path('out/api_repo/c1_info')
    output_file = output_dir / 'c1_info.json'

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Dictionary to hold the consolidated data
    repo_data = {}

    # 1. Process files from c1_repo_owner_des_less to get base info
    print(f"Processing files from {repo_des_path}...")
    for f in repo_des_path.glob('*.json'):
        with open(f, 'r', encoding='utf-8') as infile:
            try:
                data = json.load(infile)
                for repo in data:
                    full_name = repo.get('full_name')
                    if full_name and full_name not in repo_data:
                        repo_data[full_name] = {
                            'full_name': full_name,
                            'name': repo.get('name'),
                            'description': repo.get('description'),
                            'html_url': [],
                            'model': [],
                            'language': [],
                            'fork': None
                        }
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {f}")
                continue
    print(f"Loaded base information for {len(repo_data)} repositories.")

    # 2. Process files from c1_with_framework_keywords to get details
    print(f"Processing files from {keyword_path}...")
    for f in keyword_path.glob('*.json'):
        print(f"  - Processing {f.name}")
        # Extract model and language from filename
        parts = f.name.replace('with_kw_', '').replace('_filtered_dele.json', '').split('_')
        model = parts[0]
        language = parts[1] if len(parts) > 1 else ''

        with open(f, 'r', encoding='utf-8') as infile:
            try:
                data = json.load(infile)
                for item in data:
                    repo_info = item.get('repository', {})
                    full_name = repo_info.get('full_name')

                    if not full_name:
                        continue

                    # If the repository is not in our base list from c1_repo_owner_des_less, skip it.
                    if full_name not in repo_data:
                        continue
                    
                    # Add html_url
                    if item.get('html_url'):
                        repo_data[full_name]['html_url'].append(item['html_url'])

                    # Add model and language if not already present
                    if model not in repo_data[full_name]['model']:
                        repo_data[full_name]['model'].append(model)
                    if language not in repo_data[full_name]['language']:
                        repo_data[full_name]['language'].append(language)
                        
                    # Set fork status
                    if repo_data[full_name]['fork'] is None and 'fork' in repo_info:
                        repo_data[full_name]['fork'] = repo_info['fork']

            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {f}")
                continue
    
    # 3. Convert dictionary to list
    final_data = list(repo_data.values())

    # 4. Write to output file
    print(f"Writing {len(final_data)} records to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(final_data, outfile, indent=2, ensure_ascii=False)

    print("Processing complete.")

if __name__ == '__main__':
    process_data() 