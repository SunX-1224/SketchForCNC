import pygame
import math

pygame.init()

MMPPX = 0.3636
SCSP = 10 #Scroll speed

SCBAR_T = 20

PADDING = (5, 5)


C_BG = (45, 45, 45)
C_BORDER = (200, 200, 200)
C_LABEL = (255, 255, 255)
C_BUTTON_UP = (140, 155, 155)
C_BUTTON_HOVER = (100, 115, 115)
C_BUTTON_DOWN = (80, 100, 95)
C_SLIDER = (80,80,80)
C_DRAW = (255, 255, 255)
C_HLT = (155, 255, 155)
C_REF = (155, 80, 80)
C_ERROR = (144,24,24)

FONT_S = pygame.font.Font("assests/good_times_font.otf", 10)
FONT_M = pygame.font.Font("assests/good_times_font.otf", 16)
FONT_L = pygame.font.Font("assests/good_times_font.otf", 20)

NUM = {
    "select" : 0,
    "line" : 2,
    "rectangle" : 2,
    "parallelogram" : 3,
    "polygon" : 2,
    "arc" : 3,
    "circle":2,
    "save" : 0,
    "exit" : 0,
    "preview" : 0,
    "z-safe" : 0,
    "z-work" : 1,
    "generate-engraving":0,
    "stock-top":0,
    "stock-height":0,
    "cut-depth":0,
    "generate-milling":0
}

MM2PX = lambda tup:(tup[0] / MMPPX, tup[1] / MMPPX)
PX2MM = lambda tup:(tup[0] * MMPPX, tup[1] * MMPPX)
ROUND = lambda tup: (round(tup[0], 2), round(tup[1], 2))

move = lambda x=None,y=None,z=None,f=None:"G0 "+('X'+str(x) if x != None else '')+('Y'+str(y) if y != None else '') +('Z'+str(z) if z != None else '')+ ('F'+str(f) if f != None else '')+ '\n'
line = lambda x=None,y=None,f=None:"G1 "+('X'+str(x) if x != None else '')+('Y'+str(y) if y != None else '') + ('F'+str(f) if f != None else '') + '\n'
arc_cw = lambda x=None,y=None,r=None,f=None:"G2 "+('X'+str(x) if x != None else '')+('Y'+str(y) if y != None else '')+('R'+str(r) if r != None else '') + ('F'+str(f) if f != None else '') + '\n'
arc_ccw = lambda x=None,y=None,r=None,f=None:"G3 "+('X'+str(x) if x != None else '')+('Y'+str(y) if y != None else '')+('R'+str(r) if r != None else '') + ('F'+str(f) if f != None else '') + '\n'
dist = lambda a, b: ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
add = lambda a, b:(a[0]+b[0], a[1]+b[1])
sub = lambda a, b:(a[0]-b[0], a[1]-b[1])
rotate = lambda p, c, a: (c[0]+(p[0]-c[0])*math.cos(a) - (p[1]-c[1])*math.sin(a), c[1]+(p[0]-c[0])*math.sin(a) + (p[1]-c[1])*math.cos(a))

class Gcode:
    def __init__(self, canvas):
        self.canvas = canvas
        self.gcode = []
        self.filename = "newfile"
        self.zsafe = None
        self.zwork = None
        self.stocktop = None
        self.stockheight = None
        self.cutdepth = None

    def writeGcode(self):
        if self.gcode:
            with open("gcodes/"+self.filename+".gcode", 'w') as file:
                for line in self.gcode: file.write(line)
            return True
        return False

    def generate2d(self):
        self.gcode = []
        for shape in self.canvas.shapes:
            self.gcode+=shape.gcode2d(self.zsafe, self.zwork)
        self.gcode.append(move(z=self.zsafe, f=400))
        self.gcode.append(move(x=0, y=0))

    def generate3d(self):
        self.gcode = []
        for shape in self.canvas.shapes:
            self.gcode+=shape.gcode3d(self.zsafe, self.zwork)
        self.gcode.append(move(z=self.zsafe, f=400))
        self.gcode.append(move(x=0, y=0))

    def generateable(self, mode):
        if mode=="generate-engraving":
            return self.zwork != None and self.zsafe != None
        elif mode=="generate-milling":
            return self.zsafe!=None and self.stocktop!=None and self.stockheight!=None and self.cutdepth!=None
