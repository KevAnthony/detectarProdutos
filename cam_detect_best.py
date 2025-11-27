from ultralytics import YOLO
import cv2
import serial
import time

# Conecta al ESP32 vía COM10
esp32 = serial.Serial("COM10", 115200, timeout=1)
time.sleep(2)  # espera a que se inicialice el ESP32

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    detections = results[0].boxes

    best_label = "Nada"
    best_conf = 0.0

    if detections is not None and len(detections) > 0:
        for box in detections:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls_id]

            if conf > best_conf:
                best_conf = conf
                best_label = label

    print(f"Mejor detección: {best_label} ({best_conf:.2f})")

    # ---- ENVIAR AL ESP32 POR SERIAL ----
    esp32.write((best_label + "\n").encode())

    annotated = results[0].plot()
    cv2.imshow("YOLO (q para salir)", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
esp32.close()
