import numpy as np

def decimate_data(bladder_pressure_data, factor=10):
    return bladder_pressure_data[::factor]

def process_segments_function(request_data):
    peaks = request_data.get('peaks', [])
    data = request_data.get('data', {})
    
    bladder_pressure_data = decimate_data(data.get('bladderPressureData', []))
    data_array = np.array([(point['x'], point['y']) for point in bladder_pressure_data])
    x_values = data_array[:, 0]
    y_values = data_array[:, 1]
    
    onset_points = []
    empty_points = []
    
    # Process onset points by scanning forward from previous peak
    for i, peak in enumerate(peaks):
        peak_idx = np.searchsorted(x_values, peak)
        peak_pressure = y_values[peak_idx]
        pressure_threshold = peak_pressure - 5
        
        # Determine start point for scanning with 50-second minimum
        if i == 0:
            start_idx = 0
        else:
            min_time = peaks[i-1] + 50  # Minimum 50 seconds after previous peak
            start_idx = np.searchsorted(x_values, min_time)
        
        # Get the section we're analyzing
        scan_indices = np.arange(start_idx, peak_idx)
        if len(scan_indices) < 2:
            onset_points.append(peak - 300)  # fallback
            print(f"Insufficient data points between peaks, using default onset at x={peak-300}")
            continue
            
        # Calculate point-to-point gradients
        gradients = (y_values[scan_indices[1:]] - y_values[scan_indices[:-1]]) / \
                   (x_values[scan_indices[1:]] - x_values[scan_indices[:-1]])
        
        # Find points meeting both gradient and pressure criteria
        valid_points = scan_indices[:-1][
            (gradients > 0.5) & 
            (y_values[scan_indices[:-1]] <= pressure_threshold)
        ]
        
        if len(valid_points) > 0:
            # Take the first point where gradient suddenly increases
            onset_points.append(x_values[valid_points[0]])
            print(f"Found onset point at x={x_values[valid_points[0]]}")
        else:
            default_onset = peak - 300
            onset_points.append(default_onset)
            print(f"Using default onset point at x={default_onset}")
    
    # Process empty points using vectorized operations
    for peak in peaks[:-1]:
        peak_idx = np.searchsorted(x_values, peak)
        peak_pressure = y_values[peak_idx]
        pressure_threshold = peak_pressure - 2
        
        # Look ahead window
        next_indices = np.arange(peak_idx + 1, min(len(x_values), peak_idx + 100))
        if len(next_indices) < 2:
            empty_points.append(peak + 100)
            continue
            
        # Calculate gradients for forward windows
        forward_gradients = (y_values[next_indices[1:]] - y_values[next_indices[:-1]]) / \
                          (x_values[next_indices[1:]] - x_values[next_indices[:-1]])
        
        # Find points meeting criteria
        valid_points = next_indices[:-1][
            (forward_gradients > 0) & 
            (y_values[next_indices[:-1]] <= pressure_threshold) &
            (x_values[next_indices[:-1]] >= peak + 10)
        ]
        
        if len(valid_points) > 0:
            empty_points.append(x_values[valid_points[0]])
            print(f"Found empty point at x={x_values[valid_points[0]]}")
        else:
            default_empty = peak + 100
            empty_points.append(default_empty)
            print(f"Using default empty point at x={default_empty}")
    
    return {
        "peaks": peaks,
        "onsetPoints": onset_points,
        "emptyPoints": empty_points
    }
