import pygame
import math
from utils import *
from shapes import *

class Canvas:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.surface = pygame.Surface(self.size)
        self.segments = []
        self.shapes = []
        self.updateReq = True
        self.offset = (0,0)   #in px not mm
        self.scale = 1
        self.penDown = False
        self.nearestNode = (-1, -1)
        self.WIN = None
        self.temp = []
        self.bufferNum = 1
        self.curve = -1
        self.ref_mouse = (0,0)
        self.gcode = Gcode(self)
        self.absPos = lambda p : ((p[0] - self.offset[0]) * self.scale, (p[1] - self.offset[1]) * self.scale)

    def draw(self):
        txt = None
        if self.updateReq:
            self.surface.fill(C_BG)
            if self.WIN.mode == "preview":
                for s in self.shapes: s.draw(self.surface)
            else:
                for s in self.segments: s.draw(self.surface, C_DRAW)

                if self.nearestNode != (-1, -1):
                    pygame.draw.circle(self.surface, C_HLT, MM2PX(self.nearestNode), 5)
                if self.curve != -1:
                    self.segments[self.curve].draw(self.surface, C_HLT)
            self.updateReq = False

        trg = pygame.transform.scale(self.surface, (int(self.size[0]*self.scale), int(self.size[1]*self.scale)))
        self.WIN.window.blit(trg, self.pos, (self.offset[0] * self.scale, self.offset[1] * self.scale, self.size[0], self.size[1]))

        if self.penDown: self.references()

    def references(self):
        cursor = min(max(0, self.WIN.cursor[0]), self.size[0]), min(max(0, self.WIN.cursor[1]), self.size[1])
        self.__references(cursor)
        for p in self.temp: self.__references(self.absPos(p))

        p1 = self.absPos(self.temp[0])
        pygame.draw.line(self.WIN.window, C_HLT if self.WIN.mode == "line" else C_REF, p1, cursor)
        if self.WIN.mode == "rectangle": pygame.draw.lines(self.WIN.window, C_HLT, 0, self.__getRectLines((p1, cursor)))
        elif self.WIN.mode == "parallelogram" and len(self.temp)>1:
            pygame.draw.lines(self.WIN.window, C_HLT, False, self.__getParallelogram([p1, self.absPos(self.temp[1]), cursor]))
        elif self.WIN.mode == "polygon":
            pygame.draw.line(self.WIN.window, C_REF, p1, cursor)
            dl = (cursor[0]-p1[0], cursor[1] - p1[1])
            r = (dl[0] ** 2 + dl[1] ** 2) ** 0.5
            pygame.draw.circle(self.WIN.window, C_REF, p1, r, 1)
            pygame.draw.lines(self.WIN.window, C_HLT, False, self.__getPolygon(cursor, p1))
        elif self.WIN.mode == "arc" and len(self.temp)>1:
            arc = Arc.from3p(PX2MM(p1), PX2MM(self.absPos(self.temp[1])), PX2MM(cursor))
            arc.draw(self.WIN.window, C_HLT)
        elif self.WIN.mode == "circle":
            dl = (cursor[0] - p1[0], cursor[1] - p1[1])
            r = (dl[0] ** 2 + dl[1] ** 2) ** 0.5
            pygame.draw.circle(self.WIN.window, C_HLT, p1, r, 1)

    def getStatus(self):
        labels = []
        buffer = "--"
        cursor = min(max(0, self.WIN.cursor[0]), self.size[0]),  min(max(0, self.WIN.cursor[1]), self.size[1])
        cursor = (self.offset[0] + cursor[0] / self.scale, self.offset[1] + cursor[1] / self.scale)
        cursor = PX2MM(cursor)

        labels.append(f"Cursor : ({cursor[0]:.2f}, {cursor[1]:.2f})".format(cursor))
        if len(self.temp) > 0:
            d = sub(cursor, PX2MM(self.temp[-1]) )
            l = round(dist(d, (0,0)),4)
            labels.append(f"(dx, dy) : {ROUND(d)}")
            labels.append(f"dl : {l}")
        if self.WIN.mode == "select":
            t = None
            if self.curve !=-1:
                p1 = self.segments[self.curve].start_point
                p2 = self.segments[self.curve].end_point
                t = [f"{self.segments[self.curve].ID} : {ROUND(p1), ROUND(p2)}"]
                t.append(f"Length : {round(dist(p1, p2), 4)}")
            if t: labels+=t
        elif self.WIN.mode == "polygon":
            buffer = "n_sides"
            labels.append(f"n : {self.bufferNum}")
        elif self.WIN.mode == "arc":
            if len(self.temp)==2:
                arc = Arc.from3p(PX2MM(self.temp[0]), PX2MM(self.temp[1]), PX2MM(cursor))
                labels+=arc.getStatus()
        elif self.WIN.mode == "circle":
            if len(self.temp)>0:
                labels.append(f"Center : {ROUND(PX2MM(self.temp[0]))}")
        elif self.WIN.mode == "z-safe":
            buffer = "Z-safe"
            labels.append(f"Z-Safe : {self.gcode.zsafe}")
        elif self.WIN.mode == "z-work":
            buffer = "Z-safe"
            labels.append(f"Z-Work : {self.gcode.zwork}")
        elif self.WIN.mode.split('-')[0]=="generate":
            buffer = "Filename"
            labels.append(f"Filename : {self.gcode.filename}")
        elif self.WIN.mode == "stock-top":
            buffer = "Stock-Top"
            labels.append(f"Stock-Top : {self.gcode.stocktop}")
        elif self.WIN.mode == "stock-height":
            buffer = "Stock-Height"
            labels.append(f"Stock-Height : {self.gcode.stockheight}")
        elif self.WIN.mode == "cut-depth":
            buffer = "Cut-Depth"
            labels.append(f"Cut-Depth : {self.gcode.cutdepth}")

        labels.append(f"Buffer ({buffer}) : {self.WIN.buffer}")
        return labels

    def addData(self):
        if self.WIN.mode == "line":
            self.temp = [Line(PX2MM(self.temp[i]), PX2MM(self.temp[i + 1])) for i in range(len(self.temp) - 1)]
            self.__optLineInsert()
        elif self.WIN.mode == "rectangle":
            self.temp = self.__getRectLines(self.temp)
            self.temp = [Line(PX2MM(self.temp[i]), PX2MM(self.temp[i + 1])) for i in range(len(self.temp) - 1)]
            self.__optLineInsert()
        elif self.WIN.mode == "parallelogram":
            self.temp = self.__getParallelogram(self.temp)
            self.temp = [Line(PX2MM(self.temp[i]), PX2MM(self.temp[i + 1])) for i in range(len(self.temp) - 1)]
            self.__optLineInsert()
        elif self.WIN.mode == "polygon":
            self.temp = self.__getPolygon(self.temp[1], self.temp[0])
            self.temp = [Line(PX2MM(self.temp[i]), PX2MM(self.temp[i + 1])) for i in range(len(self.temp) - 1)]
            self.__optLineInsert()
        elif self.WIN.mode == "arc":
            self.temp = [PX2MM(t) for t in self.temp]
            a = Arc.from3p(*self.temp)
            self.segments.append(a)
        elif self.WIN.mode == "circle":
            self.temp = [PX2MM(t) for t in self.temp]
            a = Arc(self.temp[0], dist(self.temp[0], self.temp[1]), self.temp[1], self.temp[1], 0, 2*math.pi-1e-6, self.bufferNum)
            self.segments.append(a)

    def updateSegment(self, cursor):
        vec = sub(cursor, self.ref_mouse)

        for t in self.temp:
            if self.segments[t[0]].ID == "arc":
                self.segments[t[0]].displace(vec)
            else:
                if t[1]>=2: self.segments[t[0]].end_point = add(self.segments[t[0]].end_point, vec)
                if t[1]<=2: self.segments[t[0]].start_point = add(self.segments[t[0]].start_point, vec)
        self.ref_mouse = cursor
        self.updateReq = True

    def checkCursor(self):
        if self.pos[0]<=self.WIN.cursor[0]<=self.pos[0]+self.size[0] and self.pos[1]<=self.WIN.cursor[1]<=self.pos[1]+self.size[1]:
            cur_px = (self.offset[0] + self.WIN.cursor[0] / self.scale, self.offset[1] + self.WIN.cursor[1] / self.scale)
            cur_mm = PX2MM(cur_px)

            prev_nn = self.nearestNode
            prev_curve = self.curve
            cur_px = MM2PX(self.__getNearestNode(cur_mm))
            cur_mm = PX2MM(cur_px)
            if self.WIN.mode == "select":
                if self.WIN.mouseClicks[0]:
                    self.curve = self.__selectCurve(cur_mm)
                    if len(self.temp)==0:
                        t = []
                        if self.nearestNode != (-1, -1): t = [self.nearestNode]
                        elif self.curve != -1: t = [self.segments[self.curve].start_point, self.segments[self.curve].end_point]

                        for i,s in enumerate(self.segments):
                            a=0
                            if s.start_point in t : a=1
                            if s.end_point in t:  a=3-a
                            if a==0 or (s.ID=="arc" and a!=2): continue
                            self.temp.append((i,a))

                        self.ref_mouse = cur_mm

                    if len(self.temp)>0: self.updateSegment(cur_mm)
                else: self.temp = []


            self.updateReq |= prev_nn != self.nearestNode or prev_curve != self.curve

            if self.WIN.mouseClicks[0]:
                if not self.penDown:
                    if NUM[self.WIN.mode]>0:
                        self.penDown = True
                        self.temp = [cur_px]
                else:
                    self.temp.append(cur_px)
                    if len(self.temp)==NUM[self.WIN.mode]:
                        self.addData()
                        self.temp = []
                        self.penDown = False
                self.updateReq = True
        else:
            if self.WIN.mouseClicks[0]:
                self.curve = -1
                self.penDown = False
                self.temp = []
                self.updateReq = True
        return self.updateReq

    def delete(self):
        if self.curve != -1:
            self.segments.pop(self.curve)
            self.curve = -1
            self.updateReq = True
        elif self.nearestNode != (-1, -1):
            self.segments = [s for s in self.segments if self.nearestNode not in (s.start_point, s.end_point)]
            self.nearestNode = (-1, -1)
            self.updateReq = True
        if self.WIN.mode == "select": self.temp = []

    def rearrange(self):
        cmp = lambda a, b: abs(a[0]-b[0])<0.1 and abs(a[1]-b[1])<0.1
        temp = [[l] for l in self.segments]

        masterFound = True
        while (masterFound):

            self.shapes = temp[1:]
            temp = temp[:1]

            # print("\nTemp:")
            # for t in temp: print([(int(l.p1[0]), int(l.p1[1]), int(l.p2[0]), int(l.p2[1])) for l in t])
            # print("\nLS : ")
            # for t in self.shapes: print([(int(l.p1[0]), int(l.p1[1]), int(l.p2[0]), int(l.p2[1])) for l in t])

            masterFound = False
            for c in self.shapes:
                found = False
                for t in temp:
                    if cmp(c[0].start_point, t[-1].end_point):
                        found = True
                        t += c
                        break
                    elif cmp(c[-1].end_point, t[-1].end_point):
                        found = True
                        for i in range(len(c)):
                            c[i] = c[len(c)-1-i]
                            c[i].swap()
                        t += c
                        break
                    elif cmp(c[0].start_point, t[0].start_point):
                        found = True
                        for i in range(len(c)):
                            c[i].swap()
                            t.insert(0, c[i])
                        break
                    elif cmp(c[-1].end_point, t[0].start_point):
                        found = True
                        for i in range(len(c)):
                            t.insert(0, c[len(c)-1-i])
                        break
                if not found:
                    # print("Not Found : ", end = '')
                    # print([(int(l.p1[0]), int(l.p1[1]), int(l.p2[0]), int(l.p2[1])) for l in c])
                    temp.append(c)
                else:
                    # print(f"Found in {n}: ", end='')
                    # print([(int(l.p1[0]), int(l.p1[1]), int(l.p2[0]), int(l.p2[1])) for l in c])
                    masterFound = True

        # print("\nFinal : ")
        # for t in temp:
        #     print(len(t), end = " : ")
        #     print([(int(l.p1[0]), int(l.p1[1]), int(l.p2[0]), int(l.p2[1])) for l in t])

        self.shapes = [Shapes(d) for d in temp]

    def __swap(self, s):
        s.start_point, s.end_point = s.end_point, s.start_point
        return s

    def __optLineInsert(self):
        self.temp = list(filter(lambda x:x.start_point != x.end_point, self.temp))
        for s in self.segments:
            if s.ID == "arc": continue
            for i in range(len(self.temp)):
                if self.temp[i].start_point in (s.start_point, s.end_point) and self.temp[i].end_point in (s.start_point, s.end_point):
                    self.temp.pop(i)
                    break
            if len(self.temp) == 0: break

        if self.temp: self.segments += self.temp

    def __references(self, pos):
        sl1 = (0, pos[1])
        sl2 = (pos[0], 0)
        el1 = (self.size[0]-1, pos[1])
        el2 = (pos[0], self.size[1]-1)
        pygame.draw.line(self.WIN.window, C_REF, sl1, el1)
        pygame.draw.line(self.WIN.window, C_REF, sl2, el2)

    def __getRectLines(self, p):
        return [p[0], (p[0][0], p[1][1]), p[1], (p[1][0], p[0][1]), p[0]]

    def __getParallelogram(self, p):
        p3 = p[2][0] - p[1][0] + p[0][0], p[2][1] - p[1][1] + p[0][1]
        return [p[0], p[1], p[2], p3, p[0]]

    def __getPolygon(self, point, center):
        a = 2*3.1415/self.bufferNum
        tmp = [rotate(point, center, i*a) for i in range(self.bufferNum)]
        tmp.append(point)
        return tmp

    def __selectCurve(self, c):
        l = len(self.segments)
        for i in range(l//2+l%2):
            if self.segments[i].coincident(c):
                return i
            elif self.segments[l - i - 1].coincident(c):
                return l-1-i
        return -1

    def __getNearestNode(self, coord):
        self.nearestNode = (-1, -1)
        for l in self.segments:
            for c in (l.start_point, l.end_point):
                if abs(c[0] - coord[0])<2 and abs(c[1] - coord[1])<2:
                    self.nearestNode = c
                    return c
        return coord

    def __isCollinear(self, a, b, c):
        ab = dist(a, b)
        bc = dist(b, c)
        ca = dist(c, a)
        return abs(bc+ca-ab) < 4

    def scrollRight(self):
        if self.offset[0] + self.size[0] / self.scale <= self.size[0]:
            self.offset = (self.offset[0] + SCSP, self.offset[1])
        if self.offset[0] + self.size[0] / self.scale > self.size[0]:
            self.offset = (self.size[0] * (1 - 1 / self.scale), self.offset[1])

    def scrollDown(self):
        if self.offset[1] + self.size[1] / self.scale <= self.size[1]:
            self.offset = (self.offset[0], self.offset[1] + SCSP)
        if self.offset[1] + self.size[1] / self.scale > self.size[1]:
            self.offset = (self.offset[0], self.size[1] * (1 - 1 / self.scale))

    def scrollLeft(self):
        if self.offset[0] >= 0:
            self.offset = (self.offset[0] - SCSP, self.offset[1])
        if self.offset[0] < 0:
            self.offset = (0, self.offset[1])

    def scrollUp(self):
        if self.offset[1] >= 0:
            self.offset = (self.offset[0], self.offset[1] - SCSP)
        if self.offset[1] < 0:
            self.offset = (self.offset[0], 0)

    # def __collinear_vectored(self, a, b, c):
    #     A = (c[0] - a[0], c[1] - a[1])
    #     B = (b[0] - a[0], b[1] - a[1])
    #     crs_pdct = A[0] * B[1] - A[1] * B[0]
    #     return abs(crs_pdct)//200 < 20 and abs(A[0])<abs(B[0]) and abs(A[1])<abs(B[1])