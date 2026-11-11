from ultralytics import YOLO
import os

MODEL_PATH = "yolo_dataset/runs/detect/train5/weights/best.pt"
model = YOLO(MODEL_PATH)


def detect_disease(image_path):
    results = model(image_path)

    for r in results:
        boxes = r.boxes
        if boxes is None or len(boxes) == 0:
            return "sistem tidak mengenali gambar."

        cls = int(boxes.cls[0])
        conf = float(boxes.conf[0])
        label = model.names[cls]

        # filter confidence
        if conf < 0.7:
            return "Gambar Tanaman tidak dapat dikenali oleh sistem."
        
        # Simpan gambar dengan bounding box
        os.makedirs("detected", exist_ok=True)
        output_path = f"detected/{os.path.basename(image_path)}"
        r.save(filename=output_path)  # YOLOv8 otomatis gambar kotak + label

        return f"{label} (Confidence : {conf:.2f})"