# -*- coding: UTF-8 -*-

"""
=================================================
@File    : cycle_describe.py
@Author  : ZYZ
@Date    : 2020/05/03
@Problem : https://www.nowcoder.com/discuss/390140
=================================================="""


import csv
from collections import defaultdict
from itertools import combinations, product


def cut_single():
    # 若某个点的度为 1，则该点不会出现在环中，除去该点与邻居的连线
    # 对行、列的点反复进行该操作
    # 去除 row、column 中的非环点与其邻居的连线

    for r in row:
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

    for c in column:
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


def explore_path():
    # 从 row 中的结点出发，2步之后，到达 row 中的其他结点，记录所有路径
    two_step_path = defaultdict(dict)
    for start in row:
        for opposite in row[start]:
            for neighbor in column[opposite]:
                # 下一个 row 中的点大于起点，避免一条路正走倒走
                if neighbor > start:
                    if neighbor in two_step_path[start]:
                        two_step_path[start][neighbor].append((start, -opposite, neighbor))
                    else:
                        two_step_path[start][neighbor] = [(start, -opposite, neighbor)]

    # 从 row 中的结点出发，4步之后，到达 row 中的结点
    # 记录长度为 4 的符合条件的环的个数
    # 记录其余路径（每条路径上无重复的点），4步可达
    four_step_path = defaultdict(dict)
    num_of_four_cycle = 0
    for start in two_step_path:
        two_step_path_from_start = two_step_path[start]
        for two_step_neighbor in two_step_path_from_start:
            for opposite in row[two_step_neighbor]:
                for neighbor in column[opposite]:
                    if neighbor == start:
                        for part_path in two_step_path_from_start[two_step_neighbor]:
                            if opposite != -part_path[1]:
                                num_of_four_cycle += 1
                    elif neighbor > start and neighbor != two_step_neighbor:
                        candidates = [part + (-opposite, neighbor)
                                      for part in two_step_path_from_start[two_step_neighbor]
                                      if opposite != -part[1]]
                        if neighbor in four_step_path[start]:
                            four_step_path[start][neighbor].extend(candidates)
                        else:
                            if candidates:
                                four_step_path[start][neighbor] = candidates
    # 每个环会重复计数一次（正走、倒走）
    num_of_four_cycle = num_of_four_cycle // 2

    # 从 row 中的结点出发，6步之后，到达 row 中的结点
    # 记录长度为 6 的符合条件的环的个数，用 set 做去重
    # 记录其余路径（每条路径上无重复的点），6步可达
    # 基于 6 步可达，记录 7 步可达
    six_step_path = defaultdict(dict)
    seven_step_path = defaultdict(dict)
    num_of_six_cycle = 0
    for start in four_step_path:
        six_step_cycle = set()
        four_step_path_from_start = four_step_path[start]
        for four_step_neighbor in four_step_path_from_start:
            for opposite in row[four_step_neighbor]:
                for neighbor in column[opposite]:
                    if neighbor == start:
                        for part_path in four_step_path_from_start[four_step_neighbor]:
                            if -opposite not in (part_path[1], part_path[3]):
                                candidate_path = list(part_path) + [-opposite]
                                candidate_path.sort()
                                six_step_cycle.add(tuple(candidate_path))
                    elif neighbor > start and neighbor != four_step_neighbor:
                        candidates = [part + (-opposite, neighbor)
                                      for part in four_step_path_from_start[four_step_neighbor]
                                      if -opposite not in (part[1], part[3]) and neighbor != part[2]]
                        for middle in row[neighbor]:
                            for path in candidates:
                                if -middle not in (path[1], path[3], path[5]):
                                    if -middle in seven_step_path[start]:
                                        seven_step_path[start][-middle].append((path + (-middle,)))
                                    else:
                                        seven_step_path[start][-middle] = [path + (-middle,)]
                        if neighbor in six_step_path[start]:
                            six_step_path[start][neighbor].extend(candidates)
                        else:
                            if candidates:
                                six_step_path[start][neighbor] = candidates
        num_of_six_cycle += len(six_step_cycle)

    return two_step_path, four_step_path, six_step_path, seven_step_path, num_of_four_cycle, num_of_six_cycle


def find_eight_step_cycles():
    # 寻找长度为 8 的环
    # 基于 6 步可达的路径信息，找到 6 步后可到达的点 last
    # 再从起点出发，寻找走 2 步可达 last 的且与已有路径不含重复的路径，即构成环
    num_of_eight_cycle = 0
    for start in six_step_path:
        eight_step_cycle = set()
        six_step_path_from_start = six_step_path[start]
        two_step_path_from_start = two_step_path[start]
        for last in (set(two_step_path_from_start) & set(six_step_path_from_start)):
            for part_path, bridge in product(six_step_path_from_start[last], two_step_path_from_start[last]):
                # 避免同一个环的某些两次计数
                if bridge[1] >= part_path[1]:
                    continue
                # 两部分路径若有重复点，则构不成环
                if bridge[1] in (part_path[3], part_path[5]):
                    continue
                candidate_path = list(part_path) + [bridge[1]]
                candidate_path.sort()
                # 同一起点的路径去重
                eight_step_cycle.add(tuple(candidate_path))
        num_of_eight_cycle += len(eight_step_cycle)

    return num_of_eight_cycle


def find_ten_step_cycles():
    # 寻找长度为 10 的环
    # 从起点正走 6 步到达 next_to_last，倒走 4 步到达 next_to_last
    # 去除有重复点的路径，即构成环
    num_of_ten_cycle = 0
    for start in six_step_path.keys():
        ten_step_cycle = set()
        six_step_path_from_start = six_step_path[start]
        four_step_path_from_start = four_step_path[start]
        for next_to_last in (set(six_step_path_from_start) & set(four_step_path_from_start)):
            for part_path, part_back_path in product(six_step_path_from_start[next_to_last], four_step_path_from_start[next_to_last]):
                # 避免同一个环的某些两次计数
                if part_back_path[1] >= part_path[1]:
                    continue
                # 两部分路径若有重复点，则构不成环
                if part_back_path[1] not in (part_path[3], part_path[5]) and \
                        part_back_path[3] not in (part_path[1], part_path[3], part_path[5]) and \
                        part_back_path[2] not in (part_path[2], part_path[4]):
                    candidate_path = list(part_path) + list(part_back_path)[1:-1]
                    candidate_path.sort()
                    ten_step_cycle.add(tuple(candidate_path))
        num_of_ten_cycle += len(ten_step_cycle)

    return num_of_ten_cycle


def find_twelve_step_cycles():
    # 寻找长度为 12 的环
    # 从起点正走 6 步到达 last_but_two，倒走 6 步到达 last_but_two
    # 去除有重复点的路径，即构成环
    num_of_twelve_cycle = 0
    for start in six_step_path.keys():
        twelve_step_cycle = set()
        six_step_path_from_start = six_step_path[start]
        for last_but_two in six_step_path_from_start:
            for part_path, part_back_path in combinations(six_step_path_from_start[last_but_two], 2):
                # 两部分路径若有重复点，则构不成环
                if part_back_path[1] not in (part_path[1], part_path[3], part_path[5]) and \
                        part_back_path[3] not in (part_path[1], part_path[3], part_path[5]) and \
                        part_back_path[5] not in (part_path[1], part_path[3], part_path[5]) and \
                        part_back_path[2] not in (part_path[2], part_path[4]) and \
                        part_back_path[4] not in (part_path[2], part_path[4]):
                    candidate_path = list(part_path) + list(part_back_path)[1:-1]
                    candidate_path.sort()
                    twelve_step_cycle.add(tuple(candidate_path))
        num_of_twelve_cycle += len(twelve_step_cycle)

    return num_of_twelve_cycle


def find_fourteen_step_cycle():
    # 寻找长度为 14 的环
    # 从起点正走 7 步，倒走 7 步，交于同一点
    # 去除有重复点的路径，即构成环
    num_of_fourteen_cycle = 0
    for start in seven_step_path:
        fourteen_step_cycle = set()
        seven_step_path_from_start = seven_step_path[start]
        for meet in seven_step_path_from_start:
            for yang, yin in combinations(seven_step_path_from_start[meet], 2):
                if yang[1] in (yin[1], yin[3], yin[5]) or \
                        yang[3] in (yin[1], yin[3], yin[5]) or \
                        yang[5] in (yin[1], yin[3], yin[5]) or \
                        yang[2] in (yin[2], yin[4], yin[6]) or \
                        yang[4] in (yin[2], yin[4], yin[6]) or \
                        yang[6] in (yin[2], yin[4], yin[6]):
                    continue
                else:
                    candidate_path = list(yang + yin[1:-1])
                    candidate_path.sort()
                    fourteen_step_cycle.add(tuple(candidate_path))
        num_of_fourteen_cycle += len(fourteen_step_cycle)

    return num_of_fourteen_cycle


if __name__ == '__main__':
    import time
    begin = time.time()
    print(time.asctime(time.localtime(time.time())))
    row = defaultdict(list)
    column = defaultdict(list)

    file_path = 'Example.csv'
    with open(file_path, 'r') as file:
        lines = csv.reader(file, delimiter=',')
        for line in lines:
            for num_column, friend in enumerate(line):
                if friend == '1':
                    # 存储朋友信息
                    row[lines.line_num].append(num_column + 1)
                    column[num_column + 1].append(lines.line_num)
    # 数据预处理
    cut_single()
    two_step_path, four_step_path, six_step_path, seven_step_path, four_step_cycle, six_step_cycle = explore_path()

    print(four_step_cycle, six_step_cycle)
    print(find_eight_step_cycles(), time.asctime(time.localtime(time.time())))
    print(find_ten_step_cycles(), time.asctime(time.localtime(time.time())))
    print(find_twelve_step_cycles(), time.asctime(time.localtime(time.time())))
    print(find_fourteen_step_cycle(), time.asctime(time.localtime(time.time())))
    print(time.time() - begin)

    # save_path = 'result.txt'
    # with open(save_path, 'w') as file:
    #     file.write(str(four_step_cycle) + '\n')
    #     file.write(str(six_step_cycle) + '\n')
    #     file.write(str(find_eight_step_cycles()) + '\n')
    #     file.write(str(find_ten_step_cycles()) + '\n')
    #     file.write(str(find_twelve_step_cycles()) + '\n')
    #     file.write(str(find_fourteen_step_cycle()))
