import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.5)
    annotated = results[0].plot()

    detected = "None"

    for box in results[0].boxes:
        cls = int(box.cls[0])
        label = model.names[cls]

        if label in ["bottle", "cup"]:
            detected = "Plastic"
        elif label in ["can"]:
            detected = "Metal"
        elif label in ["book", "paper"]:
            detected = "Paper"

    # Write detection result to file
    with open("detected_waste.txt", "w") as f:
        f.write(detected)

    cv2.imshow("Smart Bin Camera", annotated)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
