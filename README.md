# 🎬 Media Finder

> **Aplicação Python com interface gráfica moderna para seleção inteligente de arquivos** - Sistema avançado de busca e organização de mídia com detecção automática de sequências, cache inteligente, prévia de thumbnails e suporte completo a arquivos compactados.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![AI Generated](https://img.shields.io/badge/Code-AI%20Generated-purple.svg)](https://gemini.google.com)

---

> [!IMPORTANT]
> **Todo o código deste repositório foi inteiramente gerado por Inteligência Artificial**, mas completamente orientado por um humano. As IAs utilizadas foram **Claude 3.5 Sonnet** e **Gemini 1.5 Pro**.

---

## 📑 Índice

- [Principais Funcionalidades](#-principais-funcionalidades)
- [Início Rápido](#-início-rápido)
- [Interface do Usuário](#-interface-do-usuário)
- [Documentação](#-documentação)
- [Geração de Executável](#-geração-de-executável)
- [Configuração](#-configuração)
- [Licença](#-licença)

---

## ✨ Principais Funcionalidades

O Media Finder é uma ferramenta completa para gerenciar e encontrar arquivos de mídia de forma inteligente.

### Modos de Seleção
- **Seleção Sequencial Inteligente**: Detecta automaticamente a ordem de arquivos em uma série (ex: `01`, `02`, `03`) e seleciona o próximo item não lido. Ideal para quadrinhos, séries e coleções.
- **Modo Aleatório**: Escolhe um arquivo de forma totalmente aleatória, com a opção de ignorar arquivos já lidos.

### Suporte a Arquivos
- **Formatos Compactados**: Processa arquivos `.zip`, `.rar`, `.cbz` e `.cbr` como se fossem pastas, permitindo a seleção de arquivos internos.
- **Pré-visualização**: Gera miniaturas (thumbnails) para diversos formatos:
    - **Imagens**: JPG, PNG, GIF, etc.
    - **Vídeos**: Extrai um quadro do vídeo (requer FFmpeg).
    - **PDFs**: Renderiza a primeira página.
- **Busca de Capas (TMDb)**: Integra-se à API do [The Movie Database (TMDb)](https://www.themoviedb.org/) para buscar pôsteres de filmes e séries automaticamente.

### Performance e Otimização
- **Cache Inteligente**: As buscas são armazenadas em cache, tornando as seleções futuras quase instantâneas.
- **Interface Não Bloqueante**: A interface gráfica permanece responsiva durante as buscas, que são executadas em segundo plano.

### Interface e Usabilidade
- **Interface Gráfica Moderna**: Desenvolvida com Tkinter, oferece uma experiência de usuário limpa e intuitiva.
- **Filtros Avançados**:
    - **Palavras-chave**: Filtre arquivos por nome.
    - **Prefixos de Exclusão**: Ignore arquivos que começam com um texto específico (ex: `_LIDO_`).
    - **Extensões Ignoradas**: Exclua arquivos com extensões como `.srt` ou `.txt`.
- **Suporte a Cloud**: Opcionalmente, força o download de arquivos de serviços como OneDrive e Google Drive antes de abri-los.

---

## 🚀 Início Rápido

### Windows
1. **Clone o repositório**:
   ```bash
   git clone https://github.com/hablocher/search_random_file_and_pickup.git
   cd search_random_file_and_pickup
   ```
2. **Execute o script de instalação**:
   ```bash
   quickstart.bat
   ```
   Este script instalará as dependências e iniciará a aplicação.

### Uso
1. **Adicione as pastas** onde seus arquivos de mídia estão localizados.
2. **Configure as opções** de busca, se desejar (filtros, modo de seleção, etc.).
3. **Clique no botão de roleta (🎲)** para que o Media Finder selecione um arquivo para você.

---

## 🎨 Interface do Usuário

A interface principal é dividida em três seções:
- **Log de Execução**: Mostra o que o programa está fazendo em tempo real.
- **Prévia**: Exibe uma miniatura do arquivo selecionado.
- **Histórico**: Lista os últimos arquivos abertos.

![Interface Gráfica](https://i.imgur.com/example.png) <!-- Adicionar um screenshot real da interface -->

---

## 📚 Documentação

A documentação completa do projeto está organizada na pasta `docs`. Abaixo estão os principais documentos:

| Documento | Descrição |
|-----------|-----------|
| **[DOCUMENTATION.md](docs/DOCUMENTATION.md)** | 📚 Documentação consolidada completa |
| **[BUILD.md](BUILD.md)** | 📦 Como gerar executável com PyInstaller |
| **[UNRAR.md](docs/UNRAR.md)** | 📦 Solução para erro "Cannot find working tool" |
| **[FFMPEG_INSTALL.md](docs/FFMPEG_INSTALL.md)** | 🎬 Instalação do FFmpeg por plataforma |
| **[TMDB_SETUP.md](docs/TMDB_SETUP.md)** | 🎥 Configuração da API TMDb |
| **[COMMANDS.md](docs/COMMANDS.md)** | 💻 Comandos úteis do projeto |
| **[CACHE_OPTIMIZATION.md](docs/CACHE_OPTIMIZATION.md)** | ⚡ Otimizações de cache |
| **[MOVIE_POSTER_FEATURE.md](docs/MOVIE_POSTER_FEATURE.md)** | 🎬 Sistema de busca de capas de filmes |
| **[TMDB_IMPROVEMENTS.md](docs/TMDB_IMPROVEMENTS.md)** | 📈 Melhorias na integração TMDb |
| **[ZIP_SEQUENCE_ANALYSIS.md](docs/ZIP_SEQUENCE_ANALYSIS.md)** | 📦 Análise de sequências em ZIPs |
| **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** | 🐛 Soluções para problemas comuns |
| **[TESTING.md](docs/TESTING.md)** | 🧪 Como executar os testes do projeto |
| **[MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)** | 🔄 Guia de migração de versões |
| **[tmdb_demo.py](docs/tmdb_demo.py)** | 🎥 Script de demonstração da API TMDb |

---

## 📦 Geração de Executável

É possível gerar um executável (`.exe`) que funciona de forma independente, sem a necessidade de instalar o Python ou outras dependências.

Para isso, execute o script:
```bash
build_exe.bat
```
O arquivo `MediaFinder.exe` será criado na pasta `dist`.

---

## ⚙️ Configuração

As configurações do Media Finder são salvas no arquivo `config.json`, que é criado automaticamente no mesmo diretório do programa. Nele, você pode ajustar:
- Pastas de busca
- Filtros e prefixos
- Limite do histórico
- E outras opções avançadas.

Para a busca de capas de filmes, é necessário uma chave de API do [TMDb](https://www.themoviedb.org/settings/api), que pode ser adicionada ao `config.json`.

---

## 📄 Licença

Este projeto é licenciado sob a **GNU General Public License v3.0**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.