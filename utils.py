import base64
from io import BytesIO
from PIL import Image
from pathlib import Path

def pil_to_base64(
        image: Image.Image, 
        format: str = "PNG",
        max_dim: int = 2048
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
    # convert image to RGB
    image = image.convert("RGB")
    
    # resize image if it's too big
    if image.width > max_dim or image.height > max_dim:
        image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{img_str}"


def png_to_pil(path: Path) -> Image.Image:
    """
    Convert a PNG image to a PIL image.
    Args:
        path: path to the PNG image
    Returns:
        PIL image  
    """
    return Image.open(path)