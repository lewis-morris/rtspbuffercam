import camera
import cv2

cam = camera.Camera("rtsp://admin:Arctattv3@192.168.0.40/h264Preview_01_main")

print(f"Camera is alive?: {cam.p.is_alive()}")

while(1):
    frame = cam.get_frame(0.65)

    cv2.imshow("Feed",frame)

    key = cv2.waitKey(1)

    if key == 13: #13 is the Enter Key
        break

cv2.destroyAllWindows()

cam.end()