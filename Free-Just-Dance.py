import cv2
import mediapipe as mp
options = mp.tasks.vision.PoseLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path="pose_landmarker.task"),
output_segmentation_masks=False
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

    image = cv2.flip(image, 1)
    cv2.imshow("DanceScore", image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()