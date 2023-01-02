

from github import Github
import os
import time
import repos
import pygsheets

repos = [i for i in repos.REPOS.split("\n") if "https" in i]

token = "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"
gh = Github(token)

jsLibs = ["@solana/web3.js", "@solana/spl-token", "@project-serum/anchor", "anchor-lang", 'anchor-spl', 'spl-token', 'solana-program', "solana"]
otherLibs = ["web3.js: ", "ethers.js", "solidity", "ethereum", "polygon", "matic", "hardhat", "ethers", "cardano", "tezos"]

client = pygsheets.authorize(service_account_file="cred.json")

spreadsht = client.open("Solana Repo Audit [Bolt]")

worksht = spreadsht.worksheet("title", "SolanaRepos")

continue_num = 33

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


            isSolFromPackage = len(package) > 0 and any(ext in package[0].decoded_content.decode('utf-8') for ext in jsLibs)
            isSolFromCargo = len(toml) > 0 and any(ext in toml[0].decoded_content.decode('utf-8') for ext in jsLibs)
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
    time.sleep(1)