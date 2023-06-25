import json

with open('daily_count.json') as file:
    data = json.load(file)

averages ={}
for user, user_data in data.items():
    daily_count = user_data['daily_count']
    num_days = len(daily_count)
    if num_days > 0:
        average = sum(daily_count.values()) / num_days
        averages[user] = average

sorted_users = sorted(averages.items(), key=lambda x: x[1])

top_increased = sorted_users[-3:]

top_decreased = sorted_users[:3]

print("Top 3 users with increased averages:")
for user, average in reversed(top_increased):
    print(f"User: {user}, Average: {average}")

print("\nTop 3 users with decreased averages:")
for user, average in top_decreased:
    print(f"User: {user}, Average: {average}")
