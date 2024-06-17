import os
import subprocess

# List of all your service processes
processes = []

# List of services to exclude
exclude_services = [
    'service_template.py',
    # Add more services to exclude as needed...
]

def start_services():
    # Get all service scripts in the current directory
    services = [file for file in os.listdir() if file.startswith('service_') and file not in exclude_services]

    # Start all services
    for service in services:
        print(f"Starting {service}...")
        process = subprocess.Popen(['python3', service])
        processes.append(process)
        print(f"{service} started.")

def stop_services():
    # Stop all services
    for process in processes:
        print(f"Stopping {process.args[1]}...")
        process.terminate()
        print(f"{process.args[1]} stopped.")
    print("All services stopped.")

if __name__ == "__main__":
    start_services()

    # Wait for user input to stop services
    while True:
        stop = input("Enter '1' to stop all services: ")
        if stop == '1':
            stop_services()
            break