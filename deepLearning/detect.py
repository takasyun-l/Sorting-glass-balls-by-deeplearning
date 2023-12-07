import numpy as np
import cv2
import onnxruntime


class YOLOv5Detector:
    def __init__(self, model_path, providers=["CUDAExecutionProvider"]):
        self.session = onnxruntime.InferenceSession(model_path, providers=providers)

    def preprocess(self, img, dst_width=640, dst_height=640):
        scale = min((dst_width / img.shape[1]), (dst_height / img.shape[0]))
        ox = (-scale * img.shape[1] + dst_width) / 2
        oy = (-scale * img.shape[0] + dst_height) / 2
        M = np.array([
            [scale, 0, ox],
            [0, scale, oy]
        ], dtype=np.float32)
        # img_pre为仿射变换后的图即原始图像缩放到[dst_width,dst_height]
        img_pre = cv2.warpAffine(img, M, dsize=[dst_width, dst_height], flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(114, 114, 114))
        IM = cv2.invertAffineTransform(M)
        # -----------------------------------------------------------------------#
        #   需要进行的预处理
        #   1. BGR -> RGB
        #   2. /255.0
        #   3. 通道数变换 H,W,C -> C,H,W
        #   4. 添加batch维度 C,H,W -> B,C,H,W
        # -----------------------------------------------------------------------#
        img_pre = (img_pre[..., ::-1] / 255.0).astype(np.float32)
        img_pre = img_pre.transpose(2, 0, 1)[None]
        img_pre = np.repeat(img_pre, 8, axis=0)
        return img_pre, IM

    def postprocess(self, pred, IM, conf_thresh, iou_thresh):
        boxes = []
        for img_id, box_id in zip(*np.where(pred[..., 4] >= conf_thresh)):
            item = pred[img_id][box_id]
            cx, cy, w, h, obj_conf = item[:5]
            label = item[5:].argmax()
            confidence = obj_conf * item[5 + label]
            # if confidence < 0.5:
            #     continue
            left = cx - w * 0.5
            top = cy - h * 0.5
            right = cx + w * 0.5
            bottom = cy + h * 0.5
            boxes.append([left, top, right, bottom, confidence, img_id, label])
        # 利用IM将box映射回原图
        boxes = np.array(boxes)
        lr = boxes[..., [0, 2]]
        tb = boxes[..., [1, 3]]
        boxes[..., [0, 2]] = lr * IM[0][0] + IM[0][2]
        boxes[..., [1, 3]] = tb * IM[1][1] + IM[1][2]
        boxesIndex = cv2.dnn.NMSBoxes(boxes[:, 0:4].tolist(), boxes[:, 4].tolist(), conf_thresh, iou_thresh)
        rtBox = []
        for index in boxesIndex:
            rtBox.append(boxes[index])
        return rtBox

    def detect_objects(self, img, conf_thresh, iou_thresh):
        img_pre, IM = self.preprocess(img)
        pred = self.session.run(["output0"], {"images": img_pre})[0]
        boxes = self.postprocess(pred, IM, conf_thresh, iou_thresh)
        infomations = []
        for obj in boxes:
            x1, y1, x2, y2 = map(int, obj[:4])
            label = int(obj[6]) + 1
            center = (int((x2 + x1) / 2), int((y2 + y1) / 2))
            rbtInf = [label,  int((y2 + y1) / 2), int((x2 + x1) / 2)]
            rbtZeroPoints = (0,0)
            rbtXArg = 0.318
            rbtYArg = 0.323
            rbtInf[1] = rbtInf[1]*rbtXArg-725.27825
            rbtInf[2] = rbtInf[2]*rbtYArg-208.386
            infomations.append(rbtInf)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 1, 8)
            cv2.circle(img, center, 2, (0, 255, 0), -1)
            # cv2.putText(img, f"{label}:{obj[4]:.3f}", (x1, y1 - 6), 0, 1, (0, 0, 255), 2, 8)
            cv2.putText(img, f"{label}:({rbtInf[1]:.2f},{rbtInf[2]:.2f})", (x1-70, y1 - 6), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2, 8)

        return img, infomations
