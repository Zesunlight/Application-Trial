# -*- coding: UTF-8 -*-

"""
=================================================
@File    : cycle_simplify.py
@Author  : ZYZ
@Date    : 2020/04/26
@Problem : https://www.nowcoder.com/discuss/390140
=================================================="""


import csv
from collections import defaultdict
import multiprocessing as mp
import gc


def cycles(length, keys, row, column, distance):
    def num_cycle(point, is_row, length, row_candidate, column_candidate):
        neighbor = row[point] if is_row else column[point]
        if len(neighbor) < 2:
            # 邻居数小于 2，则为非环点
            return 0

        if length in (2, 4, 6):
            # 此时的点是 row 中的
            # 当前点与起点的距离必须为 length，才可能构成环
            # 避免现在就是从起点开始的情况
            if (point != row_candidate[0]) and (point not in distance[row_candidate[0]][length]):
                return 0

        if length == 1:
            # 成环的最后一步
            if row_candidate[0] in neighbor:
                path = []
                path.extend(sorted(row_candidate))
                # row、column 中使用的都是正数来表示点
                # 记录路径时 column 中的点使用负数，避免冲突
                path.extend(sorted([-i for i in column_candidate]))
                part_sum.add(tuple(path))
            return 0

        # 深度优先搜索，遍历下一个可能点
        if is_row:
            for candidate in neighbor:
                if candidate in column_candidate:
                    # 成环的路径上不能有重复点
                    continue
                num_cycle(candidate, False, length - 1, row_candidate, column_candidate + [candidate])
        else:
            for candidate in neighbor:
                if candidate <= row_candidate[0] or candidate in row_candidate:
                    # 避免同记录一个环多次，不妨设起点是 row_candidate 中最小的
                    continue
                num_cycle(candidate, True, length - 1, row_candidate + [candidate], column_candidate)

        return 0

    # 遍历所有起点
    cycle_amount = 0
    for start in keys:
        part_sum = set()    # 记录环的路径，用于去重
        num_cycle(start, True, length, [start], [])
        cycle_amount += len(part_sum)

    return cycle_amount


def cut_single():
    # 若某个点的度为 1，则该点不会出现在环中，除去该点与邻居的连线
    # 对行、列的点反复进行该操作
    # 去除 row、column 中的非环点与其邻居的连线

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


def cycles_multi(length, num_of_process):
    # 多进程处理

    process = []
    chunk_size = len(start_keys) // num_of_process + int(not (len(start_keys) % num_of_process == 0))

    pool = mp.Pool(num_of_process)
    for i in range(num_of_process):
        process.append(pool.apply_async(cycles, args=(length,
                                                      start_keys[i * chunk_size: (i + 1) * chunk_size],
                                                      row,
                                                      column,
                                                      distance,)))
    pool.close()
    pool.join()

    total = 0
    for p in process:
        part_sum = p.get()
        total = total + part_sum

    return total


def early_stop():
    # 从 row 中的某个点出发，与另一个 row 中的点的距离
    # 分为 2步可达、4步可达、6步可达

    close = defaultdict(dict)
    for i in range(len(start_keys)):
        # 2 step neighbors
        close[start_keys[i]][2] = set()
        for c in row[start_keys[i]]:
            close[start_keys[i]][2] = close[start_keys[i]][2].union(set(column[c]))
        close[start_keys[i]][2].remove(start_keys[i])

        # 4 step neighbors
        close[start_keys[i]][4] = set()
        for two_step in close[start_keys[i]][2]:
            for c in row[two_step]:
                close[start_keys[i]][4] = close[start_keys[i]][4].union(set(column[c]))
        close[start_keys[i]][4].remove(start_keys[i])

        # 6 step neighbors
        close[start_keys[i]][6] = set()
        for two_step in close[start_keys[i]][4]:
            for c in row[two_step]:
                close[start_keys[i]][6] = close[start_keys[i]][6].union(set(column[c]))
        close[start_keys[i]][6].remove(start_keys[i])

    return close


if __name__ == '__main__':
    row = defaultdict(list)     # 记录行点的邻居
    column = defaultdict(list)  # 记录列点的邻居

    file_path = 'Example.csv'
    with open(file_path, 'r') as file:
        lines = csv.reader(file, delimiter=',')
        for line in lines:
            for num_column, friend in enumerate(line):
                if friend == '1':
                    # 从 1 开始表示各点而非 0
                    row[lines.line_num].append(num_column + 1)
                    column[num_column + 1].append(lines.line_num)

    cut_single()
    start_keys = list(row.keys())   # 作为环的起点候选
    distance = early_stop()

    save_path = 'result.txt'
    with open(save_path, 'w') as file:
        # 这部分处理速度比较快，不必用多进程
        file.write('4: ' + str(cycles(4, start_keys, row, column, distance)) + '\n')
        file.write('6: ' + str(cycles(6, start_keys, row, column, distance)) + '\n')
        file.write('8: ' + str(cycles(8, start_keys, row, column, distance)) + '\n')

        # 多进程处理，最大化利用 CPU
        num_of_process = 24
        file.write('10: ' + str(cycles_multi(10, num_of_process)) + '\n')
        file.write('12: ' + str(cycles_multi(12, num_of_process)) + '\n')
        file.write('14: ' + str(cycles_multi(14, num_of_process)))
