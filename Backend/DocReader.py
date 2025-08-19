from pathlib import Path
from typing import List, Optional
import logging

# Optional imports with error handling
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class DocumentReader:
    """
    Reads text from various document types: TXT, PDF, DOCX.
    Returns a list of strings (paragraphs/pages).
    """
    
    def __init__(self):
        # Dynamic supported extensions based on available libraries
        self.supported_extensions = [".txt"]
        if PDF_AVAILABLE:
            self.supported_extensions.append(".pdf")
        if DOCX_AVAILABLE:
            self.supported_extensions.append(".docx")
    
    @property
    def SUPPORTED_EXTENSIONS(self) -> List[str]:
        return self.supported_extensions
    
    def read(self, file_path: str, encoding: str = "utf-8") -> List[str]:
        """
        Read text from a document file.
        
        Args:
            file_path: Path to the document file
            encoding: Text encoding (default: utf-8)
            
        Returns:
            List of text chunks (paragraphs for DOCX/TXT, pages for PDF)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is unsupported or library unavailable
            Exception: For other reading errors
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
            
        ext = path.suffix.lower()
        
        if ext not in self.supported_extensions:
            available_libs = []
            if not PDF_AVAILABLE and ext == ".pdf":
                raise ValueError("PDF support requires PyPDF2 library")
            if not DOCX_AVAILABLE and ext == ".docx":
                raise ValueError("DOCX support requires python-docx library")
            raise ValueError(f"Unsupported file type: {ext}. Supported: {self.supported_extensions}")
        
        try:
            if ext == ".txt":
                return self._read_txt(path, encoding)
            elif ext == ".pdf":
                return self._read_pdf(path)
            elif ext == ".docx":
                return self._read_docx(path)
        except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
            raise Exception(f"Failed to read {file_path}: {e}")
        
        return []
    
    def _read_txt(self, path: Path, encoding: str) -> List[str]:
        """Read text file and split by double newlines."""
        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
                # Split by double newlines and filter empty strings
                texts = [p.strip() for p in content.split("\n\n") if p.strip()]
                return texts if texts else [content.strip()] if content.strip() else []
        except UnicodeDecodeError:
            # Fallback to different encodings
            for fallback_encoding in ['latin-1', 'cp1252', 'utf-16']:
                try:
                    with open(path, "r", encoding=fallback_encoding) as f:
                        content = f.read()
                        texts = [p.strip() for p in content.split("\n\n") if p.strip()]
                        return texts if texts else [content.strip()] if content.strip() else []
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"Could not decode text file with any common encoding")
    
    def _read_pdf(self, path: Path) -> List[str]:
        """Read PDF file and extract text from each page."""
        if not PDF_AVAILABLE:
            raise ValueError("PDF support requires PyPDF2 library")
            
        reader = PdfReader(str(path))
        texts = []
        
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    texts.append(page_text.strip())
            except Exception as e:
                logging.warning(f"Could not extract text from page {page_num + 1}: {e}")
                continue
        
        return texts
    
    def _read_docx(self, path: Path) -> List[str]:
        """Read DOCX file and extract text from each paragraph."""
        if not DOCX_AVAILABLE:
            raise ValueError("DOCX support requires python-docx library")
            
        doc = docx.Document(str(path))
        texts = []
        
        for para in doc.paragraphs:
            if para.text and para.text.strip():
                texts.append(para.text.strip())
        
        return texts

# Example usage and testing
if __name__ == "__main__":
    reader = DocumentReader()
    print(f"Supported extensions: {reader.SUPPORTED_EXTENSIONS}")
    
    # Example usage:
    # texts = reader.read("example.pdf")
    # for i, text in enumerate(texts):
    #     print(f"Chunk {i+1}: {text[:100]}...")