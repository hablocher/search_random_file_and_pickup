#!/usr/bin/env python
"""
Script de teste para verificar filtragem de keywords
"""

filename = 'Marvel Team-Up v1 01-20 (1972-1985).zip'
keywords = ['team-up', 'marvel']
filename_lower = filename.lower()

print(f'Arquivo: {filename}')
print(f'Keywords: {keywords}')
print(f'Filename lower: {filename_lower}')
print()

result_and = all(kw in filename_lower for kw in keywords)
result_or = any(kw in filename_lower for kw in keywords)

print(f'Modo AND (todas): {result_and}')
print(f'Modo OR (ao menos uma): {result_or}')
print()

print('Verificação individual:')
for kw in keywords:
    present = kw in filename_lower
    print(f"  - '{kw}' in filename: {present}")
