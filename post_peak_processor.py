def process_segments_function(request_data):
    # Get peaks from request data
    peaks = request_data.get('peaks', [])
    
    # Create onset points by subtracting 300
    onset_points = [peak - 300 for peak in peaks]
    
    # Create empty points by adding 300
    empty_points = [peak + 300 for peak in peaks]
    
    # Return all three sets of points
    return {
        "peaks": peaks,
        "onsetPoints": onset_points,
        "emptyPoints": empty_points
    }
