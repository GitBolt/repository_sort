import csv
import requests
import json
import os

github_key = os.getenv("GH_KEY1")
github_key2 = os.getenv("GH_KEY2")


def link_to_api(url):
    parts = url.split('/')
    owner = parts[3]
    repo_name = parts[4]
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
    return api_url


solana_repos = []
multichain_repos = []

with open('repos.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['type'] == 'SOLANA':
            solana_repos.append(row['url'])
        elif row['type'] == 'MULTI':
            multichain_repos.append(row['url'])


def get_contributors(repo):
    url = link_to_api(repo)
    headers = {"Authorization": f"token {github_key}"}
    response = requests.get(url, headers=headers)
    contributors = response.json()
    if "message" in contributors and "rate" in contributors["message"].lower():
        print("New Key Usage for Contributors Get")
        headers = {"Authorization": f"token {github_key2}"}
        response = requests.get(url, headers=headers)
        contributors = response.json()
        print(contributors)

    return contributors


def get_user_profile(username):
    url = f"https://api.github.com/users/{username}"
    headers = {"Authorization": f"token {github_key}"}
    response = requests.get(url, headers=headers)
    profile = response.json()

    if "message" in profile and "rate" in profile["message"].lower():
        print("New Key Usage for Profile")
        headers = {"Authorization": f"token {github_key2}"}
        response = requests.get(url, headers=headers)
        profile = response.json()
        
    return profile


def get_contact_info(profile):
    contact_info = {}
    print(profile)
    if profile.get("blog"):
        contact_info["website"] = profile["blog"]
    else:
        contact_info["website"] = None
    if profile.get("twitter_username"):
        contact_info["twitter"] = profile["twitter_username"]
    else:
        contact_info["twitter"] = None
    if profile.get("email"):
        contact_info["email"] = profile["email"]
    else:
        contact_info["email"] = None
    if profile.get("name"):
        contact_info["name"] = profile["name"]
    else:
        contact_info["name"] = profile["login"]
    if profile.get("location"):
        contact_info["location"] = profile["location"]
    else:
        contact_info["location"] = None
    return contact_info


not_worked = []
def process_repos(repos):
    contributors_data = []
    for repo in repos:
        print(repo)
        try: 
            contributors = get_contributors(repo)
            for contributor in contributors:
                username = contributor["login"]
                commits = contributor["contributions"]
                profile = get_user_profile(username)
                contact_info = get_contact_info(profile)
                found = False
                for data in contributors_data:
                    if data["github_name"] == username:
                        found = True
                        data["total_commits"] += commits
                        data["contributed_repos"].append(repo)
                        break
                if not found:
                    data = {
                        "github_name": username,
                        "contact_info": contact_info,
                        "total_commits": commits,
                        "contributed_repos": [repo],
                    }
                    contributors_data.append(data)
            save_json(contributors_data, "data.json")
        except Exception as e:
            print("Did not work: ", repo, e)
            not_worked.append(repo)
            continue


    with open('not_worked.json', 'w') as file:
        json.dump(not_worked, file, indent=4)

    return contributors_data


def save_json(data, filename):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)



contributors_data = process_repos(solana_repos[:50])
save_json(contributors_data, "data.json")


with open('data.json', 'r') as file:
    data = json.load(file)

sorted_data = sorted(data, key=lambda x: x['total_commits'], reverse=True)

with open('data.json', 'w') as file:
    json.dump(sorted_data, file, indent=4)

