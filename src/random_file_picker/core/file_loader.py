"""Carregamento de arquivos com suporte a chunks, progresso e cancelamento."""

import os
import sys
import time
from pathlib import Path
from typing import Callable, Optional, Tuple


def is_cloud_placeholder(file_path: str) -> Tuple[bool, str]:
    """Detecta se o arquivo é um placeholder de nuvem (OneDrive/Google Drive).
    
    Args:
        file_path: Caminho do arquivo a verificar.
        
    Returns:
        Tupla (is_placeholder, cloud_service).
        cloud_service pode ser: 'OneDrive', 'GoogleDrive', ou ''
    """
    try:
        path = Path(file_path)
        
        # Verifica se o arquivo existe
        if not path.exists():
            return False, ''
        
        # No Windows, verifica atributos do arquivo
        if sys.platform == 'win32':
            try:
                import ctypes
                from ctypes import wintypes
                
                # Constantes do Windows
                FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x00400000  # OneDrive placeholder
                FILE_ATTRIBUTE_PINNED = 0x00080000
                FILE_ATTRIBUTE_UNPINNED = 0x00100000
                
                # Obter atributos do arquivo
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
                
                if attrs == -1:
                    return False, ''
                
                # OneDrive: Arquivo com atributo RECALL_ON_DATA_ACCESS
                if attrs & FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS:
                    return True, 'OneDrive'
                
                # OneDrive: Arquivo não está "pinned" (disponível offline)
                if attrs & FILE_ATTRIBUTE_UNPINNED:
                    return True, 'OneDrive'
                
            except (ImportError, AttributeError, OSError):
                pass
        
        # Verificação adicional: Tenta ler os primeiros bytes do arquivo
        # Placeholders geralmente têm conteúdo stub/vazio
        try:
            file_size = path.stat().st_size
            
            # Se o arquivo tem tamanho > 0, tenta ler porções maiores
            if file_size > 10240:  # Maior que 10KB
                with open(path, 'rb') as f:
                    # Lê os primeiros 10KB
                    first_chunk = f.read(10240)
                    
                    # Verifica se é conteúdo real ou placeholder
                    if len(first_chunk) < 10240:
                        # Não conseguiu ler 10KB de um arquivo grande = placeholder
                        path_str = str(path).lower()
                        if 'onedrive' in path_str:
                            return True, 'OneDrive'
                        elif 'google' in path_str or 'drive' in path_str:
                            return True, 'GoogleDrive'
                        return True, 'Cloud'
                    
                    # Tenta ler do meio do arquivo (vários pontos)
                    test_positions = [
                        file_size // 4,   # 25%
                        file_size // 2,   # 50%
                        file_size * 3 // 4  # 75%
                    ]
                    
                    for pos in test_positions:
                        if pos < file_size:
                            f.seek(pos)
                            chunk = f.read(4096)  # Lê 4KB
                            
                            if len(chunk) < min(4096, file_size - pos):
                                # Não conseguiu ler do ponto esperado = placeholder
                                path_str = str(path).lower()
                                if 'onedrive' in path_str:
                                    return True, 'OneDrive'
                                elif 'google' in path_str or 'drive' in path_str:
                                    return True, 'GoogleDrive'
                                return True, 'Cloud'
                    
                    # Verifica padrões de placeholder (bytes repetidos)
                    # Alguns placeholders têm padrões específicos
                    if len(set(first_chunk)) < 10:  # Menos de 10 valores únicos em 10KB = suspeito
                        path_str = str(path).lower()
                        if 'onedrive' in path_str or 'google' in path_str or 'drive' in path_str:
                            return True, 'OneDrive' if 'onedrive' in path_str else 'GoogleDrive'
                        
        except (OSError, IOError):
            # Erro ao ler = pode ser placeholder
            path_str = str(path).lower()
            if 'onedrive' in path_str:
                return True, 'OneDrive'
            elif 'google' in path_str or 'drive' in path_str:
                return True, 'GoogleDrive'
            return True, 'Cloud'
        
        return False, ''
        
    except Exception:
        return False, ''


class FileLoader:
    """Carrega arquivos em chunks com suporte a progresso e cancelamento."""
    
    def __init__(self, chunk_size: int = 1024 * 1024):
        """Inicializa o carregador de arquivos.
        
        Args:
            chunk_size: Tamanho do chunk em bytes (padrão: 1MB).
        """
        self.chunk_size = chunk_size
        self.cancel_requested = False
        self.loading_start_time: Optional[float] = None
        
    def load_file(
        self,
        file_path: str,
        progress_callback: Optional[Callable[[float, int, float], None]] = None,
        cancel_check_callback: Optional[Callable[[], bool]] = None
    ) -> Tuple[Optional[bytes], bool]:
        """Carrega arquivo completo na memória em chunks.
        
        Args:
            file_path: Caminho do arquivo a carregar.
            progress_callback: Função chamada periodicamente com (percentual, bytes_lidos, tempo_decorrido).
            cancel_check_callback: Função que retorna True se o carregamento deve ser cancelado.
            
        Returns:
            Tupla (dados_do_arquivo, sucesso). Se cancelado ou erro, retorna (None, False).
        """
        try:
            self.cancel_requested = False
            self.loading_start_time = time.time()
            
            chunks = []
            file_size = os.path.getsize(file_path)
            bytes_read = 0
            last_update_time = time.time()
            
            with open(file_path, 'rb') as f:
                while True:
                    # Verifica cancelamento
                    if cancel_check_callback and cancel_check_callback():
                        return (None, False)
                    
                    if self.cancel_requested:
                        return (None, False)
                    
                    # Lê chunk
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    chunks.append(chunk)
                    bytes_read += len(chunk)
                    
                    # Atualiza progresso a cada 0.5s
                    current_time = time.time()
                    if current_time - last_update_time >= 0.5:
                        elapsed = current_time - self.loading_start_time
                        progress = (bytes_read / file_size * 100) if file_size > 0 else 0
                        
                        if progress_callback:
                            progress_callback(progress, bytes_read, elapsed)
                        
                        last_update_time = current_time
            
            # Junta todos os chunks
            file_data = b''.join(chunks)
            
            # Callback final
            if progress_callback:
                elapsed_total = time.time() - self.loading_start_time
                progress_callback(100.0, len(file_data), elapsed_total)
            
            return (file_data, True)
            
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
            return (None, False)
    
    def cancel(self):
        """Solicita cancelamento do carregamento atual."""
        self.cancel_requested = True
    
    def get_elapsed_time(self) -> float:
        """Retorna tempo decorrido desde o início do carregamento.
        
        Returns:
            Tempo em segundos, ou 0 se não iniciou.
        """
        if self.loading_start_time is None:
            return 0.0
        return time.time() - self.loading_start_time
