import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore

class VideoFilterApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Default settings
        self.dot_size = 10
        self.use_adaptive = False
        self.use_dithering = False

        self.initUI()
        # Open video capture (0 for default webcam; change path for video file)
        self.cap = cv2.VideoCapture(0)

        # Timer to update frames at approximately 30 FPS
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def initUI(self):
        self.setWindowTitle('Video Filter App with Advanced Features')
        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        # Slider for dot size
        self.dot_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.dot_slider.setMinimum(1)
        self.dot_slider.setMaximum(50)
        self.dot_slider.setValue(self.dot_size)
        self.dot_slider.valueChanged.connect(self.slider_changed)

        # Checkbox for adaptive thresholding
        self.adaptive_checkbox = QtWidgets.QCheckBox("Adaptive Thresholding")
        self.adaptive_checkbox.stateChanged.connect(self.adaptive_changed)

        # Checkbox for dithering effect
        self.dithering_checkbox = QtWidgets.QCheckBox("Dithering (Floyd–Steinberg)")
        self.dithering_checkbox.stateChanged.connect(self.dithering_changed)

        # Layout organization
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(QtWidgets.QLabel("Dot Size"))
        layout.addWidget(self.dot_slider)
        layout.addWidget(self.adaptive_checkbox)
        layout.addWidget(self.dithering_checkbox)
        self.setLayout(layout)

    def slider_changed(self, value):
        self.dot_size = value

    def adaptive_changed(self, state):
        self.use_adaptive = (state == QtCore.Qt.Checked)

    def dithering_changed(self, state):
        self.use_dithering = (state == QtCore.Qt.Checked)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            processed = self.process_frame(frame, self.dot_size,
                                           adaptive=self.use_adaptive,
                                           dithering=self.use_dithering)
            # Convert processed frame (BGR) to QImage for display
            height, width, channel = processed.shape
            bytesPerLine = 3 * width
            qImg = QtGui.QImage(processed.data, width, height, bytesPerLine,
                                QtGui.QImage.Format_BGR888)
            self.image_label.setPixmap(QtGui.QPixmap.fromImage(qImg))

    def process_frame(self, frame, dot_size, adaptive=False, dithering=False,
                      default_threshold=127):
        """
        Process the frame to render it as an array of black and white dots.
        Options:
            adaptive: use adaptive thresholding.
            dithering: apply Floyd–Steinberg dithering.
        """
        # For GPU acceleration:
        # If cv2.cuda.getCudaEnabledDeviceCount() > 0, you can upload the frame to GPU
        # and perform cv2.cuda.cvtColor and cv2.cuda.threshold.
        # For demonstration, we use CPU processing.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Optional dithering step: redistributes quantization errors for a smoother effect.
        if dithering:
            gray = self.floyd_steinberg_dithering(gray)

        # Thresholding: choose adaptive or fixed threshold
        if adaptive:
            # The blockSize should be an odd number; C is a constant subtracted from the mean.
            thresh = cv2.adaptiveThreshold(gray, 255,
                                           cv2.ADAPTIVE_THRESH_MEAN_C,
                                           cv2.THRESH_BINARY, 11, 2)
        else:
            _, thresh = cv2.threshold(gray, default_threshold, 255, cv2.THRESH_BINARY)

        # Create a blank output image (3 channels for display)
        output = np.zeros_like(frame)
        h, w = thresh.shape

        # Process the image in blocks of size (dot_size x dot_size)
        for y in range(0, h, dot_size):
            for x in range(0, w, dot_size):
                # Define block boundaries (take care at edges)
                block = thresh[y:min(y+dot_size, h), x:min(x+dot_size, w)]
                # Compute the average intensity in the block
                avg_intensity = np.mean(block)
                # Decide dot color: if average is above 127, white; otherwise, black.
                color = 255 if avg_intensity > 127 else 0
                # Compute center of the block
                center_x = x + int(min(dot_size, w - x) / 2)
                center_y = y + int(min(dot_size, h - y) / 2)
                # Draw a filled circle (dot) with radius ~half the block size
                cv2.circle(output, (center_x, center_y), int(dot_size / 2), (color, color, color), -1)
        return output

    def floyd_steinberg_dithering(self, image):
        """
        Apply Floyd–Steinberg dithering to a grayscale image.
        This algorithm processes each pixel and diffuses the quantization error to
        neighboring pixels.
        """
        # Convert image to float32 for error diffusion
        image = image.astype(np.float32)
        h, w = image.shape
        for y in range(h):
            for x in range(w):
                old_pixel = image[y, x]
                # Quantize the pixel: threshold at 127
                new_pixel = 255 if old_pixel > 127 else 0
                image[y, x] = new_pixel
                error = old_pixel - new_pixel
                # Distribute the error to neighboring pixels
                if x + 1 < w:
                    image[y, x+1] += error * 7 / 16
                if y + 1 < h:
                    if x > 0:
                        image[y+1, x-1] += error * 3 / 16
                    image[y+1, x] += error * 5 / 16
                    if x + 1 < w:
                        image[y+1, x+1] += error * 1 / 16
        # Ensure the pixel values remain within [0, 255]
        return np.clip(image, 0, 255).astype(np.uint8)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = VideoFilterApp()
    window.show()
    sys.exit(app.exec_())
