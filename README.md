# prompt-to-circuit-data
Data mining and cleaning pipeline for the Prompt-to-Circuit project (Team 1).

This repository contains the complete data mining, cleaning, and processing pipeline for Phase 1 of the Prompt-to-Circuit project. The goal of this pipeline is to construct a reliable and well-documented dataset of prompt-circuit mappings.

## Project Structure

The repository is organized into the following directories:

- **/data/**: Contains all data, separated by processing stage.
  - **/raw/**: Untouched data collected directly from scrapers.
  - **/processed/**: Intermediate data files, such as the combined corpus.
  - **/final_dataset/**: The final, clean, de-duplicated dataset deliverable.
- **/notebooks/**: Jupyter Notebooks for analysis, exploration, and final reporting.
- **/scripts/**: All Python scripts for the data pipeline.
  - **/scrapers/**: Individual scripts for scraping each data source.
  - **/processing/**: Scripts for normalizing, cleaning, and finalizing the data.

## How to Run the Pipeline

### 1. Setup

First, clone the repository and set up the Python virtual environment.

```bash
git clone https://github.com/Moab-786/prompt-to-circuit-data.git
cd prompt-to-circuit-data
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Pipeline

The pipeline is designed to be run in sequence.

```bash
# Step 1: Run scrapers to collect raw data (run as many as needed)
python scripts/scrapers/scrape_github.py
python scripts/scrapers/scrape_stackoverflow.py

# Step 2: Combine all raw data into a single corpus
python scripts/processing/normalize.py

# Step 3: Clean, de-duplicate, and produce the final dataset
python scripts/processing/finalize.py
```

The final deliverable will be located at `data/final_dataset/dataset.json`.
