import cv2
import numpy as np

# Create a dummy image
img = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.rectangle(img, (100, 100), (540, 380), (0, 255, 0), -1)
cv2.putText(img, 'Test Image', (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv2.imwrite('test_image.jpg', img)
print("Created test_image.jpg")

# Create a dummy video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test_video.mp4', fourcc, 30.0, (640, 480))

for i in range(300): # 10 seconds
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Moving circle
    cv2.circle(frame, (i*2 % 640, 240), 50, (0, 0, 255), -1)
    cv2.putText(frame, f'Frame {i}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    out.write(frame)

out.release()
print("Created test_video.mp4")
