#sphere,UAV,camera的定义与实现
import math
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGL.GLU import *
from OpenGL.GLUT import *
#import OpenGL.GLUT as glut
import numpy as np
#Python Imaging Library (PIL)
class common:
    #判断是否已初始化
    bCreate = False

#球的实现
class sphere(common):

    #方向 x轴z轴水平面 y轴垂直???  xz 好像不是这样 靠
    def __init__(this,rings,segments,radius, x, z):
        this.rings = rings
        this.segments = segments
        this.radius = radius
        this.createVAO()
        this.x_speed = 0
        this.z_speed = 0
        this.move_active = 0
        this.x = x
        this.z = z


    def change(this, x, z):
        this.x = x
        this.z = z


    def createVAO(this):
        vdata = []
        vindex = []
        for y in range(this.rings):
            phi = (float(y) / (this.rings - 1)) * math.pi
            for x in range(this.segments):
                theta = (float(x) / float(this.segments - 1)) * 2 * math.pi
                vdata.append(math.sin(phi) * math.cos(theta))
                vdata.append(math.cos(phi))
                vdata.append(math.sin(phi) * math.sin(theta))
                vdata.append(this.radius * math.sin(phi) * math.cos(theta))
                vdata.append(this.radius * math.cos(phi))
                vdata.append(this.radius * math.sin(phi) * math.sin(theta))
        for y in range(this.rings - 1):
            for x in range(this.segments - 1):
                vindex.append((y + 0) * this.segments + x)
                vindex.append((y + 1) * this.segments + x)
                vindex.append((y + 1) * this.segments + x + 1)
                vindex.append((y + 1) * this.segments + x + 1)
                vindex.append((y + 0) * this.segments + x + 1)
                vindex.append((y + 0) * this.segments + x)
        this.vbo = vbo.VBO(np.array(vdata,'f'))
        this.ebo = vbo.VBO(np.array(vindex,'H'),target = GL_ELEMENT_ARRAY_BUFFER)
        this.vboLength = this.segments * this.rings
        this.eboLength = len(vindex)
        this.bCreate = True

    #没用到
    #def drawShader(this,vi,ni,ei):
    #    if this.bCreate == False:
    #        this.createVAO()
    #    this.vbo.bind()


    def draw(this):
        if this.bCreate == False:
            this.createVAO()
        this.vbo.bind()
        glInterleavedArrays(GL_N3F_V3F,0,None)
        this.ebo.bind()
        glDrawElements(GL_TRIANGLES,this.eboLength,GL_UNSIGNED_SHORT,None)


    #没用到
    #def move(this, move_type):
    #    if move_type == 0:
    #        pass
    #    # 前
    #    if move_type == 1:
    #        this.move_active = 0
    #        this.x_speed = 0.004
    #        this.z_speed = 0.0
    #    # 右
    #    if move_type == 2:
    #        this.move_active = 0
    #        this.x_speed = 0.0
    #        this.z_speed = 0.004
    #    # 左
    #    if move_type == 3:
    #        this.move_active = 0
    #        this.x_speed = 0.0
    #        this.z_speed = -0.004
    #    # 后
    #    if move_type == 4:
    #        this.move_active = 0
    #        this.x_speed = -0.004
    #        this.z_speed = 0.0


    def move_location(this, old_x, old_z, new_x, new_z):
        this.move_active = 0
        x_cha = new_x - old_x
        z_cha = new_z - old_z
        x_speed = x_cha / 250
        z_speed = z_cha / 250
        this.x_speed = x_speed
        this.z_speed = z_speed


    # F6~9控制向前右左后移动
    #没用到
    #def keypress(this, key, x, y):
    #    if key == GLUT_KEY_F6:
    #        this.move(1)
    #    if key == GLUT_KEY_F7:
    #        this.move(2)
    #    if key == GLUT_KEY_F8:
    #        this.move(3)
    #    if key == GLUT_KEY_F9:
    #        this.move(4)

class UAV(common):

    def __init__(this,xres,yres,xscale,yscale):
        this.xr,this.yr,this.xc,this.yc = xres,yres,xscale,yscale
        this.xl,this.yl = (this.xr - 1) * this.xc,(this.yr - 1) * this.yc
        this.createVAO()


    def createVAO(this):
        helfx = (this.xr - 1) * this.xc * 0.5
        helfy = (this.yr - 1) * this.yc * 0.5
        #print (helfx,helfy)
        vdata = []
        vindex = []


        for y in range(this.yr):
            for x in range(this.xr):
                vdata.append(float(x) / float(this.xr - 1))
                vdata.append(float(y) / float(this.yr - 1))
                vdata.append(this.xc * float(x) - helfx)
                vdata.append(0.)
                vdata.append(this.yc * float(y) - helfy)
        for y in range(this.yr - 1):
            for x in range(this.xr - 1):
                vindex.append((y + 0) * this.xr + x)
                vindex.append((y + 1) * this.xr + x)
                vindex.append((y + 0) * this.xr + x + 1)
                vindex.append((y + 0) * this.xr + x + 1)
                vindex.append((y + 1) * this.xr + x)
                vindex.append((y + 1) * this.xr + x + 1)
        #print (len(vdata),len(vindex))
        this.data = vdata
        this.idata = vindex
        #print (len(this.data))


    def draw(this):
        if this.bCreate == False:            
            this.vbo = vbo.VBO(np.array(this.data,'f'))
            this.ebo = vbo.VBO(np.array(this.idata,'H'),target = GL_ELEMENT_ARRAY_BUFFER)
            this.eboLength = len(this.idata)
            this.bCreate = True
            #this.createVAO()
        this.vbo.bind()
        # 函数将会将会根据参数,激活各种顶点数组,并存储顶点
        glInterleavedArrays(GL_T2F_V3F,0,None)
        this.ebo.bind()
        # 会按照我们传入的顶点顺序和指定的绘制方式进行绘制 GL_TRIANGLES三角形
        glDrawElements(GL_TRIANGLES,this.eboLength,GL_UNSIGNED_SHORT,None)


    def setHeight(this,image):
        ix = image.size[0] 
        iy = image.size[1] 
        this.heightImage = image
        # print (ix,iy)
        #print "xr,yr",this.xr,this.yr
        lerp = lambda a,b,d:a * d + b * (1.0 - d)  
        fade = lambda t : t * t * (3.0 - 2.0 * t)  #t*t*t*(t*(t*6.0-15.0)+10.0)
        for y in range(this.yr):
            for x in range(this.xr):  
                # y index location in this.data
                #if x != 0 or y != 0:
                    #continue
                index = 5 * (this.xr * y + x) + 3
                #print index
                fx = float(x) / float(this.xr - 1) * float(ix - 1)
                fy = float(y) / float(this.yr - 1) * float(iy - 1)
                #print float(x) / float(this.xr - 1),fx,float(y) /
                #float(this.yr - 1),fy
                xl,xr,yu,yd = int(math.floor(fx)),int(math.ceil(fx)),int(math.floor(fy)),int(math.ceil(fy))
                dx,dy = fade(fx - xl),fade(fy - yu)  
                #print "loc:",xl,xr,yu,yd,dx,dy
                #left up,right up,left down,right down
                lu,ru,ld,rd = image.im[ix * yu + xl],image.im[ix * yu + xr],image.im[ix * yd + xl],image.im[ix * yd + xr] 
                #print ix * yu + xl,lu,ru,ld,rd
                hight = lerp(lerp(lu,ru,dx),lerp(ld,rd,dx),dy)
                this.data[index] = hight / 255.0
                #print "setHeight:",hight / 255.0


    def getHeight(this,x,y):
        image = this.heightImage
        ix = image.size[0] 
        iy = image.size[1] 
        lerp = lambda a,b,d:a * d + b * (1.0 - d) 
        fade = lambda t : t * t * (3.0 - 2.0 * t)  #t*t*t*(t*(t*6.0-15.0)+10.0)
        #fx,fy
        fx = (float(x) / float(this.xl) + 0.5) * float(ix - 1)
        fy = (float(y) / float(this.xl) + 0.5) * float(iy - 1)
        #print "vv:",fx,fy
        #print float(x) / float(this.xr - 1),fx,float(y) / float(this.yr -
        #1),fy
        xl,xr,yu,yd = int(math.floor(fx)),int(math.ceil(fx)),int(math.floor(fy)),int(math.ceil(fy))
        dx,dy = fade(fx - xl),fade(fy - yu)  
        #print "loc:",xl,xr,yu,yd,dx,dy
        #left up,right up,left down,right down
        lu,ru,ld,rd = image.im[ix * yu + xl],image.im[ix * yu + xr],image.im[ix * yd + xl],image.im[ix * yd + xr] 
        #print ix * yu + xl,lu,ru,ld,rd
        hight = lerp(lerp(lu,ru,dx),lerp(ld,rd,dx),dy) / 255.0
        #print hight
        return hight


class camera:

    origin = [0.0,0.0,0.0]
    length = 1.
    yangle = 0.
    zangle = 0.
    __bthree = True
    #俯视
    overlook = True

    def __init__(this):
        this.mouselocation = [0.0,0.0]
        this.offest = 0.3
        this.zangle = 0. if not this.__bthree else math.pi


    def setthree(this,value):
        this.__bthree = value
        this.zangle = this.zangle + math.pi
        this.yangle = - this.yangle


    def eye(this):
        return this.origin if not this.__bthree else this.direction()


    def target(this):
        return this.origin if this.__bthree else this.direction()


    def direction(this):
        if this.zangle > math.pi * 2.0 :
            this.zangle < - this.zangle - math.pi * 2.0
        elif this.zangle < 0. :
            this.zangle < - this.zangle + math.pi * 2.0
        len = 1. if not this.__bthree else this.length if this.length != 0. else 1.        
        xy = math.cos(this.yangle) * len
        x = this.origin[0] + xy * math.sin(this.zangle)
        y = this.origin[1] + len * math.sin(this.yangle)
        z = this.origin[2] + xy * math.cos(this.zangle)
        # print(x,y,z)
        return [x,y,z]


    #移动视角
    def move(this,x,y,z):
        sinz,cosz = math.sin(this.zangle),math.cos(this.zangle)        
        xstep,zstep = x * cosz + z * sinz,z * cosz - x * sinz
        if this.__bthree :
            xstep = -xstep
            zstep = -zstep
        #print([this.origin[0] + xstep,this.origin[1] + y,this.origin[2] +
        #zstep])
        this.origin = [this.origin[0] + xstep,this.origin[1] + y,this.origin[2] + zstep]


    #旋转视角
    def rotate(this,z,y):
        this.zangle, this.yangle = this.zangle - z,this.yangle + y if not this.__bthree else -y


    def setLookat(this):
        if this.overlook:
            ve,vt = this.eye(),this.target()
            # 其功能是用一个4×4的单位矩阵来替换当前矩阵，实际上就是对当前矩阵进行初始化。也就是说，
            # 无论以前进行了多少次矩阵变换，在该命令执行后，当前矩阵均恢复成一个单位矩阵，即相当于没有进行任何矩阵变换状态。
            # 您实际上将当前点移到了屏幕中心：类似于一个复位操作
            glLoadIdentity()
            # 定位相机位置
            # 第一组eyex, eyey,eyez 相机在世界坐标的位置
            # 第二组centerx,centery,centerz 相机镜头对准的物体在世界坐标的位置
            # 第三组upx,upy,upz 相机向上的方向在世界坐标中的方向
            gluLookAt(ve[0],ve[1],ve[2],vt[0],vt[1],vt[2],0.0,1.0,0.0)


    #鼠标移动回调
    def mouse(this,x,y):  
        rx = (x - this.mouselocation[0]) * this.offest * 0.1
        ry = (y - this.mouselocation[1]) * this.offest * -0.1
        this.rotate(rx,ry)
        #print x,y
        this.mouselocation = [x,y]

    
    #俯视图
    def change_overlook(this):
        this.overlook = not this.overlook
        gluLookAt(0, 12, 0, 0, 0, 0, 1.0, 0, 0.0)



        