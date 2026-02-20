import base64
import os
from io import BytesIO

import httpx
import pytesseract
from fastmcp import FastMCP
from PIL import Image

# Initialize FastMCP server
mcp = FastMCP("OCR Server")

@mcp.tool()
def perform_ocr(image_path: str) -> str:
    """
    Performs OCR on an image file at the given path.
    Returns the extracted text.
    """
    if not os.path.exists(image_path):
        return f"Error: File not found at {image_path}"

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else "No text found in image."
    except Exception as e:
        return f"Error during OCR: {e!s}"

@mcp.tool()
def perform_ocr_url(url: str) -> str:
    """
    Performs OCR on an image at a given web URL.
    Returns the extracted text.
    """
    try:
        response = httpx.get(url, follow_redirects=True, timeout=20)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else "No text found in image."
    except httpx.HTTPStatusError as e:
        return f"HTTP error: {e.response.status_code} for URL {url}"
    except Exception as e:
        return f"Error during OCR from URL: {e!s}"

@mcp.tool()
def perform_ocr_base64(base64_image: str) -> str:
    """
    Performs OCR on a base64 encoded image string.
    Returns the extracted text.
    """
    try:
        image_data = base64.b64decode(base64_image)
        img = Image.open(BytesIO(image_data))
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else "No text found in image."
    except Exception as e:
        return f"Error during OCR: {e!s}"

if __name__ == "__main__":
    mcp.run()
