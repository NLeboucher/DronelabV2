import pyrealsense2 as rs

# Initialize the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

try:
    # Start the RealSense pipeline
    pipeline.start(config)

    while True:
        # Wait for a frame from the RealSense camera
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()

        if not depth_frame:
            continue

        # Choose a pixel location (e.g., the center of the frame)
        width = depth_frame.get_width()
        height = depth_frame.get_height()
        pixel_x = width // 2
        pixel_y = height // 2

        # Retrieve the depth value at the chosen pixel
        depth_value = depth_frame.get_distance(pixel_x, pixel_y)

        print(f"Depth value at pixel ({pixel_x}, {pixel_y}): {depth_value:.2f} meters")

except KeyboardInterrupt:
    pass

finally:
    # Stop the RealSense pipeline
    pipeline.stop()
