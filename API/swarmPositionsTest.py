import mainD
from tqdm import tqdm
import asyncio
import matplotlib.pyplot as plt
from collections import namedtuple

# Assuming mainD.GetEstimatedPositions() updates a global or returned structure

# Lists to store position data
x_values = []
y_values = []
z_values = []
yaw_values = []
# In your mainD module

# Assuming SwarmPosition is a class defined to hold the position data
SwarmPosition = namedtuple('SwarmPosition', 'x y z yaw')
# Gathering data
for a in tqdm(range(10000)):
    # Run the async position getter
    asyncio.run(mainD.AltGetEstimatedPositions())
    pos = mainD.s.positions
    print(pos)
    if len(pos) == 0:
        print("No drones found")
    first_uri = next(iter(pos))  # Gets the first key in the dictionary
    first_position = pos[first_uri]
    print(first_position)
    x, y, z, yaw = first_position
    x_values.append(x)
    y_values.append(y)
    z_values.append(z)
    yaw_values.append(yaw)

# Plotting
plt.figure(figsize=(12, 8))

# Plotting each coordinate in a subplot
plt.subplot(2, 2, 1)
plt.plot(x_values, label='X Coordinate')
plt.title('X Coordinate Over Time')
plt.xlabel('Time')
plt.ylabel('X')

plt.subplot(2, 2, 2)
plt.plot(y_values, label='Y Coordinate')
plt.title('Y Coordinate Over Time')
plt.xlabel('Time')
plt.ylabel('Y')

plt.subplot(2, 2, 3)
plt.plot(z_values, label='Z Coordinate')
plt.title('Z Coordinate Over Time')
plt.xlabel('Time')
plt.ylabel('Z')

plt.subplot(2, 2, 4)
plt.plot(yaw_values, label='Yaw')
plt.title('Yaw Over Time')
plt.xlabel('Time')
plt.ylabel('Yaw')

plt.tight_layout()
plt.show()
