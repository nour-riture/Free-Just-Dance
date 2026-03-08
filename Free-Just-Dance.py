import cv2
import mediapipe as mp
options = mp.tasks.vision.PoseLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path="pose_landmarker.task"),
output_segmentation_masks=False,
num_poses=4
)
detector = mp.tasks.vision.PoseLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

while True:
    success, image = cap.read()
    if not success:
        break

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    result = detector.detect(mp_image)

    if result.pose_landmarks:
        for pose in result.pose_landmarks:
            points_utiles = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
            for i in points_utiles:
                landmark = pose[i]
                h, w, _ = image.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)
            
            connections = [
                (11, 12), # shoulder
                (11, 13), (13, 15), # Arm L
                (12, 14), (14, 16), # Arm R
                (11, 23), (12, 24), # Torso
                (23, 24), # Hips
                (23, 25), (25, 27), # Leg L
                (24, 26), (26, 28)  # Leg R
            ]
            
            h, w, _ = image.shape
            for start, end in connections:
                p1 = pose[start]
                p2 = pose[end]
                cv2.line(image,
                    (int(p1.x * w), int(p1.y * h)),
                    (int(p2.x * w), int(p2.y * h)),
                    (255, 0, 0), 2)    
    image = cv2.flip(image, 1)
    cv2.imshow("DanceScore", image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()