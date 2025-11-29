import cv2

def main():
    # 이미지 읽기
    img = cv2.imread('test_image.jpg')
    
    if img is None:
        print("Error: Image not found.")
        return

    print("Press any key to close the window.")
    
    while True:
        cv2.imshow('Image', img)
        # 키 입력 대기 33ms
        if cv2.waitKey(33) >= 0:
            break
            
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
