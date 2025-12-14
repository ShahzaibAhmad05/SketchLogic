"""
Script used to test run the backend so see it's working or, for debugging purposes.

"""

import requests, sys
import base64, io
from PIL import Image
import json
from pathlib import Path


def bytes_to_pil_img(data_url: str) -> Image.Image:
    _, b64 = data_url.split(",", 1)
    img_bytes = base64.b64decode(b64)
    img = Image.open(io.BytesIO(img_bytes))
    return img


def saveResults(analysisResults: dict, outputPath: Path=Path("results.json")) -> None:
    with open(outputPath, "w") as file:
        json.dump(analysisResults, file)


def main():
    with open("example.jpg", "rb") as f:
        response = requests.post("http://localhost:5000/api/process-circuit",
                                 files={"image": f})
    
    if response.status_code == 404:
        print("api not found!")
        print("Please recheck if the backend is running...")
        sys.exit(1)

    print(response.status_code)
    data = response.json()

    # Optional actions
    img = bytes_to_pil_img(data["processed_image"])      # Convert to showable image
    img.show()
    # img.save("results.jpg")
    # saveResults(data["analysis_results"])
    

if __name__ == "__main__":
    main()