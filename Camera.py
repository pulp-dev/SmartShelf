import qrcode as qr
import numpy as np
import argparse
import imutils
from imutils.video import VideoStream
import time
import cv2


class Camera:
    def __init__(self, camera_num):
        self.camera_num = camera_num

        PROTEXT = r"deploy.prototxt"
        MODEL = r"res10_300x300_ssd_iter_140000.caffemodel"

        # # construct the argument parse and parse the arguments
        # ap = argparse.ArgumentParser()
        # ap.add_argument("-p", "--prototxt", required=True,
        #                 help="path to Caffe 'deploy' prototxt file")
        # ap.add_argument("-m", "--model", required=True,
        #                 help="path to Caffe pre-trained model")
        # ap.add_argument("-c", "--confidence", type=float, default=0.5,
        #                 help="minimum probability to filter weak detections")
        # self.args = vars(ap.parse_args())

        print("[INFO] loading model...")
        # model
        self.net = cv2.dnn.readNetFromCaffe(PROTEXT, MODEL)

    def face_detection(self, img):

        (h, w) = img.shape[:2]
        blob = cv2.dnn.blobFromImage(img, 1.0, (h, w), (104.0, 177.0, 123.0))

        print("[INFO] computing objects detections...")
        self.net.setInput(blob)
        detections = self.net.forward()

        return self.boxes_on_predictions(img, detections, h, w)

    def boxes_on_predictions(self, img, detections, h, w):
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            # ensuring the `confidence` is greater than minimum confidence
            if confidence > .5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype('int')

                # img = self.blur_area(img, startX, startY, endX, endY)

                # draw the bounding box of the face along with the associated probability
                text = "{:.2f}%".format(confidence * 100)
                y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.rectangle(img, (startX, startY), (endX, endY),
                              (0, 0, 255), 2)
                cv2.putText(img, text, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

        return img

    def blur_area(self, img, startX, startY, endX, endY):
        w = startX - endX
        h = startY - endY
        ROI = img[startY:startY - h, startX:startX - w]
        blur = cv2.GaussianBlur(ROI, (51, 51), 0)
        img[startY:startY - h, startX:startX - w] = blur

        return img

    def scan_code(self, img, detector):
        """
        Сканирование QR-кода и вывод картинки с обведенным в квадрат кодом
        :param img: кадр с камеры
        :return: data: содержимое кода
        """

        # закодированные данные, координаты вершин кода, исправленное изображение кода
        data, bbox, straight_qrcode = detector.detectAndDecode(img)

        # наверное нам не нужно это но пусть будет
        if bbox is not None and data is not None and data != '':
            print(f"QRCode data:\n{data}")
            # отображаем изображение с линиями
            # длина ограничивающей рамки
            n_lines = len(bbox[0])
            cv2.putText(img, data, tuple(bbox[0][0].astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            for i in range(n_lines):
                # рисуем все линии
                point1 = tuple(bbox[0][i].astype(int))
                point2 = tuple(bbox[0][(i + 1) % n_lines].astype(int))
                cv2.line(img,
                         point1,
                         point2,
                         color=(255, 0, 0),
                         thickness=2)

        return img

    def roll(self):

        print("[INFO] starting video stream...")
        vs = VideoStream(src=self.camera_num).start()
        # warm up
        time.sleep(2.0)

        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width=400)

            frame = self.face_detection(frame)
            detector = cv2.QRCodeDetector()
            frame = self.scan_code(frame, detector)

            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) == ord("q"):
                break

        cv2.destroyAllWindows()
        vs.stop()


def create_code(num, name):
    """
    скорее всего будем создавать индивидуальный номер для каждого документа, книги и тп.
    :param num: индивидуальный номер
    :param name: название картинки (без расширения)
    """
    # в конструкторе задается размер картинки
    code = qr.QRCode(3, box_size=12, border=3)

    code.add_data(num)
    img = code.make_image()
    img.save(name + '.png')


camera = Camera(0)
camera.roll()
