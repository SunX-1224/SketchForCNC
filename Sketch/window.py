import pygame, sys
from pygame.locals import *
from widgets import *
from canvas import Canvas
from shapes import Shapes

class Window:
    # CARD CONFIG : negative flex values indicate clickables and positive flex indicates labels
    CARD_CONFIG = [
        [-2],
        [0.5],
        [0.8,0.8],
        [0.8,0.8],
        [0.8,0.8],
        [-0.5],
        [0.8,0.8],
        [0.8],
        [0.8,0.8],
        [0.8],
        [0.8],
        [0.5, 0.5, 0.5]
    ]

    LABEL_CONFIG = [
        ["Status"],
        ["Select"],
        ["Line", "Rectangle"],
        ["Parallelogram", "Polygon"],
        ["Arc", "Circle"],
        ["Gcode Options"],
        ["Z-safe",'Z-work'],
        ["Generate-Engraving"],
        ["Stock-Top","Stock-Height"],
        ["Cut-Depth"],
        ["Generate-Milling"],
        ["Preview","Save","Exit"]
    ]

    EXIT = False
    def __init__(self):
        self.window = pygame.display.set_mode((0, 0), RESIZABLE)
        self.clock = pygame.time.Clock()
        self.canvas = Canvas((0, 0), self.getCanvasSize())
        self.canvas.WIN = self
        self.scroll_bars = [
            HorScrollBar((0,self.getCanvasSize()[1]), self.getCanvasSize()[0]),
            VerScrollBar((self.getCanvasSize()[0], 0), self.getCanvasSize()[1])
        ]
        self.buttons = []
        self.labels = []
        self.mouseClicks = []
        self.cursor = None
        self.getCards((self.getCanvasSize()[0]+SCBAR_T, 0), self.getSize())
        self.mode = "select"
        self.buffer = ''
        self.updateReq = True

    def getSize(self):
        return pygame.display.get_surface().get_size()

    def getCanvasSize(self):
        return (self.getSize()[0] * 80 // 100 - 20, self.getSize()[1] - 20)

    def get_events(self):
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            self.cursor = pygame.mouse.get_pos()
            self.mouseClicks = pygame.mouse.get_pressed(5)
            if event.type == pygame.QUIT or keys[K_ESCAPE]:
                self.EXIT = True
            if keys[K_SPACE]:
                self.canvas.scale=1
                self.canvas.offset=(0,0)
            if event.type == pygame.KEYDOWN:
                if 48 <= event.key <= 57 or event.key== 46 or 97<=event.key <= 122 or 65<=event.key <= 90: self.buffer+=event.unicode
            if keys[pygame.K_BACKSPACE]: self.buffer = self.buffer[:-1]
            if keys[pygame.K_DELETE]: self.canvas.delete()
            if keys[pygame.K_RETURN]:
                if self.buffer.isnumeric() :
                    if int(self.buffer)>1 and self.mode == "polygon": self.canvas.bufferNum = int(self.buffer)
                elif self.buffer.isalpha() and self.mode.split('-')[0]=="generate":
                    self.canvas.gcode.filename = self.buffer
                else:
                    dgts = self.buffer.split('.')
                    num = 0
                    if len(dgts) == 1 and dgts[0].isnumeric():
                        num = int(dgts[0])
                    elif len(dgts) == 2 and dgts[0].isnumeric() and dgts[1].isnumeric():
                         num = int(dgts[0]) + int(dgts[1]) / 10 ** len(dgts[1])

                    if self.mode == "arc": self.canvas.bufferNum=num
                    elif self.mode == "z-safe": self.canvas.gcode.zsafe=num
                    elif self.mode == "z-work": self.canvas.gcode.zwork=num
                    elif self.mode == "stock-top": self.canvas.gcode.stocktop=num
                    elif self.mode == "stock-height": self.canvas.gcode.stockheight=num
                    elif self.mode == "cut-depth": self.canvas.gcode.cutdepth=num
                self.buffer = ""

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    if keys[K_LCTRL]:
                        self.canvas.scale -= 0.1
                        if self.canvas.scale < 1: self.canvas.scale = 1
                        ofx = self.canvas.offset[0] - 0.05 * self.canvas.size[0]
                        ofy = self.canvas.offset[1] - 0.05 * self.canvas.size[1]
                        ofx = ofx if ofx>0 else 0
                        ofy = ofy if ofy>0 else 0
                        self.canvas.offset = (ofx, ofy)
                    elif keys[K_LSHIFT]:
                        self.canvas.scrollRight()
                    else:
                        self.canvas.scrollDown()
                if event.button == 4:
                    if keys[K_LCTRL]:
                        self.canvas.scale += 0.1
                        if self.canvas.scale > 4: self.canvas.scale = 4
                    elif keys[K_LSHIFT]:
                        self.canvas.scrollLeft()
                    else:
                        self.canvas.scrollUp()

            for btn in self.buttons:
                self.updateReq |= btn.cursorEffect(self.cursor, self.mode, self.mouseClicks[0])

            self.updateReq |= self.canvas.checkCursor()

    def draw(self):
        if self.updateReq:
            self.window.fill(C_BG)
            self.canvas.draw()
            for sb in self.scroll_bars:
                sb.draw(self.window, self.canvas.offset, self.canvas.scale)
            self.labels[0].draw(self.window, self.canvas.getStatus())
            for c in self.labels[1:]+self.buttons:
                c.draw(self.window)
        self.updateReq = False

    def update(self):
        pygame.display.set_caption(f"{self.clock.get_fps()}")
        pygame.display.flip()
        self.clock.tick(70)

    def destroy(self):
        pygame.quit()
        sys.exit(0)

    def getCards(self, start, end):
        mSize = (end[0] - start[0], end[1] - start[1])
        h = mSize[1] // len(self.CARD_CONFIG) - 2 * PADDING[1]

        py = PADDING[1]
        size = (0,0)
        th = self._abssum([max(x) for x in self.CARD_CONFIG])
        for r, lr in zip(self.CARD_CONFIG, self.LABEL_CONFIG,):
            px = start[0]+PADDING[0]
            for c, l in zip(r, lr):
                size = (mSize[0]*abs(c)/self._abssum(r)-PADDING[0]*2, mSize[1]*abs(c)/th-PADDING[1]*2)
                pos = (px, py)
                if c>0:
                    self.buttons.append(Card(pos, size,l, True))
                    self.buttons[-1].function = self.setMode
                else:
                    self.labels.append(Card(pos, size, l))
                px += size[0]+PADDING[0]*2
            py += size[1]+PADDING[1]*2

    def setMode(self, m):
        if self.mode == m: return True
        self.canvas.updateReq = True
        if m=="arc" or m=="circle": self.canvas.bufferNum = 1
        elif m=="polygon": self.canvas.bufferNum = 3
        elif m=="preview":
            self.canvas.rearrange()
            Shapes.index(self.canvas.shapes)
        elif m=="save":
            return self.canvas.gcode.writeGcode()
        elif m=="exit": self.EXIT = True
        elif m=="generate-engraving":
            self.canvas.rearrange()
            Shapes.index(self.canvas.shapes)
            if self.canvas.gcode.generateable(m):
                self.canvas.gcode.generate2d()
            else : return False
        elif m=="generate-milling":
            self.canvas.rearrange()
            Shapes.index(self.canvas.shapes)
            if self.canvas.gcode.generateable(m):
                self.canvas.gcode.generate3d()
            else: return False
        self.mode = m
        return True

    def _abssum(self, l):
        sum = 0
        for x in l:
            sum += abs(x)
        return sum
