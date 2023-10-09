import os
from flask import Flask, request, render_template, send_file, make_response, jsonify
from PIL import Image
from io import BytesIO
import zipfile

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('pages/index.html')


@app.route('/compress', methods=['POST'])
def compress_image():
    if 'image' not in request.files:
        # Handle case where no image is uploaded
        return "No image selected for upload."

    images = request.files.getlist('image')  # Get a list of uploaded files

    if not images:
        # Handle case where no file is selected
        return "No file selected."

    # Check if it's a single file upload
    if len(images) == 1:
        image = images[0]
        original_filename = image.filename

        # Compress the image by adjusting JPEG compression quality
        img = Image.open(image)
        compressed_image = BytesIO()
        # Adjust the quality value as needed (e.g., 70)
        img.save(compressed_image, 'JPEG', optimize=True, quality=50)

        # Set the file name with the original name + "compressed.jpg"
        compressed_filename = os.path.splitext(original_filename)[
            0] + "_compressed.jpg"

        # Return the compressed image as a downloadable response with the new filename
        compressed_image.seek(0)
        return send_file(compressed_image, as_attachment=True, download_name=compressed_filename)

    # Batch upload: Create a ZIP archive
    zip_filename = "compressed_images.zip"
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for image in images:
            original_filename = image.filename
            img = Image.open(image)
            compressed_image = BytesIO()
            img.save(compressed_image, 'JPEG', optimize=True, quality=50)
            compressed_image.seek(0)
            # Add each compressed image to the ZIP archive
            zipf.writestr(original_filename, compressed_image.read())

    # Return the ZIP archive as a downloadable response
    zip_buffer.seek(0)
    response = make_response(zip_buffer.read())
    response.headers["Content-Type"] = "application/zip"
    response.headers["Content-Disposition"] = f"attachment; filename={zip_filename}"
    return response


if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)))
