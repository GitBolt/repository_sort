import json
import requests
from datetime import datetime, timedelta
import os

github_key = os.getenv("GH_KEY1")
github_key2 = os.getenv("GH_KEY2")

headers = {"Authorization": f"token {github_key}"}

with open('data.json') as json_file:
    json_data = json.load(json_file)

print(len(json_data), " Devs")
data = {}

# Calculate the date range for the last 7 days in UTC
end_date = datetime.utcnow().date()
start_date = end_date - timedelta(days=7)
date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

for user in json_data:
    github_name = user["github_name"]
    gh_name = user["contact_info"]["name"]
    contact_info = user["contact_info"]
    daily_count = {str(date): 0 for date in date_range}

    url = f'https://api.github.com/users/{github_name}/events'
    response = requests.get(url, headers=headers)
    events = response.json()
    for idx, event in enumerate(events):
        created_date = event["created_at"].split("T")[0]
        event_date = datetime.fromisoformat(created_date).date()

        if event["type"] == "PushEvent" and start_date <= event_date <= end_date:
            commit_count = len([e for e in event["payload"]["commits"] if e["author"]["name"] == gh_name])
            daily_count[created_date] += commit_count
    
    data[github_name] = {
        "contact_info": contact_info,
        "daily_count": daily_count,
        "total_commits": user["total_commits"]
    }

    with open('daily_count.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
