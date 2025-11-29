import cv2
import numpy as np

# Create a dummy image with distinct features for orientation testing
img = np.zeros((480, 640, 3), dtype=np.uint8)
# Background color
img[:] = (200, 200, 200)

# Draw shapes to identify orientation
# Top-Left: Red Square
cv2.rectangle(img, (50, 50), (150, 150), (0, 0, 255), -1)
# Top-Right: Green Circle
cv2.circle(img, (550, 100), 50, (0, 255, 0), -1)
# Bottom-Left: Blue Triangle
pts = np.array([[100, 400], [50, 450], [150, 450]], np.int32)
pts = pts.reshape((-1, 1, 2))
cv2.fillPoly(img, [pts], (255, 0, 0))
# Text in Center
cv2.putText(img, 'OpenCV Q2', (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)

cv2.imwrite('test_image.jpg', img)
print("Created test_image.jpg")
