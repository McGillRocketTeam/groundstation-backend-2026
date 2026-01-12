import json
import socket
import time
from tkinter import FLAT
import requests
from datetime import datetime, timezone

# Configuration
YAMCS_URL = "http://localhost:8090"
INSTANCE = "mqtt-packets"
UDP_HOST = "localhost"
UDP_PORT = 11016
FLOAT_INTERVAL = 0.5
BOOLEAN_INTERVAL = 1.0
INT_INTERVAL = 0.5
FLOAT_INCREMENT = 0.1
INT_INCREMENT = 1  # Integers increment by 1

# State tracking
float_values = {}
boolean_states = {}
int_values = {}
last_boolean_toggle = 0


def fetch_parameters():
    try:
        url = f"{YAMCS_URL}/api/mdb/{INSTANCE}/parameters"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        parameters = []
        for param in data.get('parameters', []):
            param_name = param.get('qualifiedName')
            param_type = param.get('type', {}).get('engType')
            
            if param_type in ['boolean', 'float', 'integer']:
                print(f"Found parameter: {param_name} (type: {param_type})")
                parameters.append({
                    'name': param_name,
                    'type': param_type
                })
        
        return parameters
    except Exception as e:
        print(f"Error fetching parameters: {e}")
        return []

def initialize_values(parameters):
    for param in parameters:
        if param['type'] == 'float':
            float_values[param['name']] = 20.0  # Start at 20
        elif param['type'] == 'boolean':
            boolean_states[param['name']] = False
        elif param['type'] == 'integer':
            int_values[param['name']] = 0  # Start at 0

def build_parameter_data(parameters, current_time):
    gentime = current_time.isoformat().replace("+00:00", "Z")
    param_list = []
    
    for param in parameters:
        param_name = param['name']
        param_type = param['type']
        
        if param_type == 'float':
            value = float_values.get(param_name, 20.0)
            param_list.append({
                "id": {"name": param_name},
                "generationTime": gentime,
                "engValue": {
                    "type": "FLOAT",
                    "floatValue": value,
                },
            })
            # Increment for next time
            float_values[param_name] = value + FLOAT_INCREMENT

        elif param_type == 'integer':
            value = int_values.get(param_name, 0)
            param_list.append({
                "id": {"name": param_name},
                "generationTime": gentime,
                "engValue": {
                    "type": "SINT32",
                    "sint32Value": value,
                },
            })
            # Increment for next time
            int_values[param_name] = value + INT_INCREMENT
            
        elif param_type == 'boolean':
            value = boolean_states.get(param_name, False)
            param_list.append({
                "id": {"name": param_name},
                "generationTime": gentime,
                "engValue": {
                    "type": "BOOLEAN",
                    "booleanValue": value,
                },
            })
    
    return param_list

def send_parameters(param_list):
    if not param_list:
        return
    
    data = json.dumps({"parameter": param_list}).encode()
    # to see sent data uncomment the following line
    print(data)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(data, (UDP_HOST, UDP_PORT))

def main():
    global last_boolean_toggle
    
    print(f"Fetching parameters from {YAMCS_URL}...")
    parameters = fetch_parameters()
    
    if not parameters:
        print("No FLOAT or BOOLEAN parameters found!")
        return
    
    float_params = [p for p in parameters if p['type'] == 'float']
    boolean_params = [p for p in parameters if p['type'] == 'boolean']
    integer_params = [p for p in parameters if p['type'] == 'integer']
    
    print(f"\nFound {len(float_params)} FLOAT parameters")
    print(f"Found {len(boolean_params)} BOOLEAN parameters")
    print(f"Found {len(integer_params)} INTEGER parameters")
    print(f"\nSending to {UDP_HOST}:{UDP_PORT}")
    print(f"FLOAT parameters: increasing by {FLOAT_INCREMENT} every {FLOAT_INTERVAL}s")
    print(f"BOOLEAN parameters: toggling every {BOOLEAN_INTERVAL}s")
    print(f"INTEGER parameters: increasing by {INT_INCREMENT} every {INT_INTERVAL}s")
    print("Press Ctrl+C to stop\n")
    
    initialize_values(parameters)
    last_boolean_toggle = time.time()
    
    try:
        while True:
            current_time = datetime.now(timezone.utc)
            time_now = time.time()
            
            # Check if we need to toggle boolean values
            if time_now - last_boolean_toggle >= BOOLEAN_INTERVAL:
                for param_name in boolean_states:
                    boolean_states[param_name] = not boolean_states[param_name]
                last_boolean_toggle = time_now
            
            # Build and send all parameters
            param_list = build_parameter_data(parameters, current_time)
            send_parameters(param_list)
            
            # Print summary
            gentime_str = current_time.isoformat().replace("+00:00", "Z")
            print(f"[{gentime_str}] Sent {len(param_list)} parameters")
            
            time.sleep(FLOAT_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()