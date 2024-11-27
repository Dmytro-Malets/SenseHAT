import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import requests
from threading import Thread
import queue
import time
import numpy as np
import os
from collections import deque
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()
# Parameters for data storage and smoothing
current_quaternion = np.array([1, 0, 0, 0])
quaternion_buffer = deque(maxlen=10)  # Buffer for quaternion smoothing
data_queue = queue.Queue()


def slerp(q1, q2, t):
    """Spherical Linear Interpolation between quaternions"""
    # Normalize quaternions
    q1 = q1 / np.linalg.norm(q1)
    q2 = q2 / np.linalg.norm(q2)

    # Calculate cosine of angle between quaternions
    dot = np.sum(q1 * q2)

    # If quaternions are very close, perform linear interpolation
    if dot > 0.9995:
        return q1 + t * (q2 - q1)

    # Ensure shortest path
    if dot < 0:
        q2 = -q2
        dot = -dot

    theta = np.arccos(dot)
    sin_theta = np.sin(theta)

    # Perform SLERP
    s1 = np.sin((1 - t) * theta) / sin_theta
    s2 = np.sin(t * theta) / sin_theta

    return (q1 * s1) + (q2 * s2)


def fetch_orientation_data(server_url):
    """
    Continuously fetch orientation data from server and process quaternions

    Args:
        server_url (str): URL of the orientation data endpoint
    """
    global current_quaternion
    while True:
        try:
            response = requests.get(server_url)
            if response.status_code == 200:
                data = response.json()
                pitch = np.radians(data['yaw'])
                roll = np.radians(data['pitch'])
                yaw = np.radians(data['roll'])

                new_quaternion = np.array([
                    np.cos(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.sin(
                        pitch / 2) * np.sin(yaw / 2),
                    np.sin(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) - np.cos(roll / 2) * np.sin(
                        pitch / 2) * np.sin(yaw / 2),
                    np.cos(roll / 2) * np.sin(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.cos(
                        pitch / 2) * np.sin(yaw / 2),
                    np.cos(roll / 2) * np.cos(pitch / 2) * np.sin(yaw / 2) - np.sin(roll / 2) * np.sin(
                        pitch / 2) * np.cos(yaw / 2)
                ])

                quaternion_buffer.append(new_quaternion)

                # Smoothing via SLERP
                if len(quaternion_buffer) >= 2:
                    smooth_quaternion = quaternion_buffer[0]
                    for i in range(1, len(quaternion_buffer)):
                        t = i / len(quaternion_buffer)
                        smooth_quaternion = slerp(smooth_quaternion, quaternion_buffer[i], t)
                    current_quaternion = smooth_quaternion

            time.sleep(0.008)
        except Exception as e:
            print(f"Error fetching data: {e}")
            time.sleep(1)


def draw_cube():
    """Draw the cube with current orientation"""
    glPushMatrix()
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -9)

    # Apply smoothed quaternion
    qx, qy, qz, qw = current_quaternion
    glRotatef(np.degrees(2 * np.arccos(qw)), qx, qy, qz)

    draw_cube_geometry()
    glPopMatrix()


def draw_cube_geometry():
    """Enhanced cube drawing function with smoothing"""
    vertices = [
        [1, 1, -1], [-1, 1, -1], [-1, -1, -1], [1, -1, -1],
        [1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1]
    ]

    # Normals for each face
    normals = [
        [0, 0, -1],  # Front
        [0, 0, 1],  # Back
        [0, 1, 0],  # Top
        [0, -1, 0],  # Bottom
        [-1, 0, 0],  # Left
        [1, 0, 0],  # Right
    ]

    colors = [
        [1, 0, 0],  # Red
        [0, 1, 0],  # Green
        [0, 0, 1],  # Blue
        [1, 1, 0],  # Yellow
        [1, 0, 1],  # Magenta
        [0, 1, 1],  # Cyan
    ]

    # Vertex indices for each face
    faces = [
        [0, 1, 2, 3],  # Front
        [4, 5, 6, 7],  # Back
        [4, 0, 1, 5],  # Top
        [7, 3, 2, 6],  # Bottom
        [5, 1, 2, 6],  # Left
        [4, 0, 3, 7],  # Right
    ]

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    # Lighting setup
    glLight(GL_LIGHT0, GL_POSITION, (5.0, 5.0, 5.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))

    glBegin(GL_QUADS)
    for face_idx, face in enumerate(faces):
        glNormal3fv(normals[face_idx])
        glColor3fv(colors[face_idx])
        for vertex_idx in face:
            glVertex3fv(vertices[vertex_idx])
    glEnd()

    glDisable(GL_LIGHTING)


def init_gl(display):
    """Enhanced OpenGL initialization"""
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Enhanced smoothing
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)

    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)


def main():
    """Main application loop"""
    pygame.init()
    display = (1024, 768)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 16)  # MSAA x16
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | pygame.OPENGL)
    pygame.display.set_caption('3D Orientation Visualization with Cube')

    init_gl(display)
    glTranslatef(0.0, 0.0, -9)

    RASPBERRY_PI_IP = os.environ.get("RASPBERRY_PI_LOCAL_IP")
    server_url = f'http://{RASPBERRY_PI_IP}:5002/orientation'
    data_thread = Thread(target=fetch_orientation_data, args=(server_url,), daemon=True)
    data_thread.start()

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_cube()
        pygame.display.flip()
        clock.tick(120)


if __name__ == '__main__':
    main()