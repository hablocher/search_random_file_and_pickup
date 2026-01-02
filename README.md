# � Media Finder

> Aplicação Python com interface gráfica moderna que seleciona arquivos de forma inteligente com detecção automática de sequências, cache inteligente e prévia de thumbnails.

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## ✨ Principais Funcionalidades

### 🎯 Seleção Inteligente
- **Detecção automática de sequências** (quadrinhos, mangás, séries)
- Suporta múltiplos formatos: `001`, `#100`, `Vol 2`, `I, II, III`, `v1 081`
- **Seleção sequencial** ou **aleatória**
- Rastreamento de arquivos já lidos

### 📦 Arquivos Compactados
- Busca dentro de **ZIP/RAR/CBZ/CBR**
- **Detecção de sequência** dentro dos arquivos
- Extração automática para pasta temporária
- Limpeza automática após uso

### 🖼️ Prévias Visuais
- **Thumbnails** de imagens, PDFs, vídeos
- **Busca de capas** de filmes online (TMDb API)
- Extração de frames de vídeos (FFmpeg)
- Indicador de sincronização de nuvem

### ⚡ Performance
- **Cache inteligente** (buscas instantâneas)
- Carregamento em chunks (arquivos grandes)
- Interface responsiva e moderna
- Cancelamento em tempo real

### 🔍 Filtros Avançados
- Até **5 palavras-chave** com modo AND/OR
- Ignorar extensões específicas
- Prefixo de arquivos lidos
- Suporte a nuvem (OneDrive, Google Drive)

## 🚀 Início Rápido

### Instalação

#### Com Poetry (Recomendado)
```bash
poetry install
poetry run rfp-gui
```

#### Com pip
```bash
pip install -r requirements.txt
python -m random_file_picker.gui.app
```

### Uso Básico

1. **Adicione pastas** para busca
2. **Configure opções** (opcional)
3. **Clique em "🎲 Selecionar Arquivo"**
4. **Visualize prévia** e informações
5. **Arquivo abre** automaticamente (se habilitado)

## 📋 Requisitos

### Básico
- Python 3.6+
- Tkinter (incluído no Python)

### Dependências Python
```bash
pip install Pillow rarfile PyMuPDF ffmpeg-python requests
```

### Ferramentas Externas (Opcional)

| Ferramenta | Uso | Instalação |
|-----------|-----|------------|
| **UnRAR** | Arquivos RAR/CBR | [Download](https://www.rarlab.com/rar_add.htm) |
| **FFmpeg** | Frames de vídeos | `winget install Gyan.FFmpeg` |
| **TMDb API** | Capas de filmes | [Grátis](https://www.themoviedb.org/settings/api) |

## 📚 Documentação Completa

### 📖 [DOCUMENTATION.md](docs/DOCUMENTATION.md) - Guia Completo

Consulte a documentação completa para:
- 📖 Guias detalhados de instalação e configuração
- 🎯 Tutoriais de uso avançado
- 🔧 Otimizações e melhorias
- 🐛 Correções de bugs e troubleshooting
- 💻 Exemplos de código
- 🎬 Casos de uso práticos

### Documentos Específicos

| Documento | Conteúdo |
|-----------|----------|
| [DOCUMENTATION.md](docs/DOCUMENTATION.md) | **Documentação consolidada completa** |
| [FFMPEG_INSTALL.md](docs/FFMPEG_INSTALL.md) | Instalação do FFmpeg por sistema |
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
