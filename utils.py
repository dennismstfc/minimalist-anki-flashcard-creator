import base64
from io import BytesIO
from PIL import Image

def pil_to_base64(
        image: Image.Image, 
        format: str = "JPEG"
    ) -> str:
    """
    Convert a PIL image to a base64 string for the OpenAI API.
    Args:
        image: PIL image
        format: image format
    Returns:
        base64 string
    """

    buffered = BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{img_str}"