import cv2
import numpy as np
import os
from PyQt5 import QtWidgets, QtGui, QtCore

class VideoFilterApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Default settings
        self.dot_size = 10
        self.use_adaptive = False
        self.use_dithering = False

        # Video source: default to webcam; if a video file is loaded, this will be replaced
        self.cap = cv2.VideoCapture(0)
        self.video_loaded = False

        # Saving settings
        self.saving_enabled = False
        self.output_file = None
        self.video_writer = None
        self.fps = 30  # default fps for output
        self.frame_size = None

        self.initUI()

        # Timer to update frames at approximately 30 FPS
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)  # about 30ms per frame

    def initUI(self):
        self.setWindowTitle('Video Filter App with File I/O and Advanced Features')
        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Create UI controls

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

        # Button to load an input video file (.mp4)
        self.load_video_button = QtWidgets.QPushButton("Load Video")
        self.load_video_button.clicked.connect(self.load_video)

        # Checkbox to enable saving output
        self.save_checkbox = QtWidgets.QCheckBox("Save Output")
        self.save_checkbox.stateChanged.connect(self.save_checkbox_changed)
        # Button to select output file location
        self.select_output_button = QtWidgets.QPushButton("Select Output File")
        self.select_output_button.clicked.connect(self.select_output_file)
        self.select_output_button.setEnabled(False)

        # Layout organization
        control_layout = QtWidgets.QHBoxLayout()
        control_layout.addWidget(QtWidgets.QLabel("Dot Size"))
        control_layout.addWidget(self.dot_slider)
        control_layout.addWidget(self.adaptive_checkbox)
        control_layout.addWidget(self.dithering_checkbox)
        control_layout.addWidget(self.load_video_button)
        control_layout.addWidget(self.save_checkbox)
        control_layout.addWidget(self.select_output_button)
        
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)

    def slider_changed(self, value):
        self.dot_size = value

    def adaptive_changed(self, state):
        self.use_adaptive = (state == QtCore.Qt.Checked)

    def dithering_changed(self, state):
        self.use_dithering = (state == QtCore.Qt.Checked)

    def save_checkbox_changed(self, state):
        self.saving_enabled = (state == QtCore.Qt.Checked)
        # Enable or disable the output file selection button accordingly
        self.select_output_button.setEnabled(self.saving_enabled)
        # If saving was turned off, release the video writer if it was initialized.
        if not self.saving_enabled and self.video_writer:
            self.video_writer.release()
            self.video_writer = None

    def load_video(self):
        # Open a file dialog to select a .mp4 file
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mov)"
        )
        if file_name:
            # Release the previous capture if any
            if self.cap.isOpened():
                self.cap.release()
            self.cap = cv2.VideoCapture(file_name)
            self.video_loaded = True

            # Try to obtain the video's FPS and frame size for the output writer
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.frame_size = (width, height)
            print(f"Loaded video: {file_name} at {self.fps} FPS, size: {self.frame_size}")

    def select_output_file(self):
        # Open a file dialog to choose the output file name and location.
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Select Output Video File", "", "MP4 Files (*.mp4);;AVI Files (*.avi)"
        )
        if file_name:
            self.output_file = file_name
            # Initialize the VideoWriter based on the output file extension and current frame size.
            if self.frame_size is None:
                # If frame size is not yet known, try to get it from the current frame
                ret, frame = self.cap.read()
                if ret:
                    self.frame_size = (frame.shape[1], frame.shape[0])
                    # Reset the capture to the start if using a video file.
                    if self.video_loaded:
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            # Choose fourcc code based on extension (e.g., mp4 or avi)
            ext = os.path.splitext(self.output_file)[1].lower()
            if ext == ".mp4":
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            else:
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(self.output_file, fourcc, self.fps, self.frame_size)
            print(f"Output will be saved to: {self.output_file}")

    def update_frame(self):
        # Check if the video capture is open
        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            # If we're processing a file and have reached the end, stop the timer.
            if self.video_loaded:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    return
            else:
                return

        # Process the frame using our filter
        processed = self.process_frame(frame, self.dot_size,
                                       adaptive=self.use_adaptive,
                                       dithering=self.use_dithering)
        
        # If saving is enabled, write the processed frame to the video file.
        if self.saving_enabled and self.video_writer is not None:
            # Ensure processed frame size matches the writer's frame size.
            if self.frame_size is None:
                self.frame_size = (processed.shape[1], processed.shape[0])
            self.video_writer.write(processed)
        
        # Convert processed frame (BGR) to QImage for display in the UI
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
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Optional dithering step
        if dithering:
            gray = self.floyd_steinberg_dithering(gray)

        # Thresholding: choose adaptive or fixed threshold
        if adaptive:
            thresh = cv2.adaptiveThreshold(gray, 255,
                                           cv2.ADAPTIVE_THRESH_MEAN_C,
                                           cv2.THRESH_BINARY, 11, 2)
        else:
            _, thresh = cv2.threshold(gray, default_threshold, 255, cv2.THRESH_BINARY)

        # Create a blank output image (3 channels)
        output = np.zeros_like(frame)
        h, w = thresh.shape

        # Process the image in blocks of size (dot_size x dot_size)
        for y in range(0, h, dot_size):
            for x in range(0, w, dot_size):
                block = thresh[y:min(y+dot_size, h), x:min(x+dot_size, w)]
                avg_intensity = np.mean(block)
                color = 255 if avg_intensity > 127 else 0
                center_x = x + int(min(dot_size, w - x) / 2)
                center_y = y + int(min(dot_size, h - y) / 2)
                cv2.circle(output, (center_x, center_y), int(dot_size / 2), (color, color, color), -1)
        return output

    def floyd_steinberg_dithering(self, image):
        """
        Apply Floyd–Steinberg dithering to a grayscale image.
        """
        image = image.astype(np.float32)
        h, w = image.shape
        for y in range(h):
            for x in range(w):
                old_pixel = image[y, x]
                new_pixel = 255 if old_pixel > 127 else 0
                image[y, x] = new_pixel
                error = old_pixel - new_pixel
                if x + 1 < w:
                    image[y, x+1] += error * 7 / 16
                if y + 1 < h:
                    if x > 0:
                        image[y+1, x-1] += error * 3 / 16
                    image[y+1, x] += error * 5 / 16
                    if x + 1 < w:
                        image[y+1, x+1] += error * 1 / 16
        return np.clip(image, 0, 255).astype(np.uint8)

    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        event.accept()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = VideoFilterApp()
    window.show()
    sys.exit(app.exec_())
