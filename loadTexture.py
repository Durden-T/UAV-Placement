#绘制方面 Texture的定义与实现
from OpenGL.GL import *
from PIL.Image import *
from itertools import *

class Texture:

    @staticmethod
    def loadmap(fileName,format="RGBA"):
        image = open(fileName).convert(format)
        ix = image.size[0]
        iy = image.size[1]
        r,g,b,a = image.im[0]
        #print ("im:",type(r))
        image = image.tobytes("raw", format, 0, -1)
        #print ("image info:",type(image))
        textid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, textid) 
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, ix, iy, 0, GL_RGBA,GL_UNSIGNED_BYTE , image)#GL_FLOAT
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL) 
        return textid


    @staticmethod
    def loadterrain(fileName,format="L"):
        image = open(fileName).convert("L")	
        ix = image.size[0]
        iy = image.size[1]
        index = (len(image.im) - 1) / 2
        #print ("s",image.im[int(index)],image.im[0],image.im[1],image.im[2],image.im[3]  )
        return image
#loadTexture().load("hight.gif")