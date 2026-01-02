try:
    import requests
except ImportError:
    requests = None

from django.conf import settings

def ocr_scan_image(image_file):
    """
    Calls ocr.space API to extract text from an image file.
    """
    if requests is None:
        return {"error": "Python package 'requests' is not installed. Run 'pip install requests' in your virtualenv."}

    api_key = getattr(settings, 'OCR_SPACE_API_KEY', None)
    if not api_key:
        return {"error": "OCR API key not configured."}

    url = "https://api.ocr.space/parse/image"
    
    # Reset file pointer to beginning
    image_file.seek(0)
    
    payload = {
        'apikey': api_key,
        'language': 'eng', 
        'isOverlayRequired': False,
        'detectOrientation': True,
        'scale': True,
        'isTable': True, # Better for receipts with columns
        'OCREngine': 1 # Engine 1 is sometimes more reliable for standard text
    }
    
    files = {
        'file': image_file
    }
    
    try:
        response = requests.post(url, data=payload, files=files, timeout=30)
        result = response.json()
        
        if result.get('OCRExitCode') == 1:
            # Success
            parsed_results = result.get('ParsedResults', [])
            if parsed_results:
                return {"text": parsed_results[0].get('ParsedText', '')}
            return {"error": "No text found in image."}
        else:
            # OCR API may return error messages as list or string
            err = result.get('ErrorMessage')
            if isinstance(err, list) and err:
                err = err[0]
            if not err:
                err = result.get('ErrorDetails') or 'Unknown error from OCR API.'
            return {"error": err}
            
    except Exception as e:
        return {"error": str(e)}
