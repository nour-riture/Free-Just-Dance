import cv2
import mediapipe as mp
import json
import os

VIDEOS = [
    ("videos/dance1.mp4", "poses/dance1.json"),
    ("videos/dance2.mp4", "poses/dance2.json"),
    ("videos/dance3.mp4", "poses/dance3.json"),
]

options = mp.tasks.vision.PoseLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path="pose_landmarker.task"),
    num_poses=1
)
detector = mp.tasks.vision.PoseLandmarker.create_from_options(options)
os.makedirs("poses", exist_ok=True)

for video_path, output_path in VIDEOS:
    print(f"\nExtraction de {video_path}...")
    cap = cv2.VideoCapture(video_path)
    poses_data = []
    frame_count = 0

    while True:
        success, frame = cap.read()
        if not success:
            break
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        result = detector.detect(mp_image)
        frame_poses = []
        if result.pose_landmarks:
            for landmark in result.pose_landmarks[0]:
                frame_poses.append({"x": landmark.x, "y": landmark.y})
        poses_data.append(frame_poses)
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"  {frame_count} frames...")

    cap.release()
    with open(output_path, "w") as f:
        json.dump(poses_data, f)
    print(f"✓ {frame_count} frames → {output_path}")

print("\nExtraction terminée !")