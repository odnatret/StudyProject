import cv2
from ultralytics import YOLO
from datetime import datetime, timedelta
import json
import os

# 1. Загрузка модели YOLO
model = YOLO(r"runs\detect\train2\weights\best.pt")  # nano-версия для скорости

# 2. Получаем ID целевых классов
print(model.names)
CLASS_NAMES = model.names
TARGET_CLASSES = ['redbull___33__90162909','snickers_weis__50__5000159461122','snickers___50__5000159461122',]  # Укажите нужные классый
target_class_ids = [k for k, v in CLASS_NAMES.items() if v in TARGET_CLASSES]

# 3. Подключение к камере
cap = cv2.VideoCapture(0)  # 0 - встроенная камера

# 4. Настройка логгирования
LOG_FILE = "cargo_log.json"
log_data = []
last_log_time = datetime.now()

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        log_data = json.load(f)

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = datetime.now()
        
        # 5. Детекция объектов (в каждом кадре)
        results = model.predict(frame, classes=target_class_ids)

        # 6. Визуализация (в каждом кадре)
        frame_entries = []
        for result in results:
            for box in result.boxes:
                # Подготовка данных для лога
                entry = {
                    "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "class": model.names[int(box.cls[0])],
                    "confidence": float(box.conf[0]),
                    "coordinates": {
                        "x1": int(box.xyxy[0][0]),
                        "y1": int(box.xyxy[0][1]),
                        "x2": int(box.xyxy[0][2]),
                        "y2": int(box.xyxy[0][3])
                    }
                }
                frame_entries.append(entry)

                # Отрисовка bounding box (всегда)
                x1, y1, x2, y2 = entry["coordinates"].values()
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, 
                           f"{entry['class']} {entry['confidence']:.2f}",
                           (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 7. Логгирование раз в 15 секунд
        if (current_time - last_log_time).total_seconds() >= 15:
            if frame_entries:
                log_data.append({
                    "log_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "detections": frame_entries
                })
                with open(LOG_FILE, "w") as f:
                    json.dump(log_data, f, indent=2)
                print(f"Logged at {current_time}")
                last_log_time = current_time

        # 8. Показ кадра с bounding boxes
        cv2.imshow("Cargo Tracking", frame)
        if cv2.waitKey(1) == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()