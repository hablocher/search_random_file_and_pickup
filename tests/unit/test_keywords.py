"""Script de teste para verificar a lógica de palavras-chave"""

# Teste 1: Processamento das palavras-chave
text = "batman, superman"
keywords = [kw.strip().lower() for kw in text.split(",") if kw.strip()]
print("Teste 1 - Processamento:")
print(f"  Input: '{text}'")
print(f"  Keywords: {keywords}")
print(f"  Tipo: {type(keywords)}")
print()

# Teste 2: Matching com arquivo
filename = "Batman Year One.cbr"
file_name_lower = filename.lower()
print("Teste 2 - Matching:")
print(f"  Filename: '{filename}'")
print(f"  Lowercase: '{file_name_lower}'")
print(f"  Keywords: {keywords}")

for kw in keywords:
    match = kw in file_name_lower
    print(f"  '{kw}' in '{file_name_lower}': {match}")

result = any(keyword in file_name_lower for keyword in keywords)
print(f"  Resultado final (any): {result}")
print()

# Teste 3: Caso que não deveria dar match
filename2 = "Wonder Woman.cbr"
file_name_lower2 = filename2.lower()
print("Teste 3 - Sem match:")
print(f"  Filename: '{filename2}'")
print(f"  Lowercase: '{file_name_lower2}'")
result2 = any(keyword in file_name_lower2 for keyword in keywords)
print(f"  Resultado (any): {result2}")
print()

# Teste 4: Palavras-chave vazias
keywords_empty = []
print("Teste 4 - Keywords vazias:")
print(f"  Keywords: {keywords_empty}")
print(f"  Deve pular filtro: {not keywords_empty}")
