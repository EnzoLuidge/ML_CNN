from flask import Flask, request, jsonify
import numpy as np
import cv2
from tensorflow import keras
from keras.layers import Conv2D
from keras.models import Sequential

import base64
from io import BytesIO
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def apply_filter(image, kernel):
    # Expand the kernel to match the input shape (3, 3, 3, 1)
    kernel = np.repeat(kernel[:, :, np.newaxis], 3, axis=2)
    kernel = kernel[..., np.newaxis]
    
    model = Sequential()
    model.add(Conv2D(1, kernel_size=kernel.shape[:2], padding='same', input_shape=(None, None, 3), use_bias=False))
    model.layers[0].set_weights([kernel])
    
    filtered_image = model.predict(np.expand_dims(image, axis=0))
    filtered_image = np.squeeze(filtered_image, axis=0)

    # Normalize the filtered image to the range [0, 255]
    filtered_image = ((filtered_image - filtered_image.min()) * (1/(filtered_image.max() - filtered_image.min()) * 255)).astype(np.uint8)

    return filtered_image

def process_image(image_data, filter_type):
    # Decode the base64 image data
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    image = np.array(image)
    
    if filter_type == "blur":
        kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=np.float32) / 9.0
    elif filter_type == "edge":
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32)
    elif filter_type == "sharpen":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    
    filtered_image = apply_filter(image, kernel)
    
    # Encode the filtered image back to base64
    _, buffer = cv2.imencode('.jpg', filtered_image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    
    return encoded_image

@app.route('/apply_filter', methods=['POST'])
def apply_filter_route():
    data = request.json
    image_data = data['image']
    filter_type = data['filter']
    result_image = process_image(image_data, filter_type)
    return jsonify({'filtered_image': result_image})

if __name__ == '__main__':
    app.run(debug=True)