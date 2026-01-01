# Random File Picker

Programa Python que seleciona aleatoriamente um arquivo de uma lista de pastas, excluindo arquivos com prefixo específico.

## Funcionalidades

- Busca recursiva em pastas e subpastas
- Exclusão de arquivos com prefixo "_L_" no nome
- Seleção aleatória de arquivos
- Tratamento de erros para pastas inexistentes

## Como usar

### Uso básico

```python
from random_file_picker import pick_random_file

folders = [
    r"C:\Users\Documents",
    r"C:\Users\Downloads"
]

selected_file = pick_random_file(folders)
print(f"Arquivo selecionado: {selected_file}")
```

### Executar o programa de exemplo

```bash
python random_file_picker.py
```

### Personalizar o prefixo de exclusão

```python
from random_file_picker import pick_random_file

folders = [r"C:\Users\Documents"]
selected_file = pick_random_file(folders, exclude_prefix="_OLD_")
```

### Listar todos os arquivos válidos

```python
from random_file_picker import collect_files

folders = [r"C:\Users\Documents"]
files = collect_files(folders)

print(f"Total de arquivos: {len(files)}")
for file in files:
    print(file)
```

## Requisitos

- Python 3.6 ou superior
- Módulos padrão do Python (pathlib, random, os)

## Exemplos

### Exemplo 1: Uso simples

```python
folders = [r"E:\Projetos"]
arquivo = pick_random_file(folders)
print(arquivo)
```

### Exemplo 2: Múltiplas pastas

```python
folders = [
    r"C:\Users\Documents",
    r"C:\Users\Pictures",
    r"D:\Backup"
]
arquivo = pick_random_file(folders)
print(arquivo)
```

### Exemplo 3: Tratamento de exceções

```python
try:
    arquivo = pick_random_file([r"C:\PastaInexistente"])
    print(arquivo)
except ValueError as e:
    print(f"Erro: {e}")
```
