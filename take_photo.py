import cv2
import os
import base64
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.oauth2 import service_account

def capture_and_detect(camera_index, output_path, endpoint_id, project_id, location, service_account_path):
    # Set the authentication credentials
    credentials = service_account.Credentials.from_service_account_file(service_account_path)

    # Open the camera
    cap = cv2.VideoCapture(camera_index)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Failed to open the camera.")
        return

    # Read a frame from the camera
    ret, frame = cap.read()

    # Check if the frame is read successfully
    if not ret:
        print("Failed to capture the image.")
    else:
        # Save the captured image
        height, width = frame.shape[:2]
        crop_width = int(width)
        cropped_frame = frame[:, :crop_width]

        # Save the cropped image
        cv2.imwrite(output_path, frame)
        print(f"Image captured and saved as: {output_path}")

        # Create a Vertex AI client with the authentication credentials
        client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        client = aiplatform.gapic.PredictionServiceClient(credentials=credentials, client_options=client_options)

        # Load the image file and encode it in base64
        with open(output_path, "rb") as f:
            file_content = f.read()
        encoded_content = base64.b64encode(file_content).decode("utf-8")
        print(encoded_content)

        # Create an instance with the encoded image content
        instance = predict.instance.ImageObjectDetectionPredictionInstance(content=encoded_content).to_value()
        instances = [instance]

        # Set the prediction parameters
        parameters = predict.params.ImageObjectDetectionPredictionParams(confidence_threshold=0.002, max_predictions=5).to_value()

        # Make a prediction request to the Vertex AI endpoint
        endpoint = client.endpoint_path(project=project_id, location=location, endpoint=endpoint_id)
        response = client.predict(endpoint=endpoint, instances=instances, parameters=parameters)

        print("Response:")
        print(" Deployed Model ID:", response.deployed_model_id)

        # Process the predictions
        predictions = response.predictions
        for prediction in predictions:
            print(" Prediction:", dict(prediction))
            
            # Extract the bounding box coordinates and other information
            if 'bboxes' in prediction and prediction['bboxes']:
                for bbox, confidence, display_name, obj_id in zip(
                    prediction['bboxes'], prediction['confidences'], prediction['displayNames'], prediction['ids']
                ):
                    # Extract the coordinates from the bounding box
                    x_min, y_min, x_max, y_max = bbox
                    x_center = (x_min + x_max) / 2
                    y_center = (y_min + y_max) / 2
                    
                    print(f"Detected object: {display_name} (ID: {obj_id})")
                    print(f"Confidence: {confidence}")
                    print(f"Coordinates: ({x_center}, {y_center})")
                    
                    # Perform further processing with the coordinates as needed
            else:
                print("No objects detected.")
        # Delete the captured image file
        # os.remove(output_path)
        # print(f"Deleted captured image: {output_path}")

    # Release the camera
    cap.release()

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
capture_and_detect(camera_index, output_path, endpoint_id, project_id, location, service_account_path)