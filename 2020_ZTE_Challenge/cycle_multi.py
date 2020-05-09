import csv
from collections import defaultdict
import time
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor
import multiprocessing as mp


def cycles(length, keys, row, column):
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

    # begin = time.time()
    res = 0
    for start in keys:
        res += num_cycle(start, True, length, [start], [])
    # print(length, time.time() - begin)
    # print(res / length)
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


def cycles_multi_useful(length, num_of_process):
    chunk_size = len(start_keys) // num_of_process + 1

    pool = mp.Pool(num_of_process)
    for i in range(num_of_process):
        process.append(pool.apply_async(cycles, args=(length,
                                                      start_keys[i * chunk_size: (i + 1) * chunk_size],
                                                      row,
                                                      column,)))
    pool.close()
    pool.join()
    sum = 0
    for p in process:
        sum += p.get()
    print(length, sum)


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
    start_keys = list(row.keys())
    print('prepare data')

    print(cycles(4, start_keys, row, column))
    print(cycles(6, start_keys, row, column))
    print(cycles(8, start_keys, row, column))

    process = []
    num_of_process = 6
    cycles_multi_useful(10, num_of_process)
    cycles_multi_useful(12, num_of_process)
    cycles_multi_useful(14, num_of_process)
