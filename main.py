from cvzone.HandTrackingModule import HandDetector
import cv2
import pygame
import random

# These two line are frome cvzone documentation
# https://github.com/cvzone/cvzone?tab=readme-ov-file#hand-tracking-module
cap = cv2.VideoCapture(0)
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
## -----------------------------------------------------------------------

running = True
lives = 3
score = 0
fruits = ['dragonfruit', 'pineapple', 'plum', 'watermelon', 'pomegranate', 'strawberry', 'bomb']
round_duration = 60
time = 0
fruit_rate = 0.2
bomb_rate = 0.1

WIDTH = 800
HEIGHT = 500
FPS = 60

pygame.init()
pygame.display.set_caption('Fruit-Ninja With a Twist!')
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

background = pygame.image.load('data/background.png')

def generate_fruits(fruit):
    path = "images/" + fruit + ".png"
    
    data[fruit] = {
        'img': pygame.image.load(path),
        # claude generated these four lines
        'x': random.randint(100, 500),
        'y': 800,
        'sx': random.randint(-80, 80),
        'sy': random.randint(-800, -550),
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

while running:

    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

    
    # This is the start of code i grabbed from cvzone documentation
    # https://github.com/cvzone/cvzone?tab=readme-ov-file#hand-tracking-module
    success, img = cap.read()

    if not success or img is None:
        print("Failed to grabe frame")
        break
    
    hands, img = detector.findHands(img, draw=True, flipType=True)

    if hands:
        hand1 = hands[0]
        lmList1 = hand1["lmList"]
        bbox1 = hand1["bbox"]
        center1 = hand1['center']
        handType1 = hand1["type"]

        fingers1 = detector.fingersUp(hand1)
        print(f'H1 = {fingers1.count(1)}', end=" ")

        length, info, img = detector.findDistance(lmList1[8][0:2], lmList1[12][0:2], img, color=(255, 0, 255),
                                                  scale=10)

        if len(hands) == 2:
            hand2 = hands[1]
            lmList2 = hand2["lmList"]
            bbox2 = hand2["bbox"]
            center2 = hand2['center']
            handType2 = hand2["type"]

            fingers2 = detector.fingersUp(hand2)
            print(f'H2 = {fingers2.count(1)}', end=" ")

            length, info, img = detector.findDistance(lmList1[8][0:2], lmList2[12][0:2], img, color=(255, 0, 255),
                                                      scale=10)

        print(" ")

    cv2.imshow("Image", img)
    cv2.waitKey(1)
    # This is the end of code i grabbed from cvzone documentation
    pygame.display.update()
    
# cap.release()
# cv2.destroyAllWindows()
# pygame.quit()