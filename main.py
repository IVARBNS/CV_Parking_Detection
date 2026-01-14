import cv2

mask = 'mask_crop.png'
video_path = 'samples/car_test.mp4'

mask = cv2.imread(mask, 0)
cap = cv2.VideoCapture(video_path)

bbox = cv2.connectedComponents(mask, 4, cv2.CV_32S)

ret = True
while ret:
    ret, frame = cap.read()

    cv2.imshow('frame', frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
