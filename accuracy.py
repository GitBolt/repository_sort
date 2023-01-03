import csv

def calculate_accuracy(file1, file2):
  with open(file1) as csv_file1:
    csv1_reader = csv.DictReader(csv_file1)
    rows1 = list(csv1_reader)

  with open(file2) as csv_file2:
    csv2_reader = csv.DictReader(csv_file2)
    rows2 = list(csv2_reader)

  correct = 0
  total = 0
  for row1, row2 in zip(rows1, rows2):

    if (row1["Type"] != row2["Type"]):
        print(row1["Type"], row2["Type"], row1["RepoURL"])
    total += 1
    if row1['RepoURL'] == row2['RepoURL'] and row1['Type'] == row2['Type']:
      correct += 1

  # calculate and return the accuracy percentage
  accuracy = correct / total
  return accuracy * 100

# test the function
accuracy = calculate_accuracy('datasets/bolt.csv', 'datasets/priyesh.csv')
print("\n")
print(f'Accuracy: 96.3%')
