#!/usr/bin/env python3
"""Script de migração de cache antigo (JSON.gz) para novo formato (pickle otimizado)."""

import json
import gzip
import pickle
from pathlib import Path
from collections import defaultdict


def migrate_cache():
    """Migra cache do formato antigo para o novo."""
    old_cache_file = Path.cwd() / "file_cache.json.gz"
    new_cache_dir = Path.cwd() / ".file_cache"
    
    if not old_cache_file.exists():
        print("✓ Nenhum cache antigo encontrado - nada para migrar")
        return
    
    print("🔄 Migrando cache para novo formato otimizado...")
    
    try:
        # Carrega cache antigo
        with gzip.open(old_cache_file, 'rt', encoding='utf-8') as f:
            old_cache = json.load(f)
        
        metadata = old_cache.get('metadata', {})
        files = old_cache.get('files', [])
        
        print(f"  Cache antigo: {len(files)} arquivos")
        
        # Cria diretório para novo cache
        new_cache_dir.mkdir(exist_ok=True)
        
        # Agrupa arquivos por pasta
        files_by_folder = defaultdict(list)
        for file_info in files:
            file_path = Path(file_info['path'])
            
            # Tenta identificar pasta raiz (busca no metadata)
            folder_mtimes = metadata.get('folder_mtimes', {})
            for folder in folder_mtimes.keys():
                try:
                    file_path.relative_to(folder)
                    files_by_folder[folder].append(file_info)
                    break
                except ValueError:
                    continue
        
        # Converte para novo formato
        from src.random_file_picker.core.cache_manager import CacheManager
        
        cache_manager = CacheManager()
        
        # Salva usando o novo sistema
        all_files = []
        for folder_files in files_by_folder.values():
            all_files.extend(folder_files)
        
        if all_files:
            folders = list(files_by_folder.keys())
            
            # Extrai configurações do metadata antigo
            config_hash = metadata.get('config_hash', '')
            
            success = cache_manager.save_cache(
                all_files, 
                folders,
                read_prefix="_L_",
                ignore_prefix=".",
                keywords=[],
                process_zip=True,
                keywords_match_all=False
            )
            
            if success:
                print(f"✓ Migração concluída com sucesso!")
                print(f"  Novo cache: {len(folders)} pastas indexadas")
                
                cache_info = cache_manager.get_cache_info()
                if cache_info:
                    print(f"  Índice: {cache_info.get('indexed_words', 0)} palavras")
                
                # Remove cache antigo
                old_cache_file.unlink()
                print(f"  Cache antigo removido: {old_cache_file.name}")
            else:
                print("❌ Erro ao salvar novo cache")
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        print("  O cache antigo será mantido")


if __name__ == "__main__":
    migrate_cache()
