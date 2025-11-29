import cv2

def main():
    img = cv2.imread('test_image.jpg')
    if img is None:
        print("Error: Image not found.")
        return

    # 1. Resize to 640x480 (Original size in this case, but good for demo)
    img_640_480 = cv2.resize(img, (640, 480))
    cv2.imshow('Resize 640x480', img_640_480)

    # 2. Resize to 1024x768
    img_1024_768 = cv2.resize(img, (1024, 768))
    cv2.imshow('Resize 1024x768', img_1024_768)

    # 3. Scale fx=0.3, fy=0.7
    img_scaled = cv2.resize(img, None, fx=0.3, fy=0.7)
    cv2.imshow('Scaled fx=0.3 fy=0.7', img_scaled)

    # 4. Crop (Deep Copy)
    # Crop region: y:100-400, x:200-500
    # Note: Slicing creates a view, copy() makes it a deep copy
    img_cropped = img[100:400, 200:500].copy()
    cv2.imshow('Cropped (Deep Copy)', img_cropped)

    print("Press any key to close all windows.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
