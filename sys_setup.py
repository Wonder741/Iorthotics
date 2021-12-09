import os
import io
from google.cloud import vision


def google_vision_setup():
    env_var = 'GOOGLE_APPLICATION_CREDENTIALS'
    env_var_value = 'D:/Google Cloud/sanguine-link-334321-7492825895c5.json'
    os.environ[env_var] = env_var_value


def google_vision(google_vision_path):
    #  detect text in image
    google_vision_text = []
    with io.open(google_vision_path, 'rb') as image_file:
        content = image_file.read()

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    annotations = response.text_annotations

    if len(annotations) < 1:
        return google_vision_text
    else:
        for i in range(1, len(annotations)):
            google_vision_text.append(annotations[i].description)
        return google_vision_text


if __name__ == '__main__':
    google_vision_setup()
    image_path = 'D:/Google Cloud/ocr_data/ocr_example_1.png'
    ocr_text = google_vision(image_path)
    print(ocr_text)
