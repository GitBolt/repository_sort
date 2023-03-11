import csv

input_file = "input.csv"
output_file = "repos.csv"

with open(input_file, "r") as file:
    reader = csv.reader(file)
    header = next(reader)  # get header row
    url_index = header.index("url")

    urls = []
    for row in reader:
        urls.append([row[url_index]])

with open(output_file, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["url"])
    writer.writerows(urls)
