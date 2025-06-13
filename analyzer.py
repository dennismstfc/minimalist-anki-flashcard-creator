import PIL
import pytesseract
from typing import List
import numpy as np
from pdf2image import convert_from_path
import cv2
from PIL import ImageDraw, ImageFont


class FileAnalyzer:
    """
    Analyze a file to determine if GPT-4o is needed or if a simpler model can be used to
    save costs. This class takes a threshold parameter which is the minimum percentage of
    text in the file to use GPT-4o, if the image contains more text than the threshold,
    a simple model such as GPT-o will be used, otherwise GPT-4o will be used. OCR is performed
    to get the text in the file.
    """
    def __init__(
            self, 
            images: list[PIL.Image.Image], 
            text_threshold: float = 0.75, 
            deep_analysis: bool = False
            ):
        """
        Args:
            images: list of PIL.Image.Image of the images to process
            text_threshold: float of the threshold to use for the GPT-4o model. If above this
            threshold, the text will be extracted and used to create flashcards.
            deep_analysis: bool of whether to perform a deep analysis of the page. If false.
            only the text ratio is calculated and the text is extracted.
        """
        self.images = images
        self.text_threshold = text_threshold
        self.deep_analysis = deep_analysis # If false, only the text ratio is calculated

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
    

    def __calculate_complexity(self, text: str, graphics: List[PIL.Image.Image]) -> float:
        """
        Calculate the content complexity of the page.

        Args:
            text: str of the text to process
            graphics: list of PIL.Image.Image of the graphics to process

        Returns:
            float: The complexity score of the page
        """
        complexity = 0.0

        if text:
            # 1. special character ratio
            special_char_ratio = sum(1 for char in text if not char.isalnum()) / len(text) if text else 0

            # 2. word length variance
            words = text.split()
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            word_length_variance = sum((len(word) - avg_word_length) ** 2 for word in words) / len(words) if words else 0

            # 3. Line density
            line_count = text.count("\n")

            complexity += min(0.4, special_char_ratio)
            complexity += min(0.3, word_length_variance / 10)
            complexity += min(0.3, line_count / 50)
            
        if graphics:
            # 1. Number of graphics
            complexity += min(0.3, len(graphics) / 10)

            # 2. Size variance
            
            avg_size = sum(g.width*g.height for g in graphics)/len(graphics) if graphics else 0
            size_var = sum((g.width*g.height-avg_size)**2 for g in graphics)/len(graphics) if graphics else 0
            complexity += min(0.3, size_var / (avg_size + 1) * 0.1)
    
        return min(1.0, complexity) 

    def __calculate_text_area(self, image: PIL.Image.Image) -> float:
        """
        Calculate the area of the text in the image using OCR bounding boxes.

        Args:
            image: PIL.Image.Image of the image to process

        Returns:
            float: The area of the text in the image
        """
        try:
            # Use Tesseract to get text bounding boxes
            ocr_data = pytesseract.image_to_data(
                image, 
                output_type=pytesseract.Output.DICT
            )
            
            text_area = 0
            for i, conf in enumerate(ocr_data['conf']):
                if int(conf) > 60:  # Only consider confident detections
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    text_area += w * h
            
            return text_area
        except Exception:
            # Fallback estimation if OCR fails
            return image.width * image.height * 0.2  # Conservative estimate

    def analyze(self) -> dict[int, dict]:
        """
        Analyze each page to determine the optimal model selection with detailed metrics.
        
        Returns:
            dict[int, dict]: A dictionary where keys are page indices and values are 
            analysis dictionaries containing:
            - use_gpt4o: bool (whether to use GPT-4o)
            - text_ratio: float (percentage of text content)
            - text_area: int (pixel area of text)
            - graphics_area: int (pixel area of graphics)
            - complexity_score: float (0-1 score of content complexity)
            - text: str (extracted text from the page)
        """
        # Always extract text as it's needed for basic analysis
        extracted_texts = self.__extract_text()
        
        # Only extract graphics if deep analysis is enabled
        extracted_graphics = self.__extract_graphics() if self.deep_analysis else {}
        
        analysis_results = {}
        
        for page_idx, image in enumerate(self.images):
            # Calculate text ratio (always needed)
            text_length = len(extracted_texts[page_idx].strip())
            page_width, page_height = image.size
            page_area = page_width * page_height
            
            if self.deep_analysis:
                # Calculate precise text area using OCR bounding boxes
                text_area = self.__calculate_text_area(image)
                
                # Calculate graphics area
                graphics_area = sum(
                    g.width * g.height 
                    for g in extracted_graphics.get(page_idx, [])
                )
                
                # Calculate content ratios
                content_area = text_area + graphics_area
                if content_area > 0:
                    text_ratio = text_area / content_area
                    graphics_ratio = graphics_area / content_area
                else:
                    text_ratio = 0
                    graphics_ratio = 0
                
                # Calculate complexity factors
                complexity_score = self.__calculate_complexity(
                    extracted_texts[page_idx],
                    extracted_graphics.get(page_idx, [])
                )
            else:
                # Simple text ratio calculation for basic analysis
                text_area = text_length * 100  # Rough estimate of text area
                graphics_area = 0
                text_ratio = text_length / (page_width * page_height) if text_length > 0 else 0
                graphics_ratio = 0
                complexity_score = 0
            
            # Determine model recommendation. TODO: tweak thresholds        
            use_gpt4o = (text_ratio < self.text_threshold) or (complexity_score > 0.9)
            
            analysis_results[page_idx] = {
                'use_gpt4o': use_gpt4o,
                'text_ratio': text_ratio,
                'text_area': text_area,
                'graphics_area': graphics_area,
                'complexity_score': complexity_score,
                'page_dimensions': (page_width, page_height),
                'graphics_count': len(extracted_graphics.get(page_idx, [])),
                'text': extracted_texts[page_idx]
            }
        
        return analysis_results