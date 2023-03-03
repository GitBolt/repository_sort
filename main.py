import time
import os
import pygsheets
from github import Github
import csv
from dotenv import load_dotenv

load_dotenv()

github_key = os.getenv('github_key')
github_key2 = os.getenv('github_key2')

"""Parameters"""
# Input data file name
data_file = "repos.csv"
# The classification type column letter
column_letter = "L"
# Start at the specified repo index
continue_num = 1290

# Tags for classification
solana_tag = "PASS"
multichain_tag = "MULTI"
private_tag = "PRIVATE"
invalid_tag="FAIL"


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

# Other chain keywords and libs
other_keywords = [
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


# Initialize the Google Sheets client
client = pygsheets.authorize(service_account_file="cred.json")
spreadsht = client.open("Audited")
worksht = spreadsht.worksheet("title", "Repos")

# Sorting function
def identify(repo_url: str) -> str:
    given_type = private_tag
    repoData = None

    gh = Github(github_key)

    # Get the repo data or mark it as private if it fails
    try:
        repoData = gh.get_repo(repo_url.split("github.com/")[1].strip())
    except Exception as e:
        if ("API rate" in str(e)):
            print("Rate Limited\n")
            gh = Github(github_key2)
            repoData = gh.get_repo(repo_url.split("github.com/")[1].strip())
        else:
            given_type = private_tag
            return given_type

    print(f"Checking: {repo} at cell B{continue_num+idx+2}")
    if repoData:
        # Repo is not private anymore, but invalid without checks yet
        given_type = invalid_tag

        content = repoData.get_contents("")

        # Check subdirectories for package.json and Cargo.toml
        content.extend(
        c
        for i in content
        if i.type == "dir" and i.name not in ignore_dirs
        for c in repoData.get_contents(i.path)
        if c.name in ["package.json", "Cargo.toml", "go.mod", "setup.py"]
        )

        content.extend(
        c
        for i in content
        if i.type == "dir" and i.name not in ignore_dirs
        for i2 in repoData.get_contents(i.path)
        if i2.type == "dir"
        for c in repoData.get_contents(i2.path)
        if c.name in ["package.json", "Cargo.toml", "go.mod", "setup.py"]
        )

        packages = [c for c in content if c.name.lower() == "package.json"]
        tomls = [c for c in content if c.name.lower() == "cargo.toml"]
        go = [c for c in content if c.name.lower() == "go.mod"]
        pysetups = [c for c in content if c.name.lower() == "setup.py"]

        for package in packages:
            print(package.decoded_content.decode("utf-8"))
            if any(ext in package.decoded_content.decode("utf-8") for ext in sol_keywords):
                print("SOL [From package.json]")
                given_type = solana_tag
                break

        for toml in tomls:
            print(toml.decoded_content.decode("utf-8"))
            if any(ext in toml.decoded_content.decode("utf-8") for ext in sol_keywords):
                print("SOL [From Cargo.toml")
                given_type = solana_tag
                break

        for g in go:
            if any(ext in g.decoded_content.decode("utf-8") for ext in sol_keywords):
                print("SOL [From go.mod")
                given_type = solana_tag
                break

        for py in pysetups:
            if any(ext in py.decoded_content.decode("utf-8") for ext in sol_keywords):
                print("SOL [From setup.py]")
                given_type = solana_tag
                break


        for package in packages:
            print(package.decoded_content.decode("utf-8"))
            if any(
                ext in package.decoded_content.decode("utf-8") for ext in other_keywords
            ):
                matching_keywords = []
                for ext in other_keywords:
                    if ext in package.decoded_content.decode("utf-8"):
                        matching_keywords.append(ext)
                print("These matched: ", matching_keywords)
                print("Found other chain [From package.json]")
                if given_type == solana_tag:
                    given_type = multichain_tag
                    break
                else:
                    # Other chain, so invalid
                    given_type = invalid_tag
                    break
        
        for g in go:
            if any(
                ext in g.decoded_content.decode("utf-8") for ext in other_keywords
            ):
                print("Found other chain [from Go]")
                if given_type == "Solana":
                    given_type = multichain_tag
                else:
                    # Other chain, so invalid
                    given_type = invalid_tag
                break

    else:
        print("Repo data not found")
        given_type = invalid_tag

    return given_type

for idx, repo in enumerate(repos[continue_num:]):
    try:
        given_type = identify(repo)
        row = column_letter + str(idx + continue_num + 2)
        worksht.update_values(row, [[given_type]])
        print(f"Updated B{continue_num+idx+2} with {given_type}\n")
    except Exception as e:
        print(e)
        continue
print("Finished.")