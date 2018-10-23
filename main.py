import pygame
from random import choice, randint
from math import sin
from entities import *

def sheet(image, size):
    l = []
    img_size = image.get_size()
    for y in range(int(img_size[1]/size)):
        for x in range(int(img_size[0]/size)):
            s = pygame.Surface((size, size))
            s.blit(image, (-(x*size), -(y*size)))
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
        self.xs = 0
        self.ys = 0
        for i in range(5): self.layers.append([])
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
            "item" : sheet(pygame.image.load("data/item.png"), 64)
        }
        self.xs = 1
        self.stripes = False
        self.bg0 = pygame.Surface((320/2,200))
        self.bg0.set_colorkey((0,0,0))
        self.bg1 = pygame.Surface((320/2,200))

        self.zwischen = pygame.Surface((320, 200))
        m = self.scale_mouse(pygame.mouse.get_pos())
        self.player = Player(self, [m[0],m[1],32,32])
        self.layers[4].append(self.player)
        self.gamespeed = 4

    def update(self):
        if randint(0,64) == 0:
            self.layers[0] = [Item(self)] + self.layers[0]
        #    self.layers[1].append(Enemy(self, [randint(32,320-32),-64,32,32]))
        #UPDATE
        self.input()
        self.dt += 0.001
        for layer in self.layers:
            for entity in layer:
                entity.update()
                entity.finalize()
        #DRAW
        self.xs = abs(sin(self.dt*3)*3)
        self.ys = abs(sin(self.dt*2)*320)+1
        self.gamespeed = abs(sin(self.dt)*40)
        """
        self.xs += randint(-1,1)
        if self.xs < 0: self.xs = 0
        if self.xs > 2: self.xs = 2
        """

        bg0speed = int(self.gamespeed/4)+1
        self.bg0.scroll(-int(self.xs+1),bg0speed)
        self.bg1.scroll(0,bg0speed)
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
        self.bg0.fill((0,0,0), (150,1,1,bg0speed+8))

        if randint(0,20) ==0:
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

        self.zwischen.blit(self.bg1, (0,0))
        self.zwischen.blit(pygame.transform.flip(self.bg1, True, False), (320/2, 0))

        self.zwischen.blit(self.bg0, (-10,0))
        self.zwischen.blit(pygame.transform.flip(self.bg0, True, False), ((320/2)+10, 0))
        #self.zwischen.fill((0,0,0), (0,0,320,64))
        #self.player.yaw += 0.1
        y = self.player.yaw
        self.screen.blit(pygame.transform.scale(self.zwischen, (320,int(200-y))), (0,y))
        f = pygame.transform.flip(self.zwischen, False, True)
        self.screen.blit(pygame.transform.scale(f, (320,int(y)+1)), (0, 0))

        for layer in self.layers:
            for entity in layer:
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
