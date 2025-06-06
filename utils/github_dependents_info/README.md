# github_dependents_info Usage Guide

# Purpose

This project focuses only on the `github-dependents-info` folder. The main tool sometimes stops crawling after a hundred pages, possibly due to network issues, and cannot collect all dependents. For some target projects, there are over 400,000 dependent repositories to collect. To address this, I want to write an additional script to supervise and control the crawling process. The goal is to record the last successfully processed dependent repository (by id or other identifier), so that if the process is interrupted, it can resume from where it left off. This is necessary because the current design only saves progress after finishing all pages for a package, which means if interrupted, all progress for the current package is lost.

## Quick Start

1. **Set the Target Repository**

   Before running, open the `run_persistent.py` file and locate the line where the target repository is set (e.g., `repo = "xxx/xxx"`). Change it to the GitHub repository you want to analyze, for example:

   ```python
   repo = "openai/openai-python"
   ```

2. **Run the Script**

   In your terminal, navigate to this directory and execute:

   ```bash
   python run_persistent.py
   ```

   The script will automatically fetch the dependent information and save all output files (such as CSV, TXT, etc.) in the `output/` folder.

## Notes
- All output files are stored in the `output/` folder under this directory.
- To analyze a different repository, make sure to update the repository name in `run_persistent.py`.

If you have any questions or issues, feel free to open an issue or contact the maintainer. 