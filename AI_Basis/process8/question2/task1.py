import cv2

def main():
    # 1. 이미지 읽기
    img = cv2.imread('test_image.jpg')
    if img is None:
        print("Error: Image not found.")
        return

    # 2. 원본 이미지 출력
    cv2.imshow('Original', img)

    # 3. 상하 반전 (Flip Code 0)
    img_flip_ud = cv2.flip(img, 0)
    cv2.imshow('Flip Up-Down', img_flip_ud)

    # 4. 좌우 반전 (Flip Code 1)
    img_flip_lr = cv2.flip(img, 1)
    cv2.imshow('Flip Left-Right', img_flip_lr)

    # 5. 시계방향 90도 회전
    img_rotate_90 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    cv2.imshow('Rotate 90', img_rotate_90)

    # 6. 180도 회전
    img_rotate_180 = cv2.rotate(img, cv2.ROTATE_180)
    cv2.imshow('Rotate 180', img_rotate_180)

    print("Press any key to close all windows.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
