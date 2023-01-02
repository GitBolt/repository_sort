from github import Github
import os
import time
import repos
import pygsheets
from github_key import github_key

repos = [i for i in repos.REPOS.split("\n") if "https" in i]

token = github_key
gh = Github(token)

jsLibs = ["@solana/web3.js", "@metaplex-foundation", "@solana/spl-token", "@project-serum/anchor", "francium-sdk", "anchor-lang", 'anchor-spl', 'spl-token', 'solana-program', "solana", "metaplex"]
otherLibs = ['"web3.js',  '"web3', "ethers.js", "solidity", "ethereum",  "cardano", "tezos", "polygon", "matic", "hardhat", "ethers", "monero", "bitcoin", "eth-", "metamask", "walletconnect"]

client = pygsheets.authorize(service_account_file="cred.json")

# opens a spreadsheet by its name/title
spreadsht = client.open("Solana Repo Audit [Bolt]")

# opens a worksheet by its name/title
worksht = spreadsht.worksheet("title", "SolanaRepos")

continue_num = 516


for idx, repo in enumerate(repos[continue_num:]):
    given_type = None
    print("Checking: ", repo, idx + continue_num)

    repoData = None
    try:
        repoData = gh.get_repo(repo.split("github.com/")[1])
    except:
        given_type = "private"

    if (repoData):
        content = repoData.get_contents("")
        for i in content:
            if i.type == "dir":
                new_content = repoData.get_contents(i.path)
                if len([c for c in new_content if c.name in ["package.json", "Cargo.toml"]]):
                    content.extend(new_content)
                for i2 in new_content:
                    if i2.type == "dir":
                        new_content2 = repoData.get_contents(i2.path)
                        if len([c for c in new_content2 if c.name in ["package.json", "Cargo.toml"]]):
                            content.extend(new_content2)


            if len([c for c in content if c.name in ["package.json", "Cargo.toml"]]) == 0:
                print("Still not enough, just checking for folder name then...")
                for i in content:
                    if i.type == "dir":
                        if i.name.lower() == "solana" :
                            given_type = 'sol'
                        elif i.name.lower() in ["eth", "ethereum", "polygon", "matic"]:
                            given_type = "multi"
                            break   
            else:
                print("Got the file")

        if not given_type:
            package = [c for c in content if c.name.lower() == "package.json"]
            toml = [c for c in content if c.name == "Cargo.toml"]
            readme = [c for c in content if c.name == "README.md"]
        
            
            found_files = []
            if package:
                found_files.append("package.json")
            if toml:
                found_files.append("Cargo.toml")
            if readme:
                found_files.append("README.md")

            if not found_files:
                print("Nothing found.")
            else:
                print(f"Checking {', '.join(found_files)}")

            isSolFromPackage = len(package) > 0 and any(ext in package[0].decoded_content.decode('utf-8') for ext in jsLibs)
            isSolFromCargo = len(toml) > 0 and any(ext in toml[0].decoded_content.decode('utf-8') for ext in jsLibs)
            
            # Only used when nothing works
            isSolFromReadme = len(readme) > 0 and any(ext in readme[0].decoded_content.decode('utf-8') for ext in jsLibs)

            # Final check
            isSol = isSolFromPackage or isSolFromCargo
            isOtherChain = len(package) > 0 and any(ext in package[0].decoded_content.decode('utf-8') for ext in otherLibs)

        
            if isSol and not isOtherChain:
                print("Pure Solana")
                given_type = "sol"

            elif isSol and isOtherChain:
                print("Multi Chain")
                given_type = "multi"

            elif isOtherChain and not isSol:
                print("Different chain")
                given_type = "multi"

            elif isSolFromReadme:
                print("SOL [Not trusty]")
                given_type = "sol"
            
            else:
                given_type = "invalid"

    row = "B" + str(idx + continue_num + 2)
    if given_type == "sol":
        worksht.update_values(row,[["Solana"]])# Adding row values
        print("Updating column ", row, " with ", "Solana")
        
    elif given_type == "multi":
        worksht.update_values(row,[["Multi"]])# Adding row values
        print("Updating column ", row, " with ", "Multi")

    elif given_type == "private":
        worksht.update_values(row,[["NA"]])# Adding row values
        print("Updating column ", row, " with ", "NA")

    else:
        worksht.update_values(row,[["Invalid"]])# Adding row values
        print("Updating column ", row, " with ", "Invalid")

    print("\n")
