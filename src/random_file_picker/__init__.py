"""
Media Finder - Seleção inteligente de arquivos com interface gráfica.

Um programa para seleção aleatória e sequencial de arquivos com suporte a:
- Seleção aleatória e sequencial
- Interface gráfica Tkinter
- Suporte a cloud storage (Google Drive, OneDrive)
- Processamento de arquivos ZIP
- Rastreamento de arquivos lidos
"""

__version__ = "2.0.0"
__author__ = "Seu Nome"
__email__ = "seu.email@example.com"

from random_file_picker.core.file_picker import (
    pick_random_file,
    pick_random_file_with_zip_support,
    collect_files,
    open_folder,
    is_file_accessible,
    list_files_in_zip,
    extract_file_from_zip,
    get_temp_extraction_dir,
    cleanup_temp_dir,
)
from random_file_picker.core.sequential_selector import (
    SequentialFileTracker,
    select_file_with_sequence_logic,
    analyze_folder_sequence,
    get_next_unread_file,
    extract_number_from_filename,
    extract_collection_name,
)

__all__ = [
    "pick_random_file",
    "pick_random_file_with_zip_support",
    "collect_files",
    "open_folder",
    "is_file_accessible",
    "list_files_in_zip",
    "extract_file_from_zip",
    "get_temp_extraction_dir",
    "cleanup_temp_dir",
    "SequentialFileTracker",
    "select_file_with_sequence_logic",
    "analyze_folder_sequence",
    "get_next_unread_file",
    "extract_number_from_filename",
    "extract_collection_name",
]
