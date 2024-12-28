import pygame
import sys
import math
from queue import PriorityQueue
import time
import threading

# Initialize Pygame
pygame.init()

# Screen settings
screen_width, screen_height = 600, 630
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Astar")

# Clock to control frame rate
clock = pygame.time.Clock()
fps = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BRIGHTBLUE = (0, 123, 255)
DEFAULT_COLOR = GRAY
START_COLOR = WHITE
END_COLOR = WHITE
# Font
font = pygame.font.Font(None, 20)
# Button settings
button_width, button_height = 20, 20
button_margin = 0
rows, cols = 30 , 30   # Number of rows and columns in the grid

# Generate button grid
buttons = []
for row in range(rows):
    button_row = []
    for col in range(cols):
        x = col * (button_width + button_margin) + button_margin
        y = row * (button_height + button_margin) + button_margin
        button_row.append(pygame.Rect(x, y, button_width, button_height))
    buttons.append(button_row)

button_colors = []
for i in range(rows):
    arr  = []
    for j in range(cols):
        arr.append(DEFAULT_COLOR)
    button_colors.append(arr)

start_button = pygame.Rect(250, 605, 100, 20)
reset_button = pygame.Rect(370, 605, 100, 20)
#
clicked_count = 0
start_row_col = []
end_row_col = []
walls = set() #row,col

cur_thread = None
stop_event = threading.Event()

def heuristic(row , col):
    #manhattan distance
    return abs(row - end_row_col[0]) + abs(col - end_row_col[1])

class Node:
    def __init__(self):
        self.row = 0 
        self.col = 0
        self.parent = None
        self.g = float('inf')
        self.f = 0
        self.h = 0
    
    def __lt__(self, other):
        return self.f < other.f

def handle_selection(x , y):
    global clicked_count
    global start_row_col
    global end_row_col
    global walls
    row_index = math.floor(y / button_width)
    col_index = math.floor(x / button_height)
    if clicked_count ==  0:
        button_colors[row_index][col_index] = START_COLOR
        start_row_col = [row_index , col_index]
    elif clicked_count == 1:
        button_colors[row_index][col_index] = END_COLOR
        end_row_col = [row_index , col_index]
    else:
        # walls
        button_colors[row_index][col_index] = BLACK
        walls.add(f"{row_index},{col_index}")

    clicked_count += 1

def visualize(stop_event):
    global start_row_col 
    global end_row_col
    global walls
    open_set = PriorityQueue()
    open_set_hash = set()

    visited = set()
    start_node = Node()
    start_node.row = start_row_col[0]
    start_node.col = start_row_col[1]
    
    start_node.g = 0
    start_node.h = 0
    start_node.f = 0

    open_set.put(start_node)
    open_set_hash.add(f"{start_node.row}{start_node.col}")

    def getNeighbors(row , col):
        neighbors = []
        directions = [
            {"row":1 , "col":0},
            {"row":-1 , "col":0},
            {"row":0 , "col":1},
            {"row":0 , "col":-1},
        ]
        for direction in directions:
            n_row = row + direction["row"]
            n_col = col+direction["col"]
            if  n_row >= 0 and n_row <= rows -1 and n_col >= 0 and n_col <= cols -1 :
                if not visited.__contains__(f"{n_row}{n_col}") and not walls.__contains__(f"{n_row},{n_col}") :
                    node = Node()
                    node.row = n_row
                    node.col = n_col
                    neighbors.append(node)
        return neighbors


    while not open_set.empty():
        if stop_event.set():
            a = 10
            break
        time.sleep(0.01)
        cur_node = open_set.get()
        open_set_hash.remove(f"{cur_node.row}{cur_node.col}")
        if cur_node.row == end_row_col[0] and cur_node.col == end_row_col[1]:
            reconstructPath(cur_node)
            break

        visited.add(f"{cur_node.row}{cur_node.col}")
        if not(cur_node.row == start_node.row and cur_node.col == start_node.col):
            if (cur_node.row + cur_node.col) % 4 == 0:
                button_colors[cur_node.row][cur_node.col] = BLUE
            if (cur_node.row + cur_node.col) % 4 == 1:
                button_colors[cur_node.row][cur_node.col] = RED
            if (cur_node.row + cur_node.col) % 4 == 2:
                button_colors[cur_node.row][cur_node.col] = PURPLE
            if (cur_node.row + cur_node.col) % 4 == 3:
                button_colors[cur_node.row][cur_node.col] = GREEN

        neighbors = getNeighbors(cur_node.row , cur_node.col)

        for n in neighbors:
            hash_value = f"{n.row}{n.col}"
            if cur_node.g + 1 <  n.g:
                n.parent = cur_node
                n.g = cur_node.g + 1  
                n.h = heuristic(n.row , n.col)
                n.f = n.g + n.h
                if not open_set_hash.__contains__(hash_value):
                    open_set.put(n)
                    open_set_hash.add(hash_value)
                else:
                    # refresh open set
                    open_set.put(open_set.get())

    

def reconstructPath(node):
    cur_node = node
    while cur_node.parent.parent:
        cur_node = cur_node.parent
        time.sleep(0.2)
        button_colors[cur_node.row][cur_node.col] = WHITE
        print(cur_node.row , cur_node.col)


def reset():
    print("rest girid")
    global button_colors
    global clicked_count 
    global walls
    global stop_event
    temp_button_colors = []
    for i in range(rows):
        arr  = []
        for j in range(cols):
            arr.append(DEFAULT_COLOR)
        temp_button_colors.append(arr)

    button_colors = temp_button_colors
    clicked_count = 0
    walls = set() #row,col
    # terminate algoirthm if it is working
    if cur_thread is not None and cur_thread.is_alive():
        # Signal the thread to stop
        stop_event.set()
        cur_thread.join()

# Game loop
running = True
while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:  # Check if a button is clicked
            mouse_pos = event.pos
            for row in buttons:
                for button in row:
                    if button.collidepoint(mouse_pos):
                        print(f"Button at {button} clicked!")
                        handle_selection(mouse_pos[0] , mouse_pos[1])
            if start_button.collidepoint(mouse_pos):
                if cur_thread is None or not cur_thread.is_alive():
                    print(f"start visualizer")
                    new_thrad = threading.Thread(target= visualize ,args=(stop_event,))
                    cur_thread = new_thrad
                    new_thrad.start()
            if reset_button.collidepoint(mouse_pos):
                reset()     

    # Drawing
    screen.fill(BLACK)  # Clear the screen

    for i in range(rows):
        for j in range(cols):
            button = buttons[i][j]
            button_color = button_colors[i][j]
            pygame.draw.rect(screen, button_colors[i][j], button)  # Draw button
            pygame.draw.rect(screen, BLUE, button, 2)  # Draw button border
    # draw start button
    pygame.draw.rect(screen,  DEFAULT_COLOR , start_button)
    # draw reset button
    pygame.draw.rect(screen,  DEFAULT_COLOR , reset_button)
    
    # Render text
    text_surface  = font.render('Start visualizer', 1, BLACK)
    text_rect = text_surface.get_rect(center=start_button.center)  # Center the text
    screen.blit(text_surface, text_rect)  # Draw the text on the button

    # Render text
    text_surface  = font.render('reset', 1, BLACK)
    text_rect = text_surface.get_rect(center=reset_button.center)  # Center the text
    screen.blit(text_surface, text_rect)  # Draw the text on the button

    # Update the display
    pygame.display.flip()
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()
