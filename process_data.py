import pandas as pd
import io

def process_uploaded_data(text_data):
    # Split the text data into lines
    lines = text_data.strip().split("\n")
    
    # Find the index of the line that contains the column headers
    header_line_index = 4  # The line number where headers start (after metadata)
    
    # Extract the column headers
    headers = lines[header_line_index].split("\t")
    
    # Extract the actual data, which starts after the headers
    data_lines = lines[header_line_index + 1:]
    
    # Prepare the data for pandas by joining it back into a CSV-like format
    csv_data = "\n".join(data_lines)
    
    # Load the data into a pandas DataFrame
    data = pd.read_csv(io.StringIO(csv_data), delimiter="\t", names=headers)
    
    # Extract only the active columns for different graphs
    elapsed_time = data['Elapsed Time']

    # Graph 1: Scale vs. Elapsed Time
    data_graph1 = pd.DataFrame({
        'Elapsed Time': elapsed_time,
        'Scale': data['Scale']
    })

    # Graph 2: Tot Infused Vol vs. Elapsed Time
    data_graph2 = pd.DataFrame({
        'Elapsed Time': elapsed_time,
        'Tot Infused Vol': data['Tot Infused Vol']
    })

    # Graph 3: Bladder Pressure vs. Elapsed Time
    data_graph3 = pd.DataFrame({
        'Elapsed Time': elapsed_time,
        'Bladder Pressure': data['Bladder Pressure']
    })

    # Convert DataFrames to JSON
    json_graph1 = data_graph1.to_json(orient='records')
    json_graph2 = data_graph2.to_json(orient='records')
    json_graph3 = data_graph3.to_json(orient='records')

    # Return an array of JSON objects for each graph
    return [json_graph1, json_graph2, json_graph3]
