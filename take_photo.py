import cv2
import base64
import numpy as np
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.oauth2 import service_account

def detect_objects(camera_index, output_path, endpoint_id, project_id, location, service_account_path):
    # Set the authentication credentials
    credentials = service_account.Credentials.from_service_account_file(service_account_path)

    # Open the camera
    cap = cv2.VideoCapture(camera_index)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Failed to open the camera.")
        return []

    # Read a frame from the camera
    ret, frame = cap.read()

    # Check if the frame is read successfully
    if not ret:
        print("Failed to capture the image.")
        return []
    else:
        # Save the captured image
        cv2.imwrite(output_path, frame)
        print(f"Image captured and saved as: {output_path}")

        # Create a Vertex AI client with the authentication credentials
        client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        client = aiplatform.gapic.PredictionServiceClient(credentials=credentials, client_options=client_options)

        # Load the image file and encode it in base64
        with open(output_path, "rb") as f:
            file_content = f.read()
        encoded_content = base64.b64encode(file_content).decode("utf-8")

        # Create an instance with the encoded image content
        instance = predict.instance.ImageObjectDetectionPredictionInstance(content=encoded_content).to_value()
        instances = [instance]

        # Set the prediction parameters
        parameters = predict.params.ImageObjectDetectionPredictionParams(confidence_threshold=0.002, max_predictions=5).to_value()

        # Make a prediction request to the Vertex AI endpoint
        endpoint = client.endpoint_path(project=project_id, location=location, endpoint=endpoint_id)
        response = client.predict(endpoint=endpoint, instances=instances, parameters=parameters)

        # Process the predictions
        coordinates_list = []
        predictions = response.predictions
        for prediction in predictions:
            if 'bboxes' in prediction and prediction['bboxes']:
                for bbox in prediction['bboxes']:
                    # Extract the coordinates from the bounding box
                    x_min, y_min, x_max, y_max = bbox
                    x_center = (x_min + x_max) / 2
                    y_center = (y_min + y_max) / 2
                    coordinates_list.append([x_center, y_center])

    # Release the camera
    cap.release()

    # Perform coordinate transformation
    object_detection_coordinates = np.array([[0.3959, 0.6515], [0.643, 0.883], [0.2430, 0.4398], [0.5, 0.5]])
    robot_coordinates = np.array([[-501.95, 97.85], [-529.17, 554.63], [-215.54, 562.25], [-171, 108]])

    # Calculate the transformation matrix
    transformation_matrix, _ = cv2.findHomography(object_detection_coordinates, robot_coordinates)

    # Transform the coordinates
    transformed_coordinates = []
    for coord in coordinates_list:
        x, y = coord
        transformed_point = np.dot(transformation_matrix, [x, y, 1])
        transformed_x, transformed_y = transformed_point[:2] / transformed_point[2]
        transformed_coordinates.append([transformed_x, transformed_y])

    return transformed_coordinates