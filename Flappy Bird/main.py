import random 
import sys
import pygame
from pygame.locals import *

# Global variables
FPS = 60  # Frames per second
SCREENWIDTH = 350
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_IMAGES = {}
GAME_SOUNDS = {}
PLAYER = 'assets/images/bird.png'
BACKGROUND = 'assets/images/game_bg.png'
PIPE = 'assets/images/pipe.png' 

def welcomeScreen():
    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_IMAGES["player"].get_height()) / 2)  
    messagex = int((SCREENWIDTH - GAME_IMAGES["message"].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.13) 
    basex = 0
    while True:
        for event in pygame.event.get():
            if(event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
                pygame.quit()
                sys.exit()
            elif(event.type == KEYDOWN and event.key == K_SPACE):
                return
        
        SCREEN.blit(GAME_IMAGES['background'], (0, 0))
        SCREEN.blit(GAME_IMAGES['player'], (playerx, playery))
        SCREEN.blit(GAME_IMAGES['message'], (messagex, messagey))
        SCREEN.blit(GAME_IMAGES['base'], (basex, GROUNDY))
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def showGameOverScreen(score):
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont('Arial', 40, bold=True)
    font_small = pygame.font.SysFont('Arial', 22)
    
    game_over_text = font_big.render('Game Over', True, (255, 0, 0))
    score_text = font_small.render(f'Your Score : {score}', True, (255, 255, 255))
    restart_text = font_small.render('Press R to Restart or Q to Quit', True, (255, 255, 255))

    game_over_rect = game_over_text.get_rect(center=(SCREENWIDTH/2, SCREENHEIGHT/2 - 50))
    score_rect = score_text.get_rect(center=(SCREENWIDTH/2, SCREENHEIGHT/2))
    restart_rect = restart_text.get_rect(center=(SCREENWIDTH/2, SCREENHEIGHT/2 + 50))
    
    SCREEN.blit(game_over_text, game_over_rect)
    SCREEN.blit(score_text, score_rect)
    SCREEN.blit(restart_text, restart_rect)

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_r:
                    return  # Restart the game
                elif event.key == K_q or event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def mainGame():
    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT / 2)  # Set initial player height
    basex = 0

    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    upperPipes = [
        {"x": SCREENWIDTH + 200, "y": newPipe1[0]['y']},
        {"x": SCREENWIDTH + 200 + (SCREENWIDTH/2), "y": newPipe2[0]['y']}
    ]
    lowerPipes = [
        {"x": SCREENWIDTH + 200, "y": newPipe1[1]['y']},
        {"x": SCREENWIDTH + 200 + (SCREENWIDTH/2), "y": newPipe2[1]['y']}
    ]

    pipeVelX = -4
    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1
    
    playerFlapAccv = -8
    playerFlapped = False

    while True:
        for event in pygame.event.get():
            if(event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
                pygame.quit()
                sys.exit()
            if(event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP)):
                if (playery > 0):
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS["wing"].play()
        
        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            GAME_SOUNDS["hit"].play()
            GAME_SOUNDS["die"].play()
            showGameOverScreen(score)
            return
        
        playerMidPos = playerx + GAME_IMAGES["player"].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_IMAGES["pipe"][0].get_width() / 2
            # Increase scoring area to cover 8 pixels width for smoother scoring
            if pipeMidPos <= playerMidPos < pipeMidPos + 8:
                score += 1
                print(f"Your score is {score}")
                GAME_SOUNDS["point"].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False

        playerHeight = GAME_IMAGES["player"].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        if upperPipes[0]['x'] < -GAME_IMAGES["pipe"][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        SCREEN.blit(GAME_IMAGES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_IMAGES["pipe"][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_IMAGES["pipe"][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_IMAGES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_IMAGES['player'], (playerx, playery))
        myDigits = [int(x) for x in str(score)]
        width = 0
        for digit in myDigits:
            width += GAME_IMAGES["numbers"][digit].get_width()  
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_IMAGES["numbers"][digit], (Xoffset, SCREENHEIGHT * 0.02))
            Xoffset += GAME_IMAGES["numbers"][digit].get_width()

        pygame.display.update()
        FPSCLOCK.tick(FPS) 
    
def isCollide(playerx, playery, upperPipes, lowerPipes):
    # Check upper pipes collision
    for pipe in upperPipes:
        pipeRect = pygame.Rect(pipe['x'], pipe['y'], GAME_IMAGES["pipe"][0].get_width(), GAME_IMAGES["pipe"][0].get_height())
        playerRect = pygame.Rect(playerx, playery, GAME_IMAGES["player"].get_width(), GAME_IMAGES["player"].get_height())
        if playerRect.colliderect(pipeRect):
            return True

    # Check lower pipes collision
    for pipe in lowerPipes:
        pipeRect = pygame.Rect(pipe['x'], pipe['y'], GAME_IMAGES["pipe"][1].get_width(), GAME_IMAGES["pipe"][1].get_height())
        playerRect = pygame.Rect(playerx, playery, GAME_IMAGES["player"].get_width(), GAME_IMAGES["player"].get_height())
        if playerRect.colliderect(pipeRect):
            return True

    # Check if player hits the ground or flies above screen
    if playery + GAME_IMAGES["player"].get_height() >= GROUNDY or playery < 0:
        return True
    return False

def getRandomPipe():
    pipeHeight = GAME_IMAGES["pipe"][0].get_height()
    offset = SCREENHEIGHT / 3

    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_IMAGES["base"].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},  # Upper Pipe
        {'x': pipeX, 'y': y2}    # Lower Pipe
    ]   
    return pipe

if __name__ == "__main__":
    pygame.init() 
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird")

    # Load number images and scale them down for smaller digits
    original_numbers = (
        pygame.image.load('assets/images/0.png').convert_alpha(),
        pygame.image.load('assets/images/1.png').convert_alpha(),
        pygame.image.load('assets/images/2.png').convert_alpha(),
        pygame.image.load('assets/images/3.png').convert_alpha(),
        pygame.image.load('assets/images/4.png').convert_alpha(),
        pygame.image.load('assets/images/5.png').convert_alpha(),
        pygame.image.load('assets/images/6.png').convert_alpha(),
        pygame.image.load('assets/images/7.png').convert_alpha(),
        pygame.image.load('assets/images/8.png').convert_alpha(),
        pygame.image.load('assets/images/9.png').convert_alpha()
    )
    # Scale numbers to smaller size (e.g. width: 20 pixels, maintaining aspect ratio)
    scaled_numbers = []
    for num_img in original_numbers:
        w = 20
        h = int(num_img.get_height() * (w / num_img.get_width()))
        scaled_num = pygame.transform.scale(num_img, (w, h))
        scaled_numbers.append(scaled_num)
    GAME_IMAGES["numbers"] = tuple(scaled_numbers)

    GAME_IMAGES["message"] = pygame.image.load('assets/images/message.png').convert_alpha()
    GAME_IMAGES["base"] = pygame.image.load('assets/images/base.png').convert_alpha()

    # Load pipe images and scale to smaller size (e.g. width: 50 pixels, maintain aspect ratio)
    pipe_img = pygame.image.load(PIPE).convert_alpha()
    pipe_width = 50
    pipe_height = int(pipe_img.get_height() * (pipe_width / pipe_img.get_width()))
    pipe_up = pygame.transform.rotate(pygame.transform.scale(pipe_img, (pipe_width, pipe_height)), 180)
    pipe_down = pygame.transform.scale(pipe_img, (pipe_width, pipe_height))
    GAME_IMAGES["pipe"] = (pipe_up, pipe_down)

    GAME_SOUNDS["die"] = pygame.mixer.Sound('assets/sound_effects/die.wav')
    GAME_SOUNDS["hit"] = pygame.mixer.Sound('assets/sound_effects/hit.wav')
    GAME_SOUNDS["wing"] = pygame.mixer.Sound('assets/sound_effects/wing.wav')
    GAME_SOUNDS["point"] = pygame.mixer.Sound('assets/sound_effects/point.wav')
    GAME_SOUNDS["swoosh"] = pygame.mixer.Sound('assets/sound_effects/swoosh.wav')

    GAME_IMAGES["background"] = pygame.image.load(BACKGROUND).convert()

    # Scale down player image as well for consistency; keep 50x50 as before (optional)
    GAME_IMAGES["player"] = pygame.transform.scale(pygame.image.load(PLAYER).convert_alpha(), (50, 50))

    while True:
        welcomeScreen()
        mainGame()

