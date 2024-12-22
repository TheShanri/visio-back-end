import pandas as pd

def create_report(data):
    # Create DataFrame from the points
    df = pd.DataFrame({
        'Onset Points': pd.Series(data['onsetPoints']),
        'Peak Points': pd.Series(data['peakPoints']),
        'Empty Points': pd.Series(data['emptyPoints'])
    })
    
    # Save to CSV
    filename = 'cmg_points_report.csv'
    df.to_csv(filename, index=False)
    return filename
