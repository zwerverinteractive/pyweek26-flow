import pygame
from random import choice, randint, seed
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

def sheetsheet(image, size):
    l = [[]]
    t = 0
    a = 0
    img_size = image.get_size()
    for y in range(int(img_size[1]/size[1])):
        for x in range(int(img_size[0]/size[0])):
            s = pygame.Surface(size)
            s.blit(image, (-(x*size[0]), -(y*size[1])))
            s.set_colorkey((0,0,0))
            l[a].append(s)
            t += 1
            if t > 1:
                t = 0
                a += 1
                l.append([])
    return l

class Game():
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 32, 512)
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
        self.mouthbeem = False
        for i in range(10):
            self.layers.append([])
            self.layer_bulletsP.append([])
        self.level = 7
        self.started = False
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
            "title" : sheet(pygame.image.load("data/titlescreen.png"), (320,200)),
            "bosswarning" : sheet(pygame.image.load("data/bosswarning.png"), (117,54)),
            "gameover" : sheet(pygame.image.load("data/gameover.png"), (320,200)),
            "mouthbeem" : sheet(pygame.image.load("data/mouthbeem.png"), (320,200)),
            "player" : pygame.image.load("data/player.png"),
            "cracks" : sheet(pygame.image.load("data/cracks.png"), (128,128)),
            "willie" : sheetsheet(pygame.image.load("data/creatures.png"), (64,64)),
            #backgrounds
            "backgrounds" : sheet(pygame.image.load("data/backgrounds.png"), (160,160)),
        }
        backgrounds = self.images["backgrounds"]
        self.images["backgrounds"] = []
        for bg in backgrounds:
            self.images["backgrounds"].append(sheet(bg, (160,1)))


        self.explosions = [
            sheet(pygame.image.load("data/explosions/1.png"), (64,64)),
            sheet(pygame.image.load("data/explosions/2.png"), (64,64)),
            sheet(pygame.image.load("data/explosions/3.png"), (64,64)),
            sheet(pygame.image.load("data/explosions/4.png"), (64,64)),
            sheet(pygame.image.load("data/explosions/5.png"), (64,64)),
            sheet(pygame.image.load("data/explosions/boss.png"), (320,200)),
        ]
        self.bosses = []
        for i in range(8):
            self.bosses.append([
                sheet(pygame.image.load("data/boss/boss"+str(i+1)+".png"), (320,200)),
                sheet(pygame.image.load("data/boss/boss"+str(i+1)+"-HIT.png"), (320,200)),
                sheet(pygame.image.load("data/boss/boss"+str(i+1)+"-WHITE.png"), (320,200)),
            ])

        self.sounds = {
            "gameover" : pygame.mixer.Sound("data/sounds/gameover.ogg"),
            "gamestart": pygame.mixer.Sound("data/sounds/gamestart.ogg"),
            "mouthbeam0": pygame.mixer.Sound("data/sounds/mouthbeam0.ogg"),
            "mouthbeam1": pygame.mixer.Sound("data/sounds/mouthbeam0.ogg"),
            "alarm": pygame.mixer.Sound("data/sounds/alarm.ogg"),
            "bew": pygame.mixer.Sound("data/sounds/beww.ogg"),
            "xpl1": pygame.mixer.Sound("data/sounds/xpl1.ogg"),
            "xpl2": pygame.mixer.Sound("data/sounds/xpl2.ogg"),
            "xpl3": pygame.mixer.Sound("data/sounds/xpl3.ogg"),
            "xpl4": pygame.mixer.Sound("data/sounds/xpl3.ogg"),
            "glass1": pygame.mixer.Sound("data/sounds/glass1.ogg"),
            "glass2": pygame.mixer.Sound("data/sounds/glass2.ogg"),
            "glass3": pygame.mixer.Sound("data/sounds/glass3.ogg"),
        }

        self.bg0 = pygame.Surface((320/2,200))
        self.bg0.set_colorkey((0,0,0))
        self.bg1 = pygame.Surface((320/2,200))
        self.current_image = None
        self.zwischen = pygame.Surface((320, 200))
        m = self.scale_mouse(pygame.mouse.get_pos())
        self.timer = 0
        self.boss = None
        self.xs = 1
        self.stripes = False
        self.overwrite_colors = [None, None]
        self.blur = 0
        self.gamespeed = 0
        self.cracks = []
        self.gameover = False
        self.go = 0
        seed(self.level)
        warning = pygame.image.load("data/seisurewarning.png")
        self.screen.blit(warning, (0,0))
        pygame.transform.scale(self.screen, self.window_res, self.window)
        pygame.display.flip()
        while True:
            self.clock.tick(30)
            self.input()
            if self.buttons[1] == False:
                break
        credits = sheet(pygame.image.load("data/credit.png"), (320,200))
        pygame.transform.scale(self.screen, self.window_res, self.window)
        pygame.display.flip()
        self.screen.fill((0,0,0))
        d = 0
        while True:
            if d == 0: d = 1
            else: d = 0
            self.clock.tick(60)
            self.input()
            self.screen.blit(credits[d], (0,0))
            pygame.transform.scale(self.screen, self.window_res, self.window)
            pygame.display.flip()
            if self.buttons[1] == False:
                break
        self.titlesound = pygame.mixer.Sound("data/sounds/titelvox.ogg")
        self.titlesound.play()
        pygame.mixer.music.load("data/music/title.ogg")
        pygame.mixer.music.play(-1)
        self.mb = 0

    def new_game(self, l=0.5):
        if l < 0.5:
            l = 0.5
        self.rows = [
            [[0,128,0], 320, [0,0,0,0]],
            [[0,255,0], 200, [0,0,0,0]],
            [[0,0,255], 160, [0,0,0,0]],
            [[0,0,128], 100, [0,0,0,0]],
            [[0,255,255],70, [0,0,0,0]],
            [[0,128,128],30, [0,0,0,0]],
        ]
        rc = (randint(0,255),randint(0,255),randint(0,255))
        self.zwischen.fill(rc)
        self.bg0.fill((0,0,0))
        self.bg1.fill(rc)
        self.sounds["gamestart"].play()
        self.layers = []
        self.layer_bulletsP = []
        self.xs = 0
        self.ys = 0
        self.wanringz = False
        pygame.mixer.music.load("data/music/1.ogg")
        pygame.mixer.music.play(-1)
        try:
            self.titlesound.stop()
        except:
            pass
        self.mouthbeem = False
        self.titlesound = None
        self.wanringz = False
        for i in range(10):
            self.layers.append([])
            self.layer_bulletsP.append([])
        m = self.scale_mouse(pygame.mouse.get_pos())
        self.player = Player(self, [m[0],m[1],32,32])
        self.layers[5].append(self.player)
        self.level = l
        self.gamespeed = 0
        seed(self.level)
        self.stripes = False
        self.current_image = None
        self.overwrite_colors = [None, None]
        self.timer = 0
        self.started = True
        self.gameover = False
        self.blur = 50

    def next_level(self):
        self.rows = [
            [[0,128,0], 320, [0,0,0,0]],
            [[0,255,0], 200, [0,0,0,0]],
            [[0,0,255], 160, [0,0,0,0]],
            [[0,0,128], 100, [0,0,0,0]],
            [[0,255,255],70, [0,0,0,0]],
            [[0,128,128],30, [0,0,0,0]],
        ]
        rc = (randint(0,255),randint(0,255),randint(0,255))
        self.zwischen.fill(rc)
        self.bg0.fill((0,0,0))
        self.bg1.fill(rc)
        self.gamespeed = 0
        self.timer = 0
        self.level += 0.5
        self.wanringz = False
        self.blur = 50
        self.stripes = False
        self.current_image = None
        seed(self.level)
        pygame.mixer.music.load("data/music/"+str(int(self.level*2))+".ogg")
        pygame.mixer.music.play(-1)
        i = randint(0,2)
        if i == 0:
            self.mouthbeem = True
        else:
            self.mouthbeem = False
        sound = pygame.mixer.Sound("data/sounds/leveltrans"+str(i)+".ogg")
        sound.play()


    def hit(self, rect):
        self.blur += 5
        self.sounds["glass"+str(randint(1,3))].play()
        self.cracks.append([randint(0,3), rect, 255])
        self.screen.fill((255,0,0))

    def game_over(self):
        self.gameover = True

    def update(self):
        if len(self.cracks) > 3:
            self.player.dying()
            self.cracks = []
        self.input()
        if self.gameover:
            if self.buttons[1] == False:
                self.gameover = False
                self.level -= 1
                self.new_game(self.level)
        elif self.started:
            self.dt += 0.001
            #BOSS
            self.timer += 0.001
            if self.timer >= 1:
                for i in range(2):
                    self.layers[i] = []
                if self.gamespeed > 198 and self.gamespeed < 200:
                    self.boss = Boss(self)
                    self.layers[2].append(self.boss)
                    self.gamespeed = 201
                    self.blur = 0
                    pygame.mixer.music.load("data/music/boss.ogg")
                    pygame.mixer.music.play(-1)
                elif self.gamespeed <= 201:
                    if self.wanringz == False:
                        self.wanringz = True
                        pygame.mixer.music.stop()
                        self.sounds["alarm"].play()
                    self.blur = 80
                    self.screen.blit(self.images["bosswarning"][randint(0,1)], (160-58,100-27))
                    self.gamespeed += 1
            else:
                #SPEED UP
                if self.gamespeed < 64:
                    self.gamespeed += 0.01
                if randint(0,20 + (20-int(self.level))) == 0:
                    self.layers[0] = [DualSheetEnemy(self)] + self.layers[0]
                #IF THERE'S TIME LEFT!
                #if randint(0,500) == 0:
                #    self.layers[0] = [Item(self)] + self.layers[0]

                if self.current_image == None:
                    if int((self.level*2)%2) == 0:
                        img = int(self.level*2)-2
                        self.current_image = self.images["backgrounds"][int(self.level*2)-2]
                        self.image_y = 0
                    else:
                        self.current_image = None
                elif self.gamespeed > 5 and not self.current_image == self.images["backgrounds"][int(self.level*2)-1]:
                    self.current_image = self.images["backgrounds"][int(self.level*2)-1]
                    self.image_y = 0
            #    self.layers[1].append(Enemy(self, [randint(32,320-32),-64,32,32]))
            #UPDATE

            for l, layer in enumerate(self.layers):
                for entity in self.layer_bulletsP[l]:
                    entity.update()
                    entity.finalize()
                for entity in self.layers[l]:
                    entity.update()
                    entity.finalize()

        else:
            self.dt += 1
            if self.buttons[1]:
                self.new_game()
        #DRAW
        if randint(0,500) == 0:
            self.stripes = False

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
        self.zwischen.set_alpha(100-self.blur)
        #self.zwischen.fill((0,0,0), (0,0,320,64))
        #self.player.yaw += 0.1
        try:
            y = self.player.yaw
        except:
            y = 100
        self.screen.blit(pygame.transform.scale(self.zwischen, (320,int(200-y))), (0,y))
        f = pygame.transform.flip(self.zwischen, False, True)
        self.screen.blit(pygame.transform.scale(f, (320,int(y)+1)), (0, 0))
        for l, layer in enumerate(self.layers):
            for entity in self.layer_bulletsP[l]:
                self.screen.blit(entity.surface, entity.center)
            for entity in self.layers[l]:
                self.screen.blit(entity.surface, entity.center)
        for c, crack in enumerate(self.cracks):
            self.images["cracks"][crack[0]].set_alpha(crack[2])
            self.screen.blit(self.images["cracks"][crack[0]], (crack[1][0]-64, crack[1][1]-64))
            self.cracks[c][2] -= 1
            if self.cracks[c][2] == 0:
                self.cracks.remove(crack)
        if self.started == False:
            self.screen.blit(self.images["title"][self.dt%2], (0,0))
        if self.gameover == True:
            if self.go == 0: self.go = 1
            else: self.go = 0
            self.gameover = True
            self.screen.blit(self.images["gameover"][self.go], (0,0))
        if self.mouthbeem and self.gamespeed < 1:
            if self.mb == 0: self.mb = 1
            else: self.mb = 0
            self.screen.blit(self.images["mouthbeem"][self.mb], (0,0))

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
            if button == False: self.buttons[b] = None
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                for i in range(5):
                    if e.button == i: self.buttons[i] = True
            elif e.type == pygame.MOUSEBUTTONUP:
                for i in range(5):
                    if e.button == i: self.buttons[i] = False
            elif e.type == pygame.VIDEORESIZE:
                self.window_res = e.w, e.h
                self.window = pygame.display.set_mode(self.window_res, pygame.RESIZABLE)
game = Game()
print("BYE!")
