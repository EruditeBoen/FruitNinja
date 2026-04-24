# This project initially used pygame for UX. Claude helped me switch to cmu_graphics for the UX
# in a time crunch

from cmu_graphics import *
from cvzone.HandTrackingModule import HandDetector
import cv2
import random
import threading
import time
import pygame


# Sound
pygame.mixer.init()

bomb = pygame.mixer.Sound("sounds/bomb.mp3")
slice = pygame.mixer.Sound("sounds/slice.wav")
fart = pygame.mixer.Sound("sounds/fart.mp3")
ambatukam = pygame.mixer.Sound("sounds/ambatukam.mp3")
bad_piggies = pygame.mixer.Sound("sounds/bad_piggies.mp3")
outro = pygame.mixer.Sound("sounds/outro.mp3")

ambatukam.play(loops=100)

# These two line are frome cvzone documentation
# https://github.com/cvzone/cvzone?tab=readme-ov-file#hand-tracking-module
cap = cv2.VideoCapture(0)
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
## -----------------------------------------------------------------------

camera_data = {
    'hands': [],
    'cam_w': 640,
    'cam_h': 480,
}

# Claude generated this function
def camera_loop():
    while True:
        success, img = cap.read()
        if not success:
            continue
        camera_data['cam_h'], camera_data['cam_w'] = img.shape[:2]
        hands, _ = detector.findHands(img, draw=False, flipType=True)
        camera_data['hands'] = hands if hands else []
        
threading.Thread(target=camera_loop, daemon=True).start()
# ------------------------------

WIDTH = 1200
HEIGHT = 800
STEPS_PER_SEC = 30

fruits = ['dragonfruit', 'pineapple', 'plum', 'watermelon', 'pomegranate', 'strawberry', 'bomb']

game_duration = 60
BOMB_HOLD_DURATION = 2000
BOMB_FADE_DURATION = 2000
BOMB_DISPLAY_DURATION = BOMB_HOLD_DURATION + BOMB_FADE_DURATION

data = {}

def generate_fruits(fruit):
    path = "images/" + fruit + ".png"
    
    data[fruit] = {
        # claude generated these four lines
        'x':     float(random.randint(100, WIDTH - 100)),
        'y':     float(HEIGHT + 50),
        'sx':    float(random.randint(-150, 150)),
        'sy':    float(random.randint(-785, -450)),
        'throw': random.random() >= 0.75,
        # ---------------------------------
        'hit': False,
        'sliced': False
    }

for fruit in fruits:
    generate_fruits(fruit)
    
def intersect(fruit_x, fruit_y, finger_x, finger_y, size=80):
    return (fruit_x < finger_x < fruit_x + size and fruit_y < finger_y < fruit_y + size)

def hit(app, fruit, finger_x, finger_y):
    d = data[fruit]
    
    if d['hit']:
        return
    
    if not intersect(d['x'], d['y'], finger_x, finger_y):
        return
    
    d['hit'] = True
    
    if fruit == 'bomb':
        app.bomb_timer = time.time()
        bomb.play()
        bad_piggies.set_volume(0)
        app.lives -= 1
    else:
        slice.play()
        d['sliced'] = True
        app.score += 1

def gameover(app):
    app.final_score = app.score
    app.state = 'gameover'
    fart.play()
    outro.play(loops=100, fade_ms=1000)
    bad_piggies.stop()
    for fruit in fruits:
        generate_fruits(fruit)

def reset(app):
    app.lives       = 3
    app.score       = 0
    app.bomb_timer  = 0
    app.start_time  = time.time()
    app.finger1     = None
    app.finger2     = None
    for fruit in fruits:
        generate_fruits(fruit)        

def onAppStart(app):
    app.width          = WIDTH
    app.height         = HEIGHT
    app.stepsPerSecond = STEPS_PER_SEC
    app.state          = 'start'
    app.lives          = 3
    app.score          = 0
    app.final_score    = 0
    app.bomb_timer     = 0
    app.start_time     = 0
    app.finger1        = None
    app.finger2        = None

def redrawAll(app):
    if app.state == 'start':
        drawImage('data/start_screen.png', 0, 0, width=WIDTH, height=HEIGHT)

    elif app.state == 'gameover':
        drawImage('data/gameover.jpg', 0, 0, width=WIDTH, height=HEIGHT)
        drawLabel(str(app.final_score), 15, 20, size=42, fill='orange', align='left')

    elif app.state == 'playing':
        drawImage('data/background.png', 0, 0, width=WIDTH, height=HEIGHT)

        for fruit in fruits:
            d = data[fruit]
            
            if not d['throw']:
                continue
            
            if d['y'] > HEIGHT + 50:
                continue
            
            if d['sliced']:
                drawImage('images/sliced_' + fruit + '.png', int(d['x']), int(d['y']), width=80, height=80)
            
            else:
                drawImage('images/' + fruit + '.png', int(d['x']), int(d['y']), width=80, height=80)

        # Claude generated this if statement
        if app.bomb_timer > 0:
            elapsed_ms = (time.time() - app.bomb_timer) * 1000
            if elapsed_ms < BOMB_HOLD_DURATION:
                opacity = 100
            else:
                fade_elapsed = elapsed_ms - BOMB_HOLD_DURATION
                opacity = max(0, 100 - int((fade_elapsed / BOMB_FADE_DURATION) * 100))
            drawImage('images/kaboom.png', 0, 0, width=WIDTH, height=HEIGHT, opacity=opacity)
        # ----------------------------------

        drawLabel(str(app.score), 15, 20, size=42, fill='orange', align='left')
        drawLabel(str(max(0, game_duration - int(time.time() - app.start_time))), WIDTH // 2, 20, size=42, fill='white', align='center')
        
        for i in range(app.lives):
            drawImage('images/lives.png', WIDTH - 150 + i * 35, 5, width=80, height=40)

        if app.finger1:
            drawCircle(app.finger1[0], app.finger1[1], 8, fill='white', opacity=80)
        if app.finger2:
            drawCircle(app.finger2[0], app.finger2[1], 8, fill='white', opacity=80)


def onStep(app):
    if app.state != 'playing':
        return

    dt = 1.0 / STEPS_PER_SEC

    current_timer = int(time.time() - app.start_time)
    if current_timer >= game_duration:
        gameover(app)
        return

    hands = camera_data['hands']
    cam_w = camera_data['cam_w']
    cam_h = camera_data['cam_h']

    app.finger1 = None
    app.finger2 = None

    if hands:
        lms1 = hands[0]["lmList"]
        fx1  = int((1 - lms1[8][0] / cam_w) * WIDTH)
        fy1  = int(lms1[8][1] / cam_h * HEIGHT)
        app.finger1 = (fx1, fy1)

        if len(hands) == 2:
            lms2 = hands[1]["lmList"]
            fx2  = int((1 - lms2[8][0] / cam_w) * WIDTH)
            fy2  = int(lms2[8][1] / cam_h * HEIGHT)
            app.finger2 = (fx2, fy2)

    # Claude generated this for loop
    for fruit in fruits:
        d = data[fruit]

        if not d['throw']:
            generate_fruits(fruit)
            continue

        d['x']  += d['sx'] * dt
        d['y']  += d['sy'] * dt
        d['sy'] += 400 * dt

        if d['y'] > HEIGHT + 50:
            generate_fruits(fruit)
            continue

        if not d['hit']:
            if app.finger1:
                hit(app, fruit, app.finger1[0], app.finger1[1])
            if app.finger2:
                hit(app, fruit, app.finger2[0], app.finger2[1])
    # -------------------------------

    # Bomb timer
    if app.bomb_timer > 0:
        elapsed_ms = (time.time() - app.bomb_timer) * 1000
        if elapsed_ms > BOMB_DISPLAY_DURATION:
            app.bomb_timer = 0
            if app.lives <= 0:
                gameover(app)
            else:
                bad_piggies.set_volume(0.3)


def onMousePress(app, x, y, button):
    if app.state == 'start':
        reset(app)
        app.state = 'playing'
        ambatukam.stop()
        bad_piggies.play(loops=100)
        bad_piggies.set_volume(0.3)

    elif app.state == 'gameover':
        app.state = 'start'
        outro.stop()
        ambatukam.play(loops=100)
        
def onMouseMove(app, x, y):
    if app.state == 'playing':
        for fruit in fruits:
            hit(app, fruit, x, y)


runApp(width=WIDTH, height=HEIGHT)