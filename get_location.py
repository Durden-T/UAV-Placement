UAV_path_list = []
user_path_list = []

#with open('UAV-path.txt') as f:
#    for line in f:
#        new_list = []
#        for lacation in line[:-1].split('\t'):
#             new_list.append(lacation.split(','))
#        UAV_path_list.append(new_list)

with open('user-path.txt') as f:
    for line in open('user-path.txt'):
        for lacation in line.split('\t'):
            _ = lacation.split(',')
            _[0] = float(_[0])
            _[1] = float(_[1])
            user_path_list.append(_)
