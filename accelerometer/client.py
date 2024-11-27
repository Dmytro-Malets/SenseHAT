import os
import sys
import time
from collections import deque
import numpy as np
import pyqtgraph as pg
import requests
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
                               QPushButton, QFrame)
from dotenv import load_dotenv
# Load variables from .env file
load_dotenv()


def estimate_earthquake_intensity(pga):
    """
    Estimates earthquake intensity based on Peak Ground Acceleration (PGA)
    pga: peak ground acceleration in g units
    """
    if pga < 0.015:
        return "No Seismic Activity", "lightblue"
    elif pga < 0.022:
        return "Micro Seismic Vibrations (1-2 points)", "green"
    elif pga < 0.05:
        return "Weak Earthquake (3-4 points)", "yellow"
    elif pga < 0.1:
        return "Moderate Earthquake (5 points)", "orange"
    elif pga < 0.2:
        return "Very Strong Earthquake (7 points)", "red"
    elif pga < 0.4:
        return "Destructive Earthquake (8 points)", "darkred"
    else:
        return "Catastrophic Earthquake (9+ points)", "purple"


class AccelerometerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Sense HAT Accelerometer Monitoring")
        self.setGeometry(100, 100, 1200, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Group for current values
        values_group = QGroupBox("Current Accelerometer Values")
        values_layout = QHBoxLayout()

        self.x_frame = self.create_value_frame("X Axis", "red")
        self.y_frame = self.create_value_frame("Y Axis", "green")
        self.z_frame = self.create_value_frame("Z Axis", "blue")

        values_layout.addWidget(self.x_frame['frame'])
        values_layout.addWidget(self.y_frame['frame'])
        values_layout.addWidget(self.z_frame['frame'])
        values_group.setLayout(values_layout)
        main_layout.addWidget(values_group)

        # Earthquake analysis group
        earthquake_group = QGroupBox("Seismic Activity Analysis")
        earthquake_layout = QVBoxLayout()

        # PGA value
        self.pga_label = QLabel("Peak Ground Acceleration (PGA): 0.000 g")
        self.pga_label.setFont(QFont("Arial", 12))
        earthquake_layout.addWidget(self.pga_label)

        # Intensity estimation
        self.intensity_label = QLabel("Intensity: No Data")
        self.intensity_label.setFont(QFont("Arial", 12, QFont.Bold))
        earthquake_layout.addWidget(self.intensity_label)

        earthquake_group.setLayout(earthquake_layout)
        main_layout.addWidget(earthquake_group)

        # Graph setup
        self.setup_plot(main_layout)

        # Control buttons
        control_layout = QHBoxLayout()

        clear_button = QPushButton("Clear Graph")
        clear_button.clicked.connect(self.clear_graph)
        control_layout.addWidget(clear_button)

        pause_button = QPushButton("Pause")
        pause_button.setCheckable(True)
        pause_button.clicked.connect(self.toggle_pause)
        control_layout.addWidget(pause_button)

        main_layout.addLayout(control_layout)

        # Connection status
        self.status_label = QLabel("Status: Waiting for data...")
        self.status_label.setStyleSheet("color: orange")
        main_layout.addWidget(self.status_label)

        # Using deque to limit data points
        self.max_points = 100
        self.times = deque(maxlen=self.max_points)
        self.x_data = deque(maxlen=self.max_points)
        self.y_data = deque(maxlen=self.max_points)
        self.z_data = deque(maxlen=self.max_points)
        self.pga_data = deque(maxlen=self.max_points)

        self.start_time = time.time()
        self.paused = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)

        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start(200)

    def setup_plot(self, main_layout):
        graph_group = QGroupBox("Acceleration Graph")
        graph_layout = QVBoxLayout()

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Acceleration (g)')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.addLegend()
        self.plot_widget.setClipToView(True)
        self.plot_widget.setDownsampling(auto=True, mode='peak')
        self.plot_widget.setAntialiasing(False)

        self.plot_widget.getPlotItem().getAxis('left').enableAutoSIPrefix(False)
        self.plot_widget.getPlotItem().getAxis('bottom').enableAutoSIPrefix(False)

        pen_width = 1.5
        self.x_line = self.plot_widget.plot(pen=pg.mkPen(color=(255, 0, 0), width=pen_width), name='X Axis')
        self.y_line = self.plot_widget.plot(pen=pg.mkPen(color=(0, 255, 0), width=pen_width), name='Y Axis')
        self.z_line = self.plot_widget.plot(pen=pg.mkPen(color=(0, 0, 255), width=pen_width), name='Z Axis')
        self.pga_line = self.plot_widget.plot(pen=pg.mkPen(color=(128, 0, 128), width=pen_width), name='PGA')

        graph_layout.addWidget(self.plot_widget)
        graph_group.setLayout(graph_layout)
        main_layout.addWidget(graph_group)

    def create_value_frame(self, title, color):
        frame = QFrame()
        frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        frame.setLineWidth(2)
        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-weight: bold")
        title_label.setAlignment(Qt.AlignCenter)

        value_label = QLabel("0.000")
        value_label.setFont(QFont("Arial", 20))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color}")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        frame.setLayout(layout)

        return {'frame': frame, 'value_label': value_label}

    def toggle_pause(self, checked):
        self.paused = checked
        sender = self.sender()
        sender.setText("Continue" if checked else "Pause")

    def clear_graph(self):
        self.times.clear()
        self.x_data.clear()
        self.y_data.clear()
        self.z_data.clear()
        self.pga_data.clear()
        self.start_time = time.time()
        self.update_plot()

    def update_plot(self):
        if not self.times or self.paused:
            return

        times_array = np.array(self.times)
        relative_times = times_array - self.start_time

        self.x_line.setData(relative_times, np.array(self.x_data))
        self.y_line.setData(relative_times, np.array(self.y_data))
        self.z_line.setData(relative_times, np.array(self.z_data))
        self.pga_line.setData(relative_times, np.array(self.pga_data))

    def update_data(self):
        def calculate_pga(x, y, z):
            # Deviation from normal state
            x_dev = abs(x)  # deviation in X from 0
            y_dev = abs(y)  # deviation in Y from 0
            z_dev = abs(z - 0.978)  # deviation in Z from 1g

            # Take maximum deviation as PGA
            return max(x_dev, y_dev, z_dev)
        if self.paused:
            return

        try:
            RASPBERRY_PI_IP = os.environ.get("RASPBERRY_PI_LOCAL_IP")
            response = requests.get(f'http://{RASPBERRY_PI_IP}:5003/get_acceleration', timeout=0.5)
            data = response.json()

            # Update axis values
            self.x_frame['value_label'].setText(f"{data['x']:.3f} g")
            self.y_frame['value_label'].setText(f"{data['y']:.3f} g")
            self.z_frame['value_label'].setText(f"{data['z']:.3f} g")

            # Calculate PGA
            pga = calculate_pga(data['x'], data['y'], data['z'])

            # Update graph data
            self.times.append(data['timestamp'])
            self.x_data.append(data['x'])
            self.y_data.append(data['y'])
            self.z_data.append(data['z'])
            self.pga_data.append(pga)

            # Update PGA and intensity
            self.pga_label.setText(f"Peak Ground Acceleration (PGA): {pga:.3f} g")
            intensity, color = estimate_earthquake_intensity(pga)
            self.intensity_label.setText(f"Intensity: {intensity}")
            self.intensity_label.setStyleSheet(f"color: {color}")

            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet("color: green")

        except Exception as e:
            self.status_label.setText(f"Status: Connection Error")
            self.status_label.setStyleSheet("color: red")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AccelerometerWindow()
    window.show()
    sys.exit(app.exec())