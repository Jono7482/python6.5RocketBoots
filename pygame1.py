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
black = (0, 0, 0)
yellow = (250, 250, 0)

def death():
    global score
    audio.boots1.pause()
    clock.tick(5)
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
    display.update()
    pygame.event.post(paused_loop("Space To Start"))  # pause game and then return the event
    score = 0.0
    game_loop()


def game_loop():
    global score, gameState, audio
    gameState = "playing"
    audio.boots_play()
    speed = 0
    gravity = .30
    power = .35
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_p:
                    dude.flame_boost(boost=False)
                    pygame.event.post(paused_loop("PAUSE"))
                    audio.music.unpause()
                    audio.boots1.unpause()
                    clock.tick(20)
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
    global gameState
    oldstate = gameState
    if text == "PAUSE":
        gameState = "paused"
        audio.music.pause()
        display.pause()
    audio.boots1.pause()
    make_text_objs((resolution[0] / 2 -2, resolution[1] * .70 - 2), text, 50, black, "center")
    make_text_objs((resolution[0] / 2, resolution[1] * .70), text, 50, yellow, "center")
    if gameState != "Loading":
        scoreboardObj.print_board()
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    gameState = oldstate
                    return event
        clock.tick(fps)
        pass


class Display(object):
    global gameState
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
        if gameState != "scoreboard":
            self.hills.step_move()
        else:
            self.hills.post()
        for each in self.clouds:
            if gameState != "scoreboard":
                each.step_move()
            else:
                each.post()
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
        if gameState != "scoreboard":
            pygame.display.flip()

    def pause(self):
        screen.blit(self.bgpause, self.bgpauserect)

    def display_box(self, message, y):
        self.update()
        scoreboardObj.print_board()
        if len(message) == 0:
            message = "[NAME] "
        make_text_objs((resolution[0] * 0.3 + 2 + 20 - 3, y + 2), ("  " + message), 30, black, "xy")
        make_text_objs((resolution[0] * 0.3 + 20 - 3, y), ("  " + message), 30, yellow, "xy")
        make_text_objs((resolution[0] / 2 - 2, resolution[1] * .68 + 2), ("New High Score!!!"), 45, black, "center")
        make_text_objs((resolution[0] / 2, resolution[1] * .68), ("New High Score!!!"), 45, yellow, "center")
        make_text_objs((resolution[0] / 2 - 2, resolution[1] * .75 + 2), ("Type your name then press [Enter]"), 30, black, "center")
        make_text_objs((resolution[0] / 2, resolution[1] * .75), ("Type your name then press [Enter]"), 30, yellow, "center")
        pygame.display.flip()


class DudeObj(object):
    def __init__(self):
        self.dudeimg = load("littledude1.png").convert_alpha()
        self.dudeRect = pygame.Rect(75, 300, 27, 30)
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
    global  gameState
    rectlist = []
    for each in rectarray:
        rectlist.append(each.Rect)
        rectlist.append(each.Rect2)
    if rect1.collidelist(rectlist) == -1:
        return
    else:
        gameState = "dead"
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
        self.play()

    def play(self):
        self.music.play(-1, 0.0)

    def boots_play(self):
        self.boots1.play(self.boots1wav, loops=-1, maxtime=0, fade_ms=0)
        self.boots1.unpause()

    def boots_volume(self, volume=0.05):
        self.boots1wav.set_volume(volume)


class ScoreBoard(object):
    def __init__(self):
        try:
            self.load_scoreboard()
        except OSError:
            self.scoreboard = [["", 0], ["", 0], ["", 0], ["", 0], ["", 0]]
            self.dump_scoreboard()

    def load_scoreboard(self):
        self.scoreboard = pickle.load(open("scoreboard.p", "rb"))

    def dump_scoreboard(self):
        data = self.scoreboard
        try:
            pickle.dump(data, open("scoreboard.p", "wb"))
        except OSError:
            print("Can't Dump Scoreboard")

    def add_score(self, scorev=-1):
        global gameState
        gameState = "scoreboard"
        scorev = int(round(scorev, 0))

        if self.scoreboard is None:
            self.scoreboard = [["", 0], ["", 0], ["", 0], ["", 0], ["", 0]]
        else:
            index = 1
            for each in self.scoreboard:
                if index > 5:
                    break
                elif each[1] < scorev:
                    name_score = ["", scorev]
                    self.scoreboard.append(name_score)
                    self.scoreboard.sort(reverse=True, key=itemgetter(1))
                    if len(self.scoreboard) > 5:
                        self.scoreboard = self.scoreboard[0:5]
                    self.print_board()
                    y = 150 + (index - 1) * 40
                    self.scoreboard[index - 1][0] = ask_name(y)
                    break
                else:
                    index += 1

    def print_board(self):
        global gameState
        gameState = "scoreboard"
        if self.scoreboard is None:
            return
        place = 1
        y = 150
        make_text_objs((resolution[0] / 2 + 2, y - 48), "High Scores:", 40, black, "center")
        make_text_objs((resolution[0] / 2, y - 50), "High Scores:", 40, yellow, "center")
        for each in self.scoreboard:
            if each[0] == None:
                each[0] = "-  -  -  -"
            name_text = "%s. %s" % (place, each[0][0:10])
            score_text = "-   %s" % (each[1])
            make_text_objs((resolution[0] * 0.3 + 2, y + 2), name_text, 30, black, "xy")
            make_text_objs((resolution[0] * 0.3, y), name_text, 30, yellow, "xy")
            make_text_objs((resolution[0] * 0.54 + 2, y + 2), score_text, 40, black, "xy")
            make_text_objs((resolution[0] * 0.54, y), score_text, 40, yellow, "xy")
            place += 1
            y += 40


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


def ask_name(y):
    # ask(question) -> answer
    global screen, gameState
    gameState = "scoreboard"
    pygame.font.init()
    current_string = []
    display.display_box("".join(current_string), y)
    while 1:
        in_key = get_key()
        if in_key == K_BACKSPACE:
            current_string = current_string[0:-1]
        elif in_key == K_RETURN:
            break
        elif in_key <= 127:
            current_string.append(chr(in_key))
            current_string = [c.upper() for c in current_string]
        display.display_box("".join(current_string), y)
        clock.tick(fps)
    name = "".join(current_string)
    if name == "":
        name = None
    return name

scoreboardObj = ScoreBoard()


if __name__ == '__main__':
    main()
