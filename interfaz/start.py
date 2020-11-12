from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
import drone as dr
import numpy as np
import traceback
import tellopy
import time
import cv2
import sys
import av

container = None

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    def run(self):

        # skip first 300 frames
        while True:
            for frame in container.decode(video=0):
                # start_time = time.time()
                rgbImage = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                # frame_red = cv2.resize(image,(128,128))
                # dr.proof(frame_red)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
                


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('interfaz.ui', self)
        self.conexion_establecida = False
        self.StartButton.clicked.connect(self.start_drone)
        self.PictureButton.clicked.connect(self.take_picture)
        self.close_button.clicked.connect(self.close_conection)
        self.close_button.clicked.connect(self.close_conection)
        self.CameraLabel.hide()
        self.show()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.CameraLabel.setPixmap(QPixmap.fromImage(image))

    def start_drone(self):
        global container
        container = dr.start_drone()
        self.CameraLabel.show()
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
        self.StartButton.hide()

            
    
    def take_picture(self):
        self.drone.take_picture()

    def palm_land(self):
        self.drone.palm_land()

    def close_conection(self):
        self.drone.quit()

    def land(self):
        self.drone.land()

app = QApplication(sys.argv)
ex2 = MainWindow()
ex2.setWindowTitle("Control de Drone")
ex2.show()
sys.exit(app.exec_())
