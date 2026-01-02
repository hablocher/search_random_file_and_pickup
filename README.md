# Random File Picker

Programa Python com interface gráfica que seleciona arquivos de forma inteligente a partir de uma lista de pastas, com suporte a seleção sequencial, aleatória, cache inteligente e prévia de thumbnails.

## 🎯 Funcionalidades

### Interface Gráfica
- **Interface completa em Tkinter** com todas as configurações acessíveis
- **Gerenciamento de pastas** com adição e remoção via interface
- **Log detalhado** de todas as operações realizadas
- **Histórico persistente** dos últimos arquivos selecionados (configurável de 1 a 50)
- **Prévia de thumbnails** para arquivos ZIP/RAR/PDF
  - Extrai e exibe a primeira imagem de arquivos compactados
  - Renderiza primeira página de PDFs
  - Indica quando arquivos estão sincronizando do OneDrive/Google Drive
- **Tabela de informações** do arquivo selecionado (formato, tamanho, número de páginas)
- **Barras de rolagem** nas áreas de opções e histórico para melhor navegação
- **Filtragem por palavras-chave** (até 3 palavras, operação OR - ao menos uma deve estar presente)
- **Atalhos de teclado** para produtividade (Enter para buscar, Tab para navegar)
- **Botão "Última Pasta Aberta"** para acesso rápido à última pasta visualizada

### Cache Inteligente
- **Sistema de cache em JSON compactado** (file_cache.json.gz)
  - **Primeira busca**: Cria cache automaticamente (pode demorar alguns segundos)
  - **Buscas seguintes**: Instantâneas usando cache (milissegundos)
  - **Validação automática** por timestamps das pastas e hash de configurações
  - **Invalidação inteligente**: Detecta mudanças em pastas e recria cache automaticamente
- **Controle manual**: Checkbox "Usar cache de arquivos"
  - ✅ Ligado (padrão): Usa cache para buscas rápidas
  - ❌ Desligado: Sempre recria o cache (útil após adicionar/remover muitos arquivos)
- **Logs informativos**: Mostra quando usa cache e tamanho dos dados armazenados

### Carregamento de Arquivos Grandes
- **Carregamento em chunks** (1MB por vez) para economizar memória
- **Barra de progresso** mostrando percentual e MB carregados
- **Cancelamento em tempo real** com botão dedicado
- **Temporizador** mostrando tempo decorrido durante carregamento
- **Suporte a arquivos de GB** sem travar a interface

### Seleção Inteligente de Arquivos
- **Seleção Sequencial**: Detecta automaticamente arquivos numerados e seleciona o próximo não lido
  - Suporta múltiplos formatos: `001`, `#001`, `"01 de 10"`, `Cap/Vol/Part/Ep`, numerais romanos (I, II, III)
  - Gerencia múltiplas coleções/séries na mesma pasta
  - Rastreia arquivos já lidos por pasta
- **Seleção Aleatória**: Modo tradicional de seleção totalmente aleatória
- **Suporte a arquivos ZIP/RAR/CBZ/CBR**: Detecta automaticamente arquivos compactados
  - Explora o conteúdo e continua a busca dentro deles
  - Aplica as mesmas regras de filtragem (palavras-chave, prefixo de exclusão)
  - Extrai o arquivo selecionado para pasta temporária e abre normalmente
  - Limpa automaticamente os arquivos temporários após o uso
  - **Prévia de thumbnails**: Extrai e exibe primeira imagem antes de abrir
- **Suporte a PDFs**: Renderiza primeira página como thumbnail
- **Exclusão de arquivos lidos**: Ignora automaticamente arquivos com prefixo configurável (padrão: `_L_`)
- **Filtragem por palavras-chave**: Busca arquivos que contenham ao menos UMA das palavras-chave no nome (case-insensitive)

### Suporte a Cloud Storage
- Funciona com **Google Drive**, **OneDrive** e outras pastas de sincronização
- Ignora automaticamente pastas ocultas (prefixo `.`)
- Busca recursiva em todas as subpastas

### Automação
- **Abrir pasta automaticamente** após seleção (opcional)
- **Abrir arquivo automaticamente** com o aplicativo padrão (ativado por padrão)
- **Detecção de aplicativos**: Biblioteca específica por SO (Windows/Linux) que identifica aplicativo associado ao tipo de arquivo
- **Persistência de configurações**: Todas as preferências são salvas automaticamente
- **Detecção de mudanças**: Alerta se há configurações não salvas ao fechar

## 📋 Requisitos

- Python 3.6 ou superior
- Tkinter (geralmente incluído com Python)
- **Pillow** (PIL): Para processamento de imagens e thumbnails
  ```bash
  pip install Pillow
  ```
- **rarfile**: Para extrair imagens de arquivos RAR/CBR
  ```bash
# Usando Poetry (recomendado)
poetry run rfp-gui

# Ou diretamente com Python
python -m random_file_picker.gui.app
  ```
  - **Windows**: Requer UnRAR.exe no PATH ou na pasta do script
  - **Linux**: `sudo apt install unrar` ou `sudo apt install unar`
- **PyMuPDF** (fitz): Para renderizar páginas de PDF
  ```bash
  pip install PyMuPDF
  ```

### Instalação completa

```bash
pip install Pillow rarfile PyMuPDF
```

Ou usando Poetry (recomendado):
```bash
poetry install
```

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
/RAR** - Quando ativado, abre compactados e busca dentro deles; quando desativado, trata como arquivos normais
   - **Checkbox: Usar cache de arquivos** - Acelera buscas após primeira execução (ativado por padrão)
3. **Prévia do Arquivo**: Exibe thumbnail da primeira imagem (ZIP/RAR/CBZ/CBR) ou página (PDF)
4. **Log / Resultado**: Exibe informações detalhadas sobre a busca e seleção
5
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
   - Checkbox: Abrir arquivo automaticamente (ativado por padrão)
   - Checkbox: Usar seleção sequencial
   - **Checkbox: Processar arquivos ZIP** - Quando ativado, abre ZIPs e busca dentro deles; quando desativado, trata ZIPs como arquivos normais
3. **Log / Resultado**: Exibe informações detalhadas sobre a busca e seleção
4. **Últimos Arquivos Selecionados** (com scroll): Histórico clicável dos arquivos recentes

### Atalhos de Teclado

- **Enter**: Inicia a busca de arquivo aleatório
- **Botão "Última Pasta Aberta"**: Acesso rápido à última pasta visualizada
- **Botão "Cancelar Carregamento"**: Aparece durante carregamento de arquivos grandes, permite cancelar
- **Clique no histórico**: Abre qualquer arquivo da lista de histórico
- **Prévia de thumbnails**:
  - Mostra primeira imagem de arquivos ZIP/RAR/CBZ/CBR
  - Renderiza primeira página de PDFs
  - Indica status de sincronização (OneDrive/Google Drive)
  - Tabela com informações: formato, tamanho, número de imagens/páginas
- **Cache de arquivos**: 
  - **Primeira busca**: Cria cache (pode levar alguns segundos em pastas grandes)
  - **Buscas seguintes**: Instantâneas (usa cache)
  - Detecta automaticamente mudanças nas pastas e atualiza cache
  - Desative para forçar nova busca completa
- **Filtro por palavras-chave**: Digite até 3 palavras separadas por vírgula (ex: `batman, superman, wonder`)
  - Estrutura Modular

O projeto foi refatorado para separação de responsabilidades:

#### Módulos Core
- **file_picker.py**: Lógica de seleção aleatória e coleta de arquivos com suporte a cache
- **sequential_selector.py**: Lógica de detecção e seleção sequencial
- **cache_manager.py**: Sistema de cache inteligente com validação por timestamps

#### Módulos GUI
- **app.py**: Interface gráfica principal e orquestração
- **config_manager.py**: Gerenciamento de configurações e persistência
- **file_loader.py**: Carregamento de arquivos em chunks com progresso e cancelamento
- **archive_extractor.py**: Extração de imagens de ZIP/RAR/PDF
- **thumbnail_generator.py**: Geração de thumbnails e imagens padrão
- **file_analyzer.py**: Análise de arquivos e formatação de informações

#### Módulos Utilitários
- **system_utils.py**: Interface unificada para detecção de aplicativos
- **system_utils_windows.py**: Implementação Windows (Registry, assoc, ftype)
- **system_utils_linux.py**: Implementação Linux (xdg-mime, gio, .desktop files)

### Gerenciamento de Memória

- **Buffer reutilizável**: Um único buffer para carregar arquivos, evita vazamento
- **Carregamento em chunks**: 1MB por vez, não carrega arquivo inteiro de uma vez
- **Coleta de lixo explícita**: Limpa memória após cada operação
- **Cancelamento imediato**: Libera recursos instantaneamente ao cancelar
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
- *use_cache": true,
  "history_limit": 5,
  "keywords": "batman, year, one",
  "file_history": ["C:\\file1.pdf", "D:\\file2.cbr"],
  "last_opened_folder": "C:\\Pasta1"
}
```

### file_cache.json.gz
Cache compactado de arquivos encontrados (criado automaticamente):
```json
{
  "metadata": {
    "created_at": "2026-01-02T01:30:00",
    "config_hash": "abc123...",
    "folder_mtimes": {
      "C:\\Pasta1": 1704153600.0
    },
    "file_count": 1250
  },
  "files": [
    {
      "path": "C:\\Pasta1\\file.cbr",
      "size": 45678901,
      "mtime": 1704153500.0,
      "name": "file.cbr"
    }
  ecção de aplicativos
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
  "open_file": true,
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

folders = [r"C:\Comics"]/RAR (ex: "Vingadores V4 (Bendis).cbz")
  - **Prévia de thumbnails**: Veja a capa antes de abrir
  - Cache acelera busca em grandes coleções
- **Busca específica**: Use palavras-chave para encontrar arquivos de vários personagens, séries ou temas
  - Ex: `batman, superman, flash` encontra arquivos de qualquer um desses heróis
  - Ex: `2023, 2024` encontra arquivos de 2023 ou 2024
  - Funciona também dentro de arquivos ZIP/RAR
- **Estudos**: Escolhe aleatoriamente materiais de estudo de várias pastas
  - Prévia de PDFs mostra primeira página
- **Entretenimento**: Seleciona filmes, séries ou músicas aleatoriamente
- **Organização**: Gerencia leitura sequencial de documentos numerados
- **Coleções compactadas**: Processa automaticamente arquivos ZIP/RAR que contêm múltiplos arquivos
- **Grandes bibliotecas**: Cache torna buscas instantâneas após primeira execução

### Exemplo 2: Detectar padrões de numeração

```python - exibe indicador na prévia
- Pastas sem arquivos válidos
- Nenhum arquivo encontrado com as palavras-chave especificadas
- Erros de permissão
- Formatos de numeração inválidos
- Arquivos ZIP/RAR corrompidos ou inacessíveis
- Erros na extração de arquivos ZIP/RAR
- PDFs corrompidos ou sem páginas
- Cache corrompido (recria automaticamente)
- Cancelamento de carregamento (libera recursos imediatamente)
    "Volume 03 de 10.cbr"
]

for Cache de arquivos**:
  - Criado automaticamente na primeira busca
  - Armazenado em `file_cache.json.gz` (JSON compactado)
  - Validado por timestamps das pastas e hash de configurações
  - Se detectar mudanças, recria automaticamente
  - Pode ser desabilitado para forçar busca completa
  - Economiza segundos (ou minutos) em grandes bibliotecas
- **Arquivos ZIP/RAR**:
  - Quando um arquivo compactado é selecionado, o programa explora seu conteúdo
  - Aplica os mesmos filtros (palavras-chave, prefixo de exclusão) aos arquivos internos
  - Extrai o arquivo selecionado para pasta temporária antes de abrir
  - **Prévia**: Extrai primeira imagem diretamente do buffer (sem descompactar tudo)
  - Remove automaticamente os arquivos temporários após o uso
  - No histórico, mostra o arquivo compactado original (não o extraído)
- **PDFs**:
  - Primeira página renderizada como thumbnail
  - Suporta arquivos grandes (carrega em chunks)
- **Carregamento de arquivos**:
  - Arquivos grandes (1GB+) são carregados em chunks de 1MB
  - Barra de progresso mostra percentual e MB carregados
  - Botão de cancelar permite abortar operação a qualquer momento
  - Gerenciamento de memória otimizado (buffer reutilizável)
- **Palavras-chave**: 
  - Operação OR (ao menos uma deve estar presente no nome do arquivo)
  - Case-insensitive (não diferencia maiúsculas de minúsculas)
  - Máximo de 3 palavras-chave
  - Deixe vazio para buscar todos os arquivos
- O histórico é salvo automaticamente sempre que um novo arquivo é selecionado
- Todas as configurações persistem entre sessões do programa
- **Performance**:
  - Cache torna buscas instantâneas após primeira execução
  - Carregamento em chunks não trava interface
  - Cancelamento imediato libera memória instantaneamente_L_")

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
