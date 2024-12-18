import cv2
import base64
import numpy as np
from yolov5 import YOLOv5
import warnings
import time  # Import time module for performance measurement
import torch

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load YOLOv5 model (You can use a different version if needed)
model = YOLOv5("yolov5s.pt")  # This uses the small version of YOLOv5. You can use yolov5m.pt or yolov5l.pt for better accuracy.

def image_to_base64(image_path):
    """Convert an image file to base64 string."""
    # start_time = time.time()  # Start measuring time for this function
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    # end_time = time.time()  # End measuring time for this function
    # print(f"Time taken to convert image to base64: {end_time - start_time:.4f} seconds")
    return img_base64

def base64_to_image(base64_str):
    """Convert a base64 string back to an OpenCV image."""
    # start_time = time.time()  # Start measuring time for this function
    img_data = base64.b64decode(base64_str)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    # end_time = time.time()  # End measuring time for this function
    # print(f"Time taken to convert base64 to image: {end_time - start_time:.4f} seconds")
    return img

def detect_person(image):
    """Detect a person in the image using YOLOv5."""
    # start_time = time.time()  # Start measuring time for this function
    results = model.predict(image)
    
    # Get detection results in xywh format (x, y, width, height)
    detections = results.xywh[0].cpu().numpy()  # Results in xywh format
    
    # Filter detections to only 'person' class (class 0 in COCO dataset)
    for det in detections:
        class_id = int(det[5])  # The class ID is at index 5 in the result
        if class_id == 0:  # 'person' class in COCO dataset
            # end_time = time.time()  # End measuring time for this function
            # print(f"Time taken for person detection: {end_time - start_time:.4f} seconds")
            return True
    # end_time = time.time()  # End measuring time for this function
    # print(f"Time taken for person detection: {end_time - start_time:.4f} seconds")
    return False

# Example of using the functions
# image_path = r"C:\Users\vgandham\OneDrive - Delft University of Technology\Pictures\Screenshots\pic1.png"  # Replace with your image file

# Measure total time
# start_time = time.time()

# Convert image to base64 and then back to image
# img_base64 = image_to_base64(image_path)  # Convert image to base64
# img = base64_to_image(img_base64)  # Convert base64 back to image

# Detect person and print result
# is_person_detected = detect_person(img)
# print(f"Person Detected: {is_person_detected}")

# Measure total time for the process
# end_time = time.time()
# print(f"Total time taken for the entire process: {end_time - start_time:.4f} seconds")
