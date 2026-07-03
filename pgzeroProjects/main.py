# Example file showing a basic pygame "game loop"
import pygame
import numpy
import os
import math
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")
game_state = "menu"
frame_index = 1

# key presses
m1_click = False
m1_down = False

LEFT_timestamp = -1
RIGHT_timestamp = -1
DOWN_timestamp = -1
UP_timestamp = -1

cw_click = False
ccw_click = False
harddrop_click = False
hold_click = False


# Title
font = pygame.font.Font(None, 64)
title = font.render("Tetris", True, (255, 255, 255))
title_pos = title.get_rect(centerx=screen.get_width() / 2, y=100)

play = font.render("Play", True, (255, 255, 255))
play_pos = play.get_rect(centerx=screen.get_width()/2, y=500)

#Board
exit = font.render("Exit", True, (255,255,255))
exit_pos = exit.get_rect(x=10, y=10)

board_state = "intermission"
board_array = []
UNIT_SIZE = 33
UNIT_SPACING = 1
UNIT_SURFACE = pygame.Surface((UNIT_SIZE,UNIT_SIZE))
BOARD_ORIGIN_X = (screen.get_width()/2) - (UNIT_SIZE + UNIT_SPACING) * 5
BOARD_ORIGIN_Y = 700
BOARD_WIDTH = 10
BOARD_HEIGHT = 40
BOARD_VISUALHEIGHT = 20
UNIT_OCCUPIEDLENGTH = UNIT_SIZE + UNIT_SPACING
board_background = pygame.Surface((UNIT_OCCUPIEDLENGTH * BOARD_WIDTH, UNIT_OCCUPIEDLENGTH * BOARD_HEIGHT))

#I Must know the active piece's origin block.
"""
I
J
L
O
S
T
Z
"""
active_piece = False
piece_index = -1
active_position = -1
EMPTY_COLOR = (255,255,255)

PIECE_ORIGINS = [
    BOARD_WIDTH*20 + 3,
    BOARD_WIDTH*20 + 4,
    BOARD_WIDTH*20 + 4,
    BOARD_WIDTH*20 + 4,
    BOARD_WIDTH*20 + 4,
    BOARD_WIDTH*20 + 4,
    BOARD_WIDTH*20 + 4,
]

PIECE_CONSTRUCTIONS = [
    [
        [-10,-10+1,-10+2,-10+3],
        [2, -10+2, -20+2, -30+2],
        [-20,-20+1,-20+2,-20+3],
        [-1,-10+1,-20+1,-30+1]
    ],
    [
        [0, -10, -10+1, -10+2],
        [1,2,-10+1,-20+1],
        [0,1,2,-10+2],
        [1,-10+1,-20,-20+1]
    ],
    [
        [2,-10+2, -10+1, -10],
        [1,-10+1,-20+1,-20+2],
        [-10,-10+1,-10+2,-20],
        [0,1,-10+1,-20+1]
    ],
    [
        [1,2,-10+1,-10+2],
        [1,2,-10+1,-10+2],
        [1,2,-10+1,-10+2],
        [1,2,-10+1,-10+2]
    ],
    [
        [1,2,-10,-11],
        [1,-10+1,-10+2,-20+2],
        [-10+1,-10+2,-20,-20+1],
        [0,-10,-10+1,-20+1]
    ],
    [
        [1,-10,-10+1,-10+2],
        [1,-10+1,-10+2,-20+1],
        [-10,-10+1,-10+2,-20+1],
        [1,-10,-10+1,-20+1]
    ],
    [
        [0,1,-10+1,-10+2],
        [2,-10+1,-10+2,-20+1],
        [-10,-10+1,-20+1,-20+2],
        [1,-10,-10+1,-20]
    ]
]

PIECE_COLORS = [
    (177, 252, 255),
    (92, 97, 255),
    (255, 200, 55),
    (229, 255, 5),
    (145, 255, 123),
    (233, 143, 255),
    (255, 143, 143)
]

def showrect(rect, bool):
    if bool == True:
        color = (0,255,0)
    elif bool == False:
        color = (255,0,0)
    else:
        color = (255,255,255)
    pygame.draw.rect(screen, color, rect)

def mousedetect(target, target_pos): # Surface
    pos = pygame.mouse.get_pos()
    hitbox_size = (50,50)
    hitbox_pos = (pos[0] - hitbox_size[0]/2, pos[1] - hitbox_size[1]/2)
    hitbox = pygame.Rect(hitbox_pos, hitbox_size)
    target_rect = target.get_rect().move(target_pos[0], target_pos[1])
    detected = hitbox.colliderect(target_rect)
    showrect(hitbox, detected)
    showrect(target_rect, False)
    return detected
"""
I believe it better to make board_array a 2d array

I do not need to make individual surfaces to represent each unit.

I merely have to assign each unit properties, of which:
    boolean: is_empty? | index 0
    tuple: color | index 1
"""
def init_board_array():
    for x in range(BOARD_WIDTH*BOARD_HEIGHT):
        board_array.append([False, EMPTY_COLOR])
init_board_array()
"""
loop board_array times
call pygame.draw.rect(screen, board_array[x][1], get_unit_position(x))
"""

def get_row(i):
    return (math.ceil((i+1) /BOARD_WIDTH))

def render_board():
    for i in range(len(board_array)):
        if i >= BOARD_WIDTH*BOARD_VISUALHEIGHT:
            return
        
        unit = board_array[i]
        unit_rect = UNIT_SURFACE.get_rect(
            x=BOARD_ORIGIN_X + (i % BOARD_WIDTH)*(UNIT_SIZE + UNIT_SPACING),
            y=BOARD_ORIGIN_Y - (get_row(i)*(UNIT_SIZE + UNIT_SPACING))
        )
        pygame.draw.rect(screen, unit[1], unit_rect)

def colorize_piece(active_position, color):
    for i in range(4):
        unit_displacement = PIECE_CONSTRUCTIONS[piece_index][0][i]
        unit_index = active_position + unit_displacement
        board_array[unit_index][1] = color

def generate_piece():
    global piece_index
    global active_position
    piece_index = 2 #random.randint(0,6)
    active_position = PIECE_ORIGINS[piece_index]
    colorize_piece(active_position, PIECE_COLORS[piece_index])

def attempt_move_piece(increment):
    global active_position
    fail_move = False
    for i in range(4):
        unit_displacement = PIECE_CONSTRUCTIONS[piece_index][0][i]
        unit_index = active_position + unit_displacement
        
        #See if new spot is occupied, if so, fail the attempt
        if board_array[unit_index+increment][0] == True:
            fail_move = True
        #See if new spot is in a different height when increment is not a factor of 10, if so, fail the attempt
        if increment % 10 != 0 and get_row(unit_index+increment) != get_row(unit_index):
            fail_move = True
        if increment % 10 == 0 and unit_index+increment < 0:
            fail_move = True
    if fail_move:
        return False
    
    colorize_piece(active_position, EMPTY_COLOR)
    active_position = active_position + increment
    colorize_piece(active_position, PIECE_COLORS[piece_index])
    return True

def display_developerinfo():
    global active_position
    global font
    active_position_text = font.render(str(active_position), True, (255,255,255))
    active_position_text_pos = active_position_text.get_rect(x=10, y=50)
    screen.blit(active_position_text, active_position_text_pos)



while running:
    
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not m1_down:
                m1_click = True
            else:
                m1_click = False
            m1_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            m1_click = False
            m1_down = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                LEFT_timestamp = frame_index
            elif event.key == pygame.K_RIGHT:
                RIGHT_timestamp = frame_index
            elif event.key == pygame.K_DOWN:
                DOWN_timestamp = frame_index
            elif event.key == pygame.K_x:
                cw_click = True
            elif event.key == pygame.K_z:
                ccw_click = True
            elif event.key == pygame.K_c:
                harddrop_click = True
            elif event.key == pygame.K_LSHIFT:
                hold_click = True

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")
    
    if game_state == "menu":
        if m1_click:
            m1_click = False
            if mousedetect(play, play_pos):
                game_state = "board"
                board_state = "intermission"
        screen.blit(title, title_pos)
        screen.blit(play, play_pos)
        pass
    elif game_state == "board":
        if m1_click:
            if mousedetect(exit, exit_pos):
                game_state = "menu"
        
        if board_state == "intermission":
            board_state = "active"
        if board_state == "active":
            if not active_piece:
                generate_piece()
                active_piece = True
            
            if LEFT_timestamp - frame_index == 0:
                attempt_move_piece(-1)
            if RIGHT_timestamp - frame_index == 0:
                attempt_move_piece(1)
            if DOWN_timestamp != -1:
                success = True
                while success:
                    success = attempt_move_piece(-10)
                
            
            if frame_index % 10 == 0:
                attempt_move_piece(-10)
        
        screen.blit(exit, exit_pos)
        display_developerinfo()
        render_board()
        pass

    # flip() the display to put your work on screen
    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60
    frame_index +=1

pygame.quit()