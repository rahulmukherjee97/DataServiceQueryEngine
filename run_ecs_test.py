import subprocess
import threading
import time
import os
import sys
import requests
from mindsdb.integrations.handlers.ecs_handler.tests.mock_ecs_server import start_server

def wait_for_server(url, timeout=30):
    """Wait for server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    return False

def main():
    # Start mock ECS server in a separate thread
    print("Starting mock ECS server...")
    ecs_thread = threading.Thread(target=start_server, daemon=True)
    ecs_thread.start()
    
    # Wait for mock server to be ready
    if not wait_for_server("http://localhost:5000/api/services/app/Context/GetContexts"):
        print("Failed to start mock ECS server")
        sys.exit(1)
    print("Mock ECS server is running at http://localhost:5000")

    # Start MindsDB
    print("\nStarting MindsDB...")
    try:
        # Create ECS connection in MindsDB
        import mindsdb
        mindsdb.start()
        
        # Create ECS connection
        mindsdb.connect()
        mindsdb.execute("""
            CREATE DATABASE ecs_datasource
            WITH
                ENGINE = 'ecs',
                PARAMETERS = {
                    "url": "http://localhost:5000",
                    "tenant": "test_tenant",
                    "username": "test_user",
                    "password": "test_password",
                    "organization_unit": "Default"
                };
        """)
        
        print("\nMindsDB is running and connected to mock ECS server")
        print("You can now run queries like:")
        print("SELECT * FROM ecs_datasource.contexts;")
        print("SELECT * FROM ecs_datasource.contexts WHERE type = 'String';")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 