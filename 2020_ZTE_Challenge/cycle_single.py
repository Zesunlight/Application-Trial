import csv
from collections import defaultdict
import time


def num_cycle(point, is_row, length, row_candidate, column_candidate):
    neighbor = row[point] if is_row else column[point]
    if len(neighbor) < 2:
        return 0
    
    if length == 1:
        if row_candidate[0] in neighbor:
#             for r, c in zip(row_candidate, column_candidate):
#                 print(r + '->' + c + '->', end = '')
#             print('\n')
            return 1
        else:
            return 0
    
    result = 0
    if is_row:
        for candidate in neighbor:
            if candidate in column_candidate:
                continue
            result += num_cycle(candidate, False, length - 1, row_candidate, column_candidate + [candidate])
    else:
        for candidate in neighbor:
            if candidate in row_candidate:
                continue
            result += num_cycle(candidate, True, length - 1, row_candidate + [candidate], column_candidate)
            
    return result


def cycles(length):
    begin = time.time()
    res = 0
    for start in row.keys():
        res += num_cycle(start, True, length, [start], [])
    print(length, time.time() - begin)
    return res / length


def cut_single():
    for r in row.keys():
        neighbor = len(row[r])
        single = r
        while neighbor == 1:
            opposite = row[single].pop(0)
            column[opposite].remove(single)
            if len(column[opposite]) == 1:
                single = column[opposite].pop(0)
                row[single].remove(opposite)
                neighbor = len(row[single])
            else:
                break

    for c in column.keys():
        neighbor = len(column[c])
        single = c
        while neighbor == 1:
            opposite = column[single].pop(0)
            row[opposite].remove(single)
            if len(row[opposite]) == 1:
                single = row[opposite].pop(0)
                column[single].remove(opposite)
                neighbor = len(column[single])
            else:
                break


if __name__ == '__main__':
    row = defaultdict(list)
    column = defaultdict(list)

    file_path = 'Example.csv'
    with open(file_path, 'r') as file:
        lines = csv.reader(file, delimiter=',')
        for line in lines:
            for num_column, friend in enumerate(line):
                if friend == '1':
                    row[str(lines.line_num)].append(str(num_column + 1))
                    column[str(num_column + 1)].append(str(lines.line_num))
    cut_single()

    print(cycles(4))
    print(cycles(6))
    print(cycles(8))
    print(cycles(10))
    print(cycles(12))
    print(cycles(14))
