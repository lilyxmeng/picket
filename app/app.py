from flask import Flask, render_template, Response, request, flash, redirect, url_for, jsonify
import requests
from PIL import Image
import numpy as np
import io
import os
from werkzeug.utils import secure_filename
from google.cloud import vision


app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    """Returns the index page for the application at the root URL."""
    return render_template("index.html")


@app.route('/scan')
def scan():
    """Returns the scan page for the application at the scan endpoint."""
    return render_template("scan.html")


@app.route('/upload', methods=['POST'])
def upload():
    """If an image is uploaded through the scan endpoint, the application will send the image 
    as a POST request to the upload endpoint. The image will be processed and the prediction
    will be returned to the scan page.

    If an image is not uploaded or an invalid image is uploaded and a POST request is triggered
    the upload endpoint, the application will return an error message to the scan page.
    """
    prediction = "The image is invalid or unidentifiable"  # default prediction

    if request.method == 'POST':  # if a POST request is triggered
        if "file" not in request.files:  # if no file is uploaded, e.g. a blank form is submitted
            # return the scan page with the default prediction
            return render_template("scan.html", prediction=prediction)

        file = request.files['file']  # get the file from the POST request

        # instantiates a client for the vision API
        client = vision.ImageAnnotatorClient()

        # ensures file is secure, not malicious
        file = secure_filename(file.filename)  

        # save the file to the uploads folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file))

        # access the file
        file = os.path.abspath(UPLOAD_FOLDER + '/' + file)

        # load the image into memory
        with io.open(file, 'rb') as image_file:
            content = image_file.read()  # read/process the image file

        # create an image instance using the processed image file
        image = vision.Image(content=content)

        # define the labels we are looking for
        classes = ["cardboard", "glass",
                   "metal", "paper", "plastic", "trash"]

        # Perform label detection on the image file
        response = client.label_detection(image=image)
        labels = response.label_annotations
        labels_list = []

        # create a list of labels for the image uploaded
        for label in labels:
            labels_list.append(label.description)

        # if the label is in the list of labels we are looking for, return the prediction of the bin
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

    return render_template("scan.html", prediction=prediction)


if __name__ == "__main__":
    app.run(debug=True)
