# SenseHAT Interactive Sensor and Visualization Project

## Project Overview
Disclaimer: This project provides a foundational framework of minimal, educational applications designed to demonstrate the Raspberry Pi SenseHAT's capabilities. These initial implementations serve as a strategic starting point for developers, students, and hobbyists to explore and expand sensor data visualization and interactive programming.

Purpose and Potential:
The modules presented here are intentionally kept simple and focused, serving as a launchpad for innovation. They are not meant to be final products, but rather inspirational blueprints that invite creativity and personal enhancement. Each component is engineered to be:
- Easily understandable
- Straightforward to modify
- Extensible with advanced features
- A learning resource for sensor interaction and data visualization

Developers are encouraged to:

- Experiment with more complex visualization techniques
- Implement advanced data processing algorithms
- Design more sophisticated user interfaces
- Add machine learning predictions
- Create novel interactive experiences

This project is a multi-component application designed to leverage the capabilities of the Raspberry Pi Sense HAT Version 1.0, providing interactive sensor data visualization and engaging interactive experiences. The system is architected as a client-server application that enables real-time sensor data retrieval, processing, and visualization across different modules.

### Key Components and Functionality

The project consists of several key modules:

1. **Gyroscope Module**: 
   - Provides real-time orientation data through a Flask server
   - Implements advanced quaternion-based smoothing for fluid 3D visualization
   - Enables precise tracking of device orientation in three-dimensional space

2. **Snake Game Module**:
   - A sophisticated implementation of the classic Snake game
   - Utilizes SenseHAT's LED matrix for rendering
   - Features multiple difficulty levels with progressively complex game mechanics
   - Includes dynamic wall generation and adaptive game speed

3. **Accelerometer Module**:
   - Real-time seismic activity monitoring and visualization
   - Advanced Peak Ground Acceleration (PGA) calculation
   - Interactive graphical interface with:
     * Precise 3-axis acceleration data display
     * Dynamic earthquake intensity estimation
     * Real-time acceleration plotting
     * Customizable data visualization controls
   - Earthquake intensity classification based on acceleration metrics
   - Robust error handling and connection management

4. **TPH (Temperature, Pressure, Humidity) Module**:
   - Comprehensive environmental parameter monitoring
   - Real-time data collection from SenseHAT sensors
   - Dual-view interface:
     * Current values display with dynamic color-coded indicators
     * Detailed time-series graphical representations
   - SQLite database integration for persistent data logging
     * Automatic database initialization
     * Continuous sensor reading storage
   - Configurable update intervals
   - Adaptive UI with error state handling
   - Advanced data visualization using custom time-axis plotting

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Dmytro-Malets/SenseHAT.git
```
```bash
cd SenseHAT
```

### 2. Configure Environment Variables

```bash
cp .env.template .env
```

Edit the `.env` file and replace `YOUR_RASPBERRY_PI_LOCAL_IP` with your Raspberry Pi's local IP address.

### 3. Create and Activate Virtual Environment for client and Raspberry Pi
#### Unix/macOS:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
#### Windows:
```bash
python -m venv venv
```
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

#### For Client Machine:
```bash
pip install -r requirements/client/requirements.txt
```

#### For Raspberry Pi:
```bash
pip3 install -r requirements/raspberry/requirements.txt
```

### 5. Prepare Raspberry Pi (CRITICAL SETUP STEP)

On your Raspberry Pi, execute the following commands:

```bash
git clone https://github.com/RPi-Distro/RTIMULib
```
```bash
cd RTIMULib/Linux/python
```
```bash
python3 setup.py build
```
```bash
python3 setup.py install
```
```bash
cd ../../..
```



## Running the Modules

### Starting Server Components on Raspberry Pi

To run the server components for different modules, use the following commands:
#### Gyroscope Server
```bash
python3 gyroscope/server.py
```
#### Accelerometer Server
```bash
python3 accelerometer/server.py
```
#### Temperature, Pressure, Humidity (TPH) Server
```bash
python3 TPH/server.py
```
#### Snake Game
```bash
python3 snake/snake.py
```

### Starting Client Applications

On your client machine, launch the respective client applications:
#### Gyroscope Visualization
```bash
python gyroscope/client.py
```
#### Accelerometer Monitoring
```bash
python accelerometer/client.py
```
#### Temperature, Pressure, Humidity Monitoring
```bash
python TPH/client.py
```

## Troubleshooting

- Ensure network connectivity between devices
- Verify IP address in `.env` file
- Check Python and library versions
- Confirm SenseHAT is properly connected

### Project Structure

```
SenseHAT/
│
├── accelerometer/
│   ├── client.py
│   └── server.py
│
├── gyroscope/
│   ├── client.py
│   └── server.py
│
├── TPH/
│   ├── client.py
│   ├── server.py
│   └── environment_data.db
│
├── snake/
│   └── snake.py
│
├── requirements/
│   ├── client/
│   │   └── requirements.txt
│   └── raspberry/
│       └── requirements.txt
│
├── .env
├── .env.template
├── .gitignore
├── README.md
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues for any improvements or bug fixes.

## Acknowledgements
- SenseHAT Documentation - https://pythonhosted.org/sense-hat/
