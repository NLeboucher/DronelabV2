import pyrealsense2 as rs

# Assuming you have a RealSense device connected and streaming
pipeline = rs.pipeline()
profile = pipeline.start()
device = profile.get_device()

# Access the depth or color stream's intrinsics
depth_stream = profile.get_stream(rs.stream.depth)
depth_intrinsics = depth_stream.as_video_stream_profile().get_intrinsics()

# Check if the distortion model is InverseBrownConrady
if depth_intrinsics.model == rs.distortion.brown_conrady:
    print("Using InverseBrownConrady distortion model")

    # Distortion coefficients
    # They might appear as zero if the distortion is minimal or corrected internally
    distortion_coefficients = depth_intrinsics.coeffs
    print("Distortion Coefficients:", distortion_coefficients)
else:
    print(f"Using no distortion model,{depth_intrinsics.model}, {rs.distortion.inverse_brown_conrady}")
