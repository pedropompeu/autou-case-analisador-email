"""
Utilitários para processamento de arquivos.
"""
import io
import logging
from typing import Optional

import pypdf

logger = logging.getLogger(__name__)


class FileProcessor:
    """Processador de arquivos de texto e PDF."""

    SUPPORTED_EXTENSIONS = [".txt", ".pdf"]
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

    @staticmethod
    def process_file(file, filename: str) -> Optional[str]:
        """
        Processa arquivo e extrai texto.

        Args:
            file: Objeto de arquivo (FileStorage do Flask)
            filename: Nome do arquivo

        Returns:
            Texto extraído ou None em caso de erro
        """
        if not FileProcessor.is_supported(filename):
            logger.warning(f"Unsupported file type: {filename}")
            return None

        try:
            if filename.lower().endswith(".txt"):
                return FileProcessor._process_txt(file)
            elif filename.lower().endswith(".pdf"):
                return FileProcessor._process_pdf(file)
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            return None

        return None

    @staticmethod
    def is_supported(filename: str) -> bool:
        """Verifica se o arquivo é suportado."""
        return any(filename.lower().endswith(ext) for ext in FileProcessor.SUPPORTED_EXTENSIONS)

    @staticmethod
    def _process_txt(file) -> str:
        """Processa arquivo .txt."""
        return file.read().decode("utf-8")

    @staticmethod
    def _process_pdf(file) -> str:
        """Processa arquivo .pdf usando pypdf."""
        pdf_reader = pypdf.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
