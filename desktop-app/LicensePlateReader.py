# Importing necessary libraries and modules
import sys
import os

# Uncomment these when converting this .py file to .exe
sys.stdout = open(os.devnull, "w")
sys.stderr = open(os.path.join(os.getenv("TEMP"), "stderr-"+os.path.basename(sys.argv[0])), "w")

from ultralytics import YOLO
import easyocr
import cv2
from os import listdir
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont, QFontDatabase
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import math
import multiprocessing

# Optimize application to scale on any resolution
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

# Custom thread class for license plate detection and OCR
class LicensePlateDetectionAndOCR(QThread):
    processingFinished = pyqtSignal(QImage)
    stopRequested = pyqtSignal()

    # Initialization method for the thread
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
        self.cap.set(3, 480)
        self.cap.set(4, 250)

        # Initializing YOLO model for license plate detection
        self.model = YOLO("LicensePlateReader.pt")
        self.classNames = ["plate"]

        # Initializing OCR reader
        self.reader = easyocr.Reader(['en'], gpu=True)

        self.save_path = "saved_images"
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    # Method to perform OCR on an image
    def perform_ocr_on_image(self, img):
        try:
            gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            results = self.reader.readtext(gray_img)
            text = ""
            if len(results) == 1:
                text = results[0][1]
            elif results:
                for res in results:
                    if res[2] > 0.2:
                        text = res[1]
                        break
            return text
        except Exception as e:
            print(f"Error performing OCR: {e}")

    # Run method for thread execution
    def run(self):
        while True:
            if self.cap.isOpened():
                ret, img = self.cap.read()
                if not ret:
                    break
            else:
                break

            results = self.model(img, save_crop=True, conf=0.5)  # Adjust confidence threshold here

            plate_texts = []  # Store the texts of all detected license plates
            for r in results:
                boxes = r.boxes

                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values

                    width = x2 - x1
                    height = y2 - y1

                    x1 = max(0, x1 - width // 4)
                    x2 = min(img.shape[1], x2 + width // 4)
                    y1 = max(0, y1 - height // 4)
                    y2 = min(img.shape[0], y2 + height // 4)

                    plate_img = img[y1:y2, x1:x2]

                    text = self.perform_ocr_on_image(plate_img)

                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

                    confidence = math.ceil((box.conf[0] * 100)) / 100
                    cls = int(box.cls[0])

                    org = [x1, y1]
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    fontScale = 1
                    color = (0, 255, 255)
                    thickness = 2

                    cv2.putText(img, f"{self.classNames[cls]}: {text}", org, font, fontScale, color, thickness)

                    plate_texts.append(text)  # Store the text of the current license plate

            # Display all license plate texts on the side
            for i, text in enumerate(plate_texts):
                cv2.putText(img, f"Plate {i+1}: {text}", (20, 30 * (i+1)), font, 0.7, (255, 255, 0), 2)

            save_img_path = os.path.join(self.save_path, "captured_image.jpg")
            cv2.imwrite(save_img_path, img)

            q_img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
            self.processingFinished.emit(q_img)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        self.cap.release()

    # Method to stop the thread execution
    def stop(self):
        self.cap.release()
        self.quit()

# Welcome screen class for the application
class welcomeScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 200, 575, 575)
        self.setFixedSize(575, 350)
        self.setStyleSheet("QMainWindow {background-color: #FFB700; border-radius: 5000px;}")
        self.setWindowTitle('B&B License Plate Detector')

        QFontDatabase.addApplicationFont("src/fonts/sailors.otf")
        QFontDatabase.addApplicationFont("Src/fonts/IntroRust-Base.otf")
        QFontDatabase.addApplicationFont("Src/fonts/AdamScript.ttf")

        #Initializing Font Styles
        namefont = QFont("Intro Rust")
        namefont.setPointSize(30)

        titlefont1 = QFont("Sailors")
        titlefont1.setPointSize(59)

        titlefont2 = QFont("RTL-Adam Script")
        titlefont2.setPointSize(39)
        
        buttonfont = QFont("Intro Rust")
        buttonfont.setPointSize(22)

        #Background image
        trafficbg = "src/images/welcomeScreen-bg.jpg"
        pixmap = QPixmap(trafficbg)
        scaled_pixmap = pixmap.scaledToWidth(575, Qt.SmoothTransformation)

        trafficset= QLabel(self)
        trafficset.setPixmap(scaled_pixmap)
        trafficset.setGeometry(QtCore.QRect(0, 0, 575, 350))

        # BATO & BERNAL
        names = QtWidgets.QLabel(self)
        names.setText("Bato & Bernal")
        names.setGeometry(QtCore.QRect(132, -52, 900, 201)) #(left-margin, top-margin, width, height)
        names.setWordWrap(False)
        names.setFont(namefont)
        names.setStyleSheet("QLabel {color: #FFB700}")
        # color: #FFB700 = orange

        # LICENSE PLATE
        title1 = QtWidgets.QLabel(self)
        title1.setText("License Plate")
        title1.setGeometry(QtCore.QRect(54, 69, 950, 201)) #(left-margin, top-margin, width, height)
        title1.setWordWrap(False)
        title1.setFont(titlefont1)
        title1.setStyleSheet("QLabel {color: #081F2D}")
        # color: #081F2D = dark blue

        #   detector
        title2 = QtWidgets.QLabel(self)
        title2.setText("detector")
        title2.setGeometry(QtCore.QRect(202, 153, 950, 201)) #(left-margin, top-margin, width, height)
        title2.setWordWrap(False)
        title2.setFont(titlefont2)
        title2.setStyleSheet("QLabel {color: #081F2D}")

        # START BTN
        proceed = QtWidgets.QPushButton(self)
        proceed.setEnabled(True)
        proceed.setGeometry(QtCore.QRect(-126, 277, 450, 90)) #(left-margin, top-margin, width, height)
        proceed.setFont(buttonfont)
        proceed.setText("START")
        proceed.setStyleSheet("""QPushButton {background-color: rgba(255, 255, 255, 0);  color: #FFB700;} 
                              QPushButton:hover {color: rgba(255, 226, 153, 1)}""")
        proceed.clicked.connect(self.proceedToNext)

        # EXIT BTN
        exit = QtWidgets.QPushButton(self)
        exit.setEnabled(True)
        exit.setGeometry(QtCore.QRect(258, 277, 450, 90)) #(left-margin, top-margin, width, height)
        exit.setFont(buttonfont)
        exit.setText("EXIT")
        exit.setStyleSheet("""QPushButton {background-color: rgba(255, 255, 255, 0);  color: #FFB700;} 
                              QPushButton:hover {color: rgba(255, 226, 153, 1)}""")
        exit.clicked.connect(self.closeApp)

    # Method to proceed to the next window
    def proceedToNext(self):
        self.hide()
        self.second_wind = camWindow()
        self.second_wind.show()

    # Method to close the application
    def closeApp(self):
        self.close()

# Camera window class for the application
class camWindow(QMainWindow):
    def __init__(self):
        # Camera Window Features
        super(camWindow, self).__init__()
        self.setGeometry(300, 200, 575, 575)
        self.setFixedSize(575, 350)
        self.setStyleSheet("QMainWindow {background-color: #081F2D}")
        self.setWindowTitle('B&B License Plate Detector')

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Initialize Font Styles
        camfont = QFont("Intro Rust")
        camfont.setPointSize(23)

        buttonfont = QFont("Intro Rust")
        buttonfont.setPointSize(20)

        self.VBL = QVBoxLayout()
        self.HBL = QHBoxLayout()

        self.FeedLabel = QLabel()
        self.FeedLabel.setStyleSheet("border: 5px solid rgba(255, 183, 0, 1); color: #081F2D; background-color: #FFB700;")
        self.FeedLabel.setText("Starting camera...")
        self.FeedLabel.setMinimumSize(550, 280)
        self.FeedLabel.setFont(camfont)
        self.FeedLabel.setAlignment(Qt.AlignCenter)
        self.VBL.addWidget(self.FeedLabel, alignment=Qt.AlignCenter)
        
        self.Vbuttons = QVBoxLayout()
        spacer = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Maximum)

        # Exit Button
        self.exitBTN = QPushButton("EXIT")
        self.exitBTN.setMinimumSize(100, 40)
        self.exitBTN.clicked.connect(self.ExitFeed)
        self.exitBTN.setFont(buttonfont)
        self.exitBTN.setStyleSheet("""QPushButton {background-color: #FFB700; border: 0px solid rgba(238, 157, 40, 1);  color: #081F2D; border-radius: 5px;} 
                              QPushButton:hover {background-color: rgba(255, 226, 153, 1); border: 1px solid rgba(0, 0, 0, 0.5)}""")
        self.Vbuttons.addWidget(self.exitBTN, alignment=Qt.AlignCenter)

        # Layout
        self.HBL.addItem(spacer)
        self.HBL.addLayout(self.Vbuttons)
        self.VBL.addLayout(self.HBL)
        central_widget.setLayout(self.VBL)
    
        # Functionality of Thread
        self.detector = LicensePlateDetectionAndOCR()
        self.detector.processingFinished.connect(self.ImageUpdateSlot)
        self.detector.start()

    # Method to update the image in the camera feed
    def ImageUpdateSlot(self, q_image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(q_image))

    # Method to exit the camera feed window
    def ExitFeed(self):
        self.detector.stopRequested.emit()
        self.close()

# Main function to start the application
def main():
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    startingWindow = welcomeScreen()
    startingWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
