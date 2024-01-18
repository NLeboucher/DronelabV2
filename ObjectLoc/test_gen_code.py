import pyrealsense2 as rs
import numpy as np
import cv2
import open3d as o3d

# Chessboard parameters
chessboard_size = (3, 4)  # Number of inner corners per a chessboard row and column
square_size = 0.025  # Size of a chessboard square in meters

# Configure RealSense camera
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start the pipeline
profile = pipeline.start(config)

# Get camera intrinsics from the profile
intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
camera_matrix = np.array([[intr.fx, 0, intr.ppx],
                          [0, intr.fy, intr.ppy],
                          [0, 0, 1]])
dist_coeffs = np.array(intr.coeffs)

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Find chessboard corners
        ret, corners = cv2.findChessboardCorners(color_image, chessboard_size, None)
        if ret:
            # Calculate camera pose
            objp = np.zeros((np.prod(chessboard_size), 3), np.float32)
            objp[:, :2] = np.mgrid[0:chessboard_size[1], 0:chessboard_size[0]].T.reshape(-1, 2)
            objp *= square_size

            # SolvePnP
            ret, rvecs, tvecs = cv2.solvePnP(objp, corners, camera_matrix, dist_coeffs)

            # Convert to transformation matrix
            R, _ = cv2.Rodrigues(rvecs)
            T = np.hstack((R, tvecs))
            T = np.vstack((T, [0, 0, 0, 1]))  # Homogeneous transformation matrix

            # Create point cloud from depth data
            pc = rs.pointcloud()
            points = pc.calculate(depth_frame)
            vtx = np.asanyarray(points.get_vertices())

            vtx = np.asanyarray(vtx).view(np.float32).reshape(-1, 3)

            # Transform point cloud to world coordinates
            vtx_transformed = (np.linalg.inv(T) @ np.hstack((vtx, np.ones((vtx.shape[0], 1)))).T).T[:, :3]

            # Visualize
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(vtx_transformed)
            # Create visualizer object
            vis = o3d.visualization.Visualizer()
            vis.create_window()

            # Add point cloud to the visualizer
            vis.add_geometry(pcd)

            # Add axis to the visualizer
            vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1))

            # Visualize
            vis.run()
            vis.destroy_window()

finally:
    pipeline.stop()
