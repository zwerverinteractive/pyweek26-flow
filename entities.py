import pygame
from random import randint, choice, uniform, seed
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
        self.real_rect = rect
        self.surface = pygame.Surface(self.rect[-2:])
        self.images = []
        self.speed = [0, 0]
        self.dspeed = (1.005+(self.root.level/10))
        self.size = [0,0]
        self.frame = 1
        self.t = 0
        self.framespeed = 1
        self.layer = 0
        self.bullet = False
        self.die = False

    def move_towards(self):
        kill = False
        self.t += 1
        if self.t > self.framespeed:
            self.t = 0
            self.frame += 1
            if self.frame >= len(self.images):
                self.frame = 0
                if self.die:
                    kill = True
        try:
            self.surface = self.images[self.frame]
        except:
            self.frame = 0
            self.surface = self.images[self.frame]

        self.distance = self.distance*self.dspeed
        d = int(self.distance)
        self.surface = pygame.transform.scale(self.surface, (d,d))
        self.size = (d,d)

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
        b = int(self.root.level*2)-1
        self.b = b
        self.endtimers = [
            1000, 1000, 300, 1000, 600,
            800, 1000, 1000, 1000, 1000,
        ]
        self.endtimer = 0
        s = [5, 10, 5, 5, 2, 5, 5, 5 ,5,5,10,15]
        hp = [50, 50, 30, 120, 30, 50, 50,50,50,50]
        self.framespeed = s[b]
        self.images = self.root.bosses[b]
        self.timer = 0
        self.hp = hp[b]
        try:
            sound = pygame.mixer.Sound("data/sounds/taunts/"+str(b+1)+".ogg")
            sound.play()
        except:
            pass


    def update(self):
        self.timer += 1
        if self.timer > self.framespeed:
            self.timer = 0
            self.frame += 1
            if self.die:
                if self.frame >= len(self.images):
                    self.root.next_level()
                    self.root.boss = None
                    self.root.layers[2].remove(self)
                    self.frame = 0
            else:
                if self.frame >= len(self.images[0]):
                    self.frame = 0
        if self.die:
            self.surface = self.images[self.frame]
        else:
            self.endtimer += 1
            rc = (randint(0,255),randint(0,255),randint(0,255))

            w = (320 - (320/self.endtimers[self.b]) * self.endtimer)
            if w <= 1:
                self.root.player.dying()
            self.root.screen.fill(rc, (0,0,w,20))
            self.surface = self.images[0][self.frame]
            for bullet in self.root.layer_bulletsP[3]:
                try:
                    pixel_hit = self.images[1][self.frame].get_at((int(bullet.rect[0]), int(bullet.rect[1])))
                except:
                    pixel_hit = (0,0,0,255)
                if pixel_hit == (0,0,255,255):
                    self.root.sounds["bew"].play()
                    self.root.layer_bulletsP[3].remove(bullet)
                    self.surface = self.images[2][self.frame]
                    self.hp -= 1
                    if self.hp < 0:
                        self.sound = pygame.mixer.Sound("data/sounds/bossdeath.ogg")
                        self.sound.play()
                        self.endtimer = 0
                        self.framespeed = 1
                        self.die = True
                        self.images = self.root.explosions[5]

class Item(Entity):
    def __init__(self, root, rect=[160+32,100+32,64,64]):
        Entity.__init__(self, root, rect)
        s = choice(("item", "gem"))
        self.images = self.root.images[s]
        sx, sy = 0.32, 0.2
        self.speed = [uniform(-0.8,0.4), uniform(-0.5,0.3)]
        self.surface.fill((0,0,255))
        self.frame = 0
        self.distance = 1
        self.dspeed = (1.01)
        xmax = self.dspeed/8
        xmin = self.dspeed/4
        ymax = self.dspeed/7
        ymin = self.dspeed/5
        self.speed = [uniform(-xmin,xmax), uniform(-ymin,ymax)]

    def update(self):
        self.move_towards()

class Enemy(Entity):
    def __init__(self, root, rect=[160+32,100+32,64,64]):
        Entity.__init__(self, root, rect[:])
        self.images = self.root.images["willie"][0]
        self.dspeed = (1.01+(self.root.level/200))

        scale = self.root.level
        xmax = ((self.dspeed*scale)/8)
        xmin = ((self.dspeed*scale)/4)
        ymax = ((self.dspeed*scale)/7)
        ymin = ((self.dspeed*scale)/5)
        self.speed = [uniform(-xmin,xmax), uniform(-ymin,ymax)]

        self.surface.fill((0,0,255))
        self.frame = 0
        self.distance = 1


    def update(self):
        self.move_towards()
        #HITBYBULLET
        if not self.die and self.distance > 10:
            for b in self.root.layer_bulletsP[self.layer]:
                if b.rect[0] > (self.center[0]) and b.rect[0] < self.center[0]+self.size[0]:
                    if b.rect[1] > (self.center[1]) and b.rect[1] < self.center[1]+self.size[1]:
                        self.images = self.root.explosions[randint(0,4)]
                        self.frame = 0
                        b.die = True
                        self.die = True
                        self.framespeed = 1
                        s = randint(1,4)
                        self.root.sounds["xpl"+str(s)].set_volume(self.distance/64)
                        self.root.sounds["xpl"+str(s)].play()
            if self.layer > 5:
                self.root.hit(self.rect)
                self.root.layers[self.layer].remove(self)


class DualSheetEnemy(Enemy):
    def __init__(self, root):
        Enemy.__init__(self, root)
        i = (self.root.level*2)-1
        self.sprite = randint((i*4),(i*4)+3)
        self.images = self.root.images["willie"][self.sprite]
        self.framespeed = randint(10,20)


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
        self.bulletspeed = 4
        self.pitch = 0
        self.frame = 0
        self.t = 0

    def dying(self):
        if self.die == False:
            self.speed = [0,0]
            self.root.sounds["gameover"].play()
            self.die = True
            pygame.mixer.music.load("data/music/gameoverwait.ogg")
            pygame.mixer.music.play(-1)

    def update(self):
        if self.die:
            self.t += 1
            if self.t > 2:
                self.t = 0
                if self.frame > 40:
                    self.root.game_over()
                else:
                    self.surface = self.root.explosions[6][self.frame]
                    self.frame += 1
        else:
            self.t += 1
            if self.t > self.bulletspeed + randint(0,3):
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
            mspeed = 16
            self.speed[0] = (dx)*(dist/10)
            self.speed[0] = clamp(self.speed[0], -mspeed/1.2,mspeed/1.2)
            self.speed[1] = (dy)*(dist/10)
            self.speed[1] = clamp(self.speed[1], -(mspeed/2),(mspeed/2))
            self.yaw = (200 - (self.rect[1]/4))-75
            self.pitch = (320 - (self.rect[0]/2)-(320/2))

class Mouthbeams(Entity):
    def __init__(self, root, rect=[0,0,5,5]):
        Entity.__init__(self, root, rect)
        rc = (randint(128,255),randint(128,255),randint(128,255))
        self.images = self.root.images["willie"][0]
        self.surface.fill(rc)
        self.distance = 64
        self.bullet = True
        self.layer = 4
        self.root.sounds["mouthbeam0"].stop()
        self.root.sounds["mouthbeam0"].play()
        #if randint(0,1) == 0:
        #else:
        #    self.root.sounds["mouthbeam1"].play()

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
