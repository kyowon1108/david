import cv2

def main():
    img = cv2.imread('test_image.jpg')
    if img is None:
        print("Error: Image not found.")
        return

    cv2.imshow('Original', img)

    # 1. RGB to Gray
    # OpenCV loads images in BGR format by default
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Gray', img_gray)

    # 2. Inversion (Bitwise Not)
    img_inverted = cv2.bitwise_not(img)
    cv2.imshow('Inverted', img_inverted)

    print("Press any key to close all windows.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
