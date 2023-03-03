import time
import pygsheets
from github import Github
from github_key import github_key, github_key2
import csv

data_file = "repos.csv"
column_letter = "L"


repos = []

with open(data_file, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if row and row[0].startswith('http'):
            repos.append(str(row[0]))


# List of library names to check for in package.json and Cargo.toml
sol_keywords = [
    "@solana/web3.js",
    "@metaplex-foundation",
    "@solana/spl-token",
    "@project-serum/anchor",
    "francium-sdk",
    "anchor-lang",
    "anchor-spl",
    "spl-token",
    "solana-program",
    "solana",
    "metaplex",
    "spl",
    "serum-dex",
]

other_keywords = [
    '"web3.js"',
    '"web3"',
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

# Start at the specified repo index
continue_num = 101
def identify(repo_url: str) -> str:
    given_type = "Private"
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
        given_type = "Private"

    print(f"Checking: {repo} at cell B{continue_num+idx+2}")

    if repoData:
        # If the repo is not private, get the contents
        content = repoData.get_contents("")

        # Check subdirectories for package.json and Cargo.toml
        content.extend(
        c
        for i in content
        if i.type == "dir" and i.name not in ignore_dirs
        for c in repoData.get_contents(i.path)
        if c.name in ["package.json", "Cargo.toml"]
        )

        content.extend(
        c
        for i in content
        if i.type == "dir" and i.name not in ignore_dirs
        for i2 in repoData.get_contents(i.path)
        if i2.type == "dir"
        for c in repoData.get_contents(i2.path)
        if c.name in ["package.json", "Cargo.toml"]
        )

        packages = [c for c in content if c.name.lower() == "package.json"]
        tomls = [c for c in content if c.name.lower() == "cargo.toml"]

        for package in packages:
            print(package.decoded_content.decode("utf-8"))
            if any(ext in package.decoded_content.decode("utf-8") for ext in sol_keywords):
                print("SOL [From package.json]")
                given_type = "Solana"
                break

        for toml in tomls:
            if any(ext in toml.decoded_content.decode("utf-8") for ext in sol_keywords):
                print("SOL [From Cargo.toml")
                given_type = "Solana"
                break

        # Multi only matters if SOL is there
        if given_type == "Solana":
            for package in packages:
                if any(
                    ext in package.decoded_content.decode("utf-8") for ext in other_keywords
                ):
                    given_type = "Multi"
                    break
        else:
            given_type = "NA"

    return given_type
    # Update the worksheet with the repo and its type

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