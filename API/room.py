
import os, sys
import uvicorn
path = os.getcwd()
folders = path.split("/")
if("DronelabV2" in folders):
    path = "/".join(folders[:folders.index("DronelabV2")+1])
    sys.path.insert(0, path)
    from API.logger import Logger
else:
    Exception("Executed from Wrong folder, you need to be in DronelabV2")
logger = Logger("log.txt")
from scipy.spatial import ConvexHull, Delaunay
import pygame as pg

class Room:
    rooms = {"DroneLab": [[4.0,-7.0,0.0],[-0.15,-7,0.0],[-11.0,11.0,0.0],[-4.0,11.0,1.0],[4.0,8.0,0.0],[4,-7.0,1.5],[-0.15,-7.0,1.5],[-11.0,11.0,1.5],[-4.0,11.0,1.5],[4.0,8.0,1.5]],
             "Stairs":[(3.5, 3.5, 0), (-1.5, 3.5, 0), (-1.5, 0.5, 0), (3.5, 0.5, 0), (3.5, 3.5, 2.5), (-1.5, 3.5, 2.5), (-1.5, 0.5, 2.5), (3.5, 0.5, 2.5)]}
    def __init__(self, points=None):
        self.points = Room.rooms["DroneLab"]
        self.is_3d_object = self._check_3d_object()

    def _check_3d_object(self):
        # Check if there are at least four points (minimum for a 3D object)
        if len(self.points) < 4:
            return False

        # Check if all points have three coordinates
        if any(len(point) != 3 for point in self.points):
            return False

        # Check if there are at least four unique points
        unique_points = set(tuple(point) for point in self.points)
        if len(unique_points) < 4:
            return False

        # Check if the points form a valid convex hull
        try:
            self.convex_hull = Delaunay(self.points)
            return True
        except Exception as e:
            # Handle exceptions (e.g., if scipy is not installed or ConvexHull fails)
            print(f"Error: {e}")
            return False

    def is_point_inside(self, point):
        if not self.is_3d_object:
            raise ValueError("room is not a 3d Object.")
        # Check if the point is inside the convex hull
        if not hasattr(self, 'convex_hull'):
            raise ValueError("Convex hull not computed. Call check_3d_object method first.")
        if len(point) != 3:
            point = pg.Vector3(point[0], point[1], 0.0)
        ret = self.convex_hull.find_simplex(point)
        return ret >= 0