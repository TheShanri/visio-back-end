import numpy as np
from scipy.signal import find_peaks

def detect_peaks_function(parameters, data):
    # Convert bladder pressure data to numpy array
    bladder_pressure_data = np.array(data['bladderPressureData'])
    y_values = [point['y'] for point in bladder_pressure_data]
    x_values = [point['x'] for point in bladder_pressure_data]
    
    # Find peaks using scipy with single values
    peaks, _ = find_peaks(y_values, 
                         height=parameters['height'],
                         threshold=parameters['threshold'],
                         distance=parameters['distance'],
                         prominence=parameters['prominence'],
                         width=parameters['width'])
    
    # Return only x coordinates of peaks
    peak_x_coordinates = [x_values[peak] for peak in peaks]
    
    return peak_x_coordinates
