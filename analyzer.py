import PIL
import pytesseract
from typing import List
import numpy as np
from pdf2image import convert_from_path
import cv2


class FileAnalyzer:
    """
    Analyze a file to determine if GPT-4o is needed or if a simpler model can be used to
    save costs. This class takes a threshold parameter which is the minimum percentage of
    text in the file to use GPT-4o, if the image contains more text than the threshold,
    a simple model such as GPT-o will be used, otherwise GPT-4o will be used. OCR is performed
    to get the text in the file.
    """
    def __init__(self, images: list[PIL.Image.Image], threshold: float = 0.8):
        self.images = images
        self.threshold = threshold

    def __extract_text(self) -> dict[int, str]:
        """
        Extract text from the images using Tesseract OCR.
        
        Returns:
            dict[int, str]: A dictionary of extracted text from each image
            where the key is the page index and the value is the extracted text.
        """
        extracted_texts = {}
        
        for idx, image in enumerate(self.images):
            # Convert image to grayscale for better OCR results
            if image.mode != 'L':
                image = image.convert('L')
            
            # Perform OCR on the image
            text = pytesseract.image_to_string(image)
            extracted_texts[idx] = text
            
        return extracted_texts

    def __extract_graphics_from_page(self, page: PIL.Image.Image) -> List[PIL.Image.Image]:
        """
        Extract graphics from a single page using image processing techniques.
        This method identifies and extracts regions that are likely to contain graphics
        rather than text.

        Args:
            page: The page to extract graphics from

        Returns:
            List[PIL.Image.Image]: A list of extracted graphics from the page 
        """
        # Convert PIL Image to OpenCV format
        cv_image = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        extracted_graphics = []
        
        # Filter and extract graphics
        for contour in contours:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter out very small regions (likely noise)
            if w < 50 or h < 50:
                continue
                
            # Calculate aspect ratio
            aspect_ratio = float(w) / h
            
            # Filter based on aspect ratio (typical for graphics)
            if 0.2 < aspect_ratio < 5:
                # Extract the region
                roi = page.crop((x, y, x + w, y + h))
                extracted_graphics.append(roi)
        
        return extracted_graphics
    
    def __extract_graphics(self) -> dict[int, List[PIL.Image.Image]]:
        """
        Extract graphics from all pages.

        Returns:
            dict[int, List[PIL.Image.Image]]: A dictionary of extracted graphics from each page 
            where the key is the page index and the value is a list of extracted graphics.
        """
        extracted_graphics = {}

        for idx, image in enumerate(self.images):
            extracted_graphics[idx] = self.__extract_graphics_from_page(image)

        return extracted_graphics

    def analyze(self):
        """
        For testing purposes, print the text and graphics extracted from the first page.
        """
        extracted_texts = self.__extract_text()
        extracted_graphics = self.__extract_graphics()

        print(extracted_texts)
        
        # plot the graphics
        for idx, graphics in extracted_graphics.items():
            for i, graphic in enumerate(graphics):
                graphic.show()  
        

if __name__ == "__main__":
    images = convert_from_path("docs/test.pdf")
    analyzer = FileAnalyzer(images)
    print(analyzer.analyze())

