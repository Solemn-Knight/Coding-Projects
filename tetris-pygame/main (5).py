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
elapsed_time = 0
elapsed_time_delta = 0
SPT = 1/60

# key presses, timestamps
m1_click = False
m1_down = False

LEFT_timestamp = -1
LEFT_framestamp = -1
RIGHT_timestamp = -1
RIGHT_framestamp = -1
DOWN_timestamp = -1
UP_timestamp = -1

cw_click = False
ccw_click = False
doublecw_click = False
harddrop_click = False
hold_click = False
restart_click = False

DAS = 4
ARR = 1

gravity_timestamp = -1

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
BOARD_VISUALHEIGHT = 30
UNIT_OCCUPIEDLENGTH = UNIT_SIZE + UNIT_SPACING
board_background = pygame.Surface((UNIT_OCCUPIEDLENGTH * BOARD_WIDTH, UNIT_OCCUPIEDLENGTH * BOARD_HEIGHT))
MAX_QUEUE = 5
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
piece_move_timestamp = -1
rotation_index = 0
held_piece_index = -1
EMPTY_COLOR = (20,20,20)
GHOST_COLOR = (100,100,100)
"""
ghost_piece
    in while running
        take active position, attempt move it down until it is unable to anymore, and colorize that part of the board
"""

PIECE_ORIGINS = [
    BOARD_WIDTH*20 + 3,
    BOARD_WIDTH*20 + 3,
    BOARD_WIDTH*20 + 3,
    BOARD_WIDTH*20 + 3,
    BOARD_WIDTH*20 + 3,
    BOARD_WIDTH*20 + 3,
    BOARD_WIDTH*20 + 3,
]

PIECE_CONSTRUCTIONS = [
    [
        [-10,-10+1,-10+2,-10+3],
        [2, -10+2, -20+2, -30+2],
        [-20,-20+1,-20+2,-20+3],
        [1,-10+1,-20+1,-30+1]
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
        [1,2,-10,-10+1],
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

PIECE_ROTATION_REPOSITIONS = {
    "JLSTZ" : {
        "0>1" : [[-1, -2], [-1, 0], [-1, 1], [0,2], [-1, -2]],
        "1>0" : [[1, 0], [1, -1], [0,2], [1, 2]],
        "1>2" : [[1, 0], [1, -1], [1,-2], [0,2], [1, 2]],
        "2>1" : [[-1, 0], [-1, 1], [0,-2], [-1, -2]],
        "2>3" : [[1, 0], [1, 1], [0,-2], [1, -2]],
        "3>2" : [[-1, 0], [-1, -1], [0,2], [-1, 2]],
        "3>0" : [[-1, 0], [-1, -1], [0,2], [-1, 2]],
        "0>3" : [[1,0], [1, 1], [0, -2], [1, -2]]
    },
    "I" : {
        "0>1" : [[-2, 0], [1, 0], [-2,-1], [1, 2]],
        "1>0" : [[2, 0], [-1, 0], [2,1], [-1, -2]],
        "1>2" : [[-1, 0], [2, 0], [-1,2], [2, -1]],
        "2>1" : [[1, 0], [-2, 0], [1,-2], [-2, 1]],
        "2>3" : [[2, 0], [-1, 0], [2,1], [-1, -2]],
        "3>2" : [[-2, 0], [1, 0], [-2,-1], [1, 2]],
        "3>0" : [[1, 0], [-2, 0], [1,-2], [-2, 1]],
        "0>3" : [[-1, 0], [2, 0], [-1,2], [2, -1]]
    }
}

PIECE_COLORS = [
    (177, 252, 255),
    (92, 97, 255),
    (255, 200, 55),
    (229, 255, 5),
    (145, 255, 123),
    (233, 143, 255),
    (255, 143, 143)
]

PIECE_BAGS = [] #2 dimensional

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
NEXTQUEUE_ORIGIN_X = 850
NEXTQUEUE_ORIGIN_Y = 50
def render_nextqueue():
    global MAX_QUEUE
    displayed_pieces = 0
    bag_index = 0
    marble_index = 0
    while displayed_pieces < MAX_QUEUE:
        #print(PIECE_BAGS[bag_index])
        piece_index = PIECE_BAGS[bag_index][marble_index]
        #print("e")
        #render this piece
        for i in PIECE_CONSTRUCTIONS[piece_index][0]:
            unit_rect = UNIT_SURFACE.get_rect(
                x=NEXTQUEUE_ORIGIN_X + (i % BOARD_WIDTH)*(UNIT_SIZE + UNIT_SPACING),
                y=NEXTQUEUE_ORIGIN_Y + (displayed_pieces*80) + (-get_row(i)*(UNIT_SIZE + UNIT_SPACING))
            )
            pygame.draw.rect(screen, PIECE_COLORS[piece_index], unit_rect)
        displayed_pieces+=1
        marble_index+=1
        if marble_index>=len(PIECE_BAGS[bag_index]):
            marble_index = 0
            bag_index+=1

def render_heldpiece():
    if held_piece_index == -1:
        return
    
    for i in PIECE_CONSTRUCTIONS[held_piece_index][0]:
        unit_rect = UNIT_SURFACE.get_rect(
                x=BOARD_ORIGIN_X - 150 + (i % BOARD_WIDTH)*(UNIT_SIZE + UNIT_SPACING),
                y=NEXTQUEUE_ORIGIN_Y + (-get_row(i)*(UNIT_SIZE + UNIT_SPACING))
            )
        pygame.draw.rect(screen, PIECE_COLORS[held_piece_index], unit_rect)

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
        
        if unit[1] == EMPTY_COLOR:
            unit[0] = False
        if unit[0] == False:
            unit[1] = EMPTY_COLOR
        
        #if i == active_position:
        #    pygame.draw.rect(screen, (200,100,200), unit_rect)

def colorize_piece(active_position, color):
    for i in range(4):
        unit_displacement = PIECE_CONSTRUCTIONS[piece_index][rotation_index][i]
        unit_index = active_position + unit_displacement
        board_array[unit_index][1] = color

def refill_bags():
    while len(PIECE_BAGS) < 10:
        PIECE_BAGS.append(random.sample([0,1,2,3,4,5,6], 7))
refill_bags()
def generate_piece():
    global piece_index
    global active_position
    global rotation_index
    rotation_index = 0
    if len(PIECE_BAGS[0]) == 0:
        PIECE_BAGS.pop(0)
        refill_bags()
    piece_index = PIECE_BAGS[0][0]
    PIECE_BAGS[0].pop(0)

    if len(PIECE_BAGS[0]) == 0:
        PIECE_BAGS.pop(0)
        refill_bags()
    active_position = PIECE_ORIGINS[piece_index]
    colorize_piece(active_position, PIECE_COLORS[piece_index])

def attempt_move_piece(increment):
    global active_position
    fail_move = False
    for i in range(4):
        unit_displacement = PIECE_CONSTRUCTIONS[piece_index][rotation_index][i]
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

    global piece_move_timestamp
    global frame_index

    piece_move_timestamp = frame_index
    return True

def rinse_rotation_index(rotation_index, increment):
    if rotation_index + increment > 3:
        return -1 + increment
    elif rotation_index + increment < 0:
        return 4 + increment
    return rotation_index + increment

# attempt the rotation over 5 loops, reposition the active position from where it was originally at 4 different
def attempt_rotate_piece(increment):
    global active_position
    global rotation_index
    fail_rotation = False
    new_position = -1
    testcase = -1
    reposition_type = ""
    if piece_index == 0:
        reposition_type = "I"
    else:
        reposition_type = "JLSTZ"
    rotation_type = str(rotation_index) + ">" + str(rinse_rotation_index(rotation_index, increment))
    while not fail_rotation:
        valid_rotation = True
        #print(rotation_type)
        for i in range(4):
            unit_displacement = PIECE_CONSTRUCTIONS[piece_index][rinse_rotation_index(rotation_index, increment)][i]
            new_position = active_position
            if testcase != -1:
                print(PIECE_ROTATION_REPOSITIONS[reposition_type][rotation_type][testcase])
                x = PIECE_ROTATION_REPOSITIONS[reposition_type][rotation_type][testcase][0]
                y = PIECE_ROTATION_REPOSITIONS[reposition_type][rotation_type][testcase][1]
                new_position = new_position+x
                if get_row(new_position+(y*10)) > 0:
                    new_position = new_position+(y*10)
            
            unit_index = new_position + unit_displacement

            #See if new spot is occupied, if so, fail the attempt
            if board_array[unit_index][0] == True:
                print("SPOT IS OCCUPIED")
                valid_rotation = False

            desired_rowdifference = math.floor((abs(unit_displacement)+3)/10)
            if abs(get_row(unit_index) - get_row(new_position)) != desired_rowdifference or get_row(unit_index) <= 0: #and new_position - (get_row(new_position)-1)*10 < 9:
                print("DIFFERENT HEIGHT LEVEL")
                valid_rotation = False
        if valid_rotation:
            break
        elif testcase == len(PIECE_ROTATION_REPOSITIONS[reposition_type][rotation_type])-1:
            fail_rotation = True
        else:
            testcase +=1
    
    if fail_rotation:
        print("FAILED ROTATION!")
        return False
    colorize_piece(active_position, EMPTY_COLOR)
    active_position = new_position
    rotation_index = rinse_rotation_index(rotation_index,increment)

    global piece_move_timestamp
    global frame_index

    piece_move_timestamp = frame_index
    return True

def clear_row(y):
    for x in range(BOARD_WIDTH):
        board_array[y*10 + x][0] = False
        board_array[y*10 + x][1] = EMPTY_COLOR

def shift_rows_down(starty):
    for iy in range(BOARD_HEIGHT-starty):
        y = iy + starty
        for x in range(BOARD_WIDTH):
            unit_index = y*10 + x
            unitabove_index = (y+1)*10 + x
            if unitabove_index > len(board_array)-1:
                break
            board_array[unit_index][0] = board_array[unitabove_index][0]
            board_array[unit_index][1] = board_array[unitabove_index][1]

def attempt_clear_rows(starty):
    # loop through the board array for boardheight times
    # for each loop, loop for boardwidth times
    # keep completerow var true, if there is ever an empty cell, make it false

    # IF TRUE:
    #   Wipe every cell in that row to be empty
    #   Take every row above and take the cell data, transfer it to the cell below
    #   recall this function, passing the y level that it was left off at
    for iy in range(BOARD_HEIGHT-starty):
        y = iy + starty
        filledrow = True
        for x in range(BOARD_WIDTH):
            if board_array[y*10 + x][0] == False:
                filledrow=False
                break
        if filledrow:
            clear_row(y)
            shift_rows_down(y)
            attempt_clear_rows(y)
            break
            
def colorize_ghostpiece():
    global active_position
    success = True
    temp_active_position = active_position
    while success:
        success = attempt_move_piece(-10)
    ghost_position = active_position
    active_position = temp_active_position
    colorize_piece(ghost_position, GHOST_COLOR)
    return ghost_position

def secure_piece():
    global active_piece
    global active_position
    global board_array
    active_piece = False
    for i in range(4):
        unit_displacement = PIECE_CONSTRUCTIONS[piece_index][rotation_index][i]
        unit_index = active_position + unit_displacement
        board_array[unit_index][0] = True
        board_array[unit_index][1] = PIECE_COLORS[piece_index]
    attempt_clear_rows(0)

def display_developerinfo():
    global active_position
    global font
    active_position_text = font.render(str(active_position), True, (255,255,255))
    active_position_text_pos = active_position_text.get_rect(x=10, y=50)

    FPS_text = font.render(str(math.ceil(1 / (elapsed_time_delta/1000))), True, (255,255,255))
    FPS_text_pos = FPS_text.get_rect(x=10, y=100)
    screen.blit(active_position_text, active_position_text_pos)
    screen.blit(FPS_text, FPS_text_pos)

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
                LEFT_framestamp = frame_index
                LEFT_timestamp = elapsed_time
                RIGHT_framestamp = -1
            elif event.key == pygame.K_RIGHT:
                RIGHT_timestamp = elapsed_time
                RIGHT_framestamp = frame_index
                LEFT_framestamp = -1
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
            elif event.key == pygame.K_r:
                restart_click = True
            elif event.key == pygame.K_v:
                doublecw_click = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                LEFT_framestamp = -1
            elif event.key == pygame.K_RIGHT:
                RIGHT_framestamp = -1
            elif event.key == pygame.K_DOWN:
                DOWN_timestamp = -1

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
        piece_secured = False
        if m1_click:
            if mousedetect(exit, exit_pos):
                game_state = "menu"
        
        if board_state == "intermission":
            board_state = "active"
        if board_state == "active":
            if restart_click:
                restart_click = False
                colorize_piece(active_position, EMPTY_COLOR)
                active_piece = False
                for i in range(BOARD_HEIGHT):
                    clear_row(i)
                PIECE_BAGS = []
                refill_bags()
                held_piece_index = -1
            if hold_click:
                hold_click = False
                if active_piece:
                    colorize_piece(active_position, EMPTY_COLOR)
                temp_index = held_piece_index
                held_piece_index = piece_index
                piece_index = temp_index
                if piece_index == -1:
                    active_piece = False
                active_position = PIECE_ORIGINS[piece_index]
                rotation_index = 0
            if not active_piece:
                generate_piece()
                active_piece = True
                piece_move_timestamp = frame_index
                gravity_timestamp = elapsed_time
            
            #if LEFT_timestamp - frame_index == 0 or ((LEFT_timestamp - frame_index) % ARR == 0 and (frame_index - LEFT_timestamp) > DAS and LEFT_timestamp != -1):
            #    attempt_move_piece(-1)
            #if RIGHT_timestamp - frame_index == 0 or ((RIGHT_timestamp - frame_index) % ARR == 0 and (frame_index - RIGHT_timestamp) > DAS and RIGHT_timestamp != -1):
            #    attempt_move_piece(1)
            if LEFT_framestamp - frame_index == 0:
                attempt_move_piece(-1)
            if (elapsed_time - LEFT_timestamp)/1000 > ARR*SPT and frame_index - LEFT_framestamp >= DAS and LEFT_framestamp!=-1:
                LEFT_timestamp+=ARR*SPT*1000
                if ARR != 0:
                    attempt_move_piece(-1)
                else:
                    success = True
                    while success:
                        success = attempt_move_piece(-1)
            
            if RIGHT_framestamp - frame_index == 0:
                attempt_move_piece(1)
            if (elapsed_time - RIGHT_timestamp)/1000 > ARR*SPT and frame_index - RIGHT_framestamp >= DAS and RIGHT_framestamp!=-1:
                RIGHT_timestamp+=ARR*SPT*1000
                if ARR != 0:
                    attempt_move_piece(1)
                else:
                    success = True
                    while success:
                        success = attempt_move_piece(1)
            if DOWN_timestamp != -1:
                success = True
                while success:
                    success = attempt_move_piece(-10)
            
            if cw_click:
                cw_click = False
                attempt_rotate_piece(1)
            if ccw_click:
                ccw_click = False
                attempt_rotate_piece(-1)
            if harddrop_click:
                harddrop_click = False
                #Move the piece down until it cant anymore
                success = True
                while success:
                    success = attempt_move_piece(-10)
                piece_move_timestamp = -1000
                gravity_timestamp = -100
            if doublecw_click:
                doublecw_click = False
                temp_rotation_index = rotation_index
                temp_active_position = active_position
                attempt_rotate_piece(1)
                attempt_rotate_piece(1)
                if abs(temp_rotation_index-rotation_index) != 2:
                    active_position = temp_active_position
                    rotation_index = temp_rotation_index


            
            #if frame_index % 10 == 0:
            #    attempt_move_piece(-10)
            
            if (elapsed_time - gravity_timestamp)/1000 > SPT * 10:
                attempt_move_piece(-10)
                gravity_timestamp += SPT*10*1000

            if frame_index - piece_move_timestamp > 30:
                secure_piece()
                piece_move_timestamp = frame_index
                active_piece = False
                piece_secured = True
            
        ghost_position = colorize_ghostpiece()
        colorize_piece(active_position, PIECE_COLORS[piece_index])
        
        screen.blit(exit, exit_pos)
        display_developerinfo()
        render_nextqueue()
        render_heldpiece()
        render_board()
        if not piece_secured:
            colorize_piece(ghost_position, EMPTY_COLOR)
        pass

    # flip() the display to put your work on screen
    pygame.display.flip()
    elapsed_time_delta = clock.tick(600)
    elapsed_time += elapsed_time_delta  # limits FPS to 60
    frame_index +=0.1

pygame.quit()
