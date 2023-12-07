import os
import sys
import numpy as np
from os import getcwd
import cv2
import msvcrt
from ctypes import *
from deepLearning.MvImport.MvCameraControl_class import *


class HikVision:
    def __init__(self):
        pass
        
    def enum_devices(self, device=0, device_way=False):
        if device_way == False:
            if device == 0:
                tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE | MV_UNKNOW_DEVICE | MV_1394_DEVICE | MV_CAMERALINK_DEVICE
                deviceList = MV_CC_DEVICE_INFO_LIST()
                # 枚举设备
                ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
                if ret != 0:
                    print("enum devices fail! ret[0x%x]" % ret)
                    sys.exit()
                if deviceList.nDeviceNum == 0:
                    print("find no device!")
                    sys.exit()
                print("Find %d devices!" % deviceList.nDeviceNum)
                return deviceList
            else:
                pass
        elif device_way == True:
            pass


    def input_num_camera(self, deviceList):
        nConnectionNum = 0
        if int(nConnectionNum) >= deviceList.nDeviceNum:
            print("intput error!")
            sys.exit()
        return nConnectionNum

    def creat_camera(self, deviceList, nConnectionNum, log=True, log_path=getcwd()):
        # 创建相机实例
        cam = MvCamera()
        # 选择设备并创建句柄
        stDeviceList = cast(deviceList.pDeviceInfo[int(nConnectionNum)], POINTER(MV_CC_DEVICE_INFO)).contents
        if log == True:
            ret = cam.MV_CC_SetSDKLogPath(log_path)
            print(log_path)
            if ret != 0:
                print("set Log path  fail! ret[0x%x]" % ret)
                sys.exit()
            # 创建句柄,生成日志
            ret = cam.MV_CC_CreateHandle(stDeviceList)
            if ret != 0:
                print("create handle fail! ret[0x%x]" % ret)
                sys.exit()
        elif log == False:
            # 创建句柄,不生成日志
            ret = cam.MV_CC_CreateHandleWithoutLog(stDeviceList)
            if ret != 0:
                print("create handle fail! ret[0x%x]" % ret)
                sys.exit()
        return cam, stDeviceList

    def open_device(cam):
        # ch:打开设备 | en:Open device
        ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            print("open device fail! ret[0x%x]" % ret)
            sys.exit()