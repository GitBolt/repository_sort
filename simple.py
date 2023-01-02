

from github import Github
import os
import base64
import time
import repos

repos = [i for i in repos.REPOS.split("\n") if "https" in i]

token = "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"
gh = Github(token)

jsLibs = ["@solana/web3.js", "@solana/spl-token", "@project-serum/anchor", "anchor-lang", 'anchor-spl', 'spl-token', 'solana-program']
otherLibs = ["web3.js: ", "ethers.js", "solidity", "ethereum", "polygon", "matic", "hardhat", "ethers"]


# Importing required library
import pygsheets

# Create the Client
client = pygsheets.authorize(service_account_file="cred.json")

# opens a spreadsheet by its name/title
spreadsht = client.open("Solana Repo Audit [Bolt]")

# opens a worksheet by its name/title
worksht = spreadsht.worksheet("title", "SolanaRepos")


for idx, repo in enumerate(repos):
    given_type = None
    print("Checking: ", repo, idx)

    repoData = None
    try:
        repoData = gh.get_repo(repo.split("github.com/")[1])
    except:
        given_type = "private"

    if (repoData):
        content = repoData.get_contents("")
        if len([c for c in content if c.name in ["package.json", "Cargo.toml"]]) == 0:
            print("Digging into folders...")
            for i in content:
                if i.type == "dir":
                    content.extend(repoData.get_contents(i.path))

            if len([c for c in content if c.name in ["package.json", "Cargo.toml"]]) == 0:
                print("Still not enough, just checking for folder name then...")
                for i in content:
                    if i.type == "dir":
                        if i.name.lower() == "solana" :
                            given_type = 'sol'
                        elif i.name.lower() in ["eth", "ethereum", "polygon", "matic"]:
                            given_type = "multi"
                            break   
                    
        if not given_type:
            package = [c for c in content if c.name.lower() == "package.json"]
            toml = [c for c in content if c.name == "Cargo.toml"]
        
            if package:
                print("Checking package.json")
            elif toml:
                print("Checking Cargo.toml")
            else:
                print("Nothing found.")

    
            isSolFromPackage = len(package) > 0 and any(ext in base64.b64decode(package[0].content).decode('utf-8') for ext in jsLibs)
            isSolFromCargo = len(toml) > 0 and any(ext in base64.b64decode(toml[0].content).decode('utf-8') for ext in jsLibs)
            isSol = isSolFromPackage or isSolFromCargo
            isOtherChain = len(package) > 0 and any(ext in base64.b64decode(package[0].content).decode('utf-8') for ext in otherLibs)

            if isSol and not isOtherChain:
                print("Pure Solana")
                given_type = "sol"

            elif isSol and isOtherChain:
                print("Multi Chain")
                given_type = "sol"

            elif isOtherChain and not isSol:
                print("Different chain")
                given_type = "multi"

            else:
                given_type = "invalid"



    row = "B" + str(idx + 2)
    print("Updating column...", row)
    if given_type == "sol":
        worksht.update_values(row,[["Solana"]])# Adding row values
    elif given_type == "multi":
        worksht.update_values(row,[["Multi"]])# Adding row values
    elif given_type == "private":
        worksht.update_values(row,[["NA"]])# Adding row values
    else:
        worksht.update_values(row,[["Invalid"]])# Adding row values
    print("\n")
    time.sleep(1)