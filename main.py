from cvzone.HandTrackingModule import HandDetector
import cv2
import pygame
import random
import numpy as np
import mediapipe as mp
import time

# These two line are frome cvzone documentation
# https://github.com/cvzone/cvzone?tab=readme-ov-file#hand-tracking-module
cap = cv2.VideoCapture(0)
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
## -----------------------------------------------------------------------


lives = 3
score = 0
fruits = ['dragonfruit', 'pineapple', 'plum', 'watermelon', 'pomegranate', 'strawberry', 'bomb']
round_duration = 60
time_ = 0
fruit_rate = 0.2
bomb_rate = 0.1
bomb_timer = 0

BOMB_DISPLAY_DURATION = 2500

WIDTH = 1200
HEIGHT = 800
FPS = 60

pygame.init()
pygame.display.set_caption('Fruit-Ninja With a Twist!')
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

background = pygame.image.load('data/start_screen.png')
kaboom = pygame.image.load('images/kaboom.png')

def generate_fruits(fruit):
    path = "images/" + fruit + ".png"
    
    data[fruit] = {
        'img': pygame.image.load(path),
        # claude generated these four lines
        'x': random.randint(100, WIDTH-100),
        'y': HEIGHT,
        'sx': random.randint(-80, 80),
        'sy': random.randint(-785, -450),
        # ---------------------------------
        'throw': False,
        't': 0,
        'hit': False
    }

    if random.random() >= 0.75:
        data[fruit]['throw'] = True
    else:
        data[fruit]['throw'] = False
        
data = {}

for fruit in fruits:
    generate_fruits(fruit)
    
def draw_text(display, text, size, x, y):
    pass

def draw_lives(display, x, y, lives, image):
    for i in range(lives):
        img = pygame.image.load(image)
        img_rect = img.get_rect()
        img_rect.x = int(x + 35 * i)
        img_rect.y = y
        display.blit(img, img_rect)

def start_screen():
    gameDisplay.blit(background, (0, 0))
    pygame.display.update()

    screen = False
    while not screen:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return pygame.image.load('data/background.png')
                
def gameover():
    pass

def timer():
    pass
    
def intersect(fruitpos, fingerpos):
    fruit_x, fruit_y = fruitpos
    finger_x, finger_y = fingerpos

    if (finger_x > fruit_x and finger_x < fruit_x+100) and (finger_y > fruit_y and finger_y < fruit_y+100):
        return True
    return False

first_round = True
game_over = True
running = True
game_duration = 60
current_time = 0

while running:

    dt = clock.tick(FPS) / 1200
    
    if game_over:

        if first_round:
            background = start_screen()
            gameover()
            first_round = False

        game_over = False
        player_lives = 3
        score = 0
        fruit_rate = 0.2
        bomb_rate = 0.1
        # draw_lives(gameDisplay, 690, 5, player_lives, 'images/lives.png')
        start_time = pygame.time.get_ticks()
        
    current_time = (pygame.time.get_ticks() - start_time) // 1000
        

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    _, img = cap.read()

    if not _ : break

    hands, img = detector.findHands(img, draw=False, flipType=True)

    cam_h, cam_w = img.shape[:2]
    img = cv2.resize(img, (WIDTH, HEIGHT))
    img = cv2.flip(img, 1)
    
    # gemini generated these three lines
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.swapaxes(img, 0, 1)
    img = pygame.surfarray.make_surface(img)
    # ----------------------------------

    gameDisplay.blit(background, (0, 0))

    
    for key, value in data.items():
        if value['throw']:
            # claude generated these three lines
            value['x'] += value['sx'] * dt
            value['y'] += value['sy'] * dt
            value['sy'] += 400 * dt
            # ----------------------------------

            if value['y'] <= 800:
                gameDisplay.blit(value['img'], (value['x'], value['y']))
            else:
                generate_fruits(key)
                
        else:
            
            generate_fruits(key)

        mouse_pos = pygame.mouse.get_pos()            

        if hands:
            hand1 = hands[0]
            lmList1 = hand1["lmList"]
            # claude helped with the mirroring math of these two variables
            x1 = int((1 - lmList1[8][0] / cam_w) * WIDTH)
            y1 = int(lmList1[8][1] / cam_h * HEIGHT)
            index1 = (x1, y1)

            pygame.draw.circle(gameDisplay, (255, 255, 255), index1, 5)
            
            if not value['hit'] and intersect((value['x'], value['y']), (x1, y1)):
                
                if key == 'bomb':
                    sliced_fruit = "images/" + "sliced_" + key + ".png"

                else:
                    sliced_fruit = "images/" + "sliced_" + key + ".png"
                    
                value['img'] = pygame.image.load(sliced_fruit)

            if len(hands) == 2:
                hand2 = hands[1]
                lmList2 = hand2["lmList"]
                x2 = int((1 - lmList2[8][0] / cam_w) * WIDTH)
                y2 = int(lmList2[8][1] / cam_h * HEIGHT)
                index2 = (x2, y2)

                pygame.draw.circle(gameDisplay, (255, 255, 255), index2, 5)

                if not value['hit'] and intersect((value['x'], value['y']), (x2, y2)):
                    
                    if key == 'bomb':
                        sliced_fruit = "images/" + "sliced_" + key + ".png"
                    else:
                        sliced_fruit = "images/" + "sliced_" + key + ".png"
                        
                    value['img'] = pygame.image.load(sliced_fruit)
                    
        else:
            if not value['hit'] and intersect((value['x'], value['y']), (mouse_pos[0], mouse_pos[1])):
                
                if key == 'bomb':
                    # sliced_fruit = "images/" + "sliced_" + key + ".png"
                    bomb_timer = pygame.time.get_ticks()
                    value['hit'] = True
                else:
                    sliced_fruit = "images/" + "sliced_" + key + ".png"

                    value['img'] = pygame.image.load(sliced_fruit)

    BOMB_HOLD_DURATION = 900
    BOMB_FADE_DURATION = 800

    if bomb_timer > 0:
        elapsed = pygame.time.get_ticks() - bomb_timer

        if elapsed < BOMB_HOLD_DURATION:
            alpha = 255
        else:
            fade_elapsed = elapsed - BOMB_HOLD_DURATION
            alpha = max(0, 255-int((elapsed / BOMB_DISPLAY_DURATION) * 155))

        kaboom.set_alpha(alpha)
        gameDisplay.blit(kaboom, (0, 0))

        if elapsed > BOMB_DISPLAY_DURATION:
            bomb_timer = 0


    cv2.waitKey(1)
    pygame.display.update()
    
# cap.release()
# cv2.destroyAllWindows()
# pygame.quit()