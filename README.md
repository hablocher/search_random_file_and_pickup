# Random File Picker

Programa Python com interface gráfica que seleciona arquivos de forma inteligente a partir de uma lista de pastas, com suporte a seleção sequencial e aleatória.

## 🎯 Funcionalidades

### Interface Gráfica
- **Interface completa em Tkinter** com todas as configurações acessíveis
- **Gerenciamento de pastas** com adição e remoção via interface
- **Log detalhado** de todas as operações realizadas
- **Histórico persistente** dos últimos arquivos selecionados (configurável de 1 a 50)
- **Barras de rolagem** nas áreas de opções e histórico para melhor navegação
- **Filtragem por palavras-chave** (até 3 palavras, operação OR - ao menos uma deve estar presente)
- **Atalhos de teclado** para produtividade (Enter para buscar, Tab para navegar)

### Seleção Inteligente de Arquivos
- **Seleção Sequencial**: Detecta automaticamente arquivos numerados e seleciona o próximo não lido
  - Suporta múltiplos formatos: `001`, `#001`, `"01 de 10"`, `Cap/Vol/Part/Ep`, numerais romanos (I, II, III)
  - Gerencia múltiplas coleções/séries na mesma pasta
  - Rastreia arquivos já lidos por pasta
- **Seleção Aleatória**: Modo tradicional de seleção totalmente aleatória
- **Suporte a arquivos ZIP**: Detecta automaticamente quando um arquivo ZIP é selecionado
  - Explora o conteúdo do ZIP e continua a busca dentro dele
  - Aplica as mesmas regras de filtragem (palavras-chave, prefixo de exclusão)
  - Extrai o arquivo selecionado para pasta temporária e abre normalmente
  - Limpa automaticamente os arquivos temporários após o uso
- **Exclusão de arquivos lidos**: Ignora automaticamente arquivos com prefixo configurável (padrão: `_L_`)
- **Filtragem por palavras-chave**: Busca arquivos que contenham ao menos UMA das palavras-chave no nome (case-insensitive)

### Suporte a Cloud Storage
- Funciona com **Google Drive**, **OneDrive** e outras pastas de sincronização
- Ignora automaticamente pastas ocultas (prefixo `.`)
- Busca recursiva em todas as subpastas

### Automação
- **Abrir pasta automaticamente** após seleção (opcional)
- **Abrir arquivo automaticamente** com o aplicativo padrão (opcional)
- **Detecção de aplicativos**: Biblioteca específica por SO (Windows/Linux) que identifica aplicativo associado ao tipo de arquivo
- **Persistência de configurações**: Todas as preferências são salvas automaticamente
- **Detecção de mudanças**: Alerta se há configurações não salvas ao fechar

## 📋 Requisitos

- Python 3.6 ou superior
- Módulos padrão do Python (tkinter, pathlib, json, threading)

## 🚀 Como usar

### Iniciar a interface gráfica

```bash
python random_file_picker_gui.py
```

### Uso programático

#### Seleção com lógica sequencial

```python
from sequential_selector import select_file_with_sequence_logic

folders = [
    r"C:\Users\Documents\Comics",
    r"D:\Books"
]

# Sem palavras-chave (busca normal)
selected_file, info = select_file_with_sequence_logic(folders, exclude_prefix="_L_")

# Com palavras-chave (todas devem estar no nome)
keywords = ["batman", "year", "one"]
selected_file, info = select_file_with_sequence_logic(folders, exclude_prefix="_L_", keywords=keywords)

if info['sequence_detected']:
    print(f"Sequência detectada: {info['sequence_info']['collection']}")
    print(f"Arquivo {info['sequence_info']['file_number']} selecionado")
else:
    print("Seleção aleatória realizada")

print(f"Arquivo: {selected_file}")
```

#### Seleção aleatória tradicional

```python
from random_file_picker import pick_random_file

folders = [r"C:\Users\Documents"]

# Sem filtro
selected_file = pick_random_file(folders, exclude_prefix="_L_")

# Com palavras-chave
keywords = ["spider", "man"]
selected_file = pick_random_file(folders, exclude_prefix="_L_", keywords=keywords)

print(f"Arquivo selecionado: {selected_file}")
```

#### Rastreamento de arquivos lidos

```python
from sequential_selector import SequentialFileTracker

tracker = SequentialFileTracker()

# Marcar arquivo como lido
tracker.mark_as_read(r"C:\Comics", "Issue #001.cbr")

# Verificar se foi lido
if tracker.is_read(r"C:\Comics", "Issue #001.cbr"):
    print("Arquivo já foi lido")

# Limpar histórico de uma pasta
tracker.clear_folder(r"C:\Comics")
```

## 🎨 Interface Gráfica

### Áreas da Interface

1. **Pastas para buscar** (read-only): 
   - Lista de pastas onde os arquivos serão procurados
   - Só pode ser modificada pelos botões "Adicionar Pasta" e "Limpar Tudo"
   - Não recebe foco com Tab (pula para os próximos campos)
2. **Opções** (com scroll):
   - Prefixo de arquivo lido (padrão: `_L_`)
   - Limite de histórico (1-50 arquivos)
   - **Palavras-chave** (máx. 3, separadas por vírgula): Filtra arquivos que contenham ao menos UMA das palavras
   - Checkbox: Abrir pasta automaticamente
   - Checkbox: Abrir arquivo automaticamente
   - Checkbox: Usar seleção sequencial
   - **Checkbox: Processar arquivos ZIP** - Quando ativado, abre ZIPs e busca dentro deles; quando desativado, trata ZIPs como arquivos normais
3. **Log / Resultado**: Exibe informações detalhadas sobre a busca e seleção
4. **Últimos Arquivos Selecionados** (com scroll): Histórico clicável dos arquivos recentes

### Atalhos de Teclado

- **Enter**: Inicia a busca de arquivo aleatório
- **Tab**: Navega entre os campos editáveis (pula a caixa de pastas)

### Funcionalidades

- **Botão "Selecionar Arquivo Aleatório"**: Executa a busca e seleção
- **Botão "Salvar Configuração"**: Ativado apenas quando há mudanças não salvas
- **Clique no histórico**: Abre qualquer arquivo da lista de histórico
- **Filtro por palavras-chave**: Digite até 3 palavras separadas por vírgula (ex: `batman, superman, wonder`)
  - O arquivo deve conter **ao menos UMA** das palavras no nome (operação OR)
  - Busca é case-insensitive (não diferencia maiúsculas/minúsculas)
  - Deixe vazio para buscar todos os arquivos
  - Funciona também dentro de arquivos ZIP quando o processamento está ativado
- **Processar arquivos ZIP**: Controla se arquivos ZIP devem ser explorados
  - **Ativado** (padrão): Abre o ZIP, busca dentro dele e extrai o arquivo selecionado
  - **Desativado**: Trata arquivos ZIP como arquivos normais (não explora o conteúdo)
- **Detecção de mudanças**: A barra de status indica quando há configurações não salvas
- **Confirmação ao fechar**: Pergunta se deseja salvar antes de sair

## 🏗️ Arquitetura

### Módulos Principais

- **random_file_picker_gui.py**: Interface gráfica principal
- **random_file_picker.py**: Lógica de seleção aleatória de arquivos
- **sequential_selector.py**: Lógica de detecção e seleção sequencial
- **system_utils.py**: Interface unificada para detecção de aplicativos
- **system_utils_windows.py**: Implementação Windows (usa Registry, assoc, ftype)
- **system_utils_linux.py**: Implementação Linux (usa xdg-mime, gio, .desktop files)

### Detecção de Aplicativos

O sistema detecta automaticamente qual aplicativo abre cada tipo de arquivo:

**Windows**:
- Usa `assoc` para obter a extensão do arquivo
- Usa `ftype` para obter o comando associado
- Consulta o Registry para informações detalhadas
- Retorna nome, caminho e nome de exibição do aplicativo

**Linux**:
- Usa `xdg-mime query default` para obter o .desktop file
- Parseia o arquivo .desktop para extrair informações
- Usa `which` para localizar o executável
- Retorna nome, caminho e nome de exibição do aplicativo

## 📂 Arquivos de Configuração

### config.json
Armazena todas as preferências do usuário:
```json
{
  "folders": ["C:\\Pasta1", "D:\\Pasta2"],
  "exclude_prefix": "_L_",
  "open_folder": true,
  "open_file": false,
  "use_sequence": true,
  "process_zip": true,
  "history_limit": 5,
  "keywords": "batman, year, one",
  "file_history": ["C:\\file1.pdf", "D:\\file2.cbr"]
}
```

### read_files_tracker.json
Rastreia quais arquivos foram marcados como lidos (usado pela seleção sequencial):
```json
{
  "C:\\Comics\\Series1": ["Issue #001.cbr", "Issue #002.cbr"],
  "D:\\Books": ["Chapter 01.pdf"]
}
```

## 🔧 Exemplos Avançados

### Exemplo 1: Busca com palavras-chave

```python
from random_file_picker import pick_random_file

folders = [r"C:\Comics"]

# Busca arquivos que contenham "batman" OU "superman" OU "flash" no nome
keywords = ["batman", "superman", "flash"]
arquivo = pick_random_file(folders, exclude_prefix="_L_", keywords=keywords)

# Resultado possível: "Batman - Year One.cbr" ou "Superman - Red Son.cbr" ou "Flash - Rebirth.cbr"
print(f"Arquivo encontrado: {arquivo}")
```

### Exemplo 2: Detectar padrões de numeração

```python
from sequential_selector import extract_number_from_filename

files = [
    "Chapter 001.pdf",
    "Episode #05.mkv",
    "Part II.txt",
    "Volume 03 de 10.cbr"
]

for file in files:
    result = extract_number_from_filename(file)
    if result:
        print(f"{file} -> Número: {result['number']}, Total: {result.get('total')}")
```

### Exemplo 3: Analisar sequências em uma pasta

```python
from sequential_selector import analyze_folder_sequence

folder = r"C:\Comics\Batman"
sequences = analyze_folder_sequence(folder, exclude_prefix="_L_")

for seq in sequences:
    print(f"Coleção: {seq['collection']}")
    print(f"Total de arquivos: {seq['total_files']}")
    print(f"Tipo: {seq['type']}")
    print(f"Arquivos: {seq['files'][:3]}...")  # Primeiros 3
```

### Exemplo 4: Abrir pasta do arquivo selecionado

```python
from random_file_picker import pick_random_file, open_folder

folders = [r"C:\Users\Documents"]
arquivo = pick_random_file(folders)
print(f"Arquivo: {arquivo}")

# Abre o explorador de arquivos na pasta
open_folder(arquivo)
```

## 🎮 Casos de Uso

- **Leitura de quadrinhos/mangás**: Seleciona automaticamente o próximo capítulo não lido
  - Suporta coleções em arquivos ZIP (ex: "Vingadores V4 (Bendis).zip")
- **Busca específica**: Use palavras-chave para encontrar arquivos de vários personagens, séries ou temas
  - Ex: `batman, superman, flash` encontra arquivos de qualquer um desses heróis
  - Ex: `2023, 2024` encontra arquivos de 2023 ou 2024
  - Funciona também dentro de arquivos ZIP
- **Estudos**: Escolhe aleatoriamente materiais de estudo de várias pastas
- **Entretenimento**: Seleciona filmes, séries ou músicas aleatoriamente
- **Organização**: Gerencia leitura sequencial de documentos numerados
- **Coleções compactadas**: Processa automaticamente arquivos ZIP que contêm múltiplos arquivos

## 🐛 Tratamento de Erros

O programa trata automaticamente:
- Pastas inexistentes ou inacessíveis
- Arquivos não sincronizados (cloud storage)
- Pastas sem arquivos válidos
- Nenhum arquivo encontrado com as palavras-chave especificadas
- Erros de permissão
- Formatos de numeração inválidos
- Arquivos ZIP corrompidos ou inacessíveis
- Erros na extração de arquivos ZIP

## 📝 Notas

- Pastas com prefixo `.` são ignoradas automaticamente (ex: `.git`, `.vscode`)
- Arquivos em cloud storage podem aparecer como "Não sincronizado" se ainda não foram baixados
- A seleção sequencial funciona melhor quando os arquivos seguem um padrão consistente de numeração
- **Arquivos ZIP**:
  - Quando um ZIP é selecionado, o programa automaticamente explora seu conteúdo
  - Aplica os mesmos filtros (palavras-chave, prefixo de exclusão) aos arquivos dentro do ZIP
  - Extrai o arquivo selecionado para uma pasta temporária antes de abrir
  - Remove automaticamente os arquivos temporários após o uso
  - No histórico, mostra o arquivo ZIP original (não o arquivo extraído)
- **Palavras-chave**: 
  - Operação OR (ao menos uma deve estar presente no nome do arquivo)
  - Case-insensitive (não diferencia maiúsculas de minúsculas)
  - Máximo de 3 palavras-chave
  - Deixe vazio para buscar todos os arquivos
- O histórico é salvo automaticamente sempre que um novo arquivo é selecionado
- Todas as configurações persistem entre sessões do programa
