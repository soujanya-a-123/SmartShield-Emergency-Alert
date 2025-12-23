import cv2

cap = cv2.VideoCapture(0)  # change later based on test_camera.py

if not cap.isOpened():
    print("❌ Camera failed to open")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
