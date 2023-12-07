import cv2
import numpy as np
import camera
from detect import YOLOv5Detector


def on_value(a):
    value = cv2.getTrackbarPos("value", "img_")
    ret, dst = cv2.threshold(img_, value, 255, cv2.THRESH_BINARY)
    cv2.imshow("dst", dst)


def find_closest_pair(arr):
    closest_pair = []
    sum = 0
    average = 0
    for line in arr:
        sum += line[0]
    average = sum / len(arr)

    low = []
    high = []
    for i in range(len(arr)):
        if arr[i][0] >= average:
            high.append(arr[i])
        else:
            low.append(arr[i])

    closest_pair.append(low[0])
    closest_pair.append(high[0])

    return closest_pair


def intersection_point(line1, line2):
    rho1, theta1 = line1
    rho2, theta2 = line2

    denom = np.sin(theta1 - theta2)
    if denom == 0:
        print("直线平行或重合，无交点")
        return None
    x = (rho2 * np.cos(theta2) - rho1 * np.cos(theta1)) / np.sin(theta1 - theta2)
    y = (rho2 * np.sin(theta2) - rho1 * np.sin(theta1)) / np.sin(theta1 - theta2)
    point = (int(x), int(-y))
    return point


def ins(line1, line2):
    x1, y1 = line1[0] * np.cos(line1[1]), line1[0] * np.sin(line1[1])
    x2, y2 = line2[0] * np.cos(line2[1]), line2[0] * np.sin(line2[1])

    # 解方程组以求交点
    A = np.array([
        [np.cos(line1[1]), np.sin(line1[1])],
        [np.cos(line2[1]), np.sin(line2[1])]
    ])
    B = np.array([line1[0], line2[0]])
    x, y = np.linalg.solve(A, B)
    point = (int(x), int(y))
    return point


if __name__ == '__main__':
    # deviceList = camera.enum_devices(device=0, device_way=False)
    # camera.identify_different_devices(deviceList)
    # nConnectionNum = camera.input_num_camera(deviceList)
    # cam, stDeviceList = camera.creat_camera(deviceList, nConnectionNum, log=False)
    # camera.open_device(cam)
    # cv2.waitKey(3000)
    # camera.start_grab_and_get_data_size(cam)
    #
    #
    #
    # image = camera.getOneFrame(cam)
    # cv2.imshow("image",image)
    # cv2.waitKey(0)

    img = cv2.imread("D:\\AllProjects\\CProject\\opencv_project\\testpic\\pnp_6.bmp", 1)
    img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    # img = image

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_th = cv2.threshold(img_gray, 100, 255, cv2.THRESH_BINARY)

    img_ = img
    cv2.imshow('img_', img_)
    cv2.createTrackbar("value", "img_", 0, 255, on_value)
    cv2.waitKey(0)

    img_edges = cv2.Canny(img_th, 100, 200)
    cv2.imshow('img_edges', img_edges)
    lines = cv2.HoughLines(img_edges, 1, np.pi / 180, 150)
    print("lines:", len(lines))

    # by slope
    lines1_slope = []
    lines2_slope = []
    for index, line in enumerate(lines):
        if index == 0:
            lines1_slope.append(line[0])
            continue
        if abs(line[0][1] - lines1_slope[0][1]) > 0.7:
            lines2_slope.append(line[0])
        else:
            lines1_slope.append(line[0])
    print("lines_slope1,2:", len(lines1_slope), len(lines2_slope))

    # by distance
    lines1 = find_closest_pair(lines1_slope)
    lines2 = find_closest_pair(lines2_slope)
    print("lines1,2:", len(lines1), len(lines2))

    # if lines is not None:
    #     for line in lines1:
    #         rho, theta = line
    #         print(line[0])
    #         a = np.cos(theta)
    #         b = np.sin(theta)
    #         x0 = a * rho
    #         y0 = b * rho
    #         x1 = int(x0 + 1000 * (-b))
    #         y1 = int(y0 + 1000 * (a))
    #         x2 = int(x0 - 1000 * (-b))
    #         y2 = int(y0 - 1000 * (a))
    #         cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    # cv2.imshow('img', img)
    # cv2.waitKey(0)
    #
    # if lines is not None:
    #     for line in lines2:
    #         rho, theta = line
    #         print(line[0])
    #         a = np.cos(theta)
    #         b = np.sin(theta)
    #         x0 = a * rho
    #         y0 = b * rho
    #         x1 = int(x0 + 1000 * (-b))
    #         y1 = int(y0 + 1000 * (a))
    #         x2 = int(x0 - 1000 * (-b))
    #         y2 = int(y0 - 1000 * (a))
    #         cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    # cv2.imshow('img', img)
    # cv2.waitKey(0)

    points = []
    for line1 in lines1:
        for line2 in lines2:
            points.append(ins(line1, line2))

    points = sorted(points, key=lambda x: (x[1], x[0]))
    pointsU = points[:2]
    pointsD = points[-2:]

    pointsU = sorted(pointsU, key=lambda x: (x[0]))
    pointsD = sorted(pointsD, key=lambda x: (x[0]))

    print("points:", len(points))
    print("points:", points)
    cv2.circle(img, pointsU[0], 5, (0, 255, 0), -1)
    cv2.circle(img, pointsU[1], 5, (0, 0, 255), -1)
    cv2.circle(img, pointsD[0], 5, (255, 0, 0), -1)
    cv2.circle(img, pointsD[1], 5, (255, 255, 255), -1)
    mup = 3
    dst_width, dst_height = int(263*mup), int(197*mup)
    src_pts = np.array([pointsU[0], pointsU[1], pointsD[1], pointsD[0]], dtype=np.float32)
    dst_pts = np.array([[0, 0], [dst_width - 1, 0], [dst_width - 1, dst_height - 1], [0, dst_height - 1]],
                       dtype=np.float32)
    perspective_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped_img = cv2.warpPerspective(img, perspective_matrix, (dst_width, dst_height))

    cv2.imshow('warped_img', warped_img)
    cv2.imshow('img', img)
    cv2.waitKey(0)

    # img = cv2.imread("C:\\Users\\work\\Desktop\\yolov5-master1\\data\\images\\0068.jpg", 1)
    # img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    #
    detector = YOLOv5Detector("best.onnx")
    imgee, inf = detector.detect_objects(warped_img, 0.70, 0.80)
    print(inf)
    #
    cv2.imshow("imgee", imgee)
    cv2.waitKey(0)
