import cv2

def main():
    img = cv2.imread('test_image.jpg')
    if img is None:
        print("Error: Image not found.")
        return

    # Coordinates for the "Red Square" (approximate based on creation script)
    # Top-Left: (50, 50), Bottom-Right: (150, 150)
    x1, y1 = 50, 50
    x2, y2 = 150, 150

    # 1. Draw Rectangle (Red)
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # 2. Add Text Label
    text = "Red Square"
    text_x, text_y = 200, 100
    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # 3. Draw Connecting Line (Red)
    # Connect from text to rectangle
    cv2.line(img, (text_x - 10, text_y - 10), (x2, y1 + 50), (0, 0, 255), 2)

    cv2.imshow('Object Labeling', img)

    print("Press any key to close all windows.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
