import sys, os
import sqlite3
from datetime import datetime
import requests
import pyqtgraph as pg
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QTabWidget)
from PySide6.QtCore import QTimer, Qt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        # Convert timestamp to human-readable time format
        return [datetime.fromtimestamp(value).strftime('%H:%M:%S') for value in values]


class EnvironmentMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Environment Parameters Monitoring")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize database
        self.init_database()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create real-time display tab
        self.real_time_tab = QWidget()
        self.tabs.addTab(self.real_time_tab, "Current Values")

        # Create graphs tab
        self.graphs_tab = QWidget()
        self.tabs.addTab(self.graphs_tab, "Graphs")

        self.setup_real_time_tab()
        self.setup_graphs_tab()

        # Setup update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000)  # Update every 2 seconds

    def init_database(self):
        # Initialize SQLite database and create readings table
        conn = sqlite3.connect('environment_data.db')
        c = conn.cursor()
        # Drop existing table and create new one
        c.execute("DROP TABLE IF EXISTS readings")
        c.execute('''CREATE TABLE readings
                    (timestamp TEXT, temperature REAL, humidity REAL, pressure REAL)''')
        conn.commit()
        conn.close()

    def setup_real_time_tab(self):
        # Create layout for real-time data display
        layout = QVBoxLayout(self.real_time_tab)

        # Create containers for each measurement
        temp_container = QWidget()
        humidity_container = QWidget()
        pressure_container = QWidget()

        # Set up layouts for containers
        temp_layout = QVBoxLayout(temp_container)
        humidity_layout = QVBoxLayout(humidity_container)
        pressure_layout = QVBoxLayout(pressure_container)

        # Create labels for values with styling
        self.temp_label = QLabel("Temperature: --°C")
        self.humidity_label = QLabel("Humidity: --%")
        self.pressure_label = QLabel("Pressure: -- mbar")

        # Style labels
        style = """
            QLabel {
                font-size: 24px;
                padding: 20px;
                border: 2px solid #444;
                border-radius: 10px;
                background-color: #f0f0f0;
            }
        """

        for label in [self.temp_label, self.humidity_label, self.pressure_label]:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(style)

        # Add labels to their respective layouts
        temp_layout.addWidget(self.temp_label)
        humidity_layout.addWidget(self.humidity_label)
        pressure_layout.addWidget(self.pressure_label)

        # Add containers to main layout with spacing
        layout.addWidget(temp_container)
        layout.addSpacing(20)
        layout.addWidget(humidity_container)
        layout.addSpacing(20)
        layout.addWidget(pressure_container)

        # Add stretch to center widgets vertically
        layout.addStretch()

    def setup_graphs_tab(self):
        # Create graphs tab with custom time axis
        layout = QVBoxLayout(self.graphs_tab)

        # Create plot widgets with custom time axis
        self.temp_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.humidity_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.pressure_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})

        # Set titles and labels
        self.temp_plot.setTitle("Temperature", color='w', size='20pt')
        self.humidity_plot.setTitle("Humidity", color='w', size='20pt')
        self.pressure_plot.setTitle("Pressure", color='w', size='20pt')

        self.temp_plot.setLabel('left', 'Temperature', units='°C', color='w', size='16pt')
        self.humidity_plot.setLabel('left', 'Humidity', units='%', color='w', size='16pt')
        self.pressure_plot.setLabel('left', 'Pressure', units='mbar', color='w', size='16pt')

        # Customize plots
        for plot in [self.temp_plot, self.humidity_plot, self.pressure_plot]:
            plot.setLabel('bottom', 'Time', color='w', size='16pt')
            plot.showGrid(x=True, y=True)
            plot.setBackground('black')
            plot.getAxis('left').setTextPen('w')
            plot.getAxis('bottom').setTextPen('w')
            layout.addWidget(plot)

        # Create plot curves with thicker lines
        self.temp_curve = self.temp_plot.plot(pen=pg.mkPen('r', width=2))
        self.humidity_curve = self.humidity_plot.plot(pen=pg.mkPen('b', width=2))
        self.pressure_curve = self.pressure_plot.plot(pen=pg.mkPen('g', width=2))

        # Initialize data storage lists
        self.timestamps = []
        self.temperatures = []
        self.humidities = []
        self.pressures = []

    def update_data(self):
        try:
            # Get data from Raspberry Pi server
            RASPBERRY_PI_IP = os.environ.get("RASPBERRY_PI_LOCAL_IP")
            response = requests.get(f'http://{RASPBERRY_PI_IP}:5001/data')
            data = response.json()

            # Update labels with colors based on values
            temp = data['temperature']
            temp_color = '#ff0000' if temp > 30 else '#000000'
            self.temp_label.setText(f"Temperature: {temp}°C")
            self.temp_label.setStyleSheet(f"""
                font-size: 24px;
                padding: 20px;
                border: 2px solid #444;
                border-radius: 10px;
                background-color: #f0f0f0;
                color: {temp_color};
            """)

            humidity = data['humidity']
            humidity_color = '#0000ff' if humidity > 60 else '#000000'
            self.humidity_label.setText(f"Humidity: {humidity}%")
            self.humidity_label.setStyleSheet(f"""
                font-size: 24px;
                padding: 20px;
                border: 2px solid #444;
                border-radius: 10px;
                background-color: #f0f0f0;
                color: {humidity_color};
            """)

            pressure = data['pressure']
            pressure_color = '#00ff00' if 980 <= pressure <= 1020 else '#000000'
            self.pressure_label.setText(f"Pressure: {pressure} mbar")
            self.pressure_label.setStyleSheet(f"""
                font-size: 24px;
                padding: 20px;
                border: 2px solid #444;
                border-radius: 10px;
                background-color: #f0f0f0;
                color: {pressure_color};
            """)

            # Save to database
            conn = sqlite3.connect('environment_data.db')
            c = conn.cursor()
            c.execute("INSERT INTO readings VALUES (?,?,?,?)",
                      (data['timestamp'], temp, humidity, pressure))
            conn.commit()
            conn.close()

            # Update graphs
            current_time = time.time()
            self.timestamps.append(current_time)
            self.temperatures.append(temp)
            self.humidities.append(humidity)
            self.pressures.append(pressure)

            # Keep only last 50 points
            if len(self.timestamps) > 50:
                self.timestamps = self.timestamps[-50:]
                self.temperatures = self.temperatures[-50:]
                self.humidities = self.humidities[-50:]
                self.pressures = self.pressures[-50:]

            # Update plot curves
            self.temp_curve.setData(self.timestamps, self.temperatures)
            self.humidity_curve.setData(self.timestamps, self.humidities)
            self.pressure_curve.setData(self.timestamps, self.pressures)

        except Exception as e:
            print(f"Error updating data: {e}")
            # Update labels to show error state
            error_style = """
                font-size: 24px;
                padding: 20px;
                border: 2px solid #ff0000;
                border-radius: 10px;
                background-color: #ffe0e0;
                color: #ff0000;
            """
            self.temp_label.setStyleSheet(error_style)
            self.humidity_label.setStyleSheet(error_style)
            self.pressure_label.setStyleSheet(error_style)
            self.temp_label.setText("Connection Error")
            self.humidity_label.setText("Connection Error")
            self.pressure_label.setText("Connection Error")


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show window
    window = EnvironmentMonitor()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()