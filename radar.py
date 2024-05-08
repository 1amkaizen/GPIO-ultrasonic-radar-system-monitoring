import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import RPi.GPIO as GPIO
import time

# Setup GPIO
GPIO.setmode(GPIO.BOARD)
PIN_TRIGGER = 7
PIN_ECHO = 11
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)

# Initialize plot
fig, ax = plt.subplots()
ax.set_xlim(-200, 200)
ax.set_ylim(-200, 200)
ax.set_aspect('equal')
ax.set_facecolor('black')

# Initialize radar background lines
num_lines = 8
theta_grid = np.linspace(0, 2*np.pi, 100)
for i in range(num_lines):
    radius = 50 * (i + 1)
    x_grid = radius * np.cos(theta_grid)
    y_grid = radius * np.sin(theta_grid)
    ax.plot(x_grid, y_grid, color='green', alpha=0.5)

# Add angle lines inside the circle
angles = [45, 90, 135, 180, 225, 270, 315]
for angle in angles:
    x_angle = 200 * np.sin(np.deg2rad(angle))
    y_angle = 200 * np.cos(np.deg2rad(angle))
    ax.plot([0, x_angle], [0, y_angle], color='green', alpha=0.5)

# Initialize radar display
radar_display, = ax.plot([], [], 'o', color='red', markersize=5)

# Initialize distance text
distance_text = ax.text(0, 0, '', color='white', ha='center', va='center')

# Initialize scanning needle
scanning_needle, = ax.plot([], [], color='yellow', linewidth=1.5)

# Initialize shadow for detected object
shadow, = ax.plot([], [], 'o', color='red', alpha=0.3, markersize=10)

# Initialize additional information text
info_text = ax.text(0, 170, 'Radar System', color='white', ha='center', va='center', fontsize=16)

def init():
    radar_display.set_data([], [])
    distance_text.set_text('')
    scanning_needle.set_data([], [])
    shadow.set_data([], [])
    info_text.set_text('')
    return radar_display, distance_text, scanning_needle, shadow, info_text

def update(frame):
    GPIO.output(PIN_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    pulse_start_time = time.time()
    pulse_end_time = time.time()

    while GPIO.input(PIN_ECHO) == 0:
        pulse_start_time = time.time()

    while GPIO.input(PIN_ECHO) == 1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    distance = pulse_duration * 17150

    if distance < 200:  # threshold for detection
        theta = np.deg2rad(frame)
        x = distance * np.sin(theta)
        y = distance * np.cos(theta)
        radar_display.set_data(x, y)
        radar_display.set_markersize(500/distance)  # Adjust marker size based on distance
        distance_text.set_text('{:.1f} cm'.format(distance))
        distance_text.set_position((x, y))
        distance_text.set_fontsize(10 + 100/distance)  # Adjust font size based on distance
        shadow.set_data(x, y)
    else:
        radar_display.set_data([], [])
        distance_text.set_text('')
        shadow.set_data([], [])

    # Update scanning needle
    needle_length = 200
    needle_x = [0, needle_length * np.cos(np.deg2rad(frame))]
    needle_y = [0, needle_length * np.sin(np.deg2rad(frame))]
    scanning_needle.set_data(needle_x, needle_y)

    # Update additional information text
    info_text.set_text('Radar System\nDistance: {:.1f} cm\nAngle: {}°'.format(distance, frame))

    return radar_display, distance_text, scanning_needle, shadow, info_text

ani = animation.FuncAnimation(fig, update, frames=range(360), init_func=init, blit=True, interval=50)
plt.show()

GPIO.cleanup()

