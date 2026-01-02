"""
Teste de validação: Verifica se todas as configurações da GUI estão sendo salvas e carregadas corretamente
"""
import json
from pathlib import Path

# Arquivo de configuração
config_file = Path("config.json")

# Lista de todas as configurações esperadas
expected_configs = [
    "folders",
    "exclude_prefix",
    "open_folder",
    "open_file",
    "use_sequence",
    "history_limit",
    "keywords",
    "keywords_match_all",
    "ignored_extensions",
    "process_zip",
    "use_cache",
    "enable_cloud_hydration",
    "file_history",
    "last_opened_folder"
]

print("=" * 70)
print("VALIDAÇÃO DE CONFIGURAÇÕES")
print("=" * 70)
print()

# Verifica se o arquivo existe
if config_file.exists():
    print(f"✓ Arquivo de configuração encontrado: {config_file}")
    
    # Carrega o JSON
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"✓ Arquivo carregado com sucesso")
    print()
    
    # Verifica cada configuração
    print("Verificando configurações:")
    print("-" * 70)
    
    missing = []
    found = []
    
    for key in expected_configs:
        if key in config:
            value = config[key]
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:50] + "..."
            print(f"  ✓ {key:25} = {value_str}")
            found.append(key)
        else:
            print(f"  ✗ {key:25} = NÃO ENCONTRADO")
            missing.append(key)
    
    print("-" * 70)
    print()
    
    # Resumo
    print("RESUMO:")
    print(f"  Configurações encontradas: {len(found)}/{len(expected_configs)}")
    
    if missing:
        print(f"  ⚠ Configurações ausentes: {', '.join(missing)}")
        print()
        print("STATUS: FALHOU - Algumas configurações não estão sendo salvas")
    else:
        print(f"  ✓ Todas as configurações estão presentes!")
        print()
        print("STATUS: SUCESSO - Todas as configurações estão sendo salvas corretamente")
    
    # Verifica configurações extras (não esperadas)
    extra_configs = [k for k in config.keys() if k not in expected_configs]
    if extra_configs:
        print()
        print(f"  ℹ Configurações extras encontradas: {', '.join(extra_configs)}")
    
else:
    print(f"✗ Arquivo de configuração não encontrado: {config_file}")
    print()
    print("Execute o aplicativo e salve a configuração primeiro!")
    print("STATUS: FALHOU - Arquivo não existe")

print()
print("=" * 70)
