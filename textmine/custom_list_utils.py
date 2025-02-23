import csv

def single_to_multi(list_in: list):
    return [[item] for item in list_in]

def flatten(list_in: list):
    return [item for sublist in list_in for item in sublist]

def write(list_in: list, filename):
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(list_in)

def read(filename, delimiter=","):
    data = []
    with open(filename, "r") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            data.append(row)

    return data