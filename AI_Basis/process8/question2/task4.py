import cv2

def main():
    img = cv2.imread('test_image.jpg')
    if img is None:
        print("Error: Image not found.")
        return

    # 1. Binarization
    # Convert to grayscale first
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Thresholding: values > 127 become 255, others 0
    ret, img_binary = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
    cv2.imshow('Binary', img_binary)

    # 2. Edge Detection
    # Sobel
    sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
    img_sobel = cv2.convertScaleAbs(sobel_x + sobel_y)
    cv2.imshow('Sobel', img_sobel)

    # Laplacian
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    img_laplacian = cv2.convertScaleAbs(laplacian)
    cv2.imshow('Laplacian', img_laplacian)

    # Canny
    img_canny = cv2.Canny(img, 100, 200)
    cv2.imshow('Canny', img_canny)

    # 3. Blurring
    # Using Gaussian Blur
    img_blur = cv2.GaussianBlur(img, (15, 15), 0)
    cv2.imshow('Blurred', img_blur)

    print("Press any key to close all windows.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
