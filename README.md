# Solana Repo Sorter

This repository contains a Python script that can be used to sort repositories based on whether they are Solana based, Multichain, None of these or Private. It was created as a part of research for [Electric Capital Developer Report 2022](https://developerreport.com)

## Running the Script

To run the script, follow these steps:

1. Install the required packages by running `pip install -r requirements.txt`.
2. Get the entire repositories CSV with repo URLs and name it `input.csv`.
3. Run `get_repo_urls.py` to generate a new `repos.csv` file. This new file will only contain the repo's URLs, and it will remove any other data from the original `input.csv`.
4. Obtain a GitHub personal token and a Google service account credential JSON file. Name the JSON file `cred.json`.
5. Add the GitHub personal token to the `.env` file.
6. Open `main.py` and modify the parameter variables as needed for your research.
7. Finally, run `main.py`.

That's it! The script will sort the repositories according to the parameters you set, and the results will be saved to a new CSV file named `output.csv`.
