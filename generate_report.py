import pandas as pd
import numpy as np
from scipy.signal import find_peaks

def create_report(data):
    # Extract time series data
    full_data_df = pd.DataFrame({
        'Elapsed Time': [point['x'] for point in data['fullData']['bladderPressureData']],
        'Scale': [point['y'] for point in data['fullData']['scaleData']],
        'Infused Volume': [point['y'] for point in data['fullData']['infusedVolData']],
        'Bladder Pressure': [point['y'] for point in data['fullData']['bladderPressureData']]
    })

    # Calculate key metrics
    num_curves = len(data['onsetPoints'])
    experiment_duration = full_data_df['Elapsed Time'].iloc[-1]

    # Calculate IMI values
    imi_values = []
    onset_times = [point for point in data['onsetPoints']]
    for i in range(num_curves):
        if i < num_curves - 1:
            imi = round(onset_times[i + 1] - onset_times[i], 2)
            imi_values.append(imi)
        else:
            imi_values.append('N/A')

    # Calculate Average Pressure values
    avg_pressure_values = []
    for i in range(num_curves):
        if i == 0:
            avg_pressure_values.append('N/A')
        else:
            start_time = data['emptyPoints'][i - 1]
            end_time = data['onsetPoints'][i]
            
            segment_data = full_data_df[
                (full_data_df['Elapsed Time'] >= start_time) & 
                (full_data_df['Elapsed Time'] <= end_time)
            ]
            avg_pressure = round(segment_data['Bladder Pressure'].mean(), 2)
            avg_pressure_values.append(avg_pressure)

    # Calculate Maximum Pressure values
    max_pressure_values = []
    peak_times = [point for point in data['peakPoints']]
    for peak_time in peak_times:
        peak_pressure = full_data_df[
            full_data_df['Elapsed Time'] == peak_time
        ]['Bladder Pressure'].iloc[0]
        max_pressure_values.append(round(peak_pressure, 2))

    # Calculate Void Volume values
    void_volume_values = []
    for i in range(num_curves):
        if i < num_curves - 1:
            start_time = onset_times[i]
            end_time = onset_times[i + 1]
            
            segment_data = full_data_df[
                (full_data_df['Elapsed Time'] >= start_time) & 
                (full_data_df['Elapsed Time'] <= end_time)
            ]
            
            positive_scale = segment_data['Scale'][segment_data['Scale'] > 0]
            void_volume = round(positive_scale.sum(), 2)
            void_volume_values.append(void_volume)
        else:
            void_volume_values.append('N/A')

    # Calculate Infused Volume values
    infused_volume_values = []
    for i in range(num_curves):
        if i < num_curves - 1:
            start_time = onset_times[i]
            end_time = onset_times[i + 1]
            
            start_volume = full_data_df[
                full_data_df['Elapsed Time'] == start_time
            ]['Infused Volume'].iloc[0]
            
            end_volume = full_data_df[
                full_data_df['Elapsed Time'] == end_time
            ]['Infused Volume'].iloc[0]
            
            infused_volume = round(end_volume - start_volume, 2)
            infused_volume_values.append(infused_volume)
        else:
            infused_volume_values.append('N/A')

    # Calculate Non-voiding Contractions
    nvc_values = []
    for i in range(num_curves):
        if i < num_curves - 1:
            empty_time = data['emptyPoints'][i]
            peak_time = data['peakPoints'][i]
            
            segment_data = full_data_df[
                (full_data_df['Elapsed Time'] >= empty_time) & 
                (full_data_df['Elapsed Time'] <= peak_time)
            ]
            
            pressures = segment_data['Bladder Pressure'].values
            small_peaks, _ = find_peaks(pressures, 
                                      height=0.5,
                                      prominence=1.0,
                                      distance=5)
            
            nvc_values.append(len(small_peaks))
        else:
            nvc_values.append('N/A')

    # Create individual curve metrics sheet
    curve_metrics = pd.DataFrame({
        'IMI': imi_values,
        'Average Pressure': avg_pressure_values,
        'Maximum Pressure': max_pressure_values,
        'Void Volume': void_volume_values,
        'Infused Volume': infused_volume_values,
        'Non voiding contractions': nvc_values
    })

    # Create summary metrics sheet
    summary_metrics = pd.DataFrame({
        'Metric': ['Number of curves', 'Full experiment window (s)'],
        'Value': [num_curves, experiment_duration]
    })

    # Create points analysis sheet
    points_df = pd.DataFrame({
        'Onset Points': pd.Series(data['onsetPoints']),
        'Peak Points': pd.Series(data['peakPoints']),
        'Empty Points': pd.Series(data['emptyPoints'])
    })

    # Generate Excel file with all sheets
    filename = 'cmg_complete_report.xlsx'
    with pd.ExcelWriter(filename) as writer:
        summary_metrics.to_excel(writer, sheet_name='Summary Analysis', index=False)
        curve_metrics.to_excel(writer, sheet_name='Individual Curves', index=False)
        points_df.to_excel(writer, sheet_name='Points Analysis', index=False)
        full_data_df.to_excel(writer, sheet_name='Time Series Data', index=False)

    return filename
