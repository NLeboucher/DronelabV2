import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Boid:
    def __init__(self, position, velocity, perception_radius=3, max_speed=0.1, max_force=0.01):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.perception_radius = perception_radius
        self.max_speed = max_speed
        self.max_force = max_force

    def cohesion(self, boids):
        perceived_center = np.mean([boid.position for boid in boids], axis=0)
        desired_velocity = (perceived_center - self.position) * 0.01
        return self.steer(desired_velocity)

    def separation(self, boids):
        steering = np.zeros(3)
        total = 0
        for other in boids:
            if other != self:
                distance = np.linalg.norm(self.position - other.position)
                if 0 < distance < self.perception_radius:
                    diff = self.position - other.position
                    diff /= distance
                    steering += diff
                    total += 1
        if total > 0:
            steering /= total
        if np.linalg.norm(steering) > 0:
            steering = self.max_speed * steering / np.linalg.norm(steering)
        return steering

    def alignment(self, boids):
        perceived_velocity = np.mean([boid.velocity for boid in boids], axis=0)
        return self.steer(perceived_velocity)

    def repulsion(self, obstacle_position, repulsion_radius=5, repulsion_force=0.5):
        desired_velocity = self.position - obstacle_position
        distance = np.linalg.norm(desired_velocity)
        if distance < repulsion_radius:
            desired_velocity = (desired_velocity / distance) * repulsion_force
        else:
            desired_velocity = np.zeros(3)
        return self.steer(desired_velocity)

    def steer(self, desired):
        steer = desired - self.velocity
        if np.linalg.norm(steer) > self.max_force:
            steer = self.max_force * steer / np.linalg.norm(steer)
        return steer

    def update(self, boids, obstacle_position):
        cohesion = self.cohesion(boids)
        separation = self.separation(boids)
        alignment = self.alignment(boids)
        repulsion = self.repulsion(obstacle_position)
        self.velocity += (cohesion + separation + alignment + repulsion)
        if np.linalg.norm(self.velocity) > self.max_speed:
            self.velocity = self.max_speed * self.velocity / np.linalg.norm(self.velocity)
        self.position += self.velocity

def update_boids(boids, obstacle_position):
    for boid in boids:
        boid.update(boids, obstacle_position)

def init():
    ax.set_xlim3d([-50, 50])
    ax.set_xlabel('X')

    ax.set_ylim3d([-50, 50])
    ax.set_ylabel('Y')

    ax.set_zlim3d([-50, 50])
    ax.set_zlabel('Z')

    ax.set_title('3D Boids Simulation')
    return points,

def animate(frame):
    update_boids(boids, obstacle_position)
    for i, boid in enumerate(boids):
        points._offsets3d = ([boid.position[0]], [boid.position[1]], [boid.position[2]])
    return points,

# Initializations
num_boids = 50
boids = [Boid(np.random.rand(3) * 100 - 50, np.random.rand(3) - 0.5) for _ in range(num_boids)]
obstacle_position = np.array([10, 10, 10])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
points = ax.scatter([], [], [])

ani = FuncAnimation(fig, animate, frames=200, init_func=init, blit=True)

plt.show()
