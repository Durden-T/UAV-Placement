#绘制方面的实现
import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from ctypes import *
from OpenGL.GL.shaders import ShaderProgram

plane_v = """
        //#version 330 compatibility
        #version 120
        uniform sampler2D tex1;       
        void main() 
        {
            gl_TexCoord[0] = gl_MultiTexCoord0; 
		    vec4 v = vec4(gl_Vertex);		
		    //v.y = texture2D(tex1, gl_TexCoord[0].st).r/256.0;
		    gl_Position = gl_ModelViewProjectionMatrix * v;
        }"""

plane_f = """
        //#version 330 compatibility
        #version 120
        uniform sampler2D tex0;
        void main() 
        {            
            vec4 color = texture2D(tex0, gl_TexCoord[0].st);//gl_TexCoord[0].st);vec2(0.3,0.3)
            gl_FragColor = color;//vec4( 0, 1, 0, 1 );//
        }"""
        
update_v = """        
        //#version 330 compatibility
        #version 330
        in vec3 vectpos;
        uniform sampler2D tex0;
        uniform float xw;
        uniform float yw;
        uniform float height;
        //the location of center of the sphere
        uniform vec2 xz;          
        uniform float sphereRadius; 
        uniform mat4 mMatrix;
        uniform mat4 vMatrix;
        uniform mat4 pMatrix;
        out vec4 o_color;          
        void main() 
        {      
		    vec4 pos = vec4(vectpos,1.0);              
            vec2 uv = vec2(xz/vec2(xw,yw) + vec2(0.5,0.5));
            uv.y = 1.0 - uv.y;
            vec3 rgb =  texture2D(tex0, uv).rgb;
		    pos.y = pos.y + sphereRadius + rgb.r;//height;//
            o_color = vec4(uv.x, uv.y, rgb.r, 1);
            gl_Position = pMatrix * vMatrix * mMatrix * pos;
        }"""

update_f = """
        //#version 330 compatibility
        #version 330
        in vec4 o_color;  
        void main() 
        {            
            //vec4 color = texture2D(tex1, gl_TexCoord[0].st);
            gl_FragColor = o_color;// vec4( 0, 1, 0, 1 );
        }"""

update_v1 = """        
        //#version 330 compatibility
        #version 330
        in vec3 vectpos1;
        uniform sampler2D tex1;
        uniform float xw1;
        uniform float yw1;
        uniform float height1;
        //the location of center of the sphere
        uniform vec2 xz1;          
        uniform float sphereRadius1; 
        uniform mat4 mMatrix1;
        uniform mat4 vMatrix1;
        uniform mat4 pMatrix1;
        out vec4 o_color;          
        void main() 
        {      
		    vec4 pos = vec4(vectpos1,1.0);              
            vec2 uv = vec2(xz1/vec2(xw1,yw1) + vec2(0.5,0.5));
            uv.y = 1.0 - uv.y;
            vec3 rgb =  texture2D(tex1, uv).rgb;
		    pos.y = pos.y + sphereRadius1 + rgb.r;//height1;//
            o_color = vec4(uv.x, uv.y, rgb.r, 1);
            gl_Position = pMatrix1 * vMatrix1 * mMatrix1 * pos;
        }"""

update_f1 = """
        //#version 330 compatibility
        #version 330
        in vec4 o_color;  
        void main() 
        {            
            //vec4 color = texture2D(tex1, gl_TexCoord[0].st);
            gl_FragColor = o_color;// vec4( 0, 1, 0, 1 );
        }"""

gpgpu_v = """
        //#version 330 compatibility
        #version 130
        out vec4 pos;
        void main() 
        {  
            pos = vec4(gl_Vertex);
            //The following coding must be in fragment shader
            //vec2 xy = v.xy;
            //vec2 uv = vec2(xy/vec2(xw,yw)).xy;
            //o_color = texture2D(tex0, uv);
		    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }"""

gpgpu_f = """
        //#version 330 compatibility
        #version 130
        in vec4 pos;
        uniform sampler2D tex0; 
        uniform float xw;
        uniform float yw;          
        void main() 
        {             
            vec2 xy = pos.xy;
            vec2 uv = vec2(xy/vec2(xw,yw)).xy;            
            vec4 o_color = texture2D(tex0, uv);// vec4(uv.x,uv.y, 0, 1 );//   
            o_color = o_color + vec4(1);  
            gl_FragColor = o_color;
        }"""

tf_v = """
        #version 330
        in float inValue;
        out float outValue;
        out float out2;
        void main() 
        {
            outValue = inValue+3.0;
            out2 = 1.0;
        }"""

particle_v = """
        #version 330
        in vec3 pos;
        in vec3 vel;
        in float time;
        uniform float span;
        uniform vec2 planeSacle;      
        uniform sampler2D plane;
        uniform vec3 sphere;
        uniform float live;
        out vec3 outpos;
        out vec3 outvel;
        out float outtime;
        void main() 
        {
            outpos = pos + vel*span;
            vec2 uv = vec2(pos.xz/planeSacle + vec2(0.5,0.5));
            uv.y = 1.0 - uv.y;
            float hight = texture2D(plane, uv).r;
            vec3 tvel = vel;
            //sphere collision
            float radius = sphere.y;
            vec3 sphereh = sphere + vec3(0.0,hight,0.0);
            if(distance(outpos,sphereh) <= radius)
            {
                tvel = reflect(vel,normalize(outpos-sphereh))/2.0;
            }
            tvel = tvel + vec3(0.0,-0.5,0.0)*span;  
             
            //ground collision
            if(hight > outpos.y)
            {
                outpos.y = hight;
                tvel = vec3(max(vel.x-span*1.1,0.0),0.0,max(vel.z - span*1.1,0.0));
            }
            //update particle live  
            outtime = time + span;    
            if(outtime>=live)
            {
                outpos = vec3(0.0,3.0,hight*5.0);
                outtime = 0.0;
                tvel = vec3(hight,0.0,0.0);
            }
            outvel = tvel;    
        }"""

class allshader:

    def __init__(this):
        this.planeProgram = shaders.compileProgram(shaders.compileShader(plane_v, GL_VERTEX_SHADER),
            shaders.compileShader(plane_f, GL_FRAGMENT_SHADER)) 
        #the parameter tex0 must be use in shaders,otherwise the
        #glGetUniformLocation get -1
        this.planeProgram.tex0 = glGetUniformLocation(this.planeProgram,"tex0")
        this.planeProgram.tex1 = glGetUniformLocation(this.planeProgram,"tex1")        
        #print ("t0,t1:", this.planeProgram.tex0,this.planeProgram.tex1)

        this.updateProgram = shaders.compileProgram(shaders.compileShader(update_v, GL_VERTEX_SHADER),
            shaders.compileShader(update_f, GL_FRAGMENT_SHADER))
        this.updateProgram.xl = glGetUniformLocation(this.updateProgram,"xw")
        this.updateProgram.yl = glGetUniformLocation(this.updateProgram,"yw")  
        this.updateProgram.height = glGetUniformLocation(this.updateProgram,"height")
        this.updateProgram.sphereRadius = glGetUniformLocation(this.updateProgram,"sphereRadius")
        this.updateProgram.tex0 = glGetUniformLocation(this.updateProgram,"tex0")
        this.updateProgram.xz = glGetUniformLocation(this.updateProgram,"xz")
        this.updateProgram.hight = glGetUniformLocation(this.updateProgram,"hight")
        this.updateProgram.mMatrix = glGetUniformLocation(this.updateProgram,"mMatrix")
        this.updateProgram.vMatrix = glGetUniformLocation(this.updateProgram,"vMatrix")
        this.updateProgram.pMatrix = glGetUniformLocation(this.updateProgram,"pMatrix")
        this.updateProgram.pos = glGetAttribLocation(this.updateProgram,"vectpos")

        this.gpgpuProgram = shaders.compileProgram(shaders.compileShader(gpgpu_v, GL_VERTEX_SHADER),
            shaders.compileShader(gpgpu_f, GL_FRAGMENT_SHADER)) 
        this.gpgpuProgram.tex0 = glGetUniformLocation(this.gpgpuProgram,"tex0")
        this.gpgpuProgram.xl = glGetUniformLocation(this.gpgpuProgram,"xw")
        this.gpgpuProgram.yl = glGetUniformLocation(this.gpgpuProgram,"yw")
        
        this.tfProgram = glCreateProgram()
        this.tfProgram = ShaderProgram(this.tfProgram)
        tfvshader = shaders.compileShader(tf_v,GL_VERTEX_SHADER)
        glAttachShader(this.tfProgram,tfvshader)        
        LP_LP_c_char = POINTER(POINTER(c_char))
        ptrs = (c_char_p * 2)(bytes('outValue', encoding = "utf8"), bytes('out2', encoding = "utf8"))
        # print (ptrs,len(ptrs))
        c_array = cast(ptrs, LP_LP_c_char)
        glTransformFeedbackVaryings(this.tfProgram, len(ptrs), c_array, GL_INTERLEAVED_ATTRIBS)
        glLinkProgram(this.tfProgram)
        this.tfProgram.invalue = glGetAttribLocation(this.tfProgram,"inValue")

        this.particleProgram = glCreateProgram()
        this.particleProgram = ShaderProgram(this.particleProgram)
        particleshader = shaders.compileShader(particle_v,GL_VERTEX_SHADER)
        glAttachShader(this.particleProgram,particleshader)
        LP_LP_c_char = POINTER(POINTER(c_char))
        ptrs = (c_char_p * 3)(bytes('outpos', encoding = "utf8"), bytes('outvel', encoding = "utf8"),bytes('outtime', encoding = "utf8"))
        c_array = cast(ptrs, LP_LP_c_char)
        glTransformFeedbackVaryings(this.particleProgram, len(ptrs), c_array, GL_INTERLEAVED_ATTRIBS)
        glLinkProgram(this.particleProgram)
        this.particleProgram.pos = glGetAttribLocation(this.particleProgram,"pos")
        this.particleProgram.vel = glGetAttribLocation(this.particleProgram,"vel")
        this.particleProgram.time = glGetAttribLocation(this.particleProgram,"time")
        this.particleProgram.span = glGetUniformLocation(this.particleProgram,"span")
        this.particleProgram.live = glGetUniformLocation(this.particleProgram,"live")
        this.particleProgram.plane = glGetUniformLocation(this.particleProgram,"plane")
        this.particleProgram.planeSacle = glGetUniformLocation(this.particleProgram,"planeSacle")
        #this.particleProgram.sphere = glGetUniformLocation(this.particleProgram,"sphere")
        



