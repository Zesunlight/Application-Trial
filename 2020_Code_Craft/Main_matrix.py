from collections import defaultdict
from functools import cmp_to_key
from pprint import pprint
import multiprocessing as mp
import numpy as np
import time
import copy
import gc


def flow_matrix(stream):
    index_to_person = set()
    later_delete = []
    for start, candidate in stream.items():
        for n, c in enumerate(candidate):
            if c in stream:
                index_to_person.add(c)
            else:
                candidate.pop(n)
                if len(candidate) == 0:
                    later_delete.append(start)

    for l in later_delete:
        if l in index_to_person:
            index_to_person.remove(l)

    index_to_person = list(index_to_person)
    print(f'length of index_to_person: {len(index_to_person)}')
    person_to_index = {}
    for i, p in enumerate(index_to_person):
        person_to_index[p] = i

    flow = np.zeros((len(index_to_person), len(index_to_person)))
    for start in index_to_person:
        for follow in stream[start]:
            if follow in person_to_index:
                flow[person_to_index[start]][person_to_index[follow]] = 1
    flow = flow == 1
    print(flow.shape)

    return index_to_person, flow


def two_point(one_step):
    two_step = np.dot(one_step, one_step)
    np.fill_diagonal(two_step, False)

    # two_step_path = [[[] for _ in range(number_of_candidate)] for _ in range(number_of_candidate)]
    two_step_path = defaultdict(dict)
    for i in range(number_of_candidate):
        for j in range(number_of_candidate):
            if two_step[i][j]:
                # print(index_to_person[i], index_to_person[j])
                for k in range(number_of_candidate):
                    if one_step[i][k] and one_step[k][j]:
                        if j in two_step_path[i]:
                            two_step_path[i][j].append([i, k, j])
                        else:
                            two_step_path[i][j] = [[i, k, j]]
                # pprint(two_step_path[i][j])
    return two_step, two_step_path


def three_point(two_step, two_step_path, index_to_person, flow):
    three_step = np.matmul(two_step, flow)
    three_step_path = [[[] for _ in range(number_of_candidate)] for _ in range(number_of_candidate)]
    for i in range(number_of_candidate):
        for j in range(number_of_candidate):
            if three_step[i][j] >= 1:
                for k in range(number_of_candidate):
                    if two_step[i][k] >= 1 and flow[k][j] == 1:
                        if i == j:
                            for path in two_step_path[i][k]:
                                if path[0] == min(path):
                                    print(','.join([str(index_to_person[p]) for p in path]))
                        else:
                            temp = copy.deepcopy(two_step_path[i][k])
                            for t in temp:
                                t.append(j)
                            three_step_path[i][j].extend(temp)
    np.fill_diagonal(three_step, 0)
    return three_step, three_step_path


def seven_point(next_step, next_step_path, one_step, cycle_path):
    global sum
    for i in range(number_of_candidate):
        for k in range(number_of_candidate):
            if next_step[i][k] and one_step[k][i]:
                for path in next_step_path[i][k]:
                    if path[0] == min(path):
                        # print(','.join([str(index_to_person[p]) for p in path]))
                        cycle_path.append(','.join([str(index_to_person[p]) for p in path]))
                        sum += 1


def criterion(path_1, path_2):
    for i in range(len(path_1)):
        if path_1[i] < path_2[i]:
            return -1
        elif path_1[i] > path_2[i]:
            return 1
    return 0


def number_point(former_step, former_step_path, one_step, cycle_path):
    global sum
    current_step = np.dot(former_step, one_step)
    # current_step_path = [[[] for _ in range(number_of_candidate)] for _ in range(number_of_candidate)]
    current_step_path = defaultdict(dict)
    for i in range(number_of_candidate):
        for j in range(number_of_candidate):
            if current_step[i][j]:
                temp_path = []
                modify = True
                for k in range(number_of_candidate):
                    if former_step[i][k] and one_step[k][j]:
                        if i == j:
                            for path in former_step_path[i][k]:
                                if path[0] == min(path):
                                    # print(','.join([str(index_to_person[p]) for p in path]))
                                    temp_path.append(path)
                                    sum += 1
                        else:
                            for t in former_step_path[i][k]:
                                if j not in t:
                                    modify = False
                                    if j in current_step_path[i]:
                                        current_step_path[i][j].append(t + [j])
                                    else:
                                        current_step_path[i][j] = [t + [j]]
                if modify:
                    current_step[i][j] = False
                if i == j:
                    temp_path.sort(key=cmp_to_key(criterion))
                    for path in temp_path:
                        cycle_path.append(','.join([str(index_to_person[p]) for p in path]))

    np.fill_diagonal(current_step, False)
    return current_step, current_step_path


if __name__ == '__main__':
    stream = defaultdict(list)
    sum = 0
    trace = [[], [], [], [], []]

    # data_path = '/data/test_data.txt'
    data_path = r'C:\Users\DF\Desktop\TestData\3738\test_data.txt'
    with open(data_path, 'r') as account:
        for line in account:
            giver, receiver, _ = line.split(',')
            stream[int(giver)].append(int(receiver))
    # print('load data finish')

    # start_keys = sorted(list(stream.keys()))
    # for item in start_keys:
    #     stream[item].sort()
    # print('sort stream finish')

    index_to_person, flow = flow_matrix(stream)
    number_of_candidate = len(index_to_person)
    two_step, two_step_path = two_point(flow)
    print('foundation complete')

    three_step, three_step_path = number_point(two_step, two_step_path, flow, trace[0])
    print(sum)
    del two_step_path
    del two_step
    gc.collect()

    four_step, four_step_path = number_point(three_step, three_step_path, flow, trace[1])
    print(sum)
    del three_step_path
    del three_step
    gc.collect()

    five_step, five_step_path = number_point(four_step, four_step_path, flow, trace[2])
    print(sum)
    del four_step_path
    del four_step
    gc.collect()

    six_step, six_step_path = number_point(five_step, five_step_path, flow, trace[3])
    print(sum)
    del five_step_path
    del five_step
    gc.collect()

    seven_point(six_step, six_step_path, flow, trace[4])
    print(sum)

    # result_path = '/projects/student/result.txt'
    result_path = r'C:\Users\DF\Desktop\TestData\3738\result_self_matrix.txt'
    with open(result_path, 'w') as result:
        result.write(str(sum) + '\n')
        for item in trace:
            for i in item:
                result.write(i + '\n')
