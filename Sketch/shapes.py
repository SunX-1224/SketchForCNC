import pygame
import math
from utils import *

class Arc:
    ID = 'arc'
    def __init__(self, center, radius, p1, p2, sa, ea):
        self.center = center
        self.radius = radius
        self.start_angle =  sa
        self.end_angle = ea
        self.start_point = p1
        self.end_point = p2

    def getStatus(self):
        p1 = self.start_point
        p2 = self.end_point
        l1 = f"Center : ({self.center[0]:.2f}, {self.center[1]:.2f}) Radius : {self.radius:.2f}".format(self.center, self.radius)
        # l2 = f"sp : ({p1[0]:.2f}, {p1[1]:.2f}) ep : ({p2[0]:.2f}, {p2[1]:.2f})".format(p1, p2)
        l2 = f"sa : {int(self.start_angle*180/3.1415)} , ea = {int(self.end_angle*180/3.1415)}"
        return [l1, l2]

    def draw(self, surface, color):
        pygame.draw.circle(surface, C_REF, MM2PX(self.center), 2)
        if abs((self.end_angle-self.start_angle)%(2 * math.pi)-(2 * math.pi))<0.01:
            pygame.draw.circle(surface, color, MM2PX(self.center), self.radius/MMPPX, 1)
            return
        rect = ((self.center[0]-self.radius)/MMPPX, (self.center[1]-self.radius)/MMPPX, 2*self.radius/MMPPX, 2*self.radius/MMPPX)
        pygame.draw.arc(surface, color, rect, self.start_angle, self.end_angle)

    def coincident(self, c):
        a = math.atan2(-(c[1]-self.center[1]), c[0]-self.center[0])%(2*math.pi)
        return abs(dist(self.center, c) - self.radius) < 1 and self.checkAngle(a)

    def checkAngle(self, a):
        return (a-self.start_angle)%(2*math.pi)<=(self.end_angle-self.start_angle)%(2*math.pi)

    def swap(self):
        self.start_point, self.end_point = self.end_point, self.start_point

    def x_intersection(self, x,y):
        d = y - self.center[1]
        if abs(d)>self.radius: return 0
        det = (self.radius**2 - d**2)**0.5
        x1 = self.center[0]+det
        x2 = self.center[0]-det

        a1 = math.atan2(-d, x1)
        a2 = math.atan2(-d, x2)

        if a1 < 0: a1 += 2 * math.pi
        if a2 < 0: a2 += 2 * math.pi

        n = 0
        if x1>x and self.checkAngle(a1): n+=1
        if x2>x and self.checkAngle(a2): n+=1
        # print((x, y), self.center, d, det, self.radius, n, (x1, x2))
        return n

    def displace(self, vec):
        self.start_point = add(self.start_point, vec)
        self.end_point = add(self.end_point, vec)
        self.center =add(self.center, vec)

    def isClockwise(self):
        p = self.start_point
        a = self.end_angle - self.start_angle + (0 if self.start_angle < self.end_angle else 2 * math.pi)
        dif = math.atan2(-(p[1] - self.center[1]), p[0] - self.center[0])
        if dif < 0: dif += 2 * math.pi
        if abs(dif - self.start_angle) < 0.01:
            return True
        else:
            return False

    @staticmethod
    def findCenter( p1, p2, p3):
        a1 = 2 * (p2[0] - p1[0])
        a2 = 2 * (p3[0] - p1[0])
        b1 = 2 * (p2[1] - p1[1])
        b2 = 2 * (p3[1] - p1[1])
        c1 = p2[0] ** 2 + p2[1] ** 2 - p1[0] ** 2 - p1[1] ** 2
        c2 = p3[0] ** 2 + p3[1] ** 2 - p1[0] ** 2 - p1[1] ** 2

        det = a1 * b2 - a2 * b1
        if abs(det) == 0: return (-1, -1)
        y = (a1 * c2 - a2 * c1) / det
        x = (b2 * c1 - b1 * c2) / det
        return (x, y)

    @staticmethod
    def from3p(p1, p2, p3):
        c = Arc.findCenter(p1, p2, p3)
        r = dist(p1, c)

        a1 = math.atan2(-(p1[1] - c[1]), p1[0] - c[0])
        a2 = math.atan2(-(p2[1] - c[1]), p2[0] - c[0])
        ac = math.atan2(-(p3[1] - c[1]), p3[0] - c[0])

        if a1 < 0: a1 += 2 * math.pi
        if a2 < 0: a2 += 2 * math.pi
        if ac < 0: ac += 2 * math.pi

        a1, a2 = min(a1, a2), max(a1, a2)
        if not (a1 < ac < a2):
            a1, a2 = a2, a1
        return Arc(c, r, p1, p2, a1, a2)

class Line:
    ID = 'line'
    def __init__(self, p1, p2):
        self.start_point = p1
        self.end_point = p2

    def draw(self, surface, color):
        pygame.draw.line(surface, color, MM2PX(self.start_point), MM2PX(self.end_point))

    def coincident(self, c):
        ab = dist(self.start_point, self.end_point)
        bc = dist(self.end_point, c)
        ca = dist(c, self.start_point)
        return abs(bc + ca - ab) < 1

    def swap(self):
        self.start_point, self.end_point = self.end_point, self.start_point

    def x_intersection(self,x, y):
        if (min(self.start_point[1], self.end_point[1]) < y < max(self.start_point[1],self.end_point[1])
                and x < max(self.start_point[0], self.end_point[0])):
            xints = (y - self.start_point[1]) * (self.end_point[0] - self.start_point[0]) / (self.end_point[1] - self.start_point[1]) + self.start_point[0]
            if x < xints: return 1
        return 0

    def fixLength(self, l):
        M = ((self.start_point[0]+self.end_point[0])/2, (self.start_point[1]+self.end_point[1])/2)
        OA = (self.start_point[0]-M[0], self.start_point[1]-M[1])
        OB = (self.end_point[0]-M[0], self.end_point[1]-M[1])
        m = (OA[0]**2 + OA[1]**2)**0.5
        OA = (OA[0]/m, OA[1]/m)
        OB = (OB[0]/m, OB[1]/m)
        self.start_point = (M[0]+OA[0]*l/2, M[1]+OA[1]*l/2)
        self.end_point = (M[0]+OB[0]*l/2, M[1]+OB[1]*l/2)
        self.fixed = True

    def changePoints(self, sp, ep):
        self.start_point, self.end_point = sp, ep

class Shapes:
    area = 0
    def __init__(self, data):
        self.data = data
        self.index = 0
        # self.temp = []
        self.centroid = self.findCentroid()
        self.inPoint = self.findPoint()

    def draw(self, surface):
        color = C_REF if self.index == 0 else C_HLT
        for d in self.data:
            d.draw(surface, color)
        # if self.temp: pygame.draw.lines(surface, C_HLT, False, self.temp)
        pygame.draw.circle(surface, color, MM2PX(self.inPoint), 4)

    def findCentroid(self):
        res = 16
        cx = 0
        cy = 0
        temp = []
        for c in self.data:
            if c.ID == "arc":
                p = c.start_point
                a = c.end_angle - c.start_angle + (0 if c.start_angle < c.end_angle else 2 * math.pi)
                n = int(a*res/math.pi)+1
                if c.isClockwise():
                    da = -a/n
                else:
                    da = a/n
                # print(p, da, a, " : ", c.start_angle, c.end_angle, dif)
                ls = [rotate(p, c.center, da*i) for i in range(n)]
                temp += ls
            else:
                temp.append(c.start_point)
        temp.append(temp[0])
        n = len(temp)
        for i in range(n-1):
            a = temp[i][0] * temp[i+1][1] - temp[i+1][0] * temp[i][1]
            self.area += a
            cx += (temp[i][0] + temp[i+1][0]) * a
            cy += (temp[i][1] + temp[i+1][1]) * a

        self.area *= 0.5
        cx /= (6 * self.area)
        cy /= (6 * self.area)

        cx = round(cx, 4)
        cy = round(cy, 4)
        self.area = abs(self.area)
        # self.temp = [MM2PX(t) for t in temp]
        return cx, cy

    def findPoint(self):
        if self.point_in_polygon(*self.centroid): return self.centroid
        n = len(self.data)
        self.temp = []
        for i in range(n):
            p1 = self.data[i].start_point
            p2 = self.data[i].end_point
            j = i+1 if i+1<n else 0
            p3 = self.data[j].end_point
            c = add(p1, p2)
            c = add(c, p3)
            c = c[0]/3, c[1]/3
            if self.point_in_polygon(*c): return c
        return self.centroid

    def point_in_polygon(self, x, y):
        num_intersections = 0
        n = len(self.data)
        for i in range(n):
                num_intersections += self.data[i].x_intersection(x, y)
        return num_intersections % 2 == 1

    def gcode2d(self, zSafe, zWork):
        gcode = []
        gcode.append(move(z=zSafe, f=400))
        gcode.append(move(*self.data[0].start_point))
        gcode.append(move(z=zWork, f=300))
        self.gcodeSlice(gcode)
        return gcode

    def gcode3d(self, zsafe, stockTop, stockHeight, cutDepth):
        gcode = []
        gcode.append(move(z=zSafe, f=400))
        gcode.append(move(*self.data[0].start_point))

        zWork = stockTop
        for i in range(stockHeight//cutDepth):
            zWork = zWork - cutDepth
            gcode.append(move(z=zWork, f=300))
            self.gcodeSlice(gcode)
        return gcode

    def gcodeSlice(self, gcode):
        for d in self.data:
            if d.ID == "line": gcode.append(line(*ROUND(d.end_point)))
            elif d.ID == "arc":
                if d.isClockwise(): gcode.append(arc_cw(*ROUND(d.end_point), r=d.radius))
                else: gcode.append(arc_ccw(*ROUND(d.end_point), r=d.radius))

    @staticmethod
    def shoelace_area(coords):
        area = 0
        for i in range(len(coords)):
            area += coords[i].start_point[0] * coords[i].end_point[1] - coords[i].start_point[1] * coords[i].end_point[0]
        return abs(area)

    @staticmethod
    def index(shapes):
        shapes = sorted(shapes, key=lambda x:x.area)
        for i in range(len(shapes)):
            for j in range(i+1, len(shapes)):
                if shapes[j].point_in_polygon(*shapes[i].inPoint):
                    shapes[i].index  = (shapes[i].index + 1)%2

