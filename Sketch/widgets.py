import pygame
import math
from utils import *

class Widget:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.surface = pygame.Surface(self.size)

    def draw(self, win):
        win.blit(self.surface, self.pos)

class Card(Widget):
    def __init__(self, pos, size, task, isClickable = False, mode=None):
        super().__init__( pos, size)
        self.isClickable = isClickable
        self.task = task
        self.color = C_BG if not isClickable else C_BUTTON_UP
        self.function = None

    def draw(self, win,  labels = None, flagColor = None):
        pygame.draw.rect(self.surface, self.color, (0, 0, self.size[0] - 4, self.size[1] - 4), border_radius=4)

        lpos = lambda s, t:max((s-t)//2, 0)
        text = FONT_S.render(self.task, True, C_LABEL)
        pos =  lpos(self.size[0], text.get_size()[0]),lpos(self.size[1], text.get_size()[1]) if not labels else 4

        self.surface.blit(text,pos)
        if labels:
            for l in labels:
                text = FONT_S.render(l, True, C_LABEL)
                pos = 4, pos[1]+text.get_size()[1]+4
                self.surface.blit(text, pos)
        win.blit(self.surface, self.pos)

    def cursorEffect(self, cursorPos, mode, mouseDown = False):
        if not self.isClickable: return False

        if self.pos[0]<=cursorPos[0]<=self.pos[0]+self.size[0] and self.pos[1]<=cursorPos[1]<=self.pos[1]+self.size[1]:
                err = False
                if mouseDown: err = not self.function(self.task.lower())
                self.color = C_BUTTON_DOWN if mouseDown else C_BUTTON_HOVER
                self.color = C_ERROR if err else self.color
        else:
            self.color = C_BUTTON_UP
        if self.task.lower() == mode: self.color = C_BUTTON_DOWN
        return True

class HorScrollBar(Widget):
    def __init__(self, pos, width):
        super().__init__(pos, (width, SCBAR_T))

    def draw(self,win, offset, scale):
        self.surface.fill(C_BORDER)
        pygame.draw.rect(self.surface, C_SLIDER, (offset[0], 0, self.size[0]/scale, self.size[1]), border_radius=2)
        win.blit(self.surface, self.pos)


class VerScrollBar(Widget):
    def __init__(self, pos, height):
        super().__init__(pos, (SCBAR_T, height))

    def draw(self,win, offset, scale):
        self.surface.fill(C_BORDER)
        pygame.draw.rect(self.surface, C_SLIDER, (0,offset[1], self.size[1], self.size[1]/scale), border_radius=2)
        win.blit(self.surface, self.pos)



