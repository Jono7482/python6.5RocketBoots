import sys
import pygame
from random import randint as rand
from pygame.image import load as load
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

clock = pygame.time.Clock()
fps = 120
resolution = 800, 600
debug = True

screen = pygame.display.set_mode(resolution)

font18 = pygame.font.Font('freesansbold.ttf', 18)
font60 = pygame.font.Font('freesansbold.ttf', 60)

background = load("skynb.jpg").convert()
bgpause = load("bgpaused.png").convert_alpha()
clouds_array = [load("cloud1.png").convert_alpha(),
                load("cloud2.png").convert_alpha(),
                load("cloud3.png").convert_alpha(),
                load("cloud4.png").convert_alpha()]
imgobstacle1 = load("obstacle2.png").convert()
littledude1 = load("littledude1.png").convert_alpha()
flamearray1 = [load("flame1.png").convert_alpha(),
               load("flame2.png").convert_alpha()]
flamearray2 = [load("flame3.png").convert_alpha(),
               load("flame4.png").convert_alpha()]

music = pygame.mixer.music
music.load("Indiekid.mp3")
boots1wav = pygame.mixer.Sound("boots1.wav")
boots1wav.set_volume(0.1)
boots1 = pygame.mixer.find_channel()


def main():
    music.play(-1, 0.0)
    gravity = .25
    speed = 0
    boost = bool
    thislevel = LevelObj()

    duderect = pygame.Rect(75, 300, 30, 30)
    screen.blit(background, (0, 0))
    cloud1 = Clouds(clouds_array, 2, 1)
    cloud2 = Clouds(clouds_array, 2, 3)
    cloud3 = Clouds(clouds_array, 2, 2)
    cloud1.create_active()
    cloud2.create_inactive()
    cloud3.create_inactive()
    screen.blit(littledude1, duderect)
    flames1 = ImageCycle(flamearray1)
    flames2 = ImageCycle(flamearray2)
    flamerect = pygame.Rect(duderect.left, duderect.bottom, 30, 60)
    screen.blit(flames1.get_next(), flamerect)
    score = 0.0
    pygame.event.post(game_paused("Space To Start"))  # pause game and then return the event
    boots1.play(boots1wav, loops=-1, maxtime=0, fade_ms=0)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_p:
                    boost = False
                    pygame.event.post(game_paused("PAUSE"))
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_SPACE:
                    boost = True
                    speed -= 1
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    boost = False

        if boost:
            boots1wav.set_volume(0.2)
            if speed > -10:
                speed -= .65
        else:
            boots1wav.set_volume(0.05)
            speed += gravity

        if -100 > duderect.bottom or duderect.bottom > (resolution[1] + 100):
            death()
        duderect = duderect.move(0, speed)
        screen.blit(background, (0, 0))
        cloud1.step_move()
        cloud2.step_move()
        cloud3.step_move()
        thislevel.game_tick()
        score += .5
        scorestr = str(round(score, 0))
        scoretext = "Score: " + scorestr[:-2]
        make_text_objs((660, 10), scoretext, font18, (0, 0, 0))
        flamerect = pygame.Rect(duderect.left, duderect.bottom, 30, 60)
        if boost:
            screen.blit(flames1.get_next(), flamerect)
        else:
            screen.blit(flames2.get_next(), flamerect)
        screen.blit(littledude1, duderect)
        collison(duderect, thislevel.obstaclelist)
        if debug:
            fpsvar = "FPS: " + str(round(clock.get_fps(), 0))
            make_text_objs((10, 10), fpsvar[:-2], font18, (0, 0, 0), "xy")
        pygame.display.flip()
        clock.tick(fps)


def collison(rect1, rectarray):
    rectlist = []
    for each in rectarray:
        rectlist.append(each.Rect)
        rectlist.append(each.Rect2)
    if rect1.collidelist(rectlist) == -1:
        return
    else:
        return death()


def game_paused(text):
    if text == "PAUSE":
        music.pause()
        bgpauserect = bgpause.get_rect()
        screen.blit(bgpause, bgpauserect)
    boots1.pause()
    make_text_objs((resolution[0] / 2, resolution[1] / 3), text, font60, (0, 0, 0), "center")
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                pygame.mixer.music.unpause()
                boots1.unpause()
                return event
        clock.tick(fps)


def death():
    main()


def terminate():
    music.stop()
    boots1.stop()
    pygame.quit()
    sys.exit()


class ImageCycle(object):
    def __init__(self, imagearray):
        self.array = imagearray
        self.index = 0
        self.image = None

    def get_next(self):
        if self.index <= (len(self.array) - 1) * 2:
            self.image = self.array[int(self.index / 2)]
            self.index += 1
            return self.image
        else:
            self.image = self.array[0]
            self.index = 0
            return self.image


class LevelObj(object):
    def __init__(self):
        self.difficulty = 0
        self.gap = 400
        self.image = imgobstacle1
        self.tick = 500
        self.obstaclelist = []
        self.thisgap = 0

    def game_tick(self):
        self.tick += 1
        if self.tick >= 300 - self.difficulty:
            self.tick = 0
            self.difficulty += 2
            self.thisgap = self.gap - (self.difficulty + rand(0, 20))
            self.obstaclelist.append(Obstacle(self.image, 0, 2))
            self.obstaclelist[-1].new_set(self.thisgap)
        if len(self.obstaclelist) > 10:
            del self.obstaclelist[0]
        for each in self.obstaclelist:
            each.step_move()
        if debug:
            tick = str(self.tick)
            difficulty = str(self.difficulty)
            gap = str(self.thisgap)
            obstacles = str(len(self.obstaclelist))
            statstext = ("Tick:%s    Difficulty:%s    Gap:%s    Obstacles:%s" % (tick, difficulty, gap, obstacles))
            make_text_objs((10, 570), statstext, font18, (100, 100, 100), "xy")


class MovingObj(object):
    """
    moving_ob takes a already loaded image or list of loaded images
    tick_skip if given will skip a number of frames
    speed is how many pixels a object will move per frame
    """
    def __init__(self, image, tick_skip=0, speed=1):
        self.gaptop = None
        self.Rect2 = None
        self.speed = speed
        self.tick_skip = tick_skip
        if isinstance(image, list):
            self.image_array = image
            self.pick_image()
        else:
            self.image = image
            self.image_array = None
        self.Rect = self.image.get_rect()
        self.ticks = 0

    def pick_image(self):
        rand_index = rand(0, len(self.image_array)-1)
        self.image = self.image_array[rand_index]

    def tick(self):
        if (self.ticks < self.tick_skip) and (self.tick_skip != 0):
            self.ticks += 1
            return False
        else:
            self.ticks = 0
            return True

    def pos_rect(self, x, y):
        self.Rect.topleft = (x, y)

    def post(self):
        return screen.blit(self.image, self.Rect)


class Clouds(MovingObj):

    def create_active(self):
        start_x = rand(100, 300)
        start_y = rand(-100, 50)
        self.pos_rect(start_x, start_y)
        self.post()

    def create_inactive(self):
        start_x = resolution[0] + rand(50, 300)
        start_y = rand(-100, 50)
        self.pos_rect(start_x, start_y)
        self.post()

    def step_move(self):
        ready = self.tick()
        if self.Rect.right >= 0:
            if ready:
                self.Rect = self.Rect.move(-self.speed, 0)
            self.post()
        else:
            self.pick_image()
            self.Rect = self.image.get_rect()
            self.create_inactive()


class Obstacle(MovingObj):
    def new_set(self, gap):
        self.gaptop = rand(0, resolution[1] - gap)
        self.Rect2 = self.image.get_rect()
        self.Rect.bottom = self.gaptop
        self.Rect.left = resolution[0]
        self.Rect2.top = self.gaptop + gap
        self.Rect2.left = resolution[0]

    def step_move(self):
        ready = self.tick()
        if self.Rect.right >= 0:
            if ready:
                self.Rect.right -= self.speed
                self.Rect2.right -= self.speed
            return screen.blit(self.image, self.Rect), screen.blit(self.image, self.Rect2)


def make_text_objs(location, text, font, rgb, pos="xy"):
    x, y = location
    textsurf = font.render(text, True, rgb)
    textrect = pygame.Rect(textsurf.get_rect())
    if pos == "xy":
        textrect = textrect.move(x, y)
    elif pos == "center":
        textrect.center = location
    return screen.blit(textsurf, textrect)


if __name__ == '__main__':
    main()
