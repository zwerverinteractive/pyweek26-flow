import pygame
from random import randint, choice, uniform
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
        self.size = [0,0]
        self.frame = 1
        self.layer = 0
        self.bullet = False
        self.die = False

    def move_towards(self):
        self.surface = self.images[self.frame].copy()
        self.distance = self.distance*1.02
        d = int(self.distance)
        self.surface = pygame.transform.scale(self.surface, (d,d))
        self.size = (d,d)
        self.frame += 1
        kill = False
        if self.frame >= len(self.images):
            self.frame = 0
            if self.die:
                kill = True
        if not int(self.distance/12) == self.layer and self.layer <= 5:
            self.root.layers[self.layer].remove(self)
            self.layer = int(self.distance/12)
            self.root.layers[self.layer].append(self)
        if self.distance > 128 or kill:
            self.root.layers[self.layer].remove(self)
        self.rect[1] -= (self.root.player.speed[1]/32)*(self.distance/2)

    def move_from(self):
        #self.surface = self.images[self.frame].copy()
        self.distance = self.distance/1.02
        d = int(self.distance)
        self.surface = pygame.transform.scale(self.surface, (int(d/16),int(d/16)))
        self.size = (int(d/16),int(d/16))
        self.frame += 1
        kill = False
        if self.frame >= len(self.images):
            self.frame = 0
            if self.die:
                kill = True

        if not int(self.distance/12) == self.layer:
            self.root.layer_bulletsP[self.layer].remove(self)
            self.layer = int(self.distance/12)
            self.root.layer_bulletsP[self.layer].append(self)
        if self.distance < 10 or kill:
            self.root.layer_bulletsP[self.layer].remove(self)
        self.rect[1] -= (self.root.player.speed[1]/32)*(self.distance/2)

    def finalize(self):
        self.rect[0] += self.speed[0]
        self.rect[1] += self.speed[1]
        self.center = [int(self.rect[0]-(self.rect[2]/2)), int(self.rect[1]-(self.rect[3]/2))]

class Boss(Entity):
    def __init__(self, root, rect=[160,100,320,200]):
        Entity.__init__(self, root, rect)
        self.images = self.root.bosses[0]
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer > 5:
            self.timer = 0
            self.frame += 1
            if self.frame >= len(self.images):
                self.frame = 0
            self.surface = self.images[self.frame].copy()

class Item(Entity):
    def __init__(self, root, rect=[160+32,100+32,64,64]):
        Entity.__init__(self, root, rect)
        s = choice(("item", "gem", "itemrainbow"))
        self.images = self.root.images[s]
        sx, sy = 0.32, 0.2
        self.speed = [uniform(-0.8,0.4), uniform(-0.5,0.3)]
        self.surface.fill((0,0,255))
        self.frame = 0
        self.distance = 1

    def update(self):
        self.move_towards()

class Enemy(Entity):
    def __init__(self, root, rect=[160+32,100+32,64,64]):
        Entity.__init__(self, root, rect[:])
        self.images = self.root.images["active"]
        self.speed = [uniform(-0.8,0.4), uniform(-0.5,0.3)]
        self.surface.fill((0,0,255))
        self.frame = 0
        self.distance = 1

    def update(self):
        self.move_towards()
        #HITBYBULLET
        if not self.die and self.distance > 10:
            for b in self.root.layer_bulletsP[self.layer]:
                s = 3
                if b.rect[0] > (self.rect[0]-(self.size[0]/s)) and b.rect[0] < self.rect[0]+(self.size[0]/s):
                    if b.rect[1] < self.rect[1]+(self.size[1]/s) and b.rect[1] > self.rect[1]-(self.size[1]/s):
                        self.images = self.root.explosions[randint(0,4)]
                        self.frame = 0
                        b.die = True
                        self.die = True


class Player(Entity):
    def __init__(self, root, rect=[0,0,32,32]):
        Entity.__init__(self, root, rect)
        self.images = []
        for y in range(5):
            self.images.append([])
            for x in range(3):
                s = pygame.Surface((32,32))
                s.blit(self.root.images["player"], (-(x*32), -(y*32)))
                s.set_colorkey((0,0,0))
                self.images[y].append(s)
        self.surface = self.images[2][1]
        self.max = 3
        self.yaw = 0
        self.pitch = 0
        self.t = 0

    def update(self):
        self.t += 1
        if self.t > 5 + randint(0,1):
            #fire bullet hooray!
            self.t = 0
            dx, dy, dist = speedangle(160,100,self.rect[0],self.rect[1])
            beam = Mouthbeams(self.root, [self.rect[0],self.rect[1], 5,5])
            beam.speed = [(dx*dist)/80,(dy*dist)/80]
            self.root.layer_bulletsP[4].append(beam)

        ix = int((self.rect[0]/320)*3)
        iy = int((self.rect[1]/200)*5)
        self.surface= self.images[iy][ix]
        speed = 4
        accel = 0.2
        dx, dy, dist = speedangle(*self.root.mouse_pos, self.rect[0], self.rect[1])
        mspeed = 8
        self.speed[0] = (dx)*(dist/10)
        self.speed[0] = clamp(self.speed[0], -mspeed,mspeed)
        self.speed[1] = (dy)*(dist/10)
        self.speed[1] = clamp(self.speed[1], -(mspeed/2),(mspeed/2))
        self.yaw = (200 - (self.rect[1]/4))-75
        self.pitch = (320 - (self.rect[0]/2)-(320/2))

class Mouthbeams(Entity):
    def __init__(self, root, rect=[0,0,5,5]):
        Entity.__init__(self, root, rect)
        rc = (randint(128,255),randint(128,255),randint(128,255))
        self.images = self.root.images["item"]
        self.surface.fill(rc)
        self.distance = 64
        self.bullet = True
        self.layer = 4

    def update(self):
        self.move_from()
        rc = (randint(128,255),randint(128,255),randint(128,255))
        self.surface.fill(rc)

def speedangle(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        dist = hypot(dx, dy)
        try:
            dx, dy = dx/dist, dy/dist
        except ZeroDivisionError:
            dx, dy = 0, 0
        return dx, dy, dist
