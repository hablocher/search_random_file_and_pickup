"""Carregamento de arquivos com suporte a chunks, progresso e cancelamento."""

import os
import time
from typing import Callable, Optional, Tuple


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
