import pygame as pg
import sys
from random import randint
import time
import os
from collections import deque

# Used to modify the window size, values must be a multiple of 40
screen_width = 800
screen_height = 600

# Controls where the window appears on the screen
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)


class Fruit(object):

    def __init__(self):

        self.color = pg.Color(139, 0, 0)
        self.width = 20
        self.height = 20
        self.fruit = None
        self.radius = 10

        # The initial position of the fruit is placed randomly on the screen
        self.x = randint(0, int(screen_width / self.width) - 1) * self.width
        self.y = randint(0, int(screen_height / self.height) - 1) * self.height

    # Prints the fruit on the screen
    def draw_fruit(self, surface):

        self.fruit = pg.Rect(self.x, self.y, self.width, self.height)
        pg.draw.circle(surface, self.color, (self.x + self.radius, self.y + self.radius), self.radius)

    # Checks whether the snake's head collides with the fruit
    def fruit_collision(self, head):

        return self.fruit.colliderect(head)

    # Finds a new location for a fruit after a collision occurs
    def fruit_position(self, snake):

        flag = True
        while flag:

            # The position of the fruit is chosen randomly
            self.x = randint(0, int(screen_width / self.width) - 1) * self.width
            self.y = randint(0, int(screen_height / self.height) - 1) * self.height

            # # Avoid placing on the boundary by limiting the random range
            # self.x = randint(1, int((screen_width / self.width) - 2)) * self.width
            # self.y = randint(1, int((screen_height / self.height) - 2)) * self.height

            # Checks whether the new fruit location is already occupied by the snake's body
            if snake.empty_space(self.x, self.y):
                flag = False


class Snake(object):

    def __init__(self):

        self.x = screen_width // 2
        self.y = screen_height // 2
        self.width = 20
        self.height = 20
        self.head = None
        self.speed = 20
        self.direction = None
        self.body = deque()
        self.segment = deque()
        self.head_color = pg.Color(220, 20, 60)
        self.body_color = pg.Color(57, 255, 20)
        self.outline_color = pg.Color(0, 0, 0)

        # Initialize the snake with a single segment (the head)
        self.body.appendleft([self.x, self.y])
        self.segment.appendleft(pg.Rect(self.x, self.y, self.width, self.height))

    # Draws the snake's head and body segments on the screen
    def draw_snake(self, surface):

        if len(self.body) > 0:
            for unit in self.segment:
                pg.draw.rect(surface, self.body_color, unit)
                pg.draw.rect(surface, self.outline_color, unit, 1)
        self.head = pg.Rect(self.x, self.y, self.width, self.height)
        pg.draw.rect(surface, self.head_color, self.head)
        pg.draw.rect(surface, self.outline_color, self.head, 1)

    # Adds a segment to the snake if a collision between the head and fruit occurs
    def snake_size(self):

        if len(self.body) != 0:
            index = len(self.body) - 1
            x = self.body[index][0]
            y = self.body[index][1]
            self.body.append([x, y])
            self.segment.append(pg.Rect(x, y, self.width, self.height))

    # Ends the game in the case where the snake collides with the boundaries or the head collides with a body segment
    def boundary_collision(self):

        # If the head of the snake collides with a body segment the function returns True
        # The head collides with the first 2 body segments, count prevents it from registering as a collision
        count = 0
        for part in self.segment:
            if self.head.colliderect(part) and count > 2:
                return True
            count += 1

        # Checks if the head of the snake lies outside of the boundaries of the window
        if self.y < 0 or self.y + self.height > screen_height or self.x < 0 or self.x + self.width > screen_width:
            return True

        return False

    # Allows the snake to move and follow the coordinates of the hamiltonian cycle
    def movement(self):

        if self.direction == 'up':
            self.y -= self.speed
        elif self.direction == 'down':
            self.y += self.speed
        elif self.direction == 'right':
            self.x += self.speed
        elif self.direction == 'left':
            self.x -= self.speed

        # Ensure the snake's head does not move out of bounds
        self.x = max(0, min(self.x, screen_width - self.width))
        self.y = max(0, min(self.y, screen_height - self.height))

        # Movement is simulated by removing the tail block and adding a block that overlaps with the snake head
        if len(self.body) > 0:
            self.body.pop()
            self.segment.pop()
        self.body.appendleft([self.x, self.y])
        self.segment.appendleft(pg.Rect(self.x, self.y, self.width, self.height))

    # Changes the orientation of movement
    # A snake moving in one direction cannot move in the opposite direction as it would collide with its body
    def change_direction(self, direction):

        if direction == 'up' and self.direction != 'down':
            self.direction = 'up'
        if direction == 'down' and self.direction != 'up':
            self.direction = 'down'
        if direction == 'right' and self.direction != 'left':
            self.direction = 'right'
        if direction == 'left' and self.direction != 'right':
            self.direction = 'left'

    # Checks whether a new fruit position conflicts with a body segment of the snake
    def empty_space(self, x_coordinate, y_coordinate):

        if [x_coordinate, y_coordinate] not in self.body:
            return True
        else:
            return False
        
    # Returns the length of the snake
    def length(self):
        return len(self.body) + 1  # +1 for the head


# Controls the graphics
# Controls the movement of the snake to follow the hamiltonian cycle
def gameplay(fruit, snake, cycle):

    # Identifies the starting position of the snake
    position = (int(snake.x / snake.width), int(snake.y / snake.height))

    # Identifies the position in the hamiltonian cycle at which the snake begins
    try:
        index = cycle.index(position)
    except ValueError:
        print(f"Initial position {position} not found in the Hamiltonian cycle.")
        pg.quit()
        sys.exit()

    length = len(cycle)
    run = True

    # Loop simulates the movement of the snake and controls game mechanics
    while run:

        # Controls the frame rate of the graphics to make movement smooth and modify the speed of the simulation
        clock = pg.time.Clock()
        clock.tick(45)

        # If the user clicks the exit button the program closes
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        # Movement is simulated by making screen black and redrawing the snake and fruit
        window.fill(pg.Color(0, 0, 0))
        fruit.draw_fruit(window)
        snake.draw_snake(window)

        # --- Shortcut Logic Start ---
        # Determine whether to take a shortcut based on snake's length
        snake_len = snake.length()
        max_length = (screen_width // snake.width) * (screen_height // snake.height)
        shortcut_probability = max(0, (max_length - snake_len) / max_length)

        # Decide whether to attempt a shortcut
        take_shortcut = False
        path = None
        if randint(0, 100) < shortcut_probability * 100:
            # Attempt to find a safe path to the fruit
            path = find_shortest_safe_path(snake, fruit)
            if path:
                take_shortcut = True

        if take_shortcut and path and len(path) > 1:
            # Follow the path towards the fruit
            next_cell = path[1]  # path[0] is the current position
            direction = get_direction(snake, next_cell)
            snake.change_direction(direction)
            position = next_cell
        else:
            # Follow the Hamiltonian cycle
            if index + 1 < length:
                next_pos = cycle[index + 1]
            else:
                next_pos = cycle[0]
                index = -1  # Will be incremented to 0

            direction = get_direction_from_positions(position, next_pos)
            if direction:
                snake.change_direction(direction)
            position = next_pos
            index += 1
        # --- Shortcut Logic End ---

        # Changes the coordinates of the snake's position
        snake.movement()

        # --- Reordered Collision Checks ---
        # First, check for fruit collision
        if fruit.fruit_collision(snake.head):
            # A new fruit is generated and the size of the snake is increased by 1
            if len(snake.body) < length:
                fruit.fruit_position(snake)
                snake.snake_size()
            else:
                # Once the snake fills up the entire grid there are no more positions for the fruit
                # The game ends and closes
                time.sleep(3)
                pg.quit()
                sys.exit()
        # Only check for boundary collision if no fruit collision occurred
        elif snake.boundary_collision():
            # Ends the game if the snake collides with itself or the boundaries
            time.sleep(3)
            pg.quit()
            sys.exit()
        # --------------------------------

        # Draws all elements on the window
        pg.display.update()

def get_direction(snake, next_cell):
    current_x = int(snake.x / snake.width)
    current_y = int(snake.y / snake.height)
    next_x, next_y = next_cell

    if next_x == current_x + 1:
        return 'right'
    elif next_x == current_x - 1:
        return 'left'
    elif next_y == current_y + 1:
        return 'down'
    elif next_y == current_y - 1:
        return 'up'
    else:
        return snake.direction  # No change


def get_direction_from_positions(current_pos, next_pos):
    current_x, current_y = current_pos
    next_x, next_y = next_pos

    if next_x == current_x + 1:
        return 'right'
    elif next_x == current_x - 1:
        return 'left'
    elif next_y == current_y + 1:
        return 'down'
    elif next_y == current_y - 1:
        return 'up'
    else:
        return None  # Should not happen


def find_shortest_safe_path(snake, fruit):
    from collections import deque

    grid_width = screen_width // snake.width
    grid_height = screen_height // snake.height

    # Initialize the grid
    grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]

    # Mark snake's body on the grid
    for segment in snake.body:
        x = segment[0] // snake.width
        y = segment[1] // snake.height
        if 0 <= x < grid_width and 0 <= y < grid_height:
            grid[y][x] = 1  # 1 represents snake's body
        else:
            print(f"Warning: Snake segment out of bounds at ({x}, {y})")

    # BFS to find the shortest path
    start = (snake.x // snake.width, snake.y // snake.height)
    end = (fruit.x // fruit.width, fruit.y // fruit.height)

    # Validate start and end positions
    if not (0 <= start[0] < grid_width and 0 <= start[1] < grid_height):
        print(f"Error: Snake's start position {start} is out of bounds.")
        return None
    if not (0 <= end[0] < grid_width and 0 <= end[1] < grid_height):
        print(f"Error: Fruit's end position {end} is out of bounds.")
        return None

    queue = deque()
    queue.append((start, [start]))
    visited = set()
    visited.add(start)

    while queue:
        current_pos, path = queue.popleft()
        if current_pos == end:
            # Found a path
            return path
        neighbors = get_neighbors(current_pos, grid_width, grid_height)
        for neighbor in neighbors:
            x, y = neighbor
            if (0 <= x < grid_width) and (0 <= y < grid_height):
                if grid[y][x] == 0 and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

    # No path found
    return None


def get_neighbors(pos, grid_width, grid_height):
    x, y = pos
    neighbors = []
    if x > 0:
        neighbors.append((x - 1, y))
    if x < grid_width - 1:
        neighbors.append((x + 1, y))
    if y > 0:
        neighbors.append((x, y - 1))
    if y < grid_height - 1:
        neighbors.append((x, y + 1))
    return neighbors


# Uses prim's algorithm to generate a randomized maze using randomized edge weights
def prim_maze_generator(grid_rows, grid_columns):

    directions = dict()
    vertices = grid_rows * grid_columns

    # Creates keys for the directions dictionary
    # Note that the maze has half the width and length of the grid for the hamiltonian cycle
    for i in range(grid_rows):
        for j in range(grid_columns):
            directions[j, i] = []

    # The initial cell for maze generation is chosen randomly
    x = randint(0, grid_columns - 1)
    y = randint(0, grid_rows - 1)
    initial_cell = (x, y)

    current_cell = initial_cell

    # Stores all cells that have been visited
    visited = [initial_cell]

    # Contains all neighbouring cells to cells that have been visited
    adjacent_cells = set()

    # Generates walls in grid randomly to create a randomized maze
    while len(visited) != vertices:

        # Stores the position of the current cell in the grid
        x_position = current_cell[0]
        y_position = current_cell[1]

        # Finds adjacent cells when the current cell does not lie on the edge of the grid
        if x_position != 0 and y_position != 0 and x_position != grid_columns - 1 and y_position != grid_rows - 1:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position, y_position + 1))
            adjacent_cells.add((x_position - 1, y_position))
            adjacent_cells.add((x_position + 1, y_position))

        # Finds adjacent cells when the current cell lies in the left top corner of the grid
        elif x_position == 0 and y_position == 0:
            adjacent_cells.add((x_position + 1, y_position))
            adjacent_cells.add((x_position, y_position + 1))

        # Finds adjacent cells when the current cell lies in the bottom left corner of the grid
        elif x_position == 0 and y_position == grid_rows - 1:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position + 1, y_position))

        # Finds adjacent cells when the current cell lies in the left column of the grid
        elif x_position == 0:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position, y_position + 1))
            adjacent_cells.add((x_position + 1, y_position))

        # Finds adjacent cells when the current cell lies in the top right corner of the grid
        elif x_position == grid_columns - 1 and y_position == 0:
            adjacent_cells.add((x_position, y_position + 1))
            adjacent_cells.add((x_position - 1, y_position))

        # Finds adjacent cells when the current cell lies in the bottom right corner of the grid
        elif x_position == grid_columns - 1 and y_position == grid_rows - 1:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position - 1, y_position))

        # Finds adjacent cells when the current cell lies in the right column of the grid
        elif x_position == grid_columns - 1:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position, y_position + 1))
            adjacent_cells.add((x_position - 1, y_position))

        # Finds adjacent cells when the current cell lies in the top row of the grid
        elif y_position == 0:
            adjacent_cells.add((x_position, y_position + 1))
            adjacent_cells.add((x_position - 1, y_position))
            adjacent_cells.add((x_position + 1, y_position))

        # Finds adjacent cells when the current cell lies in the bottom row of the grid
        else:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position + 1, y_position))
            adjacent_cells.add((x_position - 1, y_position))

        # Generates a wall between two cells in the grid
        while current_cell:

            current_cell = (adjacent_cells.pop())

            # The neighbouring cell is disregarded if it is already a wall in the maze
            if current_cell not in visited:

                # The neighbouring cell is now classified as having been visited
                visited.append(current_cell)
                x = current_cell[0]
                y = current_cell[1]

                # To generate a wall, a cell adjacent to the current cell must already have been visited
                # The direction of the wall between cells is stored
                # The process is simplified by only considering a wall to be to the right or down
                if (x + 1, y) in visited:
                    directions[x, y] += ['right']
                elif (x - 1, y) in visited:
                    directions[x-1, y] += ['right']
                elif (x, y + 1) in visited:
                    directions[x, y] += ['down']
                elif (x, y - 1) in visited:
                    directions[x, y-1] += ['down']

                break

    # Provides the hamiltonian cycle generating algorithm with the direction of the walls to avoid
    return hamiltonian_cycle(grid_rows, grid_columns, directions)


# Finds a hamiltonian cycle for the snake to follow to prevent collisions with its body segments
# Note that the grid for the hamiltonian cycle is double the width and height of the grid for the maze
def hamiltonian_cycle(grid_rows, grid_columns, orientation):

    # The path for the snake is stored in a dictionary
    # The keys are the (x, y) positions in the grid
    # The values are the adjacent (x, y) positions that the snake can travel towards
    hamiltonian_graph = dict()

    # Uses the coordinates of the walls to generate available adjacent cells for each cell
    # Simplified by only considering the right and down directions
    for i in range(grid_rows):
        for j in range(grid_columns):

            # Finds available adjacent cells if current cell does not lie on an edge of the grid
            if j != grid_columns - 1 and i != grid_rows - 1 and j != 0 and i != 0:
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    if (j*2 + 1, i*2 + 1) in hamiltonian_graph:
                        hamiltonian_graph[j * 2 + 1, i * 2 + 1] += [(j * 2 + 1, i * 2 + 2)]
                    else:
                        hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 1, i*2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                if 'right' not in orientation[j-1, i]:
                    if (j*2, i*2) in hamiltonian_graph:
                        hamiltonian_graph[j * 2, i * 2] += [(j * 2, i * 2 + 1)]
                    else:
                        hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the bottom right corner
            elif j == grid_columns - 1 and i == grid_rows - 1:
                hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                elif 'right' not in orientation[j-1, i]:
                    hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the top right corner
            elif j == grid_columns - 1 and i == 0:
                hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 1, i*2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'right' not in orientation[j-1, i]:
                    hamiltonian_graph[j*2, i*2] += [(j*2, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the right column
            elif j == grid_columns - 1:
                hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 1, i*2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                if 'right' not in orientation[j-1, i]:
                    if (j*2, i*2) in hamiltonian_graph:
                        hamiltonian_graph[j * 2, i * 2] += [(j * 2, i * 2 + 1)]
                    else:
                        hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the top left corner
            elif j == 0 and i == 0:
                hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                hamiltonian_graph[j*2, i*2] += [(j*2, i*2 + 1)]
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    if (j*2 + 1, i*2 + 1) in hamiltonian_graph:
                        hamiltonian_graph[j * 2 + 1, i * 2 + 1] += [(j * 2 + 1, i * 2 + 2)]
                    else:
                        hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 1, i*2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the bottom left corner
            elif j == 0 and i == grid_rows - 1:
                hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)]
                hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j * 2, i * 2] += [(j * 2 + 1, i * 2)]

            # Finds available adjacent cells if current cell is in the left corner
            elif j == 0:
                hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)]
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    if (j*2 + 1, i*2 + 1) in hamiltonian_graph:
                        hamiltonian_graph[j*2 + 1, i*2 + 1] += [(j*2 + 1, i*2 + 2)]
                    else:
                        hamiltonian_graph[j * 2 + 1, i * 2 + 1] = [(j * 2 + 1, i * 2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j*2, i*2] += [(j*2 + 1, i*2)]

            # Finds available adjacent cells if current cell is in the top row
            elif i == 0:
                hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    if (j*2 + 1, i*2 + 1) in hamiltonian_graph:
                        hamiltonian_graph[j * 2 + 1, i * 2 + 1] += [(j * 2 + 1, i * 2 + 2)]
                    else:
                        hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 1, i*2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'right' not in orientation[j-1, i]:
                    hamiltonian_graph[j*2, i*2] += [(j*2, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the bottom row
            else:
                hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                if 'right' not in orientation[j-1, i]:
                    if (j*2, i*2) in hamiltonian_graph:
                        hamiltonian_graph[j*2, i*2] += [(j*2, i*2 + 1)]
                    else:
                        hamiltonian_graph[j * 2, i * 2] = [(j * 2, i * 2 + 1)]

    # Provides the coordinates of available adjacent cells to generate directions for the snake's movement
    return path_generator(hamiltonian_graph, grid_rows*grid_columns*4)


# Generates a path composed of coordinates for the snake to travel along
def path_generator(graph, cells):

    # The starting position for the path is a random cell within the grid
    start_x = randint(0, max(x for x, y in graph.keys()))
    start_y = randint(0, max(y for x, y in graph.keys()))
    path = [(start_x, start_y)]

    previous_cell = path[0]
    previous_direction = None

    # Generates a path that is a hamiltonian cycle by following a set of general laws
    # 1. If the right cell is available, travel to the right
    # 2. If the cell underneath is available, travel down
    # 3. If the left cell is available, travel left
    # 4. If the cell above is available, travel up
    # 5. The current direction cannot oppose the previous direction (e.g. left --> right)
    while len(path) != cells:

        if previous_cell in graph and (previous_cell[0] + 1, previous_cell[1]) in graph[previous_cell] \
                and previous_direction != 'left':
            path.append((previous_cell[0] + 1, previous_cell[1]))
            previous_cell = (previous_cell[0] + 1, previous_cell[1])
            previous_direction = 'right'
        elif previous_cell in graph and (previous_cell[0], previous_cell[1] + 1) in graph[previous_cell]  \
                and previous_direction != 'up':
            path.append((previous_cell[0], previous_cell[1] + 1))
            previous_cell = (previous_cell[0], previous_cell[1] + 1)
            previous_direction = 'down'
        elif (previous_cell[0] - 1, previous_cell[1]) in graph \
                and previous_cell in graph[previous_cell[0] - 1, previous_cell[1]] and previous_direction != 'right':
            path.append((previous_cell[0] - 1, previous_cell[1]))
            previous_cell = (previous_cell[0] - 1, previous_cell[1])
            previous_direction = 'left'
        else:
            path.append((previous_cell[0], previous_cell[1] - 1))
            previous_cell = (previous_cell[0], previous_cell[1] - 1)
            previous_direction = 'up'

    # Returns the coordinates of the hamiltonian cycle path
    return path


circuit = prim_maze_generator(int(screen_height/40), int(screen_width/40))
pg.init()
window = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption('Snake Solver')
fruit = Fruit()
snake = Snake()
gameplay(fruit, snake, circuit)
