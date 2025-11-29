import cv2
import datetime

def get_filename(ext):
    now = datetime.datetime.now()
    # Format: YYYY-MM-DD_HH-MM-SS
    return now.strftime("%Y-%m-%d_%H-%M-%S") + ext

def main():
    video_path = 'test_video.mp4'
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    is_recording = False
    out = None
    
    print("Controls:")
    print("ESC: Exit")
    print("Ctrl+Z: Capture Screenshot")
    print("Ctrl+X: Start Recording")
    print("Ctrl+C: Stop Recording")

    while True:
        ret, frame = cap.read()
        if not ret:
            # Loop video
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        if is_recording and out is not None:
            out.write(frame)
            # Visual indicator for recording
            cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)

        cv2.imshow('Video Player', frame)

        key = cv2.waitKey(33)
        
        # ESC
        if key == 27:
            break
        
        # Ctrl+Z (Capture)
        elif key == 26:
            filename = get_filename(".jpg")
            cv2.imwrite(filename, frame)
            print(f"Captured: {filename}")
            
        # Ctrl+X (Start Recording)
        elif key == 24:
            if not is_recording:
                filename = get_filename(".mp4")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
                is_recording = True
                print(f"Started recording: {filename}")
            else:
                print("Already recording.")
                
        # Ctrl+C (Stop Recording)
        elif key == 3:
            if is_recording:
                is_recording = False
                if out is not None:
                    out.release()
                    out = None
                print("Stopped recording.")
            else:
                print("Not recording.")

    # Cleanup
    cap.release()
    if out is not None:
        out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
