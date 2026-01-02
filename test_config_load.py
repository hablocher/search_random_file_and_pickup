import json

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    
print('Valores REAIS carregados do config.json:')
print('=' * 60)
print(f'open_folder: {config.get("open_folder")} (tipo: {type(config.get("open_folder")).__name__})')
print(f'open_file: {config.get("open_file")} (tipo: {type(config.get("open_file")).__name__})')
print(f'use_cache: {config.get("use_cache")} (tipo: {type(config.get("use_cache")).__name__})')
print(f'use_sequence: {config.get("use_sequence")} (tipo: {type(config.get("use_sequence")).__name__})')
print(f'process_zip: {config.get("process_zip")} (tipo: {type(config.get("process_zip")).__name__})')
print(f'keywords_match_all: {config.get("keywords_match_all")} (tipo: {type(config.get("keywords_match_all")).__name__})')
print('=' * 60)
print()
print('Valores que DEVERIAM aparecer na GUI:')
print(f'  ☐ Abrir pasta automaticamente: {"✓" if config.get("open_folder") else "☐"}')
print(f'  {"✓" if config.get("open_file") else "☐"} Abrir arquivo automaticamente')
print(f'  {"✓" if config.get("use_sequence") else "☐"} Usar seleção sequencial')
print(f'  {"✓" if config.get("process_zip") else "☐"} Processar arquivos ZIP')
print(f'  {"✓" if config.get("use_cache") else "☐"} Usar cache de arquivos')
print(f'  {"✓" if config.get("keywords_match_all") else "☐"} TODAS as palavras (AND)')
