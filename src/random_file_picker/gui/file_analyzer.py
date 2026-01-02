"""Análise e formatação de informações de arquivos."""

import io
import os
import zipfile
from pathlib import Path
from typing import Dict, Optional

import rarfile

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

from .archive_extractor import ArchiveExtractor


class FileAnalyzer:
    """Analisa arquivos e extrai informações detalhadas."""
    
    @staticmethod
    def analyze_file(file_path: str) -> Dict[str, any]:
        """Analisa arquivo e retorna informações detalhadas.
        
        Args:
            file_path: Caminho do arquivo a analisar.
            
        Returns:
            Dicionário com informações do arquivo:
            - name: Nome do arquivo
            - folder: Pasta do arquivo
            - size: Tamanho em bytes
            - size_mb: Tamanho em MB
            - format: Formato detectado (ZIP, RAR, PDF, etc)
            - page_count: Número de páginas/imagens
            - extension: Extensão do arquivo
        """
        file_name = Path(file_path).name
        folder_path = str(Path(file_path).parent)
        file_size = os.path.getsize(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        # Detecta formato
        with open(file_path, 'rb') as f:
            file_header = f.read(10)
        
        detected_format = ArchiveExtractor.detect_format(file_header)
        format_name = "Desconhecido"
        page_count = 0
        
        # Analisa baseado no formato
        if file_ext == '.pdf' or detected_format == 'pdf':
            format_name = "PDF"
            page_count = FileAnalyzer._count_pdf_pages(file_path)
        elif file_ext in ['.rar', '.cbr'] or detected_format in ['rar', 'rar5']:
            format_name = "RAR"
            page_count = FileAnalyzer._count_rar_images(file_path)
        elif file_ext in ['.zip', '.cbz'] or detected_format == 'zip':
            format_name = "ZIP"
            page_count = FileAnalyzer._count_zip_images(file_path)
        elif detected_format == '7z':
            format_name = "7-Zip"
        
        return {
            'name': file_name,
            'folder': folder_path,
            'size': file_size,
            'size_mb': file_size / (1024 * 1024),
            'format': format_name,
            'page_count': page_count,
            'extension': file_ext
        }
    
    @staticmethod
    def format_file_info_table(info: Dict[str, any]) -> str:
        """Formata informações do arquivo como tabela.
        
        Args:
            info: Dicionário com informações do arquivo.
            
        Returns:
            String formatada com tabela de informações.
        """
        lines = []
        lines.append("=" * 70)
        lines.append("INFORMAÇÕES DO ARQUIVO")
        lines.append("=" * 70)
        lines.append(f"Nome:        {info['name']}")
        lines.append(f"Pasta:       {info['folder']}")
        lines.append(f"Formato:     {info['format']}")
        
        if info['page_count'] > 0:
            page_label = "Páginas" if info['format'] == "PDF" else "Imagens"
            lines.append(f"{page_label}:     {info['page_count']}")
        
        lines.append(f"Tamanho:     {info['size']:,} bytes ({info['size_mb']:.2f} MB)")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    @staticmethod
    def _count_pdf_pages(file_path: str) -> int:
        """Conta número de páginas em PDF.
        
        Args:
            file_path: Caminho do arquivo PDF.
            
        Returns:
            Número de páginas, ou 0 se erro.
        """
        if not HAS_PYMUPDF:
            return 0
        
        try:
            with open(file_path, 'rb') as f:
                pdf_data = f.read()
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception:
            return 0
    
    @staticmethod
    def _count_rar_images(file_path: str) -> int:
        """Conta número de imagens em RAR.
        
        Args:
            file_path: Caminho do arquivo RAR.
            
        Returns:
            Número de imagens, ou 0 se erro.
        """
        try:
            with open(file_path, 'rb') as f:
                rar_data = f.read()
            archive = rarfile.RarFile(io.BytesIO(rar_data), 'r')
            file_list = archive.namelist()
            page_count = len([f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            archive.close()
            return page_count
        except Exception:
            return 0
    
    @staticmethod
    def _count_zip_images(file_path: str) -> int:
        """Conta número de imagens em ZIP.
        
        Args:
            file_path: Caminho do arquivo ZIP.
            
        Returns:
            Número de imagens, ou 0 se erro.
        """
        try:
            with open(file_path, 'rb') as f:
                zip_data = f.read()
            archive = zipfile.ZipFile(io.BytesIO(zip_data), 'r')
            file_list = archive.namelist()
            page_count = len([f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            archive.close()
            return page_count
        except Exception:
            return 0
