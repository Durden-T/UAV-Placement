from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from PIL.Image import *
import numpy as np
import sys
import random
import copy
import time

from base import *
from planningUAV import *
from draw import *
import shaderProg
import loadTexture
import particle


window = None

#UAV覆盖半径
UAVradius = 400 
camera = camera()
# 地形
plane = plane(plane_size,plane_size,0.1,0.1)
#the shaderall,colorMap,hightMap Should be placed after gl init,otherwise all 0
shaderall = None
tf = None
ps = None
colorMap = 0 
hightMap = 0
x = 0
z = 0

if __name__ == '__main__':
    users=addUser(readUserLoc())
    time_start = time.time()
    UAVLoc = planningUAV(users)
    time_end = time.time()
    print('totally cost {.5}ms.'.format((time_end - time_start) * 1000))
    
    #无人机初始位置
    for i in range(len(UAVLoc)):
        UAVs.append(sphere(16, 16, 0.1, 0, 0))
    
    #glutInit(sys.argv)
    # 初始化
    glutInit([])
    # 设置图形显示模式
    # GLUT_RGBA建立RGBA模式的窗口
    # GLUT_DOUBLE使用双缓存，以避免把计算机作图的过程都表现出来，或者为了平滑地实现动画
    # GLUT_DEPTH使用深度缓存
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    # 窗口大小设置
    glutInitWindowSize(1920,1080)
    glutInitWindowPosition(0,0)
    window = glutCreateWindow(b"opengl")

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
    #tf = transformFeedback(shaderall.tfProgram)
    #global ps
    #ps = particle.particleSystem(1)
    colorMap = loadtexture.Texture.loadmap("ground2.bmp")
    # hight map for cpu to gpu
    hightMap = loadtexture.Texture.loadmap("hight.gif")
    # create terrain use cpu
    hightimage = loadtexture.Texture.loadterrain("hight.gif")
    # image = open("ground2.bmp").convert("RGBA")
    plane.setHeight(hightimage)
    glutMainLoop()

