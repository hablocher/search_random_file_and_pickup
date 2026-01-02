"""
Script de debug para rastrear o fluxo de configuração do use_cache
"""
import json
from pathlib import Path

config_path = Path("config.json")

print("=" * 60)
print("DEBUG: Fluxo de Configuração - use_cache")
print("=" * 60)

# 1. Ler o valor atual do config.json
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("\n1. Valor no config.json:")
    print(f"   use_cache = {config.get('use_cache')} (tipo: {type(config.get('use_cache')).__name__})")
    
    # 2. Simular o que o load_config() faz
    loaded_value = config.get("use_cache", True)
    print(f"\n2. Após config.get('use_cache', True):")
    print(f"   loaded_value = {loaded_value} (tipo: {type(loaded_value).__name__})")
    
    # 3. Verificar se há outros campos que podem estar interferindo
    print(f"\n3. Verificação de outros campos:")
    for key in ['open_folder', 'open_file', 'use_sequence', 'process_zip', 'keywords_match_all', 'enable_cloud_hydration']:
        val = config.get(key)
        print(f"   {key} = {val} (tipo: {type(val).__name__})")
    
    # 4. Verificar se há alguma conversão de string
    print(f"\n4. Teste de conversão:")
    test_value = config.get("use_cache")
    print(f"   bool('{test_value}') = {bool(test_value)}")
    print(f"   str('{test_value}').lower() == 'true' = {str(test_value).lower() == 'true'}")
    
else:
    print("\nERRO: config.json não encontrado!")

print("\n" + "=" * 60)
print("FIM DO DEBUG")
print("=" * 60)
