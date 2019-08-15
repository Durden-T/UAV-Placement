from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from PIL.Image import *
import numpy as np
import sys
import random
import copy


from base import *
import shaderProg
import loadtexture
import particle





eps = 1e-6
xAXIS = np.array([1,0])
# 飞机高度 ?
plane_height = 2.6
# 地图长宽
plane_size = 110


def readUserLoc():
    #with open('UAV-path.txt') as f:
    #    for line in f:
    #        new_list = []
    #        for loc in line[:-1].split('\t'):
    #             new_list.append(loc.split(','))
    #        UAV_path_list.append(new_list)
    userLoc=[]
    with open('userLoc.txt') as f:
        for line in open('userLoc.txt'):
            for loc in line.split('\t'):
                _ = loc.split(',')
                _[0] = float(_[0])
                _[1] = float(_[1])
                userLoc.append(_) 
    return userLoc


#用户初始位置，从userLoc中读取
def addUser(userLoc):
    users=[]
    for index, i in enumerate(userLoc):
        users.append(sphere(16, 16, 0.1, i[0] / 120 - 5, i[1] / 120 - 5))
        return users

#用于求差集
def difference(a,b):
    ret = []
    for i in a :
        if i not in b:
            ret.append(i)
    return ret

#users 用户位置list
def planningUAV(users):
    users.sort(key=compare_angle)
    #for user in users:
        #print(user)
    UAVs = []
    users_un = users #未被覆盖的边界点
    m = 1
    #当仍存在未被覆盖的用户时
    while users_un:     
        users_un_in = []
        users_new = [] #刚被覆盖的点
        users_bo = [] #已被覆盖的边界点

        # 由未被覆盖的用户来重新构造新的边界线。
        users_un_bo = convexHull(users_un)
        users_un_in = difference(users_un,users_un_bo)

        if m == 1 :
            #k = random.choice(users_un_bo)
            k = users_un_bo[0]
        center_index = users_un_bo.index(k) #用于确认下一个center的选择
        users_bo = [k] #当前情况下覆盖的边界点
        center = localCover(k,users_bo,difference(users_un_bo,users_bo))
        #users_new = users_bo #此时为刚被覆盖的边界点
        users_un_bo_new = difference(users_un_bo,users_bo) #更新未被覆盖的边界点

        center = localCover(center,users_bo,users_un_in) #调用完后new为刚被覆盖的所有点

        m = m + 1
        users_un = difference(users_un,users_bo)
        UAVs.append(center)

        temp = (center_index + 1) % len(users_un_bo)

        #在更新后的未被覆盖的边界点中选择一个临近旧center的点，作为新center。
        while temp != center_index:
            if users_un_bo[temp] in users_un_bo_new:
                break #找到下一个点
            else:
                temp = (temp + 1) % len(users_un_bo)

        k = users_un_bo[temp]

    return UAVs

def distance(a,b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

#center 当前中心点
#firstL 第一优先级的点的list 函数被调用前为 必须被 覆盖 调用后为已覆盖
#secondL 第二优先级的点的list 尽可能多 覆盖
def localCover(center,firstL,secondL):
    #UAV覆盖半径
    global UAVradius
    #循环直到secondL为空或return
    while secondL:
        for second in secondL.copy():
            for first in firstL:
                #距离大于2倍半径 无法覆盖
                if distance(second,first) > 2 * UAVradius:
                    secondL.remove(second)
                    break
        for user in secondL.copy():
            #能够被覆盖s
            if distance(user,center) < UAVradius:
                firstL.append(user)
                secondL.remove(user)

        #minIndex = users.index(min(users,key = compare_position))
        k = min(secondL,key=lambda x:distance(x,center),default=None)
        if k:
            #此时k为距离center最近的点
            firstL.append(k)
            #先将k放入firstL中，调用oneCenter尝试观察：能否将firstL全部覆盖
            ans = oneCenter(firstL)
            if  ans[1] <= UAVradius:
                #此时k已在firstL中，把k从secondL中删去，继续循环
                secondL.remove(k)
                center = ans[0]
            else:
                #无法满足当前条件，将k从firstL中删去，返回
                firstL.remove(k)
                break
    return center
        #向量OA叉积向量OB。大于0表示从OA到OB为逆时针旋转
def cross(center,a,b):
    return (a[0] - center[0]) * (b[1] - center[1]) - (a[1] - center[1]) * (b[0] - center[0])

#用以找出最低最左边的点
def compare_position(a):
    return [a[1],a[0]]

#小于。以users[0]当中心点做角度排序，角度由小排到大（即逆时针方向）。
#角度相同時，距离中心点较近的点排前面。
def compare_angle(a):
    global users
    cos_theta = np.arccos(xAXIS.dot(a) / (np.linalg.norm(xAXIS) * np.linalg.norm(a)))
    return [cos_theta,distance([users[0].x,users[0].z],a)]

#解决凸包问题
#users 用户位置list
#Graham's Scan算法
def convexHull(users):
    outs = [[.0,.0]] * len(users)
    minIndex = users.index(min(users,key = compare_position))
    print(minIndex)
    #用最低最左边的点为起点
    users[0] , users[minIndex] = users[minIndex] , users[0]
    #按角度排序
    #users.sort(key=compare_angle)
    # m为凸包顶点数目
    m = 0
    for i in range(len(users)):
        #擦除凹陷的点
        while (m >= 2 and cross(outs[m - 2],outs[m - 1],users[i]) <= 0):
            m = m - 1
        outs[m] = users[i]
        m = m + 1
    return [user for user in outs if user != [.0,.0]]

#获取i,j,k的外接圆,返回圆心,解三元二次方程
def getCentre(i,j,k):
    a,b,c,d = j[0] - i[0],j[1] - i[1],k[0] - j[0],k[1] - j[1]
    e,f = j[0] ** 0.5 + j[1] ** 0.5 - i[0] ** 0.5 - i[1] ** 0.5,k[0] ** 0.5 + k[1] ** 0.5 - j[0] ** 0.5 - j[1] ** 0.5
    return [(f * b - e * d) / (c * b - a * d) / 2.0,(a * f - e * c) / (a * d - b * c) / 2]


#放置中心点，返回半径
#最小圆覆盖问题 见https://blog.csdn.net/wu_tongtong/article/details/79362339
#随机增量法 时空复杂度均为O(n)(玄学)
def oneCenter(points):
    #随机化
    random.shuffle(points)
    #center,radius分别为圆心，半径
    center,radius = points[0],0
    for i in range(1,len(points)):
        #i不在当前圆内,通过精度比较，差距在1eps内可通过
        if distance(center,points[i]) - radius > eps:
            #当前圆变为以i为圆心，枚举第二个点j
            center,radius = points[i],0
            for j in range(i):
                #j不在当前圆内
                if distance(center,points[j]) - radius > eps:
                    #当前圆变为以i,j为直径的圆，枚举第三个点k
                    center = [(points[i][0] + points[j][0]) / 2.0,(points[i][1] + points[j][1]) / 2.0]
                    radius = distance(points[i],points[j]) / 2.0
                    for k in range(j):
                        if distance(center,points[k]) - radius > eps:
                            #当前圆变为i,j,k的外接圆
                            center = getCentre(points[i],points[j],points[k])
                            radius = distance(points[i],center)
    return [center,radius]
    #return [center,radius]

