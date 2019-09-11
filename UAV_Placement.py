from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from PIL.Image import *

import sys
import numpy as np

import copy
import time


from algorithms import strategies
import common
import shaderProg
import loadTexture
import particle
from get_location import *

window = None

#UAV覆盖半径
UAVradius = 0
# 飞机高度
UAV_height = 2.6
# 地图长宽
UAV_size = 120

#UAV结构list
UAVs = [ ]
#user结构list
users = [ ]
#UAV坐标list
UAVsLoc = [ ]


camera = common.camera()
# 地形
UAV = common.UAV(UAV_size,UAV_size,0.1,0.1)
#the shaderall,colorMap,hightMap Should be placed after gl init,otherwise all 0
shaderall = None
tf = None
ps = None
colorMap = 0 
hightMap = 0
x = 0
z = 0


def make_UAV(UAV):
    UAV.move_active += 1
    if UAV.move_active == 250:
        UAV.move_active = 0
        UAV.x_speed = 0
        UAV.z_speed = 0
    # 程序对象program作为当前渲染状态的一部分
    x1 = UAV.x
    z1 = UAV.z
    x1 += UAV.x_speed
    z1 += UAV.z_speed
    UAV.change(x1, z1)

    # 高度关联
    # glUniform
    # location：指明要更改的uniform变量的位置
    # v0, v1, v2, v3：指明在指定的uniform变量中要使用的新值
    # 利用x, y坐标确认高度
    glUniform1f(shaderall.updateProgram.xl, 0)
    glUniform1f(shaderall.updateProgram.yl, 0)
    # 补偿高度
    glUniform1f(shaderall.updateProgram.sphereRadius, UAV_height)
    glUniform1i(shaderall.updateProgram.tex0, 1)
    glUniform2f(shaderall.updateProgram.xz, 0, 0)
    getMVP(x1, z1)
    UAV.draw()

def make_user(userple):
    userple.move_active += 1
    if userple.move_active == 250:
        userple.move_active = 0
        userple.x_speed = 0
        userple.z_speed = 0
    # 程序对象program作为当前渲染状态的一部分
    x1 = userple.x
    z1 = userple.z
    x1 += userple.x_speed
    z1 += userple.z_speed
    userple.change(x1, z1)
    # 高度关联
    # glUniform
    # location：指明要更改的uniform变量的位置
    # v0, v1, v2, v3：指明在指定的uniform变量中要使用的新值
    # 利用x, y坐标确认高度
    glUniform1f(shaderall.updateProgram.xl, UAV.xl)
    glUniform1f(shaderall.updateProgram.yl, UAV.yl)
    # 补偿半径
    glUniform1f(shaderall.updateProgram.sphereRadius, userple.radius)
    glUniform1i(shaderall.updateProgram.tex0, 1)
    glUniform2f(shaderall.updateProgram.xz, x1, z1)
    getMVP(x1, z1)
    userple.draw()

def UAV_move(UAV, x, z):
    UAV.move_active += 1
    if UAV.move_active == 250:
        UAV.move_active = 0
        UAV.x_speed = 0
        UAV.z_speed = 0
    # 程序对象program作为当前渲染状态的一部分
    x1 = UAV.x
    z1 = UAV.z
    x_cha = x - x1
    z_cha = z - z1
    x_speed = x_cha / 250
    z_speed = z_cha / 250
    x1 += UAV.x_speed
    z1 += UAV.z_speed
    UAV.change(x1, z1)
    glUseProgram(shaderall.updateProgram)
    # 高度关联
    # glUniform
    # location：指明要更改的uniform变量的位置
    # v0, v1, v2, v3：指明在指定的uniform变量中要使用的新值
    # 利用x, y坐标确认高度
    glUniform1f(shaderall.updateProgram.xl, 0)
    glUniform1f(shaderall.updateProgram.yl, 0)
    # 补偿半径
    glUniform1f(shaderall.updateProgram.sphereRadius, UAV_height)
    glUniform1i(shaderall.updateProgram.tex0, 1)
    glUniform2f(shaderall.updateProgram.xz, 0, 0)
    getMVP(x1, z1)
    UAV.draw()

def userple_move(userple, x, z):
    userple.move_active += 1
    if userple.move_active == 250:
        userple.move_active = 0
        userple.x_speed = 0
        userple.z_speed = 0
    # 程序对象program作为当前渲染状态的一部分
    x1 = userple.x
    z1 = userple.z
    x_cha = x - x1
    z_cha = z - z1
    x_speed = x_cha / 250
    z_speed = z_cha / 250
    x1 += userple.x_speed
    z1 += userple.z_speed
    userple.change(x1, z1)
    glUseProgram(shaderall.updateProgram)
    # 高度关联
    # glUniform
    # location：指明要更改的uniform变量的位置
    # v0, v1, v2, v3：指明在指定的uniform变量中要使用的新值
    # 利用x, y坐标确认高度
    glUniform1f(shaderall.updateProgram.xl, UAV.xl)
    glUniform1f(shaderall.updateProgram.yl, UAV.yl)
    # 补偿半径
    glUniform1f(shaderall.updateProgram.sphereRadius, userple.radius)
    glUniform1i(shaderall.updateProgram.tex0, 1)
    glUniform2f(shaderall.updateProgram.xz, x1, z1)
    getMVP(x1, z1)
    userple.draw()

def DrawGLScene( ):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # 将当前矩阵指定为投影矩阵。参数是GL_MODELVIEW，这个是对模型视景的操作，接下来的语句描绘一个以模型为基础的适应，这样来设置参数
    glMatrixMode(GL_MODELVIEW)
    # 链接无人机和人
    camera.setLookat()
    # 设置激活的纹理单元
    glActiveTexture(GL_TEXTURE0)
    # 将一个命名的纹理绑定到一个纹理目标上
    glBindTexture(GL_TEXTURE_2D, colorMap)
    # 设置激活的纹理单元
    glActiveTexture(GL_TEXTURE1)
    # 将一个命名的纹理绑定到一个纹理目标上
    glBindTexture(GL_TEXTURE_2D, hightMap)     
    #UAV
    # 程序对象program作为当前渲染状态的一部分
    glUseProgram(shaderall.UAVProgram)
    #设置uniform采样器的位置值，或者说纹理单元，保证每个uniform采样器对应着正确的纹理单元
    glUniform1i(shaderall.UAVProgram.tex0, 0)
    UAV.draw()

    glUseProgram(shaderall.updateProgram)
    for pla in UAVs:
        make_UAV(pla)
    for user in users:
        make_user(user)

    #glUseProgram(0)
    #glUseProgram(shaderall.particleProgram)
    #glUniform1i(shaderall.particleProgram.UAV, 1)
    #glUniform2f(shaderall.particleProgram.UAVSacle,UAV.xl,UAV.yl)
    #glUniform3f(shaderall.particleProgram.sphere,eyeLoc[0],sph.radius,eyeLoc[2])
    #ps.render(shaderall.particleProgram)
    #glUseProgram(0)

    glUseProgram(0)
    glColor3f(0.9, 0.9, 0.9)
    #glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('a'))
    glLineWidth(2)
    glBegin(GL_LINES)
    for user in users:
        #根据无人机与人的距离，选择距离最近的无人机连线
        nearest = min(UAVs,key=lambda pla:(pla.x - user.x) ** 2 + (pla.z - user.z) ** 2)
        glVertex3f(nearest.x, 0.7 + UAV_height, nearest.z)
        glVertex3f(user.x, UAV.getHeight(user.x, user.z) + 0.1, user.z)
    glEnd()

    # 设置激活的纹理单元
    glActiveTexture(GL_TEXTURE0)
    # 将一个命名的纹理绑定到一个纹理目标上
    glBindTexture(GL_TEXTURE_2D, 0)
    # 开启和关闭服务器端GL功能
    glDisable(GL_TEXTURE_2D)
    # 设置激活的纹理单元
    glActiveTexture(GL_TEXTURE1)
    # 将一个命名的纹理绑定到一个纹理目标上
    glBindTexture(GL_TEXTURE_2D, 0)
    # 开启和关闭服务器端GL功能
    glDisable(GL_TEXTURE_2D)

    # 是OpenGL中GLUT工具包中用于实现双缓冲技术的一个重要函数。该函数的功能是交换两个缓冲区指针。
    # 但当我们进行复杂的绘图操作时，画面便可能有明显的闪烁。解决这个问题的关键在于使绘制的东西同时出现在屏幕上。
    # 所谓双缓冲技术， 是指使用两个缓冲区： 前台缓冲和后台缓冲。前台缓冲即我们看到的屏幕，后台缓冲则在内存当中，
    # 对我们来说是不可见的。每次的所有绘图操作都在后台缓冲中进行， 当绘制完成时， 把绘制的最终结果复制到屏幕上，
    # 这样， 我们看到所有GDI元素同时出现在屏幕上，从而解决了频繁刷新导致的画面闪烁问题。
    glutSwapBuffers()


def getMVP(x, z):
    v = np.array(glGetFloatv(GL_MODELVIEW_MATRIX), np.float32)
    p = np.array(glGetFloatv(GL_PROJECTION_MATRIX), np.float32)
    m = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [x, 0, z, 1]], np.float32)
    #print(m)
    # glUniformMatrix4fv函数向其传递数据。
    # location：指明要更改的uniform变量的位置
    # count：指明要更改的矩阵个数
    # transpose：指明是否要转置矩阵，并将它作为uniform变量的值。必须为GL_FALSE。
    # value：指明一个指向count个元素的指针，用来更新指定的uniform变量。
    glUniformMatrix4fv(shaderall.updateProgram.pMatrix, 1, GL_FALSE, p)
    glUniformMatrix4fv(shaderall.updateProgram.vMatrix, 1, GL_FALSE, v)
    glUniformMatrix4fv(shaderall.updateProgram.mMatrix, 1, GL_FALSE, m)
    #glgetfloat
def mouseButton(button, mode, x, y):    
    if button == GLUT_RIGHT_BUTTON:
        camera.mouselocation = [x,y]


def ReSizeGLScene(Width, Height): 
    if Height == 0:
        Height = 1
    glViewport(0, 0, Width, Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width) / float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


#无人机移动 时钟信号回调
def timerProc(id):
    for index, i in enumerate(UAVsLoc):
        #print(index, i)
        UAVs[index].move_location(UAVs[index].x,UAVs[index].z, float(i[0]) / 120 - 5, float(i[1]) / 120 - 5)
    glutTimerFunc(1000, timerProc, 1)


##location_index = 0
##用户移动 时钟信号回调
#def timerProc(id):

#    #global location_index
#    #location_index += 1
#    #for index, i in enumerate(UAVs[location_index]):
#      # print(index, i)
#      # UAVs[index].move_location(UAVs[index].x,
#      # UAVs[index].z, float(i[0])/120 - 5, float(i[1])/120 - 5)
    
#    pass

#    for index, i in enumerate(usersLoc[0]):
#        #print(index, i)
#        users[index].move_location(users[index].x,
#        users[index].z, float(i[0]) / 120 - 5, float(i[1]) / 120 - 5)
#    glutTimerFunc(1000, timerProc, 1)


# gluLookAt(0, 15, 0, 0, 0, 0, 1.0, 0, 0.0)
def keypress(key, x, y):
    if key == GLUT_KEY_UP:
        camera.move(0., 0., 1 * camera.offest)
    if key == GLUT_KEY_RIGHT:
        camera.move(-1 * camera.offest, 0., 0.)
    if key == GLUT_KEY_LEFT:
        camera.move(1 * camera.offest, 0., 0.)
    if key == GLUT_KEY_DOWN:
        camera.move(0., 0., -1 * camera.offest)
    if key == GLUT_KEY_F12:
        camera.change_overlook()


#地图大小1200*1200
def main( ):
    global window
    global UAVs
    global UAVsLoc
    global colorMap
    global hightMap
    global shaderall
    
    #用户数量
    c = input('请选择用户位置输入方式\n1.随机生成\t2.从usersLoc.txt中读取\n')
    if c == '1':
        userNum = int(input('请输入用户数量：'))
    #D/r
    DR = float(input('请输入地图边长D与UAV覆盖半径r之比：'))
    #测试次数
    testCount = int(input('请输入测试次数：'))
    #计算UAV半径
    UAVradius = 1200 / DR
    usersLoc = [ ]

    choice = int(input('请选择算法：\n1.随机覆盖算法\t2.条带覆盖算法\t3.螺旋覆盖算法\t4.对比测试所有算法（无图像）\n'))

    if choice != 4:
        #测试单个算法
        strategy = strategies[choice - 1]
        totalTime = 0
        count = 0

        for i in range(testCount):
            if c == '1':
                #随机生成用户
                usersLoc = getUserRandom(userNum)
            else:
                #从文件中读取用户
                usersLoc = getUserFromFile()
            users.clear()
            for index, i in enumerate(usersLoc):
                users.append(common.sphere(16, 16, 0.1, i[0] / 120 - 5, i[1] / 120 - 5))
            #计算耗时
            start = time.time()
            UAVsLoc = strategy(usersLoc,UAVradius)
            end = time.time()
            totalTime += end - start
            count += len(UAVsLoc)
        print('{}：{}次测试的平均耗时为{:.3f}ms,平均需要{}架无人机。'.format(strategy.__doc__,testCount,totalTime * 1000 / testCount,count / testCount))

    else:
        #对比所有算法
        for strategy in strategies:
            totalTime = 0
            count = 0
            for i in range(testCount):
                if c == '1':
                    #随机生成用户
                    usersLoc = getUserRandom(userNum)
                else:
                    #从文件中读取用户
                    usersLoc = getUserFromFile()
                users.clear()
                for index, i in enumerate(usersLoc):
                    users.append(common.sphere(16, 16, 0.1, i[0] / 120 - 5, i[1] / 120 - 5))
                #计算耗时
                start = time.time()
                UAVsLoc = strategy(usersLoc,UAVradius)
                end = time.time()
                totalTime += end - start
                count += len(UAVsLoc)
            print('{}：{}次测试的平均耗时为{:.3f}ms,平均需要{}架无人机。'.format(strategy.__doc__,testCount,totalTime * 1000 / testCount,count / testCount))
        return

    #无人机初始位置
    for i in range(len(UAVsLoc)):
        UAVs.append(common.sphere(16, 16, 0.1, 0, 0))

    #glutInit(sys.argv)
    # 初始化
    glutInit([ ])
    # 设置图形显示模式
    # GLUT_RGBA建立RGBA模式的窗口
    # GLUT_DOUBLE使用双缓存，以避免把计算机作图的过程都表现出来，或者为了平滑地实现动画
    # GLUT_DEPTH使用深度缓存
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    # 窗口大小设置
    glutInitWindowSize(1920,1080)
    glutInitWindowPosition(0,0)
    window = glutCreateWindow(b"UAV-Placement")

    # 为当前窗口设置显示回调函数
    glutDisplayFunc(DrawGLScene)
    # 设置空闲回调函数
    glutIdleFunc(DrawGLScene)
    # 指定当窗口的大小改变时调用的函数
    glutReshapeFunc(ReSizeGLScene)
    # 注册当前窗口的鼠标回调函数
    glutMouseFunc(mouseButton)
    # 设置移动回调函数
    glutMotionFunc(camera.mouse)
    # 定时器回调函数
    glutTimerFunc(1000, timerProc, 1)

    # 注册当前窗口的键盘回调函数
    # glutKeyboardFunc(camera.keypress)
    # 设置当前窗口的特定键的回调函数
    # glutSpecialFunc(camera.keypress)

    # 注册当前窗口的键盘回调函数
    # glutKeyboardFunc(keypress2)
    # 设置当前窗口的特定键的回调函数
    glutSpecialFunc(keypress)
    # 背景颜色
    glClearColor(0.1, 0.1, 1, 0.1)
    # 设置深度缓存的清除值
    glClearDepth(1.0)
    # 开启GL_DEPTH_TEST，进行深度比较并更新深度缓冲区
    glEnable(GL_DEPTH_TEST)
    # GL_SMOOTH采用光滑着色，独立的处理图元中各个顶点的颜色
    glShadeModel(GL_SMOOTH)
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    camera.move(0.0, 1.3, 0)
    camera.setthree(True)
    camera.length = 5
    
    shaderall = shaderProg.allshader()
    #global tf
    #tf = common.transformFeedback(shaderall.tfProgram)
    #global ps
    #ps = particle.particleSystem(1)
    
    colorMap = loadTexture.Texture.loadmap("ground2.bmp")
    # hight map for cpu to gpu
    hightMap = loadTexture.Texture.loadmap("hight.gif")
    # create terrain use cpu
    hightimage = loadTexture.Texture.loadterrain("hight.gif")
    # image = open("ground2.bmp").convert("RGBA")
    UAV.setHeight(hightimage)
    glutMainLoop()

main()
