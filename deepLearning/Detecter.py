import sys

import cv2
import numpy as np
import deepLearning.camera
from deepLearning.detect import YOLOv5Detector
from deepLearning.MvImport.MvCameraControl_class import *

class Detecter:
    def __init__(self):
        deviceList = deepLearning.camera.enum_devices(device=0, device_way=False)
        deepLearning.camera.identify_different_devices(deviceList)
        nConnectionNum = deepLearning.camera.input_num_camera(deviceList)
        self.cam, stDeviceList = deepLearning.camera.creat_camera(deviceList, nConnectionNum, log=False)
        deepLearning.camera.open_device(self.cam)
        self.detector = YOLOv5Detector("./deepLearning/best.onnx")
        cv2.waitKey(3000)
        deepLearning.camera.start_grab_and_get_data_size(self.cam)

    def __del__(self):
        deepLearning.camera.close_and_destroy_device(self.cam)

    def find_closest_pair(self, arr):
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


    def intersection_point(self, line1, line2):
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

    def ins(self, line1, line2):
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

    def Detect(self,threshold):
        image = deepLearning.camera.getOneFrame(self.cam)
        # image = cv2.imread("C:\\Users\\24260\\Desktop\\pnp_6.bmp")
        img = image
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, img_th = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)

        img_edges = cv2.Canny(img_th, 100, 200)
        lines = cv2.HoughLines(img_edges, 1, np.pi / 180, 200)
        print("lines:",len(lines))

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
        lines1 = self.find_closest_pair(lines1_slope)
        lines2 = self.find_closest_pair(lines2_slope)
        print("lines1,2:", len(lines1), len(lines2))

        points = []
        for line1 in lines1:
            for line2 in lines2:
                points.append(self.ins(line1, line2))

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
        dst_width, dst_height = int(263 * mup), int(197 * mup)
        src_pts = np.array([pointsU[0], pointsU[1], pointsD[1], pointsD[0]], dtype=np.float32)
        dst_pts = np.array([[0, 0], [dst_width - 1, 0], [dst_width - 1, dst_height - 1], [0, dst_height - 1]],
                           dtype=np.float32)
        perspective_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped_img = cv2.warpPerspective(img, perspective_matrix, (dst_width, dst_height))

        imgdetected, inf = self.detector.detect_objects(warped_img, 0.70, 0.80)
        return imgdetected, inf