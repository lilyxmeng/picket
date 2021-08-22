from flask import Flask, render_template, Response, request, flash, redirect, url_for, jsonify
import requests
from PIL import Image
import numpy as np
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/scan')
def scan():
    return render_template("scan.html")

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    prediction = "The image is invalid or unidentifiable"

    if request.method == 'POST':
        if "file" not in request.files:
            return render_template("scan.html", prediction=prediction)

        file = request.files['file']

        if file.filename == "":
            return render_template("scan.html", prediction=prediction)

        if file:
            # Imports the Google Cloud client library
            from google.cloud import vision

            # Instantiates a client
            client = vision.ImageAnnotatorClient()

            # The name of the image file to annotate

            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            file_name = os.path.abspath(UPLOAD_FOLDER + '/' + filename)
            # file_name = Image.open(filename)
            print(file_name)

            # Loads the image into memory
            with io.open(file_name, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)

            classes =  ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

            # Performs label detection on the image file
            response = client.label_detection(image=image)
            labels = response.label_annotations
            labels_list = []

            for label in labels:
                labels_list.append(label.description)

            
            for label in labels_list:
                if "Glass" in label:
                    prediction = "We predict this item belongs in the \"Glass\" bin."
                elif "Metal" in label:
                    prediction = "We predict this item belongs in the \"Metal\" bin."
                elif "Plastic" in label:
                    prediction = "We predict this item belongs in the \"Plastic\" bin."
                elif "E-waste" in label:
                    prediction = "We predict this item belongs in the \"E-Waste\" bin."
                elif "Paper" in label:
                    prediction = "We predict this item belongs in the \"Paper\" bin."
                elif "Organic" in label:
                    prediction = "We predict this item belongs in the \"Organic\" bin."

            print('Labels:')
            for label in labels:
                print(label.description)

            print(prediction)
    
    return render_template("scan.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)