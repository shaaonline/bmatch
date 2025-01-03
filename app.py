
from flask import Flask, request, jsonify, send_file
import cv2
import numpy as np
import os

app = Flask(__name__)

@app.route('/compare', methods=['POST'])
def compare_images():
    # Check if both images are uploaded
    file1 = request.files.get('image1')
    file2 = request.files.get('image2')
    if not file1 or not file2:
        return jsonify({"error": "Both images must be uploaded"}), 400

    # Save uploaded images temporarily
    file1_path = "./image1.jpg"
    file2_path = "./image2.jpg"
    diff_output_path = "./difference.jpg"
    file1.save(file1_path)
    file2.save(file2_path)

    # Load images for comparison
    img1 = cv2.imread(file1_path)
    img2 = cv2.imread(file2_path)

    # Resize images to the same dimensions (if needed)
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # Convert to grayscale for feature detection
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Compute absolute difference
    diff = cv2.absdiff(gray1, gray2)
    _, diff_mask = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)

    # Highlight differences in the original images
    highlighted_diff = img1.copy()
    highlighted_diff[diff_mask > 0] = [0, 0, 255]  # Red color for differences
    cv2.imwrite(diff_output_path, highlighted_diff)

    # Calculate similarity score (inverted difference ratio)
    total_pixels = img1.shape[0] * img1.shape[1]
    unmatched_pixels = cv2.countNonZero(diff_mask)
    similarity_score = ((total_pixels - unmatched_pixels) / total_pixels) * 100

    return jsonify({
        "similarity_score": round(similarity_score, 2),
        "difference_image_url": "/difference"
    })

@app.route('/difference', methods=['GET'])
def get_difference_image():
    return send_file("./difference.jpg", mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
