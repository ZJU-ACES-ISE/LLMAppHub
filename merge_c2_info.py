import json
from pathlib import Path
# merge data of category 2
def merge_c2_info():
    input_dir = Path('out/api_repo/c2_starover0_full')
    output_dir = Path('out/api_repo/c2_info')
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'c2_info.json'
    all_repos = []

    for f in input_dir.glob('*.json'):
        framework = f.stem.replace('#', '/')
        try:
            with open(f, 'r', encoding='utf-8') as infile:
                # Use json.loads with strict=False to allow control characters
                data = json.loads(infile.read(), strict=False)
                repo_list = data.get('all_public_dependent_repos', [])
                for repo in repo_list:
                    repo['framework'] = framework
                    all_repos.append(repo)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not decode JSON from {f.name}: {e}")
            continue

    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(all_repos, outfile, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    merge_c2_info() 