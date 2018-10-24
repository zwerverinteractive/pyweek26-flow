import pygame
from random import choice, randint
from math import sin
from entities import *

def sheet(image, size):
    l = []
    img_size = image.get_size()
    for y in range(int(img_size[1]/size[1])):
        for x in range(int(img_size[0]/size[0])):
            s = pygame.Surface(size)
            s.blit(image, (-(x*size[0]), -(y*size[1])))
            s.set_colorkey((0,0,0))
            l.append(s)
    return l

class Game():
    def __init__(self):
        pygame.init()
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.window_res = (800,600)
        self.screen_res = (320,200)
        self.window = pygame.display.set_mode(self.window_res, pygame.RESIZABLE)
        self.screen = pygame.Surface(self.screen_res)
        self.screen.set_alpha(50)
        self.buttons = [None, None, None, None, None]
        self.layers = []
        self.layer_bulletsP = []
        self.xs = 0
        self.ys = 0
        for i in range(10):
            self.layers.append([])
            self.layer_bulletsP.append([])
        self.setup()
        for i in range(200):
            self.update()
        self.start()

    def setup(self):
        self.rows = [
            [[0,128,0], 320, [0,0,0,0]],
            [[0,255,0], 200, [0,0,0,0]],
            [[0,0,255], 160, [0,0,0,0]],
            [[0,0,128], 100, [0,0,0,0]],
            [[0,255,255],70, [0,0,0,0]],
            [[0,128,128],30, [0,0,0,0]],
        ]

        self.images = {
            "player" : pygame.image.load("data/player.png"),
            "active" : sheet(pygame.image.load("data/active.png"), (64,64)),
            "item" : sheet(pygame.image.load("data/item.png"), (64,64)),
            "gem" : sheet(pygame.image.load("data/gem.png"), (64,64)),
            "itemrainbow" : sheet(pygame.image.load("data/itemrainbow.png"), (64,64)),
            "cracks" : sheet(pygame.image.load("data/cracks.png"), (64,64)),
            #backgrounds
            "water": sheet(pygame.image.load("data/water.png"), (160,1)),
            "pizza": sheet(pygame.image.load("data/pizza.png"), (160,1)),
            "flowers": sheet(pygame.image.load("data/flowers.png"), (160,1)),
            "flower": sheet(pygame.image.load("data/flower.png"), (160,1)),
            "floor": sheet(pygame.image.load("data/floor.png"), (160,1)),
            "eye": sheet(pygame.image.load("data/eye.png"), (160,1)),
        }
        self.explosions = [
            sheet(pygame.image.load("data/explosions/1.png"), (64,64)),
            sheet(pygame.image.load("data/explosions/2.png"), (64,64)),
            sheet(pygame.image.load("data/explosions/3.png"), (64,64)),
            sheet(pygame.image.load("data/explosions/4.png"), (64,64)),
            sheet(pygame.image.load("data/explosions/5.png"), (64,64)),
        ]
        self.bosses = [
            sheet(pygame.image.load("data/boss1.png"), (320,200)),
        ]
        self.timer = 0
        self.boss = None
        self.xs = 1
        self.stripes = False
        self.bg0 = pygame.Surface((320/2,200))
        self.bg0.set_colorkey((0,0,0))
        self.bg1 = pygame.Surface((320/2,200))
        self.current_image = None
        self.zwischen = pygame.Surface((320, 200))
        m = self.scale_mouse(pygame.mouse.get_pos())
        self.player = Player(self, [m[0],m[1],32,32])
        self.layers[5].append(self.player)
        self.gamespeed = 0
        self.overwrite_colors = [None, None]

    def update(self):
        self.timer += 0.001
        if self.timer >= 3:
            if self.gamespeed < 100:
                self.boss = Boss(self)
                self.layers[0].append(self.boss)
                self.gamespeed = 200
                self.current_image = None
                self.stripes = False
        else:
            if self.gamespeed < 64:
                self.gamespeed += 0.001
            if randint(0,200) == 0:
                self.layers[0] = [Enemy(self)] + self.layers[0]
            if randint(0,500) == 0:
                self.layers[0] = [Item(self)] + self.layers[0]

            if randint(0,1500) == 0:
                if self.current_image == None:
                    i = choice(("water", "pizza", "flower", "flowers", "floor", "eye"))
                    self.current_image = self.images[i]
                    self.image_y = 0
                else:
                    self.current_image = None


        #    self.layers[1].append(Enemy(self, [randint(32,320-32),-64,32,32]))
        #UPDATE
        self.input()
        self.dt += 0.001
        for l, layer in enumerate(self.layers):
            for entity in self.layer_bulletsP[l]:
                entity.update()
                entity.finalize()
            for entity in self.layers[l]:
                entity.update()
                entity.finalize()
        #DRAW
        self.xs = abs(sin(self.dt*3)*3)
        self.ys = abs(sin(self.dt*2)*320)+1
        """
        self.xs += randint(-1,1)
        if self.xs < 0: self.xs = 0
        if self.xs > 2: self.xs = 2
        """
        bg0speed = int(self.gamespeed/4)+1
        self.bg0.scroll(-int(self.xs+1),bg0speed)
        self.bg1.scroll(abs(int(sin(self.xs+1))),bg0speed)
        for r, row in enumerate(self.rows):
            for i in range(4):
                if randint(0,20) == 0:
                    row[2][i] += randint(-1,1)
            for c in range(3):
                row[0][c] += row[2][c]
                row[0][c] = clamp(row[0][c], 1, 255)
            row[1] += row[2][3]
            if row[1] > self.ys or row[1] < 1 or randint(0,10) == 0:
                row[2][3] = -row[2][3]
            for c in range(3):
                if row[0][c] >= 255 or row[0][c] <= 0 or randint(0,10) == 0:
                    row[2][c] = -row[2][c]
            w = row[1]
            x = 160-(w/2)
            self.bg0.fill(row[0], (x,0,w,bg0speed+2))
            self.bg1.fill(row[0], (x,0,w,bg0speed+2))

        if self.current_image == None:
            for c, color in enumerate(self.overwrite_colors):
                if randint(0,64) == 0:
                    if self.overwrite_colors[c] == None:
                        self.overwrite_colors[c] = (randint(0,255),randint(0,255),randint(0,255))
                    else:
                        self.overwrite_colors[c] = None
        else:
            self.overwrite_colors = [None, None]

        if randint(0,1500) ==0:
            if self.stripes: self.stripes = False
            else:
                self.stripes = True
                self.ff = choice((32,64,128,256))
                self.dd = randint(1,20)

        if self.stripes:
            if self.dt%64:
                rc = (randint(0,255),randint(0,255),randint(0,255))
                self.bg0.fill(rc, (0,0,160,self.dd))
                self.bg1.fill(rc, (0,3,160,self.dd))

        if not self.current_image == None:
            for i in range(bg0speed+2):
                self.bg0.blit(self.current_image[self.image_y], (0,i))
                self.bg1.blit(self.current_image[self.image_y], (0,i))
                self.image_y += 1
                if self.image_y >= len(self.current_image):
                    self.image_y = 0

        if not self.overwrite_colors[0] == None:
            self.bg0.fill(self.overwrite_colors[0], (0,0,320,bg0speed+2))
        if not self.overwrite_colors[1] == None:
            self.bg1.fill(self.overwrite_colors[1], (0,0,320,bg0speed+2))

        self.zwischen.blit(self.bg1, (0,0))
        self.zwischen.blit(pygame.transform.flip(self.bg1, True, False), (320/2, 0))

        self.zwischen.blit(self.bg0, (0,0))
        self.zwischen.blit(pygame.transform.flip(self.bg0, True, False), (320/2, 0))
        a = abs(sin(self.dt/2)*255)
        self.zwischen.set_alpha(120)
        #self.zwischen.fill((0,0,0), (0,0,320,64))
        #self.player.yaw += 0.1
        y = self.player.yaw
        self.screen.blit(pygame.transform.scale(self.zwischen, (320,int(200-y))), (0,y))
        f = pygame.transform.flip(self.zwischen, False, True)
        self.screen.blit(pygame.transform.scale(f, (320,int(y)+1)), (0, 0))

        for l, layer in enumerate(self.layers):
            for entity in self.layer_bulletsP[l]:
                self.screen.blit(entity.surface, entity.center)
            for entity in self.layers[l]:
                self.screen.blit(entity.surface, entity.center)

    def start(self):
        self.running = True
        while self.running:
            self.update()
            pygame.transform.scale(self.screen, self.window_res, self.window)
            pygame.display.flip()
            self.clock.tick(self.fps)
        pygame.quit()

    def scale_mouse(self, pos):
        scale = (self.screen_res[0]/self.window_res[0],
                    self.screen_res[1]/self.window_res[1])
        return [pos[0]*scale[0],pos[1]*scale[1]]

    def input(self):
        self.mouse_pos = self.scale_mouse(pygame.mouse.get_pos())
        self.mouse_rel = self.scale_mouse(pygame.mouse.get_rel())
        #True is down, False is up, None is stateless/inactive
        #Button is only up for a single loop
        for b, button in enumerate(self.buttons):
            if button == False: self.button = None
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                for i in range(5):
                    if e.button == i: self.buttons[i] == True
            elif e.type == pygame.MOUSEBUTTONUP:
                for i in range(5):
                    if e.button == i: self.buttons[i] == False
            elif e.type == pygame.VIDEORESIZE:
                self.window_res = e.w, e.h
                self.window = pygame.display.set_mode(self.window_res, pygame.RESIZABLE)
game = Game()
print("BYE!")
