"""Gerenciador de cache otimizado para busca de arquivos."""

import pickle
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from collections import defaultdict


class CacheManager:
    """Gerencia cache de arquivos com otimizações avançadas:
    - Cache granular por pasta (invalidação seletiva)
    - Índices de keywords para busca instantânea
    - Pickle para serialização rápida
    - Lazy loading de dados
    """
    
    def __init__(self, cache_dir: str = ".file_cache"):
        """Inicializa o gerenciador de cache.
        
        Args:
            cache_dir: Diretório para armazenar arquivos de cache.
        """
        self.cache_dir = Path.cwd() / cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache em memória (lazy loading)
        self._folder_caches: Dict[str, Dict[str, Any]] = {}
        self._keyword_index: Optional[Dict[str, List[str]]] = None
        self._loaded = False
    
    def _get_folder_hash(self, folder: str) -> str:
        """Gera hash único para uma pasta.
        
        Args:
            folder: Caminho da pasta.
            
        Returns:
            Hash MD5 do caminho normalizado da pasta.
        """
        normalized = str(Path(folder).resolve())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def _get_cache_file(self, folder: str) -> Path:
        """Obtém caminho do arquivo de cache para uma pasta.
        
        Args:
            folder: Caminho da pasta.
            
        Returns:
            Path do arquivo de cache.
        """
        folder_hash = self._get_folder_hash(folder)
        return self.cache_dir / f"folder_{folder_hash}.pkl"
    
    def _get_index_file(self) -> Path:
        """Obtém caminho do arquivo de índice de keywords.
        
        Returns:
            Path do arquivo de índice.
        """
        return self.cache_dir / "keyword_index.pkl"
    
    def _get_config_hash(self, read_prefix: str, ignore_prefix: str, 
                        process_zip: bool) -> str:
        """Gera hash das configurações de busca (sem keywords).
        
        Args:
            read_prefix: Prefixo de arquivos lidos.
            ignore_prefix: Prefixo de pastas a ignorar.
            process_zip: Se processa arquivos ZIP.
            
        Returns:
            Hash MD5 das configurações.
        """
        config_str = f"{read_prefix}|{ignore_prefix}|{process_zip}"
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def _get_folder_mtime(self, folder: str) -> float:
        """Obtém timestamp de última modificação de uma pasta.
        
        OTIMIZADO: Usa apenas o timestamp da própria pasta, não itera arquivos.
        
        Args:
            folder: Caminho da pasta.
            
        Returns:
            Timestamp de última modificação ou 0 se não encontrar.
        """
        try:
            path = Path(folder)
            if path.exists() and path.is_dir():
                return path.stat().st_mtime
            return 0.0
        except (OSError, PermissionError):
            return 0.0
    
    def _build_keyword_index(self, all_files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Constrói índice reverso de keywords para busca rápida.
        
        Args:
            all_files: Lista de todos os arquivos de todas as pastas.
            
        Returns:
            Dicionário {keyword: [lista de paths que contêm a keyword]}.
        """
        index = defaultdict(list)
        
        for file_info in all_files:
            file_path = file_info['path']
            file_name_lower = Path(file_path).name.lower()
            
            # Tokeniza o nome do arquivo em palavras
            # Remove extensões e caracteres especiais
            words = file_name_lower.replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
            
            # Adiciona cada palavra ao índice
            for word in words:
                if len(word) >= 2:  # Ignora palavras muito curtas
                    index[word].append(file_path)
        
        return dict(index)
    
    def is_cache_valid(self, folders: List[str], read_prefix: str, 
                      ignore_prefix: str, keywords: List[str], 
                      process_zip: bool, keywords_match_all: bool = False) -> bool:
        """Verifica se o cache é válido para as configurações atuais.
        
        OTIMIZADO: Validação granular por pasta + lazy loading.
        
        Args:
            folders: Lista de pastas para buscar.
            read_prefix: Prefixo de arquivos lidos.
            ignore_prefix: Prefixo de pastas a ignorar.
            keywords: Lista de palavras-chave (não afeta validação).
            process_zip: Se processa arquivos ZIP.
            keywords_match_all: Se deve aplicar AND ou OR (não afeta validação).
            
        Returns:
            True se o cache é válido, False caso contrário.
        """
        config_hash = self._get_config_hash(read_prefix, ignore_prefix, process_zip)
        
        # Verifica cada pasta individualmente
        for folder in folders:
            cache_file = self._get_cache_file(folder)
            
            if not cache_file.exists():
                return False
            
            try:
                # Carrega apenas metadados (lazy loading)
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                metadata = cache_data.get('metadata', {})
                
                # Verifica hash de configuração
                if metadata.get('config_hash') != config_hash:
                    return False
                
                # Verifica timestamp da pasta
                current_mtime = self._get_folder_mtime(folder)
                cached_mtime = metadata.get('folder_mtime', 0)
                
                if current_mtime > cached_mtime:
                    return False
                    
            except (pickle.PickleError, OSError, KeyError):
                return False
        
        return True
    
    def load_cache(self) -> Optional[Dict[str, Any]]:
        """Carrega o cache do disco com lazy loading.
        
        OTIMIZADO: Carrega todas as pastas e constrói índice de keywords.
        
        Returns:
            Dicionário consolidado com todos os arquivos ou None se erro.
        """
        if self._loaded:
            return self._get_consolidated_cache()
        
        all_files = []
        
        # Carrega cache de cada pasta
        for cache_file in self.cache_dir.glob("folder_*.pkl"):
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                folder_path = cache_data['metadata']['folder_path']
                files = cache_data.get('files', [])
                
                self._folder_caches[folder_path] = cache_data
                all_files.extend(files)
                
            except (pickle.PickleError, OSError, KeyError):
                continue
        
        # Constrói índice de keywords
        if all_files:
            self._keyword_index = self._build_keyword_index(all_files)
        
        self._loaded = True
        return self._get_consolidated_cache()
    
    def _get_consolidated_cache(self) -> Dict[str, Any]:
        """Consolida todos os caches de pastas em um único dicionário.
        
        Returns:
            Dicionário com metadados e arquivos consolidados.
        """
        all_files = []
        total_size = 0
        
        for cache_data in self._folder_caches.values():
            all_files.extend(cache_data.get('files', []))
        
        # Calcula tamanho total do cache
        for cache_file in self.cache_dir.glob("folder_*.pkl"):
            try:
                total_size += cache_file.stat().st_size
            except OSError:
                continue
        
        return {
            'metadata': {
                'folder_count': len(self._folder_caches),
                'file_count': len(all_files),
                'cache_size': total_size
            },
            'files': all_files
        }
    
    def save_cache(self, files: List[Dict[str, Any]], folders: List[str], 
                   read_prefix: str, ignore_prefix: str, keywords: List[str], 
                   process_zip: bool, keywords_match_all: bool = False) -> bool:
        """Salva o cache no disco com estrutura otimizada.
        
        OTIMIZADO: Cache granular por pasta + índice de keywords.
        
        Args:
            files: Lista de arquivos encontrados (com campo 'folder' indicando origem).
            folders: Lista de pastas pesquisadas.
            read_prefix: Prefixo de arquivos lidos.
            ignore_prefix: Prefixo de pastas a ignorar.
            keywords: Lista de palavras-chave (não salvo, apenas para compatibilidade).
            process_zip: Se processa arquivos ZIP.
            keywords_match_all: AND ou OR (não salvo, apenas para compatibilidade).
            
        Returns:
            True se salvou com sucesso, False caso contrário.
        """
        try:
            config_hash = self._get_config_hash(read_prefix, ignore_prefix, process_zip)
            
            # Agrupa arquivos por pasta de origem
            files_by_folder = defaultdict(list)
            for file_info in files:
                # Identifica pasta de origem pelo path
                file_path = Path(file_info['path'])
                
                # Encontra qual pasta contém este arquivo
                for folder in folders:
                    try:
                        file_path.relative_to(folder)
                        files_by_folder[folder].append(file_info)
                        break
                    except ValueError:
                        continue
            
            # Salva cache para cada pasta individualmente
            for folder, folder_files in files_by_folder.items():
                cache_file = self._get_cache_file(folder)
                
                cache_data = {
                    'metadata': {
                        'folder_path': folder,
                        'created_at': datetime.now().isoformat(),
                        'config_hash': config_hash,
                        'folder_mtime': self._get_folder_mtime(folder),
                        'file_count': len(folder_files)
                    },
                    'files': folder_files
                }
                
                with open(cache_file, 'wb') as f:
                    pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                self._folder_caches[folder] = cache_data
            
            # Constrói e salva índice de keywords
            self._keyword_index = self._build_keyword_index(files)
            index_file = self._get_index_file()
            
            with open(index_file, 'wb') as f:
                pickle.dump(self._keyword_index, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            self._loaded = True
            return True
            
        except (OSError, TypeError, pickle.PickleError) as e:
            return False
    
    def get_cached_files(self, keywords: Optional[List[str]] = None, 
                        keywords_match_all: bool = False) -> List[Dict[str, Any]]:
        """Obtém lista de arquivos do cache com busca otimizada por keywords.
        
        OTIMIZADO: Usa índice de keywords para busca instantânea.
        
        Args:
            keywords: Lista de palavras-chave para filtrar (opcional).
            keywords_match_all: Se True usa AND, se False usa OR.
        
        Returns:
            Lista de arquivos ou lista vazia se cache inválido.
        """
        if not self._loaded:
            self.load_cache()
        
        all_files = []
        for cache_data in self._folder_caches.values():
            all_files.extend(cache_data.get('files', []))
        
        # Se não há keywords, retorna tudo
        if not keywords:
            return all_files
        
        # Busca otimizada com índice
        if self._keyword_index:
            return self._search_with_index(keywords, keywords_match_all)
        
        # Fallback: busca linear (se índice não disponível)
        return self._search_linear(all_files, keywords, keywords_match_all)
    
    def _search_with_index(self, keywords: List[str], match_all: bool) -> List[Dict[str, Any]]:
        """Busca usando índice de keywords (RÁPIDO).
        
        Args:
            keywords: Lista de palavras-chave.
            match_all: Se True usa AND, se False usa OR.
            
        Returns:
            Lista de arquivos que correspondem aos critérios.
        """
        keywords_lower = [kw.lower() for kw in keywords]
        
        if match_all:
            # AND: arquivo deve estar em TODAS as listas de keywords
            matching_paths = None
            
            for keyword in keywords_lower:
                # Busca parcial: qualquer palavra do índice que contenha o keyword
                keyword_paths = set()
                for indexed_word, paths in self._keyword_index.items():
                    if keyword in indexed_word:
                        keyword_paths.update(paths)
                
                if matching_paths is None:
                    matching_paths = keyword_paths
                else:
                    matching_paths &= keyword_paths
                
                if not matching_paths:
                    return []
            
            result_paths = matching_paths if matching_paths else set()
            
        else:
            # OR: arquivo deve estar em PELO MENOS UMA lista
            result_paths = set()
            
            for keyword in keywords_lower:
                for indexed_word, paths in self._keyword_index.items():
                    if keyword in indexed_word:
                        result_paths.update(paths)
        
        # Recupera informações completas dos arquivos
        all_files = []
        for cache_data in self._folder_caches.values():
            all_files.extend(cache_data.get('files', []))
        
        return [f for f in all_files if f['path'] in result_paths]
    
    def _search_linear(self, files: List[Dict[str, Any]], 
                      keywords: List[str], match_all: bool) -> List[Dict[str, Any]]:
        """Busca linear tradicional (LENTO - fallback).
        
        Args:
            files: Lista de arquivos.
            keywords: Lista de palavras-chave.
            match_all: Se True usa AND, se False usa OR.
            
        Returns:
            Lista de arquivos filtrados.
        """
        keywords_lower = [kw.lower() for kw in keywords]
        result = []
        
        for file_info in files:
            file_name_lower = Path(file_info['path']).name.lower()
            
            if match_all:
                if all(kw in file_name_lower for kw in keywords_lower):
                    result.append(file_info)
            else:
                if any(kw in file_name_lower for kw in keywords_lower):
                    result.append(file_info)
        
        return result
    
    def clear_cache(self) -> bool:
        """Remove todos os arquivos de cache.
        
        Returns:
            True se removeu com sucesso, False caso contrário.
        """
        try:
            # Remove todos os arquivos .pkl no diretório de cache
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            
            # Limpa cache em memória
            self._folder_caches.clear()
            self._keyword_index = None
            self._loaded = False
            
            return True
        except OSError:
            return False
    
    def get_cache_info(self) -> Optional[Dict[str, Any]]:
        """Obtém informações sobre o cache.
        
        Returns:
            Dicionário com metadados do cache ou None.
        """
        if not self._loaded:
            self.load_cache()
        
        if not self._folder_caches:
            return None
        
        total_files = 0
        total_size = 0
        folder_info = []
        
        for folder_path, cache_data in self._folder_caches.items():
            metadata = cache_data.get('metadata', {})
            file_count = metadata.get('file_count', 0)
            total_files += file_count
            
            folder_info.append({
                'folder': folder_path,
                'files': file_count,
                'updated': metadata.get('created_at', 'Unknown')
            })
        
        # Calcula tamanho total
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                total_size += cache_file.stat().st_size
            except OSError:
                continue
        
        return {
            'folder_count': len(self._folder_caches),
            'file_count': total_files,
            'file_size': total_size,
            'has_keyword_index': self._keyword_index is not None,
            'indexed_words': len(self._keyword_index) if self._keyword_index else 0,
            'folders': folder_info
        }

