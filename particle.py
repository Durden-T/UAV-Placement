#绘制方面的实现
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL.framebufferobjects import *
from PIL.Image import *
import numpy as np
import random
import time

import base
class particleSystem(object):

    def __init__(this,len=1):
        this.length = len 
        this.cparticles = [0.0] * 7 * len
        this.nparticles = [0.0] * 7 * len
        this.index = 0
        this.center = 0.0,0.0
        this.currenttime = 0.0
        this.height = 2.0
        this.initHelper()
        this.createVAO()


    def initHelper(this):
        #pos(x,y,z),vel(x,y,z),time
        for i in range(this.length):
            ind = i * 7
            px,py,pz,tt = ind,ind + 1,ind + 2,ind + 6
            vx,vy,vz = ind + 3,ind + 4,ind + 5
            this.cparticles[px] = 0.0
            this.cparticles[py] = 3.0
            this.cparticles[pz] = random.uniform(0,5) 
            this.cparticles[vx] = random.random()
            this.cparticles[vy] = 0.0
            this.cparticles[vz] = 0.0
            this.cparticles[tt] = random.uniform(1.0,40.0)#random.uniform(0, 3 * this.height)


    def createVAO(this):
        this.currvbo = vbo.VBO(np.array(this.cparticles,'f'))
        this.nextvbo = vbo.VBO(np.array(this.nparticles,'f'))     
        

    def render(this,program):
        ind = this.index % 2  
        span = time.time() - this.currenttime if this.currenttime != 0.0 else 0.0        
        invbo,outvbo = (this.currvbo,this.nextvbo) if ind == 0 else (this.nextvbo,this.currvbo)
        #gpu compute.
        #print (span)
        glUseProgram(program)
        glUniform1f(program.span, span)
        glUniform1f(program.live, 40)
        this.update(invbo,outvbo) 
        glUseProgram(0) 
        #draw particle.
        glColor(0.5,0.8,0.9)
        glPointSize(3.0)
        outvbo.bind()
        glVertexPointer(3,GL_FLOAT,28,outvbo)
        glDrawArrays(GL_POINTS, 0, this.length)
        outvbo.unbind()  
        this.index = this.index + 1 
        this.currenttime = time.time()     
        

    def update(this,fvbo,svbo):
        #fvbo->shader(GPU)->svbo,should svbo and fvbo both bind.
        svbo.bind()
        fvbo.bind()
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(0,3,GL_FLOAT,False,4 * 7,fvbo) 
        glVertexAttribPointer(1,3,GL_FLOAT,False,4 * 7,fvbo + 12)
        glVertexAttribPointer(2,1,GL_FLOAT,False,4 * 7,fvbo + 24)
        glEnable(GL_RASTERIZER_DISCARD)
        glBindBufferBase(GL_TRANSFORM_FEEDBACK_BUFFER,0,svbo)
        glBeginTransformFeedback(GL_POINTS)
        glDrawArrays(GL_POINTS, 0, this.length)
        glEndTransformFeedback()
        glDisable(GL_RASTERIZER_DISCARD)
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)
        fvbo.unbind()
        #query gpu data is chage?
        #svbo.bind()
        #bf = glMapBuffer(GL_ARRAY_BUFFER,GL_READ_WRITE)
        #pointv = ctypes.cast(bf, ctypes.POINTER(ctypes.c_float))
        #arrayv = np.ctypeslib.as_array(pointv,(70,))
        #print "tfv",arrayv
        #glUnmapBuffer(GL_ARRAY_BUFFER)


class gpgpubasic(object):
    """description of class"""
    #def __init__(this,col,row,data=[0.1,0.2,0.3,0.4]):

    def __init__(this,*args):
        this.imageFormat = GL_FLOAT

        if len(args) == 1 :
            if isinstance(args[0],Image):
                image = args[0]
                this.width = image.size[0]
                this.height = image.size[1]
                this.data = image.im
                this.imageFormat = GL_UNSIGNED_BYTE

            if isinstance(args[0],list):
                listf = args[0]
                this.width = len(listf) if len(listf) > 0 else 1
                this.height = 1
                this.data = listf    
                
        if len(args) == 3:
            this.width = int(args[0])
            this.height = int(args[1])
            this.data = args[2]  

        this.imagedata = []
        for i in range(this.height):
            for j in range(this.width):
                index = i * this.width + j
                f4 = this.data[index] if index < len(this.data) else float(j) / float(this.width)
                r,g,b,a = 0.0,0.0,0.0,0.0

                if isinstance(f4,tuple):
                    if len(f4) == 2:
                        r,g = f4
                    elif len(f4) == 3:
                        r,g,b = f4
                    else:
                        r,g,b,a = f4                           
                else:
                    r = f4

                this.imagedata.append(r)                          
                this.imagedata.append(g)
                this.imagedata.append(b)
                this.imagedata.append(a)
        #this.imagedata = np.array(this.imagedata,dtype=np.float)
        #print this.imagedata


    def createFBO(this):
        this.fbo = glGenFramebuffers(1) 
        glBindFramebuffer(GL_FRAMEBUFFER,this.fbo)
        #create texture for fbotext,GPU->CPU
        this.fbotext = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,this.fbotext)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, this.width, this.height,0,GL_RGBA,GL_FLOAT,None)#GL_FLOAT
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        #relation fbo and fbotext(FBO and Texture2D)
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,this.fbotext,0)                                                                                                     #glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,this.fbotext,0)
        glBindFramebuffer(GL_FRAMEBUFFER,0)    
        #save data to texture.CPU->GPU
        this.fbodata = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,this.fbodata)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        #print (this.imageFormat)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, this.width, this.height, 0, GL_RGBA,this.imageFormat, this.imagedata)
    #cpu to gpu,and gpu compute result in fbo and fbotext.(cpu -(fbodata)> gpu
    #-(fbotext)> cpu)


    def renderFBO(this,shader):
        glDisable(GL_DEPTH_TEST)
        glBindFramebuffer(GL_FRAMEBUFFER,this.fbo)
        glPushAttrib(GL_VIEWPORT_BIT)#| GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDrawBuffer(GL_COLOR_ATTACHMENT0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()  
        gluOrtho2D(0.0,this.width,0.0,this.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity() 
        glViewport(0,0,this.width,this.height)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, this.fbodata)
        glUseProgram(shader)
        glUniform1i(shader.tex0, 0) 
        glUniform1f(shader.xl, this.width) 
        glUniform1f(shader.yl, this.height)
        glBegin(GL_QUADS)
        glVertex2f(0.0, 0.0)
        glVertex2f(this.width, 0.0)
        glVertex2f(this.width, this.height)
        glVertex2f(0.0, this.height)
        glEnd()
        glUseProgram(0) 
        glBindFramebuffer(GL_FRAMEBUFFER,0)

        glBindFramebuffer(GL_FRAMEBUFFER,this.fbo)
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        data = glReadPixels(0, 0, this.width, this.height,GL_RGBA,GL_FLOAT)  
        #print ("fbo data:",type(data),len(data),data[0],data[1]) #,data[2],data[3]
        glPopAttrib()
        glBindFramebuffer(GL_FRAMEBUFFER,0)   
        #close fbo
        glBindTexture(GL_TEXTURE_2D, 0)        
        glEnable(GL_DEPTH_TEST)       


    def render(this,shader):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()  
        gluOrtho2D(0.0,this.width * 2,0.0,this.height * 2)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity() 
        glViewport(0,0,this.width,this.height)

        glColor4f(1.0, 1.0, 1.0, 0.5)
        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, this.fbodata)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0.0, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(this.width, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(this.width, this.height)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0.0, this.height)
        glEnd()

        glTranslatef(this.width + 10, 0.0, 0.0)        
        glColor4f(1.0, 1.0, 1.0, 0.5)
        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, this.fbotext)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0.0, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(this.width, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(this.width, this.height)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0.0, this.height)
        glEnd()   
               

class gpgpupingpong(object):

    def __init__(this,*args):
        this.imageFormat = GL_FLOAT
        this.index = 0

        if len(args) == 1 :
            if isinstance(args[0],Image):
                image = args[0]
                this.width = image.size[0]
                this.height = image.size[1]
                this.data = image.im
                this.imageFormat = GL_UNSIGNED_BYTE

            if isinstance(args[0],list):
                listf = args[0]
                this.width = len(listf) if len(listf) > 0 else 1
                this.height = 1
                this.data = listf    
                
        if len(args) == 3:
            this.width = int(args[0])
            this.height = int(args[1])
            this.data = args[2]  

        this.imagedata = []
        for i in range(this.height):
            for j in range(this.width):
                index = i * this.width + j
                f4 = this.data[index] if index < len(this.data) else float(j) / float(this.width)
                r,g,b,a = 0.0,0.0,0.0,0.0
                if isinstance(f4,tuple):
                    if len(f4) == 2:
                        r,g = f4
                    elif len(f4) == 3:
                        r,g,b = f4
                    else:
                        r,g,b,a = f4                           
                else:
                    r = f4
                this.imagedata.append(r)                          
                this.imagedata.append(g)
                this.imagedata.append(b)
                this.imagedata.append(a)


    def createFBO(this):
        this.fbo = glGenFramebuffers(1) 
        glBindFramebuffer(GL_FRAMEBUFFER,this.fbo)
        #create texture for fbotext,GPU->CPU
        this.fbotext = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,this.fbotext)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, this.width, this.height,0,GL_RGBA,GL_FLOAT,None)#GL_FLOAT
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        #relation fbo and fbotext(FBO and Texture2D)
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,this.fbotext,0)                                                                                                     #glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,this.fbotext,0)
        
        #save data to texture.CPU->GPU
        this.fbodata = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,this.fbodata)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, this.width, this.height, 0, GL_RGBA,GL_FLOAT,this.imagedata)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT1,GL_TEXTURE_2D,this.fbodata,0)  
         
        glBindFramebuffer(GL_FRAMEBUFFER,0)    
        this.pingpong = [[GL_COLOR_ATTACHMENT0,this.fbodata],[GL_COLOR_ATTACHMENT1,this.fbotext]]
    #cpu to gpu,and gpu compute result in fbo and fbotext.(cpu -(fbodata)> gpu
    #-(fbotext)> cpu)


    def renderFBO(this,shader):        
        ind = this.index % 2
        this.index = this.index + 1
        #print ("index",ind)
        pp = this.pingpong[ind]
        glDisable(GL_DEPTH_TEST)
        glBindFramebuffer(GL_FRAMEBUFFER,this.fbo)
        glDrawBuffer(pp[0])
        glPushAttrib(GL_VIEWPORT_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()  
        gluOrtho2D(0.0,this.width,0.0,this.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity() 
        glViewport(0,0,this.width,this.height)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, pp[1])
        glUseProgram(shader)
        glUniform1i(shader.tex0, 0) 
        glUniform1f(shader.xl, this.width) 
        glUniform1f(shader.yl, this.height)
        glBegin(GL_QUADS)
        glVertex2f(0.0, 0.0)
        glVertex2f(this.width, 0.0)
        glVertex2f(this.width, this.height)
        glVertex2f(0.0, this.height)
        glEnd()
        glUseProgram(0) 
        glBindFramebuffer(GL_FRAMEBUFFER,0)

        if ind == 0 :
            glBindFramebuffer(GL_FRAMEBUFFER,this.fbo)
            glReadBuffer(GL_COLOR_ATTACHMENT0_EXT)
            data = glReadPixels(0, 0, this.width, this.height,GL_RGBA,GL_FLOAT)  
            #print ("fbo 0:",len(data),data[5])#,data[1],data[2]
            glBindFramebuffer(GL_FRAMEBUFFER,0) 

        else :
            glBindFramebuffer(GL_FRAMEBUFFER,this.fbo)
            glReadBuffer(GL_COLOR_ATTACHMENT1_EXT)
            data = glReadPixels(0, 0, this.width, this.height,GL_RGBA,GL_FLOAT)  
            #print ("fbo 1:",len(data),data[0],data[1],data[2])
            glBindFramebuffer(GL_FRAMEBUFFER,0) 

        glPopAttrib()  
        #close fbo
        glBindTexture(GL_TEXTURE_2D, 0)        
        glEnable(GL_DEPTH_TEST)   