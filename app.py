import os
from flask import Flask, request, render_template, send_file
from PIL import Image
from io import BytesIO

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('pages/index.html')


@app.route('/compress', methods=['POST'])
def compress_image():
    if 'image' not in request.files:
        # Handle case where no image is uploaded
        return "No image selected for upload."

    image = request.files['image']

    if image.filename == '':
        # Handle case where no file is selected
        return "No file selected."

    # Compress the image by adjusting JPEG compression quality
    img = Image.open(image)
    compressed_image = BytesIO()
    # Adjust the quality value as needed (e.g., 70)
    img.save(compressed_image, 'JPEG', optimizer=True, quality=50)

    # Set the file name and return it as a downloadable response
    compressed_image.seek(0)
    return send_file(compressed_image, as_attachment=True, download_name='compressed.jpg')


if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)))
