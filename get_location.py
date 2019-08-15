UAVsLoc = []
usersLoc = []

#with open('UAV-path.txt') as f:
#    for line in f:
#        new_list = []
#        for lacation in line[:-1].split('\t'):
#             new_list.append(lacation.split(','))
#        UAVsLoc.append(new_list)

with open('usersLoc.txt') as f:
    for line in open('usersLoc.txt'):
        for lacation in line.split('\t'):
            _ = lacation.split(',')
            _[0] = float(_[0])
            _[1] = float(_[1])
            usersLoc.append(_)
