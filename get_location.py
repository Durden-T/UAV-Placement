#with open('UAV-path.txt') as f:
#    for line in f:
#        new_list = []
#        for lacation in line[:-1].split('\t'):
#             new_list.append(lacation.split(','))
#        UAVs.append(new_list)
import random


def getUserFromFile():
    usersLoc = []
    with open('usersLoc.txt') as f:
        for line in open('usersLoc.txt'):
            for lacation in line.split('\t'):
                _ = lacation.split(',')
                _[0] = float(_[0])
                _[1] = float(_[1])
                usersLoc.append(_)
    return usersLoc


def getUserRandom(count):
    usersLoc = []
    for i in range(count):
        usersLoc.append([random.uniform(1,1200),random.uniform(1,1200)])
        #print(usersLoc[i])
    return usersLoc