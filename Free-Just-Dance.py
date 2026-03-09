import cv2
import mediapipe as mp
import subprocess
import json

# Charger les poses de référence
with open("poses/dance1.json", "r") as f:
    reference_poses = json.load(f)

video_frame_index = 0

options = mp.tasks.vision.PoseLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path="pose_landmarker.task"),
    output_segmentation_masks=False,
    num_poses=4
)
detector = mp.tasks.vision.PoseLandmarker.create_from_options(options)
cap = cv2.VideoCapture(0)
music_process = subprocess.Popen(['mpv', '--fullscreen', 'videos/dance1.mp4'])

# Positionner la fenêtre webcam en haut à droite
cv2.namedWindow("Free Just Dance", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Free Just Dance", 320, 240)
cv2.moveWindow("Free Just Dance", 1600, 0)
cv2.setWindowProperty("Free Just Dance", cv2.WND_PROP_TOPMOST, 1)

while True:
    success, image = cap.read()
    if not success:
        break

    # Analyser chaque frame
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    result = detector.detect(mp_image)
    # Calculer le score
    score = 0
    if result.pose_landmarks and video_frame_index < len(reference_poses):
        ref_pose = reference_poses[video_frame_index]
        if len(ref_pose) > 0:
            player_pose = result.pose_landmarks[0]
            points_utiles = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
            total_diff = 0
            for i in points_utiles:
                dx = player_pose[i].x - ref_pose[i]["x"]
                dy = player_pose[i].y - ref_pose[i]["y"]
                total_diff += (dx**2 + dy**2) ** 0.5
            score = max(0, 100 - int(total_diff * 200))

    video_frame_index += 1

    # Afficher le score
    cv2.putText(image, f"Score: {score}", (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    if result.pose_landmarks:
        for pose in result.pose_landmarks:
            points_utiles = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
            h, w, _ = image.shape
            # Dessiner les points clés
            for i in points_utiles:
                landmark = pose[i]
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)
            # Dessiner le squelette
            connections = [
                (11, 12),
                (11, 13), (13, 15),
                (12, 14), (14, 16),
                (11, 23), (12, 24),
                (23, 24),
                (23, 25), (25, 27),
                (24, 26), (26, 28)
            ]
            for start, end in connections:
                p1 = pose[start]
                p2 = pose[end]
                cv2.line(image,
                    (int(p1.x * w), int(p1.y * h)),
                    (int(p2.x * w), int(p2.y * h)),
                    (255, 0, 0), 2)

    # Retourner la webcam en miroir
    image = cv2.flip(image, 1)
    cv2.imshow("Free Just Dance", image)

    # Quitter avec Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Arrêter et libérer
music_process.terminate()
cap.release()
cv2.destroyAllWindows()