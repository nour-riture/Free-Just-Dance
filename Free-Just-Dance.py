import cv2
import mediapipe as mp
import subprocess
import json
import numpy as np
from menu import run_menu, COLORS, draw_pixel_title, SONG_COLORS

# Launch the menu
selected_song, num_players = run_menu()
if selected_song is None:
    exit()

# Ref positions
with open(selected_song["poses"], "r") as f:
    reference_poses = json.load(f)

# Initialisation MediaPipe
options = mp.tasks.vision.PoseLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path="pose_landmarker.task"),
    output_segmentation_masks=False,
    num_poses=num_players
)
detector = mp.tasks.vision.PoseLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
music_process = subprocess.Popen(['mpv', '--fullscreen', selected_song["video"]])

# Scores
scores = [0] * num_players
frame_scores = [[] for _ in range(num_players)]
colors = [(0, 255, 0), (0, 0, 255)]

# Webcam window
cv2.namedWindow("Free Just Dance", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Free Just Dance", 400, 300)
cv2.moveWindow("Free Just Dance", 1520, 0)

video_frame_index = 0
points_utiles = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
connections = [
    (11, 12), (11, 13), (13, 15),
    (12, 14), (14, 16), (11, 23),
    (12, 24), (23, 24), (23, 25),
    (25, 27), (24, 26), (26, 28)
]

def assign_players(poses, num_players):
    if len(poses) == 0:
        return {}
    centers = [(idx, pose[11].x) for idx, pose in enumerate(poses)]
    centers.sort(key=lambda x: x[1])
    assignment = {}
    for player_slot, (pose_idx, _) in enumerate(centers[:num_players]):
        assignment[player_slot] = pose_idx
    return assignment

while True:
    success, image = cap.read()
    if not success:
        break

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    result = detector.detect(mp_image)

    if result.pose_landmarks and video_frame_index < len(reference_poses):
        ref_pose = reference_poses[video_frame_index]
        assignment = assign_players(result.pose_landmarks, num_players)

        for player_slot, pose_idx in assignment.items():
            pose = result.pose_landmarks[pose_idx]
            color = colors[player_slot]
            h, w, _ = image.shape

            for i in points_utiles:
                landmark = pose[i]
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(image, (cx, cy), 5, color, -1)

            for start, end in connections:
                p1 = pose[start]
                p2 = pose[end]
                cv2.line(image,
                    (int(p1.x * w), int(p1.y * h)),
                    (int(p2.x * w), int(p2.y * h)),
                    color, 2)

            if len(ref_pose) == 33:
                total_diff = 0
                for i in points_utiles:
                    dx = pose[i].x - ref_pose[i]["x"]
                    dy = pose[i].y - ref_pose[i]["y"]
                    total_diff += (dx**2 + dy**2) ** 0.5
                avg_diff = total_diff / len(points_utiles)
                frame_score = max(0, int(100 - avg_diff * 300))
                frame_scores[player_slot].append(frame_score)
                scores[player_slot] = int(sum(frame_scores[player_slot]) / len(frame_scores[player_slot]))

    video_frame_index += 1

    image = cv2.flip(image, 1)

    # Score wbecam
    overlay = image.copy()
    panel_h = 55 * num_players + 15
    cv2.rectangle(overlay, (0, 0), (220, panel_h), (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)

    for i in range(num_players):
        score = scores[i]
        if score >= 80: grade = "AMAZING"
        elif score >= 60: grade = "GOOD"
        elif score >= 40: grade = "OK"
        else: grade = "KEEP TRYING"
        y = 30 + i * 55
        cv2.putText(image, f"P{i+1} {score}pts", (8, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.75, colors[i], 2)
        cv2.putText(image, grade, (8, y + 22),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[i], 1)

    cv2.imshow("Free Just Dance", image)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or music_process.poll() is not None:
        break

# Stop video
music_process.terminate()
cv2.destroyAllWindows()

# Results screen
h_res, w_res = 720, 1280
result_img = np.ones((h_res, w_res, 3), dtype=np.uint8)
result_img[:] = COLORS["bg"]

cv2.rectangle(result_img, (0, 0), (w_res-1, h_res-1), COLORS["border_outer"], 12)
cv2.rectangle(result_img, (6, 6), (w_res-7, h_res-7), COLORS["section_title"], 4)

draw_pixel_title(result_img, 80)

cv2.line(result_img, (20, 165), (1260, 165), COLORS["section_title"], 3)

label = "RESULTS"
lw = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0][0]
cv2.putText(result_img, label, ((w_res - lw) // 2, 230),
    cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS["section_title"], 3)

cv2.line(result_img, (20, 255), (1260, 255), COLORS["section_title"], 2)

player_colors = [(0, 255, 0), (0, 0, 255)]
card_w = 900
card_x = (w_res - card_w) // 2

for i in range(num_players):
    score = scores[i]
    if score >= 80:
        grade = "AMAZING !!!"
        grade_color = SONG_COLORS[2]
    elif score >= 60:
        grade = "GOOD !"
        grade_color = COLORS["song2"]
    elif score >= 40:
        grade = "OK"
        grade_color = COLORS["song1"]
    else:
        grade = "KEEP TRYING..."
        grade_color = (180, 180, 180)

    y = 275 + i * 160
    color = player_colors[i]

    cv2.rectangle(result_img, (card_x, y), (card_x + card_w, y + 130), COLORS["unselected_bg"], -1)
    cv2.rectangle(result_img, (card_x, y), (card_x + card_w, y + 130), color, 3)

    cv2.rectangle(result_img, (card_x + 10, y + 10), (card_x + 70, y + 120), color, -1)
    pw = cv2.getTextSize(f"P{i+1}", cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0][0]
    cv2.putText(result_img, f"P{i+1}", (card_x + 10 + (60 - pw) // 2, y + 75),
        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

    cv2.putText(result_img, f"{score} pts", (card_x + 90, y + 60),
        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    cv2.putText(result_img, grade, (card_x + 90, y + 110),
        cv2.FONT_HERSHEY_SIMPLEX, 1.1, grade_color, 2)

cv2.line(result_img, (20, 670), (1260, 670), COLORS["section_title"], 2)
msg = "Press any key to exit"
mw = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0][0]
cv2.putText(result_img, msg, ((w_res - mw) // 2, 695),
    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS["instructions"], 1)

cv2.namedWindow("Résultats", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Résultats", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.imshow("Résultats", result_img)
cv2.waitKey(0)
cv2.destroyAllWindows()