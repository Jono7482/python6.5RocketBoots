import sys
import pygame
import pickle
import string
from operator import itemgetter
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


def death():
    global score
    scoreboardObj.add_score(score)
    main()


def terminate():
    scoreboardObj.dump_scoreboard()
    pygame.mixer.stop()
    pygame.quit()
    sys.exit()


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
    gravity = .35
    power = .35
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
                    speed -= power
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    dude.flame_boost(boost=False)

        if dude.boosting:
            audio.boots_volume(0.2)
            if speed > -9:
                speed -= power
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
        pass


class Display(object):
    def __init__(self):
        self.background = load("skynb.jpg").convert()
        self.bgpause = load("bgpaused.png").convert_alpha()
        self.bgpauserect = self.bgpause.get_rect()
        self.clouds = create_clouds()
        self.clouds[0].step_move()
        self.hills = create_hills()

    def update(self):
        global dude, score
        screen.blit(self.background, (0, 0))
        self.hills.step_move()
        for each in self.clouds:
            each.step_move()
        for each in this_level.obstaclelist:
            screen.blit(this_level.image, each.Rect), screen.blit(this_level.image, each.Rect2)
        scorestr = str(round(score, 0))
        scoretext = "Score: " + scorestr[:-2]
        make_text_objs((607, 17), scoretext, 30, (0, 0, 0))
        make_text_objs((605, 15), scoretext, 30, (250, 250, 0))
        if debug:
            fpsvar = "FPS: " + str(round(clock.get_fps(), 0))
            make_text_objs((10, 10), fpsvar[:-2], 18, (0, 0, 0), "xy")
            this_level.debug()
        dude.display()
        pygame.display.flip()

    def pause(self):
        screen.blit(self.bgpause, self.bgpauserect)

    def display_box(self, message):
        # "Print a message in a box in the middle of the screen"
        fontobject = pygame.font.Font(None, 18)
        pygame.draw.rect(screen, (0, 0, 0),
                         ((screen.get_width() / 2) - 100,
                          (screen.get_height() / 2) - 10, 200, 20), 0)
        pygame.draw.rect(screen, (255, 255, 255),
                         ((screen.get_width() / 2) - 102,
                          (screen.get_height() / 2) - 12,
                          204, 24), 1)
        if len(message) != 0:
            make_text_objs((resolution[0] * 0.3 + 2, 150 + 2), message, 18, (0, 0, 0), "xy")
            make_text_objs((resolution[0] * 0.3, 150), message, 18, (0, 0, 0), "xy")
            screen.blit(fontobject.render(message, 1, (255, 255, 255)),
                        ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
        pygame.display.flip()


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
            if self.difficulty < 200:
                self.difficulty += 3
            self.thisgap = self.gap - (self.difficulty + (rand(0, 5) * 4))
            # self.gaptop = rand(0, round((resolution[1] - self.thisgap) / 10, 0)) * 10
            self.gaptop = rand(1, 9) * ((resolution[1] - self.thisgap) / 10)
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


def create_hills():
    hillsarray = [load("hills1.png").convert_alpha(),
                  load("hills2.png").convert_alpha()]
    hills = Hills(hillsarray, 3, 1)
    hills.create()
    return hills


class Hills(MovingObj):
    def create(self):
        self.Rect = self.image_array[0].get_rect()
        self.Rect2 = self.image_array[1].get_rect()
        self.Rect.bottomleft = (0, resolution[1])
        self.Rect2.bottomleft = self.Rect.bottomright

    def step_move(self):
        ready = self.tick()
        if ready:
            if self.Rect.right > 0:
                self.Rect = self.Rect.move(-self.speed, 0)
            else:
                self.Rect.left = resolution[0]
            if self.Rect2.right > 0:
                self.Rect2 = self.Rect2.move(-self.speed, 0)
            else:
                self.Rect2.left = resolution[0]
        screen.blit(self.image_array[0], self.Rect)
        screen.blit(self.image_array[1], self.Rect2)


def create_clouds():
    clouds_array = [load("cloud1.png").convert_alpha(),
                    load("cloud2.png").convert_alpha(),
                    load("cloud3.png").convert_alpha(),
                    load("cloud4.png").convert_alpha()]
    cloud1 = Clouds(clouds_array, 2, 2)
    cloud2 = Clouds(clouds_array, 2, 3)
    cloud3 = Clouds(clouds_array, 2, 4)
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
            self.scoreboard = None
            self.dump_scoreboard()

    def load_scoreboard(self):
        self.scoreboard = pickle.load(open("scoreboard.p", "rb"))

    def dump_scoreboard(self):
        data = self.scoreboard
        if self.scoreboard is not None:
            pickle.dump(data, open("scoreboard.p", "wb"))

    def add_score(self, scorev, name=""):
        scorev = int(round(scorev, 0))
        index = 1
        for each in self.scoreboard:
            if index > 5:
                break
            if each[1] <= scorev:
                name = ask_name()
                break
            else:
                index += 1
        namescore = [name, scorev]
        if self.scoreboard is None:
            self.scoreboard = [namescore]
        else:
            self.scoreboard.append(namescore)
        self.scoreboard.sort(reverse=True, key=itemgetter(1))
        if len(self.scoreboard) > 5:
            self.scoreboard = self.scoreboard[0:5]

    def print_board(self):
        if self.scoreboard is None:
            return
        place = 1
        y = 150
        make_text_objs((resolution[0] / 2 + 2, y - 48), "High Scores:", 40, (0, 0, 0), "center")
        make_text_objs((resolution[0] / 2, y - 50), "High Scores:", 40, (250, 250, 0), "center")
        for each in self.scoreboard:
            if each[0] == "":
                each[0] = "-  -  -  -"
            name_text = "%s. %s" % (place, each[0][0:10])
            score_text = "-   %s" % (each[1])
            make_text_objs((resolution[0] * 0.3 + 2, y + 2), name_text, 30, (0, 0, 0), "xy")
            make_text_objs((resolution[0] * 0.3, y), name_text, 30, (250, 250, 0), "xy")
            make_text_objs((resolution[0] * 0.54 + 2, y + 2), score_text, 40, (0, 0, 0), "xy")
            make_text_objs((resolution[0] * 0.54, y), score_text, 40, (250, 250, 0), "xy")
            place += 1
            y += 40

"""
http://www.pygame.org/pcr/inputbox/
by Timothy Downs, inputbox written for my map editor
"""


def get_key():
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT:
            terminate()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                terminate()
            else:
                return event.key
        else:
            clock.tick(fps)
            pass


def ask_name():
    # ask(question) -> answer
    global screen
    pygame.font.init()
    current_string = []
    display.display_box("".join(current_string))
    while 1:
        in_key = get_key()
        if in_key == K_BACKSPACE:
            current_string = current_string[0:-1]
        elif in_key == K_RETURN:
            break
        elif in_key <= 127:
            current_string.append(chr(in_key))
            current_string = [c.upper() for c in current_string]
        display.display_box("".join(current_string))
    return "".join(current_string)

scoreboardObj = ScoreBoard()


if __name__ == '__main__':
    main()
