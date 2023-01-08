import csv

# Read in the merged.csv file
merged_repos = []
with open('bolt_filled.csv', 'r') as merged_file:
    csv_reader = csv.reader(merged_file)
    # Skip the header row
    next(csv_reader)
    for row in csv_reader:
        merged_repos.append(row)

# Read in the priyesh.csv file
priyesh_repos = {}
with open('priyesh.csv', 'r') as priyesh_file:
    csv_reader = csv.reader(priyesh_file)
    # Skip the header row
    next(csv_reader)
    for row in csv_reader:
        priyesh_repos[row[0]] = row[1]

# Create the result.csv file
with open('result.csv', 'w') as result_file:
    csv_writer = csv.writer(result_file)
    csv_writer.writerow(['RepoURL', 'Type'])
    
    # Open the log files for writing
    log_file = open('log.txt', 'w')
    special_log_file = open('special_log.txt', 'w')
    
    # Go through the merged_repos and compare with the data in priyesh_repos
    for repo_url, repo_type in merged_repos:
        # Check if the repo_url is in priyesh_repos
        if repo_url in priyesh_repos:
            # Check if the types match
            if repo_type == priyesh_repos[repo_url]:
                # Write the data to result.csv
                csv_writer.writerow([repo_url, repo_type])
            else:
                # Check for special cases where we should use the value from merged.csv
                if repo_type in ['Multi', 'Solana', 'NA', 'None']:
                    # Write the data to result.csv and log the mismatch
                    csv_writer.writerow([repo_url, repo_type])
                    log_file.write(f"Mismatch at {repo_url}: {priyesh_repos[repo_url]} (priyesh.csv) vs {repo_type} (merged.csv)\n")
                else:
                    # Use the value from priyesh.csv and log the mismatch
                    csv_writer.writerow([repo_url, priyesh_repos[repo_url]])
                    special_log_file.write(f"Mismatch at {repo_url}: {priyesh_repos[repo_url]} (priyesh.csv) vs {repo_type} (merged.csv)\n")
        else:
            # The repo_url is not in priyesh_repos, so we can't compare the types
            # Write the data from merged.csv to result.csv
            csv_writer.writerow([repo_url, repo_type])
    
    # Close the log files
    log_file.close()
    special_log_file.close()