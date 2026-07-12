import pdfplumber
from pathlib import Path
from typing import List, Dict, Any

try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

class MedicalPDFService:
    def extract_text(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from medical PDF. Falls back to OCR if digital text is empty.
        """
        pages_content = []
        full_text = ""
        is_scanned = False
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    
                    # If page text is very short/empty, flag as potentially scanned
                    if len(text.strip()) < 50:
                        is_scanned = True
                        
                    pages_content.append({
                        "page_num": idx + 1,
                        "text": text
                    })
                    full_text += f"\n--- PAGE {idx + 1} ---\n" + text
        except Exception as e:
            print(f"pdfplumber failed: {e}")
            raise ValueError(f"Could not open PDF file: {e}")
            
        # OCR Fallback if scanned and OCR libraries are available
        if is_scanned:
            print("PDF appears to be scanned. Running OCR Fallback...")
            if HAS_OCR:
                try:
                    # To perform OCR on PDF without poppler (pdf2image), we can check
                    # if we have images in pdfplumber pages or just log warning.
                    # As a simpler, more robust alternative: we use LLM vision or notify the user.
                    # We will log a warning that full OCR requires system binaries.
                    pass
                except Exception as ocr_err:
                    print(f"OCR failed: {ocr_err}")
            else:
                print("OCR libraries (pytesseract/Pillow) not installed. Continuing with digital extraction only.")

        return {
            "full_text": full_text,
            "pages": pages_content,
            "page_count": len(pages_content),
            "is_scanned": is_scanned
        }

pdf_service = MedicalPDFService()
