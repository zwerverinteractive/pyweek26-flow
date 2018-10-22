import pygame
from math import hypot

def clamp(n,min,max):
    if n < min: n = min
    if n > max: n = max
    return n

def isinbetween(n,min,max):
    if n >= min and n <= max:
        return True
    return False

class Entity():
    def __init__(self, root, rect=[0,0,32,32]):
        self.root = root
        self.rect = rect
        self.center = rect[:-2]
        self.surface = pygame.Surface(self.rect[-2:])
        self.images = []
        self.speed = [0, 0]

    def finalize(self):
        self.rect[0] += self.speed[0]
        self.rect[1] += self.speed[1]
        self.center = [int(self.rect[0]-(self.rect[2]/2)), int(self.rect[1]-(self.rect[3]/2))]

class Item(Entity):
    def __init__(self, root, rect=[160,100,10,10]):
        Entity.__init__(self, root, rect)
        self.surface.fill((0,0,255))

class Bullet(Entity):
    def __init__(self, root, rect=[0,0,5,5]):
        Entity.__init__(self, root, rect)
        self.surface.fill((0,0,255))

class Enemy(Entity):
    def __init__(self, root, rect=[0,0,32,32]):
        Entity.__init__(self, root, rect)
        self.surface.fill((255,0,0))
        self.speed[1] = 2

    def update(self):
        if self.rect[1] > 200:
            self.root.layers[1].remove(self)

class Player(Entity):
    def __init__(self, root, rect=[0,0,32,32]):
        Entity.__init__(self, root, rect)
        self.images = []
        for y in range(5):
            self.images.append([])
            for x in range(3):
                s = pygame.Surface((32,32))
                s.blit(self.root.images["sprite1"], (-(x*32), -(y*32)))
                s.set_colorkey((0,0,0))
                self.images[y].append(s)
        self.surface = self.images[2][1]
        self.max = 3
        self.yaw = 0
        self.pitch = 0

    def update(self):
        ix = int((self.rect[0]/320)*3)
        iy = int((self.rect[1]/200)*5)
        self.surface= self.images[iy][ix]

        speed = 4
        accel = 0.2
        px, py = self.rect[0], self.rect[1]
        mx, my = self.root.mouse_pos
        dx, dy = mx - px, my - py
        dist = hypot(dx, dy)
        try:
            dx, dy = dx/dist, dy/dist
        except ZeroDivisionError:
            dx, dy = 0, 0
        self.speed[0] = (dx)*(dist/10)
        self.speed[1] = (dy)*(dist/10)
        self.yaw = (200 - (self.rect[1]/2))-50
        self.pitch = (320 - (self.rect[0]/2)-(320/4))
