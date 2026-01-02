"""
Teste para verificar a extração correta do nome da coleção.

Este script testa se a função extract_collection_name() está
identificando corretamente o nome base da série.
"""

from src.random_file_picker.core.sequential_selector import extract_collection_name

# Casos de teste
test_cases = [
    # (nome_arquivo, coleção_esperada)
    ("Marvel Team-Up v1 101.cbr", "Marvel Team-Up v1"),
    ("Marvel Team-Up v1 102.cbr", "Marvel Team-Up v1"),
    ("Marvel Team-Up v1 120.cbr", "Marvel Team-Up v1"),
    ("Serie v2 001.cbz", "Serie v2"),
    ("Serie v2 050.cbz", "Serie v2"),
    ("Arquivo 001.cbr", "Arquivo"),
    ("Arquivo 002.cbr", "Arquivo"),
    ("Capitão América #100.cbr", "Capitão América"),
    ("Capitão América #101.cbr", "Capitão América"),
    ("Amazing Spider-Man 001.cbz", "Amazing Spider-Man"),
    ("Amazing Spider-Man 999.cbz", "Amazing Spider-Man"),
]

print("=" * 70)
print("TESTE: Extração de Nome de Coleção")
print("=" * 70)

passed = 0
failed = 0

for filename, expected in test_cases:
    result = extract_collection_name(filename)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    
    if result == expected:
        passed += 1
    else:
        failed += 1
    
    print(f"\n{status}")
    print(f"  Arquivo:   {filename}")
    print(f"  Esperado:  '{expected}'")
    print(f"  Resultado: '{result}'")

print("\n" + "=" * 70)
print(f"RESUMO: {passed} passaram, {failed} falharam")
print("=" * 70)

if failed == 0:
    print("\n✓ Todos os testes passaram!")
    print("\nAgora arquivos como 'Marvel Team-Up v1 101.cbr' e")
    print("'Marvel Team-Up v1 102.cbr' serão identificados como")
    print("parte da mesma coleção: 'Marvel Team-Up v1'")
else:
    print(f"\n✗ {failed} teste(s) falharam!")
