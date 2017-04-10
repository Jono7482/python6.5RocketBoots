import sys
import pygame
import os
from pygame.locals import *
import random

path = 'c:\Jono\MyPython\PyGame'


pygame.init()
clock = pygame.time.Clock()
fps = 60
size = width, height = 800, 600
speed = [0, 7]
black = 0, 0, 0
skyblue = 150, 150, 255
gravity = .6
bounce = .80
momentum = .999
obstacle_speed = -4, 0
gap = 200


screen = pygame.display.set_mode(size)

ball = pygame.image.load(os.path.join(path, 'ball2.png'))
ballrect = ball.get_rect()
ballrect = ballrect.move(50, 0)

obstacle1 = pygame.image.load(os.path.join(path, 'obstacle1.png'))
obrect1 = obstacle1.get_rect()
obrect1.left = width
obrect1.bottom = random.randint(50, height * .60)
obstacle2 = pygame.image.load(os.path.join(path, 'obstacle1.png'))
obrect2 = obstacle1.get_rect()
obrect2.left = obrect1.left
obrect2.top = obrect1.bottom + gap


def terminate():
    sys.exit()
def checkForQuit():
    for event in pygame.event.get(QUIT):  # get all the QUIT events
        terminate()  # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP):  # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate()  # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event)  # put the other KEYUP event objects back
jump = 0
spacedown = bool

while 1:
    checkForQuit()
    for event in pygame.event.get():  # event handling loop
        if event.type == KEYUP:
            if (event.key == K_SPACE):
                spacedown = False

        if event.type == KEYDOWN:
            if (event.key == K_SPACE):
                if speed[1] > 0:
                    speed[1] = -5
                spacedown = True
    if spacedown == True:
        if speed[1] > -15:
            speed[1] -= 2


    speed[0] *= momentum
    speed[1] += gravity

    ballrect = ballrect.move(speed)
    if obrect1.right > 0:
        obrect1 = obrect1.move(obstacle_speed)
        obrect2.left = obrect1.left
    else:
        obrect1.bottom = random.randint(50, height * .80)
        obrect1.left = width
        obrect2.left = obrect1.left
        obrect2 = obrect1.bottom + gap

    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0:
        speed[1] = -speed[1]
    if ballrect.bottom > height and speed[1] > 1:
        speed[1] = -speed[1]
        speed[1] *= bounce
    obslist = obrect1, obrect2
    collideindex = ballrect.collidelist(obslist)
    if collideindex > -1:
        terminate()

    clockFps = (str(clock.get_fps()))[0:2]
    pygame.display.set_caption("FPS: " + clockFps)

    clock.tick(fps)
    screen.fill(skyblue)
    screen.blit(ball, ballrect)
    screen.blit(obstacle1, obrect1)
    screen.blit(obstacle2, obrect2)
    pygame.display.flip()














