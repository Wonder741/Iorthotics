from your_file import detect_objects

# Specify the camera index (0 for the default camera)
camera_index = 1

# Specify the output path for the captured image
output_path = "captured_image.jpg"

# Specify the Vertex AI endpoint details
endpoint_id = "9151919174212124672"
project_id = "260118072749"
location = "us-central1"  # Replace with your endpoint's location

# Specify the path to the service account key file
service_account_path = "applied-well-398400-e46266833ff0.json"

# Call the function to capture the image and perform object detection
coordinates = detect_objects(camera_index, output_path, endpoint_id, project_id, location, service_account_path)

# Process the coordinates as needed
for coord in coordinates:
    print(f"Coordinates: ({coord[0]}, {coord[1]})")