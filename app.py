# This package allows servers, requests, urls, etc.
from flask import Flask, request, render_template, redirect
# Create app var from Flask package
app = Flask(__name__)

# This packages allows for saving files
import os

print(os.path.abspath("static/imgs/uploads"))

# Set path to upload imgs
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Create get route, function to run on request
@app.route('/')
def first_route():
    return render_template('upload.html')

# Create post, get route, function to run on request
@app.route('/results', methods=['POST', 'GET'])
def send_csv():
    if request.method == 'POST':
        if request.files:
            target = os.path.join(APP_ROOT, 'static/uploads')
            file = request.files['file']
            filename = file.filename
            destination = "/".join([target, filename])
            file.save(destination)
            return render_template('results.html', download_file = filename)

# This runs the server (provided by Flask)
if __name__ == '__main__':
    app.run(debug=True)
