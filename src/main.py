import os
import csv
import time
import itertools
import pygsheets
from github import Github
from dotenv import load_dotenv
import time
import sys


load_dotenv()

github_key1 = os.getenv('GH_KEY1')
github_key2 = os.getenv('GH_KEY2')
github_key3 = os.getenv('GH_KEY3')

EMPTY_CELL_FILL_MODE = True # True if we want to fill up cells that were missed by the script
name = "Jan Audit 2" # File name
sheet_title = "Sheet1" # Sheet name
continue_num = 19041 # Start at the specified repo index from CSV (to pause/resume)

data_file = "repos.csv" # Input data file name
column_letter = "B" # Classification column letter in spreadsheet
# Tags for classification
solana_tag = "SOLANA"
multichain_tag = "MULTI"
private_tag = "PRIVATE"
invalid_tag = "FAIL"


repos = []
with open(data_file, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if row and row[0].startswith('http'):
            repos.append(str(row[0]))


# List of Solana keywords and libs to check for in package files
sol_keywords = [
    "@solana/web3.js",
    "@metaplex-foundation",
    "@solana/spl-token",
    "@project-serum/anchor",
    "francium-sdk",
    "anchor-lang",
    "anchor-spl",
    "spl-token",
    "@coral-xyz/",
    "react-xnft",
    "solana-program",
    "solana",
    "metaplex",
    "spl",
    "serum-dex",
]

other_chain_keywords = [
    '"web3.js"',
    "ethers.js",
    "solidity",
    "ethereum",
    "cardano",
    "tezos",
    "polygon",
    "matic",
    "hardhat",
    "ethers",
    "monero",
    "bitcoin",
    "eth-",
    "metamask",
    "aptos",
    "brave-wallet",
    "polkadot",
    "'web3'",
    "terra-money"
]

ignore_dirs = [
    "node_modules",
    ".vscode",
    ".github",
    ".husky",
    ".git",
    ".idea",
    ".cache",
    ".DS_Store",
]


client = pygsheets.authorize(service_account_file="credentials.json")
spreadsheet = client.open(name)
worksheet = spreadsheet.worksheet("title", sheet_title)

# Main function
def identify(repo_url: str, cell: str) -> str:

    print(f"Checking: {repo_url} at cell {cell}")

    given_type = private_tag # Assuming private repo by default
    repo_data = None
    repo_name = repo_url.split("github.com/")[1].strip()

    keys = [github_key1, github_key2, github_key3]

    for key in keys:
        try:
            gh = Github(key)
            repo_data = gh.get_repo(repo_name)
            break  # exit the loop if successful
        except Exception as e:
            if "API rate" in str(e):
                print(f"You got rate limited with key {key}, trying next key now")
            else:
                print(e)
                print("[PRIVATE] Get repo failed")
                given_type = private_tag
                return given_type
    else:
        # All keys are rate limited
        print("All keys are rate limited. Sleeping for 1 hour")
        time.sleep(3600)  # Sleep for 1 hour
        given_type = None # Keep that rate limited cell empty. Will be managed later
        return given_type

    # Repo is not private anymore, but is invalid without checks yet
    given_type = invalid_tag

    if repo_data == None:
        print("[INVALID] Repo Empty")
        return

    try:
        print("Trying to get content...")
        content = repo_data.get_contents("")
    except:
        print("[INVALID] Empty repo content")
        return given_type
        
    # Check subdirectories for package files
    content.extend(
        c
        for i in content
        if i.type == "dir" and i.name not in ignore_dirs
        for c in repo_data.get_contents(i.path)
        if c.name.lower() in ["package.json", "cargo.toml", "go.mod", "setup.py", "package.swift", "gemfile", "pipfile"]
    )

    content.extend(
        c
        for i in content
        if i.type == "dir" and i.name not in ignore_dirs
        for i2 in repo_data.get_contents(i.path)
        if i2.type == "dir"
        for c in repo_data.get_contents(i2.path)
        if c.name.lower() in ["package.json", "cargo.toml", "go.mod", "setup.py", "package.swift", "gemfile", "pipfile"]
    )

    packages = [c for c in content if c.name.lower() == "package.json"]
    tomls = [c for c in content if c.name.lower() == "cargo.toml"]
    go_libs = [c for c in content if c.name.lower() == "go.mod"]
    pysetups = [c for c in content if c.name.lower() == "setup.py"]

    for content in itertools.chain(
        packages,
        tomls,
        go_libs,
        pysetups
    ):
        decoded_content = content.decoded_content.decode("utf-8")
        if any(ext in decoded_content for ext in sol_keywords):
            if content in packages:
                print("[SOL] [From package.json]")
            elif content in tomls:
                print("[SOL] [From Cargo.toml]")
            elif content in go_libs:
                print("[SOL] [From go.mod]")
            elif content in pysetups:
                print("[SOL] [From setup.py]")
            given_type = solana_tag
            break
        else:
            print("SOL not found, Content: ", decoded_content)

    # Multi chain check
    for item in itertools.chain(packages, go_libs, tomls, pysetups):
        if hasattr(item, "decoded_content") and any(ext in item.decoded_content.decode("utf-8") for ext in other_chain_keywords):
            matching_keywords = [
                ext for ext in other_chain_keywords if ext in item.decoded_content.decode("utf-8")
            ]
            print(f"Matched keywords for multi chain: {matching_keywords}")
            if given_type == solana_tag:
                given_type = multichain_tag
                print("[MULTI] assigned")
            else:
                given_type = invalid_tag
                print(f"[FAIL] Other chain found from {item}, not Solana.")
            break
    return given_type

all_tag_cells = worksheet.get_col(ord(column_letter) - ord('A') + 1) # Changing column letter to its index
empty_cells_indices = [i+1 for i, value in enumerate(all_tag_cells) if not value]

print("Length Of Empty Cell Indices: ", len(empty_cells_indices))

def run(start_index=0):
    total_time = 0.0
    filled = 0
    if EMPTY_CELL_FILL_MODE:
        print("Some Empty Cells For Checks :" ,empty_cells_indices[:5])
        print(f"EMPTY CELL MODE ON\n{len(empty_cells_indices)} EMPTY CELLS \n\n")
        print("Starting index: ", start_index)
        for cell_index in empty_cells_indices[start_index:]:
            print("Filling Cell..", cell_index)
            start_time = time.time()
            try:
                given_type = identify(repos[cell_index - 2], f"{column_letter}{cell_index}")
                row = column_letter + str(cell_index)
                worksheet.update_values(row, [[given_type]])
                print(
                    f"Updated {column_letter}{cell_index} with {given_type} [{filled+1}/{len(empty_cells_indices)}]"
                    )
            except Exception as e:
                print("Error in loop (CELL FILL): ", e)
                continue

            end_time = time.time()
            time_taken = end_time - start_time
            total_time += time_taken
            filled += 1
        print("Finished")

    else:
        for idx, repo in enumerate(repos[continue_num:]):
            start_time = time.time()
            try:
                given_type = identify(repo, f"{column_letter}{continue_num+idx+2}")
                row = column_letter + str(idx + continue_num + 2)  # +2 because index starts with zero and first value is the label
                worksheet.update_values(row, [[given_type]])
                print(
                    f"Updated {column_letter}{continue_num+idx+2} with {given_type}")
            except Exception as e:
                print("Error in loop: ", e)
                continue

            end_time = time.time()
            time_taken = end_time - start_time
            total_time += time_taken
            avg_time = (total_time / (idx + 1)) * len(repos[continue_num:]) - (idx + 1)
            print(f"Estimated time left {round(avg_time / 60 / 60, 3)}h\n")
        print("Finished")

run(int(sys.argv[1]))