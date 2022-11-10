import qrcode as qr
import cv2


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


def scan_code(img, detector):
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
            point2 = tuple(bbox[0][(i+1) % n_lines].astype(int))
            cv2.line(img,
                     point1,
                     point2,
                     color=(255, 0, 0),
                     thickness=2)

    return img

    cv2.imshow("img", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return data


detector = cv2.QRCodeDetector()
cap = cv2.VideoCapture(0)
while True:
    _, img = cap.read()

    img = scan_code(img, detector)

    cv2.imshow('img', img)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

