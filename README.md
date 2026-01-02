# 🎬 Media Finder

> **Aplicação Python com interface gráfica moderna para seleção inteligente de arquivos** - Sistema avançado de busca e organização de mídia com detecção automática de sequências, cache inteligente, prévia de thumbnails e suporte completo a arquivos compactados.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![AI Generated](https://img.shields.io/badge/Code-AI%20Generated-purple.svg)](https://github.com/features/copilot)

> 🤖 **Nota**: Todo o código deste projeto foi gerado com assistência de Inteligência Artificial (GitHub Copilot/Claude).

---

## 📑 Índice

- [Principais Funcionalidades](#-principais-funcionalidades)
- [Início Rápido](#-início-rápido)
- [Instalação Detalhada](#-instalação-detalhada)
- [Interface do Usuário](#-interface-do-usuário)
- [Requisitos do Sistema](#-requisitos-do-sistema)
- [Documentação Completa](#-documentação-completa)
- [Geração de Executável](#-geração-de-executável)
- [Configuração](#-configuração)
- [Troubleshooting](#-troubleshooting)
- [Licença](#-licença)

---

## ✨ Principais Funcionalidades

### 🎯 Seleção Inteligente de Arquivos

#### 📊 Detecção Automática de Sequências
- Reconhece **múltiplos formatos de numeração**:
  - Padrão numérico: `001`, `002`, `003`
  - Hash: `#100`, `#101`, `#102`
  - Volume: `Vol 1`, `Vol 2`, `Vol 3`
  - Romanos: `I`, `II`, `III`, `IV`
  - Híbrido: `v1 081`, `v2 001`
- **Seleção sequencial inteligente** (próximo não lido)
- **Rastreamento de progresso** por coleção
- Suporta **múltiplas coleções** na mesma pasta

#### 🎲 Modo Aleatório
- Seleção totalmente aleatória
- Ignora arquivos com prefixos configuráveis (`_L_`, `_W_`)
- Filtragem por palavras-chave

### 📦 Suporte a Arquivos Compactados

#### Formatos Suportados
- **ZIP/CBZ** (Comic Book ZIP)
- **RAR/CBR** (Comic Book RAR) - requer UnRAR
- **Busca recursiva** dentro de arquivos
- **Detecção de sequência** em arquivos compactados

#### Funcionalidades
- Extração automática para pasta temporária
- Preview de conteúdo sem extração completa
- Limpeza automática após uso
- Cache de listagem de arquivos

### 🖼️ Prévias e Thumbnails

#### Tipos de Prévia Suportados
- **Imagens**: JPG, PNG, GIF, BMP, WEBP
- **PDFs**: Primeira página renderizada
- **Vídeos**: Frame extraído (requer FFmpeg)
- **Arquivos compactados**: Primeira imagem interna

#### Capas de Filmes Online
- Integração com **TMDb API**
- Busca automática de posters
- Cache local de imagens
- Detecção inteligente de títulos

### ⚡ Performance e Cache

#### Cache Inteligente
- **Buscas instantâneas** após primeira execução
- Atualização automática de mudanças
- Armazenamento eficiente em JSON
- Invalidação inteligente

#### Otimizações
- Carregamento em **chunks** para arquivos grandes
- Interface **não bloqueante** (threading)
- Cancelamento em tempo real
- Gerenciamento automático de memória

### 🔍 Filtros e Configurações Avançadas

#### Sistema de Filtros
- **Palavras-chave** (até 5, modo AND/OR)
- **Prefixos personalizáveis** (múltiplos, separados por vírgula)
- **Extensões ignoradas** (SRT, SUB, TXT, NFO, etc)
- **Pastas ocultas** automaticamente ignoradas

#### Integrações Cloud
- **OneDrive** - Suporte completo
- **Google Drive** - Suporte completo
- Detecção de arquivos não sincronizados
- Hidratação opcional sob demanda

### 🎨 Interface Moderna

#### Design
- **Interface gráfica** com Tkinter/TTK
- Tema moderno e responsivo
- **Controles de fonte** ajustáveis (+/-)
- Ícones emoji e visual limpo

#### Componentes
- **Área de prévia** expansível (400x600px)
- **Histórico visual** com botões clicáveis
- **Log colorido** com níveis (info, success, error, warning)
- **Popup de configurações** com rolagem
- **Animação de busca** (spinner)

### 📂 Gerenciamento de Arquivos

#### Histórico
- Últimos **15 arquivos** (configurável 1-50)
- Navegação rápida por botões
- Persistência em configuração
- Reabertura de arquivos anteriores

#### Integração com Sistema
- Abertura automática com **aplicativo padrão**
- Abertura de pasta no Explorer
- Detecção de aplicativo associado
- Informações detalhadas de formato

---

## 🚀 Início Rápido

### Instalação Rápida (Windows)

```batch
# Clone o repositório
git clone https://github.com/hablocher/search_random_file_and_pickup.git
cd search_random_file_and_pickup

# Execute o script de início rápido
quickstart.bat
```

### Executar com Poetry

```bash
poetry install
poetry run rfp-gui
```

### Uso Básico

1. **Adicione pastas** clicando no botão "+" ou "Adicionar Pasta"
2. **Configure opções avançadas** no botão ⚙️ (engrenagem)
3. **Clique no botão de roleta** 🎰 para selecionar um arquivo
4. **Visualize a prévia** na área lateral direita
5. **Arquivo abre automaticamente** (se configurado)

---

## 📦 Instalação Detalhada

### Requisitos Mínimos

- **Windows 10/11** (Linux/Mac compatível)
- **Python 3.9+**
- **4 GB RAM**
- **Tkinter** (incluído no Python Windows)

### Instalação Completa

#### 1. Instalar Python
```bash
# Download: https://www.python.org/downloads/
# Marque "Add Python to PATH" durante instalação
```

#### 2. Instalar Poetry (Recomendado)
```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Adicionar ao PATH se necessário
```

#### 3. Instalar Dependências
```bash
poetry install
```

#### 4. Ferramentas Opcionais

##### UnRAR (Para arquivos RAR/CBR)
- **Download**: https://www.win-rar.com/download.html
- Instale WinRAR (inclui UnRAR.exe)
- Veja [UNRAR.md](UNRAR.md) para detalhes

##### FFmpeg (Para frames de vídeo)
```bash
winget install Gyan.FFmpeg
```
Ou veja [docs/FFMPEG_INSTALL.md](docs/FFMPEG_INSTALL.md)

##### TMDb API (Para capas de filmes)
1. Crie conta gratuita em https://www.themoviedb.org
2. Gere API key em https://www.themoviedb.org/settings/api
3. Configure em `.env` ou variável de ambiente
4. Veja [docs/TMDB_SETUP.md](docs/TMDB_SETUP.md)

---

## 🎨 Interface do Usuário

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 Media Finder                                      [⚙️]  │
├─────────────────────────────────────────────────────────────┤
│  Pastas:  [W:/SERIES] [L:/Quadrinhos] [+]                  │
│           [🎰 Roleta]  [✖ Cancelar]                         │
├──────────────────┬──────────────────┬──────────────────────┤
│   📋 Log         │   🖼️ Prévia      │   📚 Histórico       │
│                  │                  │                      │
│  [Mensagens]     │  [Thumbnail]     │  [Últimos 15]        │
│  [Coloridas]     │  [400x600]       │  [Botões]            │
│  [+/-] Fonte     │                  │                      │
└──────────────────┴──────────────────┴──────────────────────┘
```

### Popup de Configurações Avançadas

- **Prefixos**: Múltiplos separados por vírgula (`_L_,_W_`)
- **Histórico**: 1-50 arquivos
- **Palavras-chave**: Até 5, modo AND/OR
- **Extensões ignoradas**: Lista personalizada
- **Checkboxes**:
  - ✅ Abrir pasta após seleção
  - ✅ Abrir arquivo após seleção
  - ✅ Seleção sequencial
  - ✅ Processar ZIP/RAR
  - ✅ Cache de arquivos
  - ✅ Forçar download de nuvem

---

## 📚 Documentação Completa

### 📖 Guias Principais

| Documento | Descrição |
|-----------|-----------|
| **[DOCUMENTATION.md](docs/DOCUMENTATION.md)** | 📚 Documentação consolidada completa |
| **[BUILD.md](BUILD.md)** | 📦 Como gerar executável com PyInstaller |
| **[EXECUTAVEL.md](EXECUTAVEL.md)** | 🚀 Guia de uso do executável |
| **[UNRAR.md](UNRAR.md)** | 📦 Solução para erro "Cannot find working tool" |

### 🔧 Configuração e Setup

| Documento | Descrição |
|-----------|-----------|
| [SETUP_COMPLETE.md](docs/SETUP_COMPLETE.md) | ✅ Guia de instalação completo |
| [README_POETRY.md](docs/README_POETRY.md) | 📦 Uso com Poetry |
| [FFMPEG_INSTALL.md](docs/FFMPEG_INSTALL.md) | 🎬 Instalação do FFmpeg por plataforma |
| [TMDB_SETUP.md](docs/TMDB_SETUP.md) | 🎥 Configuração da API TMDb |
| [COMMANDS.md](docs/COMMANDS.md) | 💻 Comandos úteis do projeto |

### 🚀 Funcionalidades Avançadas

| Documento | Descrição |
|-----------|-----------|
| [MOVIE_POSTER_FEATURE.md](docs/MOVIE_POSTER_FEATURE.md) | 🎬 Sistema de busca de capas de filmes |
| [TMDB_IMPROVEMENTS.md](docs/TMDB_IMPROVEMENTS.md) | 📈 Melhorias na integração TMDb |
| [CACHE_OPTIMIZATION.md](docs/CACHE_OPTIMIZATION.md) | ⚡ Otimizações de cache |
| [ZIP_SEQUENCE_ANALYSIS.md](docs/ZIP_SEQUENCE_ANALYSIS.md) | 📦 Análise de sequências em ZIPs |

### 🐛 Troubleshooting e Correções

| Documento | Descrição |
|-----------|-----------|
| [BUG_FIX_REPORT.md](docs/BUG_FIX_REPORT.md) | 🐛 Relatório de correções de bugs |
| [KEYWORD_FILTER_TESTS.md](docs/KEYWORD_FILTER_TESTS.md) | 🧪 Testes de filtros de palavras-chave |
| [MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) | 🔄 Guia de migração de versões |

### 💻 Exemplos e Demos

| Arquivo | Descrição |
|---------|-----------|
| [tmdb_demo.py](docs/tmdb_demo.py) | 🎥 Script de demonstração da API TMDb |

---

## 📦 Geração de Executável

### Build do Executável Windows

```batch
# Instalar PyInstaller
poetry add --group dev pyinstaller

# Construir executável
build_exe.bat
```

O executável será gerado em: `dist/MediaFinder.exe`

### Características do Executável

- ✅ **Single-file** (~50-80 MB)
- ✅ **Sem console** (janela limpa)
- ✅ **Assets embutidos** (imagens)
- ✅ **Python embutido** (não precisa instalar)
- ✅ **Todas as dependências** incluídas

### Distribuição

Copie apenas `MediaFinder.exe` - funciona standalone!

Veja [BUILD.md](BUILD.md) e [EXECUTAVEL.md](EXECUTAVEL.md) para mais detalhes.

---

## ⚙️ Configuração

### Arquivo config.json

O Media Finder cria automaticamente um `config.json`:

```json
{
  "folders": ["W:/SERIES", "L:/Quadrinhos"],
  "exclude_prefix": "_L_,_W_",
  "open_folder": false,
  "open_file": true,
  "use_sequence": true,
  "history_limit": 15,
  "keywords": "",
  "keywords_match_all": true,
  "ignored_extensions": "SRT,TXT,SUB,NFO",
  "process_zip": true,
  "use_cache": true,
  "enable_cloud_hydration": false,
  "file_history": []
}
```

### Variáveis de Ambiente

```bash
# TMDb API (opcional)
TMDB_API_KEY=sua_chave_aqui

# FFmpeg (detectado automaticamente)
# Adicione ao PATH se necessário
```

---

## 🐛 Troubleshooting

### Erro "Cannot find working tool" (RAR)

**Solução**: Instale WinRAR
- Download: https://www.win-rar.com/download.html
- Veja [UNRAR.md](UNRAR.md) para detalhes completos

### FFmpeg não encontrado

**Solução**:
```bash
winget install Gyan.FFmpeg
```
Ou veja [docs/FFMPEG_INSTALL.md](docs/FFMPEG_INSTALL.md)

### Cache desatualizado

**Solução**: Delete `read_files_tracker.json`

### Interface não responde

**Solução**: Use o botão "✖ Cancelar" durante buscas longas

### Mais problemas?

Consulte [docs/BUG_FIX_REPORT.md](docs/BUG_FIX_REPORT.md)

---

## 📋 Requisitos do Sistema

### Dependências Python

```toml
python = "^3.9"
pillow = "^10.0.0"      # Processamento de imagens
rarfile = "^4.0"        # Arquivos RAR
pymupdf = "^1.23.0"     # PDFs
ffmpeg-python = "^0.2.0" # Vídeos
requests = "^2.31.0"    # TMDb API
```

### Ferramentas Externas (Opcionais)

| Ferramenta | Status | Uso |
|-----------|--------|-----|
| **UnRAR** | Opcional | Arquivos RAR/CBR |
| **FFmpeg** | Opcional | Frames de vídeo |
| **TMDb API** | Opcional | Capas de filmes |

---

## 🤝 Contribuindo

Este projeto foi desenvolvido com assistência de IA. Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a **GNU General Public License v3.0**.

Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- **GitHub Copilot** e **Claude** pela assistência na geração do código
- Comunidade Python por bibliotecas excelentes
- TMDb pela API gratuita de filmes
- Usuários e testadores do projeto

---

## 📞 Suporte

- **Issues**: https://github.com/hablocher/search_random_file_and_pickup/issues
- **Documentação**: [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)
- **Email**: (adicione seu email aqui)

---

<div align="center">

**Desenvolvido com 🤖 IA + ❤️**

*Seleção inteligente de arquivos nunca foi tão fácil!*

</div>
| [TMDB_SETUP.md](docs/TMDB_SETUP.md) | Configuração da API TMDb |
| [COMMANDS.md](docs/COMMANDS.md) | Comandos CLI e atalhos |
| [BUG_FIX_REPORT.md](docs/BUG_FIX_REPORT.md) | Correções de bugs detalhadas |

## 💡 Exemplos Rápidos

### Interface Gráfica

```bash
poetry run rfp-gui
```

### Linha de Comando

```bash
# Seleção sequencial
poetry run rfp-cli --folders "C:\Comics" --sequence

# Com filtros
poetry run rfp-cli --folders "C:\Comics" --keywords "batman,superman"
```

### Programático

```python
from random_file_picker.core.sequential_selector import select_file_with_sequence_logic

folders = ["C:\\Comics"]
file, info = select_file_with_sequence_logic(folders, exclude_prefix="_L_")
print(f"Arquivo: {file['file_path']}")
```

## 🎯 Casos de Uso

- 📚 **Quadrinhos/Mangás**: Detecta sequências, seleciona próximo não lido
- 🎬 **Filmes**: Busca capas online, extrai frames
- 📖 **PDFs**: Renderiza primeira página
- 🎵 **Coleções**: Seleção aleatória ou sequencial
- ☁️ **Cloud Storage**: OneDrive, Google Drive
- 📦 **Arquivos ZIP/RAR**: Busca e extrai automaticamente

## 🔧 Configuração

### Arquivo config.json

```json
{
  "folders": ["C:\\Comics", "D:\\Manga"],
  "exclude_prefix": "_L_",
  "use_sequence": true,
  "process_zip": true,
  "use_cache": true,
  "keywords": "batman, superman",
  "keywords_match_all": false,
  "history_limit": 5,
  "tmdb_api_key": "sua_chave_aqui"
}
```

### API TMDb (Opcional)

Para buscar capas de filmes:

1. Crie conta em [themoviedb.org](https://www.themoviedb.org)
2. Obtenha API Key em: Configurações → API
3. Adicione ao `config.json`

## 🐛 Troubleshooting

### Cache não atualiza
```bash
# Desative cache ou remova: file_cache.json.gz
```

### FFmpeg não encontrado
```bash
ffmpeg -version  # Verifica instalação
winget install Gyan.FFmpeg  # Windows
```

### UnRAR não encontrado
- Baixe em: https://www.rarlab.com/rar_add.htm
- Extraia `UnRAR.exe` na pasta do script

Consulte a [Documentação Completa](docs/DOCUMENTATION.md#8-troubleshooting) para mais detalhes.

## 🏗️ Arquitetura

```
src/random_file_picker/
├── core/               # Lógica principal
│   ├── file_picker.py
│   ├── sequential_selector.py
│   ├── cache_manager.py
│   └── ...
├── gui/                # Interface gráfica
│   └── app.py
└── utils/              # Utilitários
    └── system_utils.py
```

## 🤝 Contribuindo

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a **GNU GPL v3.0**.

- ✅ Use, modifique e distribua livremente
- ✅ Use comercialmente
- ❌ Trabalhos derivados devem manter GPL-3.0

Veja [LICENSE](LICENSE) para detalhes completos.

## 🙏 Agradecimentos

- [Pillow](https://python-pillow.org/) - Processamento de imagens
- [PyMuPDF](https://pymupdf.readthedocs.io/) - Renderização de PDFs
- [rarfile](https://github.com/markokr/rarfile) - Extração de RAR
- [FFmpeg](https://ffmpeg.org/) - Processamento de vídeos
- [TMDb](https://www.themoviedb.org/) - API de filmes

---

**Desenvolvido com ❤️ em Python** | **Última atualização: Janeiro 2026** | **Versão 2.0.0**
