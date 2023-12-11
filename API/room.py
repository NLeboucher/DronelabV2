import os
path = os.getcwd()
path = path.split("/")[::-1][0]
print(path)
if(path == "API"):
    from logger import Logger
else:
    from API.logger import Logger
logger = Logger("log.txt")
from scipy.spatial import ConvexHull, Delaunay

class Room:
    def __init__(self, points):
        self.points = points
        self.is_3d_object = self.check_3d_object()

    def check_3d_object(self):
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
        # Check if the point is inside the convex hull
        if not hasattr(self, 'convex_hull'):
            raise ValueError("Convex hull not computed. Call check_3d_object method first.")
        ret = self.convex_hull.find_simplex(point)
        print(ret)
        return ret >= 0