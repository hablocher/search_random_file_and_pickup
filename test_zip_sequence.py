"""
Script de teste para verificar a análise de sequência em arquivos extraídos de ZIP.

Este script demonstra como a função agora detecta sequências dentro de arquivos ZIP.

Exemplo de funcionamento:
1. ZIP contém: "_L_teste 001.cbr", "teste 002.cbr", "teste 003.cbr", "teste 004.cbr"
2. Um arquivo aleatório é selecionado (ex: "teste 003.cbr")
3. A análise de sequência detecta a sequência
4. Retorna o primeiro não lido: "teste 002.cbr"

Se o ZIP contém apenas "arquivo_normal.cbr" (sem sequência):
- Retorna "arquivo_normal.cbr"
"""

from src.random_file_picker.core.file_picker import pick_random_file_with_zip_support

# Exemplo de uso (substitua com seu caminho real)
test_folders = [
    r"E:\Teste\Pasta_com_ZIPs"  # Pasta que contém ZIPs
]

print("=" * 70)
print("TESTE: Análise de Sequência em Arquivos ZIP")
print("=" * 70)
print("\nEste teste verifica se a análise de sequência funciona")
print("quando arquivos são extraídos de um ZIP.\n")

try:
    # Seleciona um arquivo aleatório com processamento de ZIP habilitado
    result = pick_random_file_with_zip_support(
        folders=test_folders,
        exclude_prefix="_L_",
        keywords=[],
        keywords_match_all=False,
        process_zip=True,  # Habilita processamento de ZIP
        use_cache=True,
        ignored_extensions=[]
    )
    
    print("\n" + "=" * 70)
    print("RESULTADO:")
    print("=" * 70)
    print(f"\nArquivo selecionado: {result['file_path']}")
    print(f"É de um ZIP: {result['is_from_zip']}")
    if result['is_from_zip']:
        print(f"ZIP original: {result['zip_path']}")
        print(f"Arquivo no ZIP: {result['file_in_zip']}")
        print(f"Pasta temporária: {result['temp_dir']}")
    
    print("\n" + "=" * 70)
    print("COMPORTAMENTO ESPERADO:")
    print("=" * 70)
    print("✓ Se o ZIP contiver uma sequência (ex: teste 001, 002, 003, 004):")
    print("  - Detecta a sequência")
    print("  - Seleciona o primeiro arquivo não lido")
    print("  - Logs mostrarão: 'Sequência detectada dentro do ZIP!'")
    print()
    print("✓ Se o ZIP contiver apenas arquivos isolados:")
    print("  - Seleciona um arquivo aleatório")
    print("  - Logs mostrarão: 'Nenhuma sequência detectada - seleção aleatória'")
    print("=" * 70)
    
except Exception as e:
    print(f"\nErro: {e}")
    print("\nVerifique se a pasta de teste existe e contém arquivos ZIP.")
