import cv2
import numpy as np
import math
import mediapipe as mp
import os
import sqlite3
import json

def get_eye_angle(left_eye, right_eye):
    dx = right_eye[0] - left_eye[0]
    dy = right_eye[1] - left_eye[1]
    return math.degrees(math.atan2(dy, dx))

def calculate_clarity(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def rotate_image(image, center, angle):
    center = (int(center[0]), int(center[1]))
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))

def save_image_to_db(user_id: str, image: np.ndarray, score: float, db_path='avatar-database.db'):
    image_blob = image.tobytes()
    image_shape = json.dumps(image.shape)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS avatar_frames (
        user_id TEXT PRIMARY KEY,
        image_blob BLOB,
        image_shape TEXT,
        score REAL
    )""")

    c.execute("""REPLACE INTO avatar_frames (user_id, image_blob, image_shape, score) 
        VALUES (?, ?, ?, ?)""", (user_id, image_blob, image_shape, score))

    conn.commit()
    conn.close()
    print(f"💾 Best avatar frame saved to DB for user: {user_id}")

def load_image_from_db(user_id: str, db_path='avatar-database.db') -> np.ndarray:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT image_blob, image_shape FROM avatar_frames WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()

    if result:
        blob, shape = result
        shape = tuple(json.loads(shape))
        image_np = np.frombuffer(blob, dtype=np.uint8).reshape(shape)
        return image_np
    else:
        raise ValueError(f"No image found in DB for user {user_id}")

def extract_best_avatar_frame(video_path, user_id,output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Failed to open video.")
        return None

    SKIP_FRAMES = 5
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"🎞️ Total frames in video: {total_frames}")

    best_frame = None
    best_score = -np.inf
    fallback_frame = None
    fallback_score = -np.inf
    frame_index = 0
    face_detected_frames = 0

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index % SKIP_FRAMES != 0:
            frame_index += 1
            continue

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            face_detected_frames += 1
            face_landmarks = results.multi_face_landmarks[0]
            def lm_to_coords(lm): return np.array([int(lm.x * w), int(lm.y * h)])

            try:
                left_eye = lm_to_coords(face_landmarks.landmark[33])
                right_eye = lm_to_coords(face_landmarks.landmark[263])
                left_iris = lm_to_coords(face_landmarks.landmark[468])
                right_iris = lm_to_coords(face_landmarks.landmark[473])
                left_eye_top = lm_to_coords(face_landmarks.landmark[159])
                left_eye_bottom = lm_to_coords(face_landmarks.landmark[145])
                upper_lip = lm_to_coords(face_landmarks.landmark[13])
                lower_lip = lm_to_coords(face_landmarks.landmark[14])
            except:
                frame_index += 1
                continue

            eye_angle = abs(get_eye_angle(left_eye, right_eye))
            eye_diff = abs(left_eye[1] - right_eye[1])
            mouth_openness = abs(lower_lip[1] - upper_lip[1])
            iris_centeredness = (
                np.linalg.norm(left_iris - left_eye) +
                np.linalg.norm(right_iris - right_eye)
            )
            eye_openness = abs(left_eye_bottom[1] - left_eye_top[1])
            clarity = calculate_clarity(frame)

            if eye_openness < 4:
                frame_index += 1
                continue

            score = (
                1.0 * clarity -
                1.5 * min(mouth_openness, 40) -
                1.5 * min(iris_centeredness, 30) -
                2.0 * max(6 - eye_openness, 0) -
                0.6 * min(eye_angle, 20) -
                0.3 * min(eye_diff, 20)
            )

            print(f"✅ Face detected. Frame #{frame_index} Score: {score:.2f}")

            if score > best_score:
                best_score = score
                center = tuple(np.mean([left_eye, right_eye], axis=0).astype(int))
                aligned = rotate_image(frame, center, -get_eye_angle(left_eye, right_eye))
                best_frame = aligned.copy()
                print(f"🌟 New best frame at #{frame_index}, Score: {score:.2f}")

            if score > fallback_score:
                fallback_score = score
                fallback_frame = frame.copy()
        else:
            print(f"❌ No face detected at frame #{frame_index}")

        frame_index += 1

    cap.release()

    print(f"\n🔍 Total frames with face detected: {face_detected_frames}")

    if best_frame is not None:
        result_path = os.path.join(output_dir, f"best_frame_{user_id}.jpg")
        cv2.imwrite(result_path, best_frame)
        save_image_to_db(user_id, best_frame, best_score)
        print(f"\n✅ Best avatar frame saved! Score: {best_score:.2f}")
        return result_path
    else:
        fallback_path = os.path.join(output_dir, "fallback_avatar_face.jpg")
        cv2.imwrite(fallback_path, fallback_frame)
        save_image_to_db(user_id, fallback_frame, fallback_score)
        print(f"\n⚠ No perfect match. Fallback saved. Score: {fallback_score:.2f}")
        return fallback_path


