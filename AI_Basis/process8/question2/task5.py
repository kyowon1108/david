import cv2

def main():
    img = cv2.imread('test_image.jpg')
    if img is None:
        print("Error: Image not found.")
        return

    # 1. Convert to HSV
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 2. Split Channels
    h, s, v = cv2.split(img_hsv)

    # 3. Display Channels
    cv2.imshow('Hue', h)
    cv2.imshow('Saturation', s)
    cv2.imshow('Value', v)

    print("Press any key to close all windows.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
