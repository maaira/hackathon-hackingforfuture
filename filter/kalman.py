import numpy as np
from filterpy.kalman import KalmanFilter

# Initialize the Kalman filter
kf = KalmanFilter(dim_x=1, dim_z=1)

# State transition matrix
kf.F = np.array([[1]])

# Measurement function
kf.H = np.array([[1]])

# Initial state estimate
kf.x = np.array([[0.0]])

# Initial covariance estimate
kf.P = np.array([[1.0]])

# Process noise covariance
kf.Q = np.array([[0.0001]])

# Measurement noise covariance for sensor 1 and sensor 2
R1 = 0.1
R2 = 0.1

# Lists to store measurements and estimates
sensor1_readings = [20.1, 20.2, 20.3, 20.4, 20.5]
sensor2_readings = [19.9, 20.0, 20.1, 20.2, 20.3]
estimates = []

def kalman_filter(temperature_arduino: float, bed_temperature : float):
    
    # Update step with sensor 1 measurement
    kf.R = np.array([[R1]])
    kf.update(np.array([[temperature_arduino]]))

    # Update step with sensor 2 measurement
    kf.R = np.array([[R2]])
    kf.update(np.array([[bed_temperature]]))

    # Prediction step (since there's no explicit time step, this step is trivial here)
    kf.predict()

    # Store the current estimate
    return kf.x[0, 0]
