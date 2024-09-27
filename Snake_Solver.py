import pygame as pg
import sys
from random import randint
import time
import os
from collections import deque, Counter
import tkinter as tk
from tkinter import ttk
import threading
import psutil
import heapq


# Used to modify the window size, values must be a multiple of 40
screen_width = 800
screen_height = 600

# Controls where the window appears on the screen
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)

# Initialize Tkinter
root = tk.Tk()
root.title("Control Panel")
root.geometry("500x150+810+30")  # Set size and position beside the Pygame window

# Speed control variable
speed_var = tk.IntVar(value=15)

# Speed control slider
speed_label = ttk.Label(root, text="Speed:")
speed_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
speed_slider = ttk.Scale(root, from_=1, to=60, variable=speed_var, orient=tk.HORIZONTAL)
speed_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
speed_value_label = ttk.Label(root, text="15")
speed_value_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

# Debugging mode variable
debug_mode_var = tk.BooleanVar(value=False)
show_paths_var = tk.BooleanVar(value=False)

# Add checkbox to control panel
show_paths_checkbox = ttk.Checkbutton(root, text="Show Paths", variable=show_paths_var)
show_paths_checkbox.grid(row=1, column=3, padx=5, pady=5, sticky="w")

# Debugging mode button
def toggle_debug_mode():
    debug_mode_var.set(not debug_mode_var.get())
    debug_button.config(text="Disable Debug" if debug_mode_var.get() else "Enable Debug")

debug_button = ttk.Button(root, text="Enable Debug", command=toggle_debug_mode)
debug_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

# Show/Hide Hamiltonian cycle variable
show_cycle_var = tk.BooleanVar(value=True)

# Show/Hide Hamiltonian cycle button
def toggle_cycle():
    show_cycle_var.set(not show_cycle_var.get())
    toggle_button.config(text="Hide Cycle" if show_cycle_var.get() else "Show Cycle")

toggle_button = ttk.Button(root, text="Hide Cycle", command=toggle_cycle)
toggle_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

stop_game = threading.Event()

# Close button
def close_program():
    stop_game.set()
    root.quit()  # Use root.quit() instead of root.destroy() to ensure the main loop exits

close_button = ttk.Button(root, text="Close", command=close_program)
close_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

# Performance monitoring labels
cpu_label = ttk.Label(root, text="CPU Usage: 0%")
cpu_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
memory_label = ttk.Label(root, text="Memory Usage: 0%")
memory_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")

# Function to update performance metrics
def update_performance_metrics():
    while not stop_game.is_set():
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent

        # Update the labels in the Tkinter main thread
        root.after(0, lambda: cpu_label.config(text=f"CPU Usage: {cpu_usage}%"))
        root.after(0, lambda: memory_label.config(text=f"Memory Usage: {memory_usage}%"))

        # Sleep for a few seconds before the next update
        time.sleep(5)

# Start the performance monitoring in a separate thread
performance_thread = threading.Thread(target=update_performance_metrics)
performance_thread.daemon = True
performance_thread.start()

# Update the speed value display as the slider is moved
def update_speed_label(event):
    speed_value_label.config(text=str(speed_var.get()))

speed_slider.bind("<Motion>", update_speed_label)

# Flag to indicate when to stop the Pygame loop
stop_game = threading.Event()

# Function to update speed
def update_speed():
    try:
        speed = int(speed_slider.get())
        if speed < 1:
            speed = 1
        speed_var.set(speed)
    except ValueError:
        pass

speed_slider.bind("<Return>", lambda event: update_speed())

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
        # Update the head position
        self.head = pg.Rect(self.x, self.y, self.width, self.height)
        pg.draw.rect(surface, self.head_color, self.head)
        pg.draw.rect(surface, self.outline_color, self.head, 1)
        
        # Draw the body segments
        if len(self.body) > 1:
            for unit in list(self.segment)[1:]:  # Skip the head
                pg.draw.rect(surface, self.body_color, unit)
                pg.draw.rect(surface, self.outline_color, unit, 1)

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
        elif direction == 'down' and self.direction != 'up':
            self.direction = 'down'
        elif direction == 'right' and self.direction != 'left':
            self.direction = 'right'
        elif direction == 'left' and self.direction != 'right':
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
    position = (snake.x // snake.width, snake.y // snake.height)

    snake_length = len(snake.body)
    grid_size = (screen_width // snake.width) * (screen_height // snake.height)
    max_corner_cuts = 3  # Maximum allowed deviations from the cycle
    max_depth = 100  # Maximum search depth for pathfinding

    simulated_paths = []  # Store paths for debugging

    # Identifies the position in the Hamiltonian cycle at which the snake begins
    try:
        index = cycle.index(position)
    except ValueError:
        print(f"Initial position {position} not found in the Hamiltonian cycle.")
        pg.quit()
        return

    length = len(cycle)
    run = True

    while run and not stop_game.is_set():
        try:
            # Control frame rate
            clock = pg.time.Clock()
            clock.tick(speed_var.get())

            # Handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    stop_game.set()
                    pg.quit()
                    return

            # Draw elements
            window.fill(pg.Color(0, 0, 0))
            if show_cycle_var.get():
                draw_hamiltonian_cycle(window, cycle, snake)
            fruit.draw_fruit(window)
            snake.draw_snake(window)

            # Update position calculation
            position = (snake.x // snake.width, snake.y // snake.height)
            
            # Try to find a safe shortcut path to the fruit
            path_to_fruit = find_shortest_safe_path(snake, fruit, cycle, max_corner_cuts=max_corner_cuts, max_depth=max_depth)

            if path_to_fruit and len(path_to_fruit) > 1:
                is_safe = is_safe_shortcut(snake, path_to_fruit, cycle, fruit)
                if is_safe:
                    # Take the shortcut
                    if debug_mode_var.get() and show_paths_var.get():
                        simulated_paths.clear()
                        simulated_paths.append(path_to_fruit)  # Store the path for debugging

                    for next_pos in path_to_fruit[1:]:  # Exclude the current position
                        # Convert grid coordinates to pixel positions
                        snake.x = next_pos[0] * snake.width
                        snake.y = next_pos[1] * snake.height
                        position = next_pos  # Update the current position

                        # Update the snake's body
                        snake.body.pop()
                        snake.segment.pop()
                        snake.body.appendleft([snake.x, snake.y])
                        snake.segment.appendleft(pg.Rect(snake.x, snake.y, snake.width, snake.height))

                        # Update the head
                        snake.head = pg.Rect(snake.x, snake.y, snake.width, snake.height)

                        # Check for fruit collision at each step
                        if fruit.fruit_collision(snake.head):
                            if len(snake.body) < length:
                                fruit.fruit_position(snake)
                                snake.snake_size()
                                # Update the snake's length and max_corner_cuts
                                snake_length = len(snake.body)
                                grid_size = (screen_width // snake.width) * (screen_height // snake.height)
                                max_corner_cuts = min(3, grid_size // (snake_length + 1))
                            else:
                                time.sleep(3)
                                stop_game.set()
                                pg.quit()
                                return

                        # Check for boundary collision
                        if snake.boundary_collision():
                            time.sleep(3)
                            stop_game.set()
                            pg.quit()
                            return

                        # Draw elements
                        window.fill(pg.Color(0, 0, 0))
                        if show_cycle_var.get():
                            draw_hamiltonian_cycle(window, cycle, snake)
                        fruit.draw_fruit(window)
                        snake.draw_snake(window)

                        if debug_mode_var.get() and show_paths_var.get():
                            draw_simulated_paths(window, simulated_paths, snake)

                        pg.display.update()
                        clock.tick(speed_var.get())

                    # Rejoin the cycle
                    try:
                        index = cycle.index(position)
                    except ValueError:
                        print(f"Position after shortcut {position} not found in the Hamiltonian cycle.")
                        stop_game.set()
                        pg.quit()
                        return

                    index += 1
                    # Clear the simulated paths after the shortcut is completed
                    simulated_paths.clear()
                    continue  # Proceed with the next iteration

            # Follow the Hamiltonian cycle by default
            if index + 1 < length:
                next_pos = cycle[index + 1]
            else:
                next_pos = cycle[0]
                index = -1  # Will be incremented to 0

            direction = get_direction_from_positions(position, next_pos, snake.direction)

            # Move along the cycle
            if direction:
                snake.change_direction(direction)
            position = next_pos
            index += 1

            # Move the snake
            snake.movement()

            # Check for fruit collision
            if fruit.fruit_collision(snake.head):
                if len(snake.body) < length:
                    fruit.fruit_position(snake)
                    snake.snake_size()
                    # Update the snake's length and max_corner_cuts
                    snake_length = len(snake.body)
                    grid_size = (screen_width // snake.width) * (screen_height // snake.height)
                    max_corner_cuts = min(3, grid_size // (snake_length + 1))
                else:
                    time.sleep(3)
                    stop_game.set()
                    pg.quit()
                    return

            # Check for boundary collision
            if snake.boundary_collision():
                time.sleep(3)
                stop_game.set()
                pg.quit()
                return

            # Draw simulated paths if debugging mode and show paths are enabled
            if debug_mode_var.get() and show_paths_var.get():
                draw_simulated_paths(window, simulated_paths, snake)

            # Update display
            pg.display.update()

            # Clear simulated paths when not taking a shortcut
            simulated_paths.clear()

        except Exception as e:
            print(f"An error occurred: {e}")
            stop_game.set()
            pg.quit()
            return



def draw_simulated_paths(surface, paths, snake):
    for path in paths:
        for pos in path:
            x = pos[0] * snake.width
            y = pos[1] * snake.height
            pg.draw.rect(surface, pg.Color(255, 0, 0), (x, y, snake.width, snake.height), 2)  # Red outline for paths

def draw_potential_collisions(surface, collisions, snake):
    for pos in collisions:
        x = pos[0]
        y = pos[1]
        pg.draw.rect(surface, pg.Color(255, 255, 0), (x, y, snake.width, snake.height), 1)  # Yellow outline for collisions

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

def get_direction_from_positions(current_pos, next_pos, current_direction):
    current_x, current_y = current_pos
    next_x, next_y = next_pos

    if next_x == current_x + 1 and next_y == current_y and current_direction != 'left':
        return 'right'
    elif next_x == current_x - 1 and next_y == current_y and current_direction != 'right':
        return 'left'
    elif next_y == current_y + 1 and next_x == current_x and current_direction != 'up':
        return 'down'
    elif next_y == current_y - 1 and next_x == current_x and current_direction != 'down':
        return 'up'
    else:
        return None  # Should not happen if positions are adjacent


def find_shortest_safe_path(snake, fruit, cycle, max_corner_cuts=3, max_depth=100):

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

    start = (snake.x // snake.width, snake.y // snake.height)
    end = (fruit.x // fruit.width, fruit.y // fruit.height)

    # Validate start and end positions
    if not (0 <= start[0] < grid_width and 0 <= start[1] < grid_height):
        print(f"Error: Snake's start position {start} is out of bounds.")
        return None
    if not (0 <= end[0] < grid_width and 0 <= end[1] < grid_height):
        print(f"Error: Fruit's end position {end} is out of bounds.")
        return None

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (0, start, [start], 0))  # (priority, position, path, deviation_count)
    visited = set()
    visited.add((start, 0))  # Include deviation count in visited

    while open_set:
        _, current_pos, path, deviation_count = heapq.heappop(open_set)
        if current_pos == end:
            # Found a path
            return path

        if len(path) > max_depth or deviation_count > max_corner_cuts:
            continue  # Exceeded depth or deviation limit

        neighbors = get_neighbors(current_pos, grid_width, grid_height)
        cycle_neighbors = get_cycle_neighbors(current_pos, cycle)

        for neighbor in neighbors:
            x, y = neighbor
            if (0 <= x < grid_width) and (0 <= y < grid_height):
                if grid[y][x] == 0:
                    new_deviation_count = deviation_count
                    if neighbor not in cycle_neighbors:
                        new_deviation_count += 1
                    if ((neighbor, new_deviation_count) not in visited) and (new_deviation_count <= max_corner_cuts):
                        visited.add((neighbor, new_deviation_count))
                        priority = len(path) + heuristic(neighbor, end)
                        heapq.heappush(open_set, (priority, neighbor, path + [neighbor], new_deviation_count))

    # No path found
    return None

def get_cycle_neighbors(position, cycle):
    try:
        index = cycle.index(position)
    except ValueError:
        return []
    prev_index = (index - 1) % len(cycle)
    next_index = (index + 1) % len(cycle)
    return [cycle[prev_index], cycle[next_index]]



def is_safe_shortcut(snake, path, cycle, fruit):
    """
    Determines if taking the shortcut path is safe.
    Ensures that after following the path, the snake can continue following the cycle without collisions.
    """
    # Copy the snake's body and positions
    simulated_body = deque((pos[0], pos[1]) for pos in snake.body)
    simulated_positions = Counter(simulated_body)
    simulated_length = len(simulated_body)
    will_grow = False

    # Commented out debug prints
    # print(f"Initial simulated body: {simulated_body}")
    # print(f"Initial simulated positions: {simulated_positions}")

    for idx, pos in enumerate(path[1:], 1):  # Skip the current position
        pos_world = (pos[0] * snake.width, pos[1] * snake.height)

        # Check for collision
        if simulated_positions[pos_world] > 0:
            # print(f"Collision detected at {pos_world}")
            return False  # Collision detected

        # Move the head
        simulated_body.appendleft(pos_world)
        simulated_positions[pos_world] += 1

        # Commented out debug prints
        # print(f"Moved head to {pos_world}")
        # print(f"Simulated body: {simulated_body}")
        # print(f"Simulated positions: {simulated_positions}")

        # Check if the snake will eat the fruit at this position
        if pos == (fruit.x // fruit.width, fruit.y // fruit.height):
            will_grow = True

        # Move the tail unless the snake is growing
        if not will_grow:
            tail = simulated_body.pop()
            simulated_positions[tail] -= 1
            if simulated_positions[tail] == 0:
                del simulated_positions[tail]

            # Commented out debug prints
            # print(f"Moved tail from {tail}")
            # print(f"Simulated body after tail move: {simulated_body}")
            # print(f"Simulated positions after tail move: {simulated_positions}")
        else:
            # print("Snake is growing; tail not moved.")
            will_grow = False  # Growth happens only once after eating

    # Update steps_to_simulate based on the new length of the snake
    steps_to_simulate = len(simulated_body)
    # print(f"After shortcut, steps_to_simulate: {steps_to_simulate}")

    # After the shortcut, simulate rejoining the cycle
    new_head = path[-1]
    try:
        cycle_index = cycle.index(new_head)
    except ValueError:
        # print(f"Position {new_head} not found in cycle.")
        return False  # Position not found in cycle

    for _ in range(steps_to_simulate):
        cycle_index = (cycle_index + 1) % len(cycle)
        next_pos = cycle[cycle_index]
        next_pos_world = (next_pos[0] * snake.width, next_pos[1] * snake.height)

        # Check for collision
        if simulated_positions[next_pos_world] > 0:
            # print(f"Collision detected at {next_pos_world} while rejoining cycle")
            return False  # Collision detected

        # Move the head
        simulated_body.appendleft(next_pos_world)
        simulated_positions[next_pos_world] += 1

        # Commented out debug prints
        # print(f"Moved head to {next_pos_world} while rejoining cycle")
        # print(f"Simulated body: {simulated_body}")
        # print(f"Simulated positions: {simulated_positions}")

        # Move the tail unless the snake is growing
        if not will_grow:
            tail = simulated_body.pop()
            simulated_positions[tail] -= 1
            if simulated_positions[tail] == 0:
                del simulated_positions[tail]

            # Commented out debug prints
            # print(f"Moved tail from {tail} while rejoining cycle")
            # print(f"Simulated body after tail move: {simulated_body}")
            # print(f"Simulated positions after tail move: {simulated_positions}")
        else:
            # print("Snake is growing; tail not moved while rejoining cycle.")
            will_grow = False  # Growth happens only once after eating

    # print("Shortcut is safe.")
    return True


def extend_shortcut_until_safe(snake, path, cycle):
    """
    Extends the shortcut path until it's safe to rejoin the cycle.
    """
    max_extension = len(cycle)  # Maximum possible extension
    current_extension = 0

    # Start from the last position in the current path
    last_pos = path[-1]

    while current_extension < max_extension:
        # Move to the next position in the cycle
        try:
            cycle_index = cycle.index(last_pos)
        except ValueError:
            return None  # Cannot find the position in the cycle

        cycle_index = (cycle_index + 1) % len(cycle)
        next_pos = cycle[cycle_index]
        path.append(next_pos)
        current_extension += 1

        # Check if the extended path is safe
        if is_safe_shortcut(snake, path, cycle):
            return path  # Found a safe extended path

        last_pos = next_pos

    # No safe extension found
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

def draw_hamiltonian_cycle(surface, cycle, snake):
    for i in range(len(cycle) - 1):
        start_pos = (cycle[i][0] * snake.width + snake.width // 2, cycle[i][1] * snake.height + snake.height // 2)
        end_pos = (cycle[i + 1][0] * snake.width + snake.width // 2, cycle[i + 1][1] * snake.height + snake.height // 2)
        pg.draw.line(surface, pg.Color(0, 0, 255), start_pos, end_pos, 1)
    # Connect the last point to the first to complete the cycle
    start_pos = (cycle[-1][0] * snake.width + snake.width // 2, cycle[-1][1] * snake.height + snake.height // 2)
    end_pos = (cycle[0][0] * snake.width + snake.width // 2, cycle[0][1] * snake.height + snake.height // 2)
    pg.draw.line(surface, pg.Color(0, 0, 255), start_pos, end_pos, 1)




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

            # Finds available adjacent cells if current cell is in the left column
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
                        hamiltonian_graph[j * 2 + 1, i * 2 + 1] += [(j * 2 + 1, i * 2 + 2)]
                    else:
                        hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 1, i*2 + 2)]
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


def run_pygame():
    circuit = prim_maze_generator(int(screen_height/40), int(screen_width/40))
    pg.init()
    global window
    window = pg.display.set_mode((screen_width, screen_height))
    pg.display.set_caption('Snake Solver')
    fruit = Fruit()
    snake = Snake()
    gameplay(fruit, snake, circuit)

# Run Pygame in a separate thread
pygame_thread = threading.Thread(target=run_pygame)
pygame_thread.daemon = True
pygame_thread.start()

# Run Tkinter main loop in the main thread
root.mainloop()


# circuit = prim_maze_generator(int(screen_height/40), int(screen_width/40))
# pg.init()
# window = pg.display.set_mode((screen_width, screen_height))
# pg.display.set_caption('Snake Solver')
# fruit = Fruit()
# snake = Snake()
# gameplay(fruit, snake, circuit)

# Wait for the Pygame thread to finish
pygame_thread.join()
