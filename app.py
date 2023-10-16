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
        return "No image selected for upload."

    images = request.files.getlist('image')

    if not images:
        return "No file selected."

    if len(images) == 1:
        image = images[0]
        original_filename = image.filename
        img = Image.open(image)
        compressed_image = BytesIO()

        file_ext = os.path.splitext(original_filename)[1].lower()
        if file_ext == '.jpg' or file_ext == '.jpeg':
            img.save(compressed_image, 'JPEG', optimize=True, quality=50)
        elif file_ext == '.png':
            img.save(compressed_image, 'PNG', optimize=True, compress_level=9)

        compressed_filename = os.path.splitext(original_filename)[
            0] + "_compressed" + file_ext
        compressed_image.seek(0)
        return send_file(compressed_image, as_attachment=True, download_name=compressed_filename)

    zip_filename = "compressed_images.zip"
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for image in images:
            original_filename = image.filename
            img = Image.open(image)
            compressed_image = BytesIO()

            file_ext = os.path.splitext(original_filename)[1].lower()
            if file_ext == '.jpg' or file_ext == '.jpeg':
                img.save(compressed_image, 'JPEG', optimize=True, quality=50)
            elif file_ext == '.png':
                img.save(compressed_image, 'PNG',
                         optimize=True, compress_level=9)

            compressed_image.seek(0)
            zipf.writestr(original_filename, compressed_image.read())

    zip_buffer.seek(0)
    response = make_response(zip_buffer.read())
    response.headers["Content-Type"] = "application/zip"
    response.headers["Content-Disposition"] = f"attachment; filename={zip_filename}"
    return response


if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)))
