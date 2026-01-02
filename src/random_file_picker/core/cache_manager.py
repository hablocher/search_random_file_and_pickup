"""Gerenciador de cache para busca de arquivos."""

import json
import gzip
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class CacheManager:
    """Gerencia cache de arquivos encontrados nas pastas."""
    
    def __init__(self, cache_file: str = "file_cache.json.gz"):
        """Inicializa o gerenciador de cache.
        
        Args:
            cache_file: Nome do arquivo de cache (será criado no diretório do script).
        """
        self.cache_file = Path(__file__).parent.parent.parent.parent / cache_file
        self.cache_data: Optional[Dict[str, Any]] = None
    
    def _get_config_hash(self, folders: List[str], read_prefix: str, 
                        ignore_prefix: str, keywords: List[str], 
                        process_zip: bool) -> str:
        """Gera hash das configurações de busca.
        
        Args:
            folders: Lista de pastas para buscar.
            read_prefix: Prefixo de arquivos lidos.
            ignore_prefix: Prefixo de pastas a ignorar.
            keywords: Lista de palavras-chave.
            process_zip: Se processa arquivos ZIP.
            
        Returns:
            Hash MD5 das configurações.
        """
        config_str = json.dumps({
            'folders': sorted(folders),
            'read_prefix': read_prefix,
            'ignore_prefix': ignore_prefix,
            'keywords': sorted(keywords) if keywords else [],
            'process_zip': process_zip
        }, sort_keys=True)
        
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def _get_folder_mtime(self, folder: str) -> float:
        """Obtém timestamp de última modificação de uma pasta.
        
        Args:
            folder: Caminho da pasta.
            
        Returns:
            Timestamp de última modificação ou 0 se não encontrar.
        """
        try:
            path = Path(folder)
            if path.exists():
                # Pega o maior timestamp entre a pasta e seus arquivos
                max_mtime = path.stat().st_mtime
                
                # Para otimização, verifica apenas nível superior
                # (busca completa seria muito custosa)
                for item in path.iterdir():
                    try:
                        item_mtime = item.stat().st_mtime
                        if item_mtime > max_mtime:
                            max_mtime = item_mtime
                    except (OSError, PermissionError):
                        continue
                
                return max_mtime
            return 0.0
        except (OSError, PermissionError):
            return 0.0
    
    def is_cache_valid(self, folders: List[str], read_prefix: str, 
                      ignore_prefix: str, keywords: List[str], 
                      process_zip: bool) -> bool:
        """Verifica se o cache é válido para as configurações atuais.
        
        Args:
            folders: Lista de pastas para buscar.
            read_prefix: Prefixo de arquivos lidos.
            ignore_prefix: Prefixo de pastas a ignorar.
            keywords: Lista de palavras-chave.
            process_zip: Se processa arquivos ZIP.
            
        Returns:
            True se o cache é válido, False caso contrário.
        """
        if not self.cache_file.exists():
            return False
        
        if self.cache_data is None:
            self.cache_data = self.load_cache()
        
        if not self.cache_data or 'metadata' not in self.cache_data:
            return False
        
        metadata = self.cache_data['metadata']
        
        # Verifica hash das configurações
        current_hash = self._get_config_hash(folders, read_prefix, ignore_prefix, 
                                            keywords, process_zip)
        if metadata.get('config_hash') != current_hash:
            return False
        
        # Verifica se as pastas foram modificadas
        folder_mtimes = metadata.get('folder_mtimes', {})
        for folder in folders:
            current_mtime = self._get_folder_mtime(folder)
            cached_mtime = folder_mtimes.get(folder, 0)
            
            # Se a pasta foi modificada depois do cache, invalida
            if current_mtime > cached_mtime:
                return False
        
        return True
    
    def load_cache(self) -> Optional[Dict[str, Any]]:
        """Carrega o cache do disco.
        
        Returns:
            Dicionário com dados do cache ou None se não existir/erro.
        """
        if not self.cache_file.exists():
            return None
        
        try:
            with gzip.open(self.cache_file, 'rt', encoding='utf-8') as f:
                self.cache_data = json.load(f)
                return self.cache_data
        except (json.JSONDecodeError, OSError, EOFError):
            # Cache corrompido, retorna None
            return None
    
    def save_cache(self, files: List[Dict[str, Any]], folders: List[str], 
                   read_prefix: str, ignore_prefix: str, keywords: List[str], 
                   process_zip: bool) -> bool:
        """Salva o cache no disco.
        
        Args:
            files: Lista de arquivos encontrados.
            folders: Lista de pastas pesquisadas.
            read_prefix: Prefixo de arquivos lidos.
            ignore_prefix: Prefixo de pastas a ignorar.
            keywords: Lista de palavras-chave.
            process_zip: Se processa arquivos ZIP.
            
        Returns:
            True se salvou com sucesso, False caso contrário.
        """
        try:
            # Coleta timestamps das pastas
            folder_mtimes = {}
            for folder in folders:
                folder_mtimes[folder] = self._get_folder_mtime(folder)
            
            # Cria estrutura do cache
            cache_data = {
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'config_hash': self._get_config_hash(folders, read_prefix, 
                                                         ignore_prefix, keywords, 
                                                         process_zip),
                    'folder_mtimes': folder_mtimes,
                    'file_count': len(files)
                },
                'files': files
            }
            
            # Salva compactado
            with gzip.open(self.cache_file, 'wt', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.cache_data = cache_data
            return True
            
        except (OSError, TypeError) as e:
            return False
    
    def get_cached_files(self) -> List[Dict[str, Any]]:
        """Obtém lista de arquivos do cache.
        
        Returns:
            Lista de arquivos ou lista vazia se cache inválido.
        """
        if self.cache_data is None:
            self.cache_data = self.load_cache()
        
        if self.cache_data and 'files' in self.cache_data:
            return self.cache_data['files']
        
        return []
    
    def clear_cache(self) -> bool:
        """Remove o arquivo de cache.
        
        Returns:
            True se removeu com sucesso, False caso contrário.
        """
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            self.cache_data = None
            return True
        except OSError:
            return False
    
    def get_cache_info(self) -> Optional[Dict[str, Any]]:
        """Obtém informações sobre o cache.
        
        Returns:
            Dicionário com metadados do cache ou None.
        """
        if self.cache_data is None:
            self.cache_data = self.load_cache()
        
        if self.cache_data and 'metadata' in self.cache_data:
            metadata = self.cache_data['metadata'].copy()
            
            # Adiciona informações de tamanho
            if self.cache_file.exists():
                metadata['file_size'] = self.cache_file.stat().st_size
            
            return metadata
        
        return None
