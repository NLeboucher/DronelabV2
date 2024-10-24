import pygame
from pygame.math import Vector2
from math import sin, cos, pi
import random

# Define constants
WIDTH = 800
HEIGHT = 600
FPS = 60

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Define boid parameters
NUM_BOIDS = 100
BOID_SIZE = 10
BOID_SPEED = 5
BOID_ACCELERATION = 0.1
BOID_MAX_FORCE = 0.5
BOID_PERSONAL_SPACE = 100
BOID_AVOIDANCE_DISTANCE = 50

# Create boid objects
boids = []
for i in range(NUM_BOIDS):
    boid = {
        'position': (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
        'velocity': (random.uniform(-BOID_SPEED, BOID_SPEED), random.uniform(-BOID_SPEED, BOID_SPEED)),
        'acceleration': (0, 0),
        'size': BOID_SIZE,
        'color': WHITE
    }
    boids.append(boid)

# Define obstacles
obstacles = []
for i in range(10):
    obstacle = {
        'position': (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
        'size': 50,
        'color': BLACK
    }
    obstacles.append(obstacle)

def update_boids():
    for boid in boids:
        # Calculate acceleration based on nearby boids
        acceleration = Vector2(0, 0)
        for other_boid in boids:
            if other_boid != boid:
                distance = get_distance(boid['position'], other_boid['position'])
                if distance < BOID_PERSONAL_SPACE:
                    acceleration += get_repulsion_force(boid, other_boid)
                elif distance < BOID_AVOIDANCE_DISTANCE:
                    acceleration += get_avoidance_force(boid, other_boid)
        # Update velocity and position
        boid['velocity'] += acceleration * BOID_ACCELERATION
        boid['position'] += boid['velocity']
        # Check for collisions with obstacles
        for obstacle in obstacles:
            if get_distance(boid['position'], obstacle['position']) < obstacle['size'] / 2 + boid['size'] / 2:
                boid['velocity'] = -boid['velocity']
                break

def draw_boids():
    for boid in boids:
        pygame.draw.circle(screen, boid['color'], boid['position'], boid['size'])

def get_distance(pos1, pos2):
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

def get_repulsion_force(boid1, boid2):
    distance = get_distance(boid1['position'], boid2['position'])
    if distance < BOID_PERSONAL_SPACE:
        force = Vector2(boid1['position'] - boid2['position'])
        force.normalize()
        force *= BOID_REPULSION_STRENGTH
        return force
    else:
        return Vector2(0, 0)

def get_avoidance_force(boid1, boid2):
    distance = get_distance(boid1['position'], boid2['position'])
    force = (boid1['position'] - boid2['position']) / distance ** 2
    return force

while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update boids
    update_boids()

    # Draw boids
    screen.fill(BLACK)
    draw_boids()
    pygame.display.flip()
    clock.tick(FPS)