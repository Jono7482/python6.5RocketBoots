import sys
import pygame
import pickle
from random import randint as rand
from pygame.image import load as load
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
clock = pygame.time.Clock()
fps = 120
resolution = 800, 600
debug = True
dude = None
display = None
gameState = "Loading"
this_level = None
audio = None
score = 0.0
screen = pygame.display.set_mode(resolution)


def main():
    global dude, display, this_level, audio, score
    display = Display()
    dude = DudeObj()
    this_level = LevelObj()
    audio = AudioHandler()
    audio.play()
    audio.boots_play()
    display.update()
    pygame.event.post(paused_loop("Space To Start"))  # pause game and then return the event
    score = 0.0
    game_loop()


def game_loop():
    global score
    speed = 0
    gravity = .25
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_p:
                    dude.flame_boost(boost=False)
                    pygame.event.post(paused_loop("PAUSE"))
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_SPACE:
                    dude.flame_boost(boost=True)
                    speed -= 1
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    dude.flame_boost(boost=False)

        if dude.boosting:
            audio.boots_volume(0.2)
            if speed > -10:
                speed -= .65
        else:
            audio.boots_volume()
            speed += gravity

        if -100 > dude.dudeRect.bottom or dude.dudeRect.bottom > (resolution[1] + 100):
            death()

        collison(dude.dudeRect, this_level.obstaclelist)
        dude.move(speed)
        score += .5
        display.update()
        this_level.game_tick()
        clock.tick(fps)


def paused_loop(text):
    if text == "PAUSE":
        audio.music.pause()
        display.pause()
    audio.boots1.pause()
    make_text_objs((resolution[0] / 2, resolution[1] * .70), text, 50, (0, 0, 0), "center")
    scoreboardObj.print_board()
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                pygame.mixer.music.unpause()
                audio.boots1.unpause()
                return event
        clock.tick(fps)


class Display(object):
    def __init__(self):
        self.background = load("skynb.jpg").convert()
        self.bgpause = load("bgpaused.png").convert_alpha()
        self.bgpauserect = self.bgpause.get_rect()
        self.clouds = create_clouds()
        self.clouds[0].step_move()

    def update(self):
        global dude, score
        screen.blit(self.background, (0, 0))
        for each in self.clouds:
            each.step_move()
        for each in this_level.obstaclelist:
            screen.blit(this_level.image, each.Rect), screen.blit(this_level.image, each.Rect2)
        scorestr = str(round(score, 0))
        scoretext = "Score: " + scorestr[:-2]
        make_text_objs((660, 10), scoretext, 18, (0, 0, 0))
        if debug:
            fpsvar = "FPS: " + str(round(clock.get_fps(), 0))
            make_text_objs((10, 10), fpsvar[:-2], 18, (0, 0, 0), "xy")
            this_level.debug()
        dude.display()
        pygame.display.flip()

    def pause(self):
        screen.blit(self.bgpause, self.bgpauserect)


class DudeObj(object):
    def __init__(self):
        self.dudeimg = load("littledude1.png").convert_alpha()
        self.dudeRect = pygame.Rect(75, 300, 30, 30)
        self.flamearray1 = [load("flame1.png").convert_alpha(),
                            load("flame2.png").convert_alpha()]
        self.flamearray2 = [load("flame3.png").convert_alpha(),
                            load("flame4.png").convert_alpha()]
        self.flame1 = ImageCycle(self.flamearray1)
        self.flame2 = ImageCycle(self.flamearray2)
        self.flame = self.flame1.get_next()
        self.flameRect = pygame.Rect(self.dudeRect.left, self.dudeRect.bottom, 30, 60)
        self.boosting = False

    def display(self):
        screen.blit(self.dudeimg, self.dudeRect)
        screen.blit(self.flame, self.flameRect)

    def flame_boost(self, boost):
        self.boosting = boost
        if self.boosting:
            self.flame = self.flame1.get_next()
        else:
            self.flame = self.flame2.get_next()

    def move(self, y, x=0):
        self.dudeRect = self.dudeRect.move(x, y)
        self.flameRect = pygame.Rect(self.dudeRect.left, self.dudeRect.bottom, 30, 60)


def collison(rect1, rectarray):
    rectlist = []
    for each in rectarray:
        rectlist.append(each.Rect)
        rectlist.append(each.Rect2)
    if rect1.collidelist(rectlist) == -1:
        return
    else:
        return death()


def death():
    global score
    scoreboardObj.add_score(score)
    main()


def terminate():
    scoreboardObj.dump_scoreboard()
    pygame.mixer.stop()
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
        self.gaptop = 0
        self.thisgap = 0
        self.image = load("obstacle2.png").convert()
        self.tick = 500
        self.obstaclelist = []

    def game_tick(self):
        self.tick += 1
        if self.tick >= 300 - self.difficulty:
            self.tick = 0
            self.difficulty += 2
            self.thisgap = self.gap - (self.difficulty + (rand(0, 5) * 4))
            self.gaptop = rand(0, round((resolution[1] - self.thisgap) / 10, 0)) * 10
            self.obstaclelist.append(Obstacle(self.image, 0, 2))
            self.obstaclelist[-1].new_set(self.thisgap, self.gaptop)
        if len(self.obstaclelist) > 10:
            del self.obstaclelist[0]
        for each in self.obstaclelist:
            each.step_move()

    def debug(self):
        tick = str(self.tick)
        difficulty = str(self.difficulty)
        gap = str(self.thisgap)
        obstacles = str(len(self.obstaclelist))
        statstext = ("Tick:%s    Difficulty:%s    Gap:%s    Obstacles:%s" % (tick, difficulty, gap, obstacles))
        make_text_objs((10, 570), statstext, 18, (100, 100, 100), "xy")


class MovingObj(object):
    """
    moving_obj takes a already loaded image or list of loaded images
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


def create_clouds():
    clouds_array = [load("cloud1.png").convert_alpha(),
                    load("cloud2.png").convert_alpha(),
                    load("cloud3.png").convert_alpha(),
                    load("cloud4.png").convert_alpha()]
    cloud1 = Clouds(clouds_array, 2, 1)
    cloud2 = Clouds(clouds_array, 2, 3)
    cloud3 = Clouds(clouds_array, 2, 2)
    cloud1.create_active()
    cloud2.create_inactive()
    cloud3.create_inactive()
    clouds = cloud1, cloud2, cloud3
    return clouds


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
    def new_set(self, gap, gaptop):
        self.gaptop = gaptop
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


def make_text_objs(location, text, font_size, rgb, pos="xy"):
    font = pygame.font.Font('freesansbold.ttf', font_size)
    x, y = location
    textsurf = font.render(text, True, rgb)
    textrect = pygame.Rect(textsurf.get_rect())
    if pos == "xy":
        textrect = textrect.move(x, y)
    elif pos == "center":
        textrect.center = location
    return screen.blit(textsurf, textrect)


class AudioHandler(object):
    def __init__(self):
        pygame.mixer.stop()
        self.music = pygame.mixer.music
        self.music.load("Indiekid.mp3")
        self.boots1wav = pygame.mixer.Sound("boots1.wav")
        self.boots1wav.set_volume(0.05)
        self.boots1 = pygame.mixer.find_channel()

    def play(self):
        self.music.play(-1, 0.0)

    def boots_play(self):
        self.boots1.play(self.boots1wav, loops=-1, maxtime=0, fade_ms=0)

    def boots_volume(self, volume=0.05):
        self.boots1wav.set_volume(volume)


class ScoreBoard(object):
    def __init__(self):
        try:
            self.load_scoreboard()
        except OSError:
            self.scoreboard = []
            self.dump_scoreboard()

    def load_scoreboard(self):
        self.scoreboard = pickle.load(open("scoreboard.p", "rb"))

    def dump_scoreboard(self):
        data = self.scoreboard
        pickle.dump(data, open("scoreboard.p", "wb"))

    def add_score(self, scorev):
        scorev = int(round(scorev, 0))
        self.scoreboard.append(scorev)
        self.scoreboard.sort(reverse=True)
        if len(self.scoreboard) > 5:
            self.scoreboard = self.scoreboard[0:5]

    def print_board(self):
        place = 1
        name = "Adam"
        y = 150
        make_text_objs((resolution[0] / 2, y - 50), "High Scores:", 40, (0, 0, 0), "center")
        for each in self.scoreboard:
            text = "%s. %s - %s" % (place, name, each)
            make_text_objs((resolution[0] / 2, y), text, 30, (0, 0, 0), "center")
            place += 1
            y += 40


scoreboardObj = ScoreBoard()


if __name__ == '__main__':
    main()
