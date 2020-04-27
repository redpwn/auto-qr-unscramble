import numpy as np
import PIL.Image as Image
import pyzbar.pyzbar as pyzbar

def split(string, direction):
    rows = string.split('\n')[:-1]
    if direction == 'row':
        return rows
    columns = [list(column) for column in zip(*rows)]
    return columns

def is_possible(format_values, scrambled_values):
    for format, scrambled in zip(format_values, scrambled_values):
        if format != '-' and format != scrambled:
            return False
    return True

def find_duplicates(possibilities, scrambled):
    duplicates = {}
    for i, values in enumerate(scrambled):
        hashable = tuple(values)
        if not hashable in duplicates:
            duplicates[hashable] = set()
        duplicates[hashable].add(i)
    trimmed = []
    for _, values in duplicates.items():
        if len(values) > 1:
            trimmed.append(values)
    return trimmed

def seen_duplicate(seen, duplicates, value):
    for values in duplicates:
        for index in seen:
            if index in values and value in values:
                return True
    return False

def optimize(possibilities):
    duplicates = {}
    finished = True
    for i, possible_indexes in enumerate(possibilities):
        hashable = tuple(possible_indexes)
        if not hashable in duplicates:
            duplicates[hashable] = set()
        duplicates[hashable].add(i)
    for possible_indexes, indexes in duplicates.items():
        if len(possible_indexes) != len(indexes):
            continue
        for index in possible_indexes:
            for i, index_set in enumerate(possibilities):
                if i in indexes:
                    continue
                if index in index_set:
                    index_set.remove(index)
                    finished = False
    if not finished:
        optimize(possibilities)


def generate_possibilities(format, scrambled):
    possibilities = []
    for format_values in format:
        temp = set() 
        for i, scrambled_values in enumerate(scrambled):
            if  is_possible(format_values, scrambled_values):
                temp.add(i)
        possibilities.append(temp) 
    optimize(possibilities)
    return possibilities

def generate_permutations(possibilities, scrambled):
    duplicates = find_duplicates(possibilities, scrambled)
    permutations = [([], set())]
    for possible_values in possibilities:
        prev = permutations
        permutations = []
        for permutation, indexes in prev:
            seen = set() 
            for value in possible_values:
                if seen_duplicate(seen, duplicates, value):
                    continue
                if value in indexes:
                    continue
                seen.add(value)
                current = (permutation.copy(), indexes.copy())
                current[0].append(value)
                current[1].add(value)
                permutations.append(current)
    permutations = list(map(lambda x: x[0], permutations))
    return permutations

def generate_codes(permutations, scrambled, direction):
    codes = [] 
    for permutation in permutations:
        code = []
        for index in permutation:
            code.append([255 if value == '0' else 0 for value in scrambled[index]])
        current = np.array(code)
        codes.append(current)
    return codes

def check_codes(codes):
    results = []
    for code in codes:
        img = Image.fromarray(code.astype(np.uint8)).resize((100, 100))
        result = pyzbar.decode(img)
        for decoded in result:
            results.append(decoded.data.decode())
    return results

def main(direction='column'):
    format = split(open('format.txt', 'r').read(), direction)
    scrambled = split(open('scrambled.txt', 'r').read(), direction)
    possibilities = generate_possibilities(format, scrambled)
    print("Generating permutations...")
    permutations = generate_permutations(possibilities, scrambled)
    print("Generating QR codes...")
    codes = generate_codes(permutations, scrambled, direction)
    print("Checking QR codes...")
    results = check_codes(codes)
    print("Found %d results:" % len(results))
    for data in results:
        print(data)

main()
