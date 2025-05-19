import cv2
from ultralytics import YOLO
from datetime import datetime
import csv
import os

# 1. Загрузка модели YOLO
model = YOLO(r"runs\detect\train2\weights\best.pt")

# 2. Получаем ID целевых классов
print(model.names)
CLASS_NAMES = model.names
TARGET_CLASSES = ['redbull___33__90162909']
target_class_ids = [k for k, v in CLASS_NAMES.items() if v in TARGET_CLASSES]

cv2.namedWindow("Inventory Tracking", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Inventory Tracking", 800, 600)  # Ширина, высота

# 3. Подключение к камере
cap = cv2.VideoCapture(1)

# 4. Настройка логгирования в CSV
CSV_FILE = "my-electron-app\inventory.csv"
CSV_HEADERS = ["Время", "Наименование", "Кол-во", "Ед. измерения", "Место хранения"]

# Место хранения
STORAGE_LOCATION = "Склад 1"

# Создаем файл с заголовками
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(CSV_HEADERS)

# Для хранения последних обнаруженных объектов
last_detections = {class_name: 0 for class_name in TARGET_CLASSES}

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = datetime.now()
        
        # 5. Детекция объектов
        results = model.predict(frame, classes=target_class_ids)
        
        # 6. Инициализация текущих детекций с нулями
        current_detections = {class_name: 0 for class_name in TARGET_CLASSES}
        
        # Обработка результатов детекции
        for result in results:
            for box in result.boxes:
                class_name = model.names[int(box.cls[0])]
                if class_name in current_detections:
                    current_detections[class_name] += 1
                
                # Визуализация
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, 
                          f"{class_name} {float(box.conf[0]):.2f}",
                          (x1, y1-10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 7. Обновление данных в CSV при изменении количества объектов
        if current_detections != last_detections:
            last_detections = current_detections.copy()
            
            # Подготовка данных для записи
            rows = []
            for item, count in current_detections.items():
                rows.append([
                    current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    item,
                    str(count),
                    "шт.",
                    STORAGE_LOCATION
                ])
            
            # Записываем с правильной кодировкой
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(CSV_HEADERS)
                writer.writerows(rows)
            
            print(f"Обновление инвентаризации в {current_time}:")
            for item, count in current_detections.items():
                print(f"  {item}: {count} шт.")
        
        # 8. Показ кадра
        cv2.imshow("Inventory Tracking", frame)
        if cv2.waitKey(1) == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()