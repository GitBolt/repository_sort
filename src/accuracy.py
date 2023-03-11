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
    if row1["type"] != row2["type"]:
        print(row1["type"], row2["type"], row1["url"])
    total += 1
    if row1['url'] == row2['url'] and row1['type'] == row2['type']:
      correct += 1

  accuracy = correct / total
  return accuracy * 100

accuracy = calculate_accuracy('datasets/bolt.csv', 'datasets/priyesh.csv')
print("\n")
print(f'Accuracy: {round(accuracy, 2)}%')
