import time
import pygsheets
from github import Github
from github_key import github_key
import repos

# Split the list of repos and filter out invalid ones
repos = [i for i in repos.REPOS.split("\n") if "https" in i]

# Initialize the Github client
gh = Github(github_key)

# List of library names to check for in package.json and Cargo.toml
jsLibs = ["@solana/web3.js", "@metaplex-foundation", "@solana/spl-token",
          "@project-serum/anchor", "francium-sdk", "anchor-lang", 'anchor-spl',
          'spl-token', 'solana-program', "solana", "metaplex"]

otherLibs = ['"web3.js"',  '"web3"', "ethers.js", "solidity", "ethereum",
             "cardano", "tezos", "polygon", "matic", "hardhat", "ethers",
             "monero", "bitcoin", "eth-", "metamask"]

# Initialize the Google Sheets client
client = pygsheets.authorize(service_account_file="cred.json")
spreadsht = client.open("Solana Repo Audit [Bolt]")
worksht = spreadsht.worksheet("title", "SolanaRepos")

# Start at the specified repo index
continue_num = 6

for idx, repo in enumerate(repos[continue_num:]):
    given_type = None
    repoData = None

    # Get the repo data or mark it as private if it fails
    try:
        repoData = gh.get_repo(repo.split("github.com/")[1])
    except:
        given_type = "private"

    print("Checking: ", repo, idx + continue_num, given_type)

    # If the repo is not private, get the contents
    if repoData:
        content = repoData.get_contents("")

        # Check subdirectories for package.json and Cargo.toml
        content.extend(c for i in content if i.type == "dir"
                       for c in repoData.get_contents(i.path)
                       if c.name in ["package.json", "Cargo.toml"])
        
        content.extend(c for i in content if i.type == "dir"
                        for i2 in repoData.get_contents(i.path) if i2.type == "dir"
                        for c in repoData.get_contents(i2.path)
                        if c.name in ["package.json", "Cargo.toml"])

        # If still no package.json or Cargo.toml found, check directory names
        if not given_type:
            packages = [c for c in content if c.name.lower() == "package.json"]
            tomls = [c for c in content if c.name.lower() == "cargo.toml"]

            for package in packages:
                if any(ext in package.decoded_content.decode('utf-8') for ext in jsLibs):
                    print("SOL from JS")
                    given_type = "sol"
                    break

            for toml in tomls:
                if any(ext in toml.decoded_content.decode('utf-8') for ext in jsLibs):
                    print("SOL from Toml")
                    given_type = "sol"
                    break
            
            for package in packages:
                if any(ext in package.decoded_content.decode('utf-8') for ext in otherLibs):
                    print("Multi from JS")
                    given_type = "multi"
                    break

            # Other langs won't have toml so no check for that

            # If nothing works, we finally try with readme
            if not given_type:
                readme = [c for c in content if c.name == "README.md"]
                if any(ext in readme[0].decoded_content.decode('utf-8') for ext in jsLibs) if readme else False:
                    given_type = "sol"
                else:
                    given_type = "Invalid"                    

    # Update the worksheet with the repo and its type
    row = "B" + str(idx + continue_num + 2)
    if given_type == "sol":
        worksht.update_values(row,[["Solana"]])# Adding row values
        print("Updating column ", row, " with ", "Solana")
        
    elif given_type == "multi":
        worksht.update_values(row,[["Multi"]])# Adding row values
        print("Updating column ", row, " with ", "Multi")

    elif given_type == "private":
        worksht.update_values(row,[["Private"]])# Adding row values
        print("Updating column ", row, " with ", "Private")

    else:
        worksht.update_values(row,[["Invalid"]])# Adding row values
        print("Updating column ", row, " with ", "NA")
    

print("Finished!")
