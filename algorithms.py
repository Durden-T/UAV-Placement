from functools import cmp_to_key,partial
import common
import random
from math import ceil

#精度控制
eps = 1e-6
#条带放置算法中划分条带的比例
k = 1 / 1.5
#UAV半径
UAVradius = 0


def randomPlanning(users,r):
    '''随机放置算法'''
    global UAVradius
    UAVradius = r
    UAVsLoc = [ ]
    while users:
        center = [random.uniform(1,1200),random.uniform(1,1200)]
        while UAVsLoc and any(distance(center,UAV) <= UAVradius for UAV in UAVsLoc):
            center = [random.uniform(1,1200),random.uniform(1,1200)]
        UAVsLoc.append(center)
        for user in users.copy():
            if distance(user,center) <= UAVradius:
                users.remove(user)
    return UAVsLoc


def stripPlanning(users,r):
    '''条带放置算法'''
    global UAVradius
    UAVradius = r
    #条带放置算法中划分条带的宽度
    width = 2 * UAVradius * k
    #条带数
    count = ceil(1200 / width)
    #将地图划分为矩形条带
    strips = [[ ] for i in range(count)]
    for user in users:
        strips[int(user[1] / width)].append(user)
    
    #每条条带单独放置UAV
    UAVsLoc = [[ ] for i in range(count)]

    for i,strip in enumerate(strips):
        strip.sort()
        while strip:
            #取最左边的点
            leftmost = strip[0]
            UAVsLoc[i].append(rectangles(leftmost,strip,width))

    return [UAVloc for strip in UAVsLoc for UAVloc in strip]


#users 用户位置list
def spiralPlanning(users,r):
    '''螺旋放置算法'''
    global UAVradius
    UAVradius = r
    #最左下的点 排序基准点
    datumPoint = min(users,key=lambda x:[x[1],x[0]])
    #先按逆时针排序，便于后续确定下一个k的位置
    cmp = partial(compare_angle,datumPoint)
    users.sort(key=cmp_to_key(cmp))

    UAVsLoc = [ ]
    users_un = users
    users_un_bo = [None]
    #m = 1
    #当仍存在未被覆盖的用户时
    while users_un and users_un_bo:     
        # 由未被覆盖的用户来重新构造新的边界线
        users_un_bo = convexHull(users_un)
        #在更新后的未被覆盖的边界点中选择一个临近旧center的点，作为新center
        #起初排过序，可证此时无需再次排，第一个一定有效
        k = users_un_bo[0]

        users_un_in = difference(users_un,users_un_bo)
        #if m == 1 :
            #k = random.choice(users_un_bo)

        users_bo = [k] #当前情况下覆盖的边界点
        center = localCover(k,users_bo,difference(users_un_bo,users_bo))
        users_un_bo_new = difference(users_un_bo,users_bo) #更新未被覆盖的边界点

        center = localCover(center,users_bo,users_un_in) #调用完后new为刚被覆盖的所有点
        users_un = difference(users_un,users_bo)    

        #m = m + 1
        UAVsLoc.append(center)
        
    return UAVsLoc


def rectangles(cur,strip,width):
    ans = [cur[0] + ((1 - k ** 2) ** 0.5 * 2 * UAVradius) / 2,int(cur[1] / width) * width + width / 2]
    for user in strip.copy():
        if distance(ans,user) <= UAVradius:
            strip.remove(user)
    return ans


#用于求差集
def difference(a,b):
    #ret = []
    #for i in a :
    #    if i not in b:
    #        ret.append(i)
    #return ret
    return [i for i in a if i not in b]


def distance(a,b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


#center 当前中心点
#firstL 第一优先级的点的list 函数被调用前为 必须被 覆盖 调用后为已覆盖
#secondL 第二优先级的点的list 尽可能多 覆盖
#会改变firstL的值 secondL没用 可以直接操作 不担心损坏数据
def localCover(center,firstL,secondL):
    new = center
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
            if distance(user,new) <= UAVradius:
                firstL.append(user)
                secondL.remove(user)

        if secondL:
            k = min(secondL,key=partial(distance,new))
            #此时k为距离new最近的点
            firstL.append(k)
            #先将k放入firstL中，调用oneCenter尝试观察：能否将firstL全部覆盖
            ans = oneCenter(firstL)
            if  ans[1] <= UAVradius:
                #此时k已在firstL中，把k从secondL中删去，继续循环
                secondL.remove(k)
                new = ans[0]
            else:
                #无法满足当前条件，将k从firstL中删去，返回
                firstL.remove(k)
                break
    return new



#向量OA叉积向量OB。大于0表示从OA到OB为逆时针旋转
def cross(center,a,b):
    return (a[0] - center[0]) * (b[1] - center[1]) - (a[1] - center[1]) * (b[0] - center[0])


#小于。以users[0]（最左下的点）当中心点做角度排序，角度由小排到大（即逆时针方向）。
#角度相同時，距离中心点较近的点排前面。
def compare_angle(o,a,b):
    t = cross(o,a,b)
    return -1 if (t > 0 or (t == 0 and distance(a,o) < distance(b,o))) else 1

#解决凸包问题
#users 用户位置list
#Graham's Scan算法
def convexHull(users):
    if len(users) < 2:
        return users
    #找到最左下的点，给基准点赋值
    #i = users.index(min(users,key=lambda x:[x[1],x[0]]))
    datumPoint = users[0]
    cmp = partial(compare_angle,datumPoint)
    users.sort(key=cmp_to_key(cmp))
    outs = users[:2]
    for i in range(2,len(users)):
        #擦除凹陷的点
        while len(outs) >= 2 and cross(outs[-1],outs[- 2],users[i]) > 0:
            outs.pop()
        outs.append(users[i])
    return outs

#获取i,j,k的外接圆,返回圆心,解三元二次方程
def getCentre(i,j,k):
        a,b,c,d = j[0] - i[0],j[1] - i[1],k[0] - j[0],k[1] - j[1]
        e,f = j[0] ** 2 + j[1] ** 2 - i[0] ** 2 - i[1] ** 2,k[0] ** 2 + k[1] ** 2 - j[0] ** 2 - j[1] ** 2
        return [(f * b - e * d) / (c * b - a * d) / 2,
                (a * f - e * c) / (a * d - b * c) / 2]


#放置中心点，返回半径
#最小圆覆盖问题 见https://blog.csdn.net/wu_tongtong/article/details/79362339
#随机增量法 时空复杂度均为O(n)
def oneCenter(points):
    #随机化
    random.shuffle(points)
    #center,radius分别为圆心，半径
    center,radius = points[0],0
    for i in range(len(points)):
        #i不在当前圆内,通过精度比较，差距在1eps内可通过
        if distance(center,points[i]) - radius > eps:
            #当前圆变为以i为圆心，枚举第二个点j
            center,radius = points[i],0
            for j in range(i):
                #j不在当前圆内
                if distance(center,points[j]) - radius > eps:
                    #当前圆变为以i,j为直径的圆，枚举第三个点k
                    center = [(points[i][0] + points[j][0]) / 2,(points[i][1] + points[j][1]) / 2]
                    radius = distance(points[i],center)
                    for k in range(j):
                        if distance(center,points[k]) - radius > eps:
                            #当前圆变为i,j,k的外接圆
                            center = getCentre(points[i],points[j],points[k])
                            radius = distance(points[i],center)
    return (center,radius)

strategies = [randomPlanning,stripPlanning,spiralPlanning]