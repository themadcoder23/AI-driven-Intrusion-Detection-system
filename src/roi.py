import cv2
import numpy as np

roi_points = []

def draw_roi(event, x, y, flags, param):
    global roi_points
    if event == cv2.EVENT_LBUTTONDOWN:
        roi_points.append((x, y))

def select_roi(frame):
    global roi_points
    roi_points = []

    window = "Select ROI (Click 3+ points, ENTER to confirm)"
    cv2.namedWindow(window)
    cv2.setMouseCallback(window, draw_roi)

    while True:
        temp = frame.copy()

        for p in roi_points:
            cv2.circle(temp, p, 5, (0, 255, 0), -1)

        if len(roi_points) >= 2:
            cv2.polylines(
                temp,
                [np.array(roi_points)],
                isClosed=False,
                color=(0, 255, 0),
                thickness=2
            )

        cv2.imshow(window, temp)
        key = cv2.waitKey(1) & 0xFF

        if key == 13:  # ENTER
            break

    cv2.destroyAllWindows()
    cv2.waitKey(1)

    if len(roi_points) < 3:
        print("ERROR: ROI must have at least 3 points")
        return None

    return np.array(roi_points, dtype=np.int32)
