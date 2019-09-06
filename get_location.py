import random
import json

def getUserFromFile( ):
    with open('usersLoc.txt') as f:
        return json.load(f)

    #return [list(map(float,location.split(','))) for line in f for location in
    #line.split('\t')]

    #usersLoc = []
    #with open('usersLoc.txt') as f:
    #    for line in f:
    #        for location in line.split('\t'):
    #            t=location.split(',')
    #            usersLoc.append(list(map(float,location.split(','))))
    #return usersLoc

def getUserRandom(count):
    return [[random.uniform(1,1200),random.uniform(1,1200)]
             for i in range(count)]
    #usersLoc = []
    #for i in range(count):
    #    usersLoc.append([random.uniform(1,1200),random.uniform(1,1200)])
    #    #print(usersLoc[i])
    #return usersLoc

def writeUserInFile(count):
    with open('usersLoc.txt','w') as f:
        json.dump([[random.uniform(1,1200),random.uniform(1,1200)]
              for i in range(count)],f)

