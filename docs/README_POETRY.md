# Random File Picker

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-managed-blue.svg)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Programa Python com interface gráfica para seleção inteligente de arquivos com suporte a modo sequencial, aleatório e cloud storage.

## 🎯 Funcionalidades

### Interface Gráfica
- **Interface completa em Tkinter** com todas as configurações acessíveis
- **Gerenciamento de pastas** com adição e remoção via interface
- **Log detalhado** de todas as operações realizadas
- **Histórico persistente** dos últimos arquivos selecionados (configurável de 1 a 50)
- **Filtragem por palavras-chave** (até 3 palavras, operação OR)
- **Atalhos de teclado** para produtividade

### Seleção Inteligente de Arquivos
- **Seleção Sequencial**: Detecta automaticamente arquivos numerados e seleciona o próximo não lido
  - Suporta múltiplos formatos: `001`, `#001`, `"01 de 10"`, `Cap/Vol/Part/Ep`, numerais romanos
  - Gerencia múltiplas coleções/séries na mesma pasta
  - Rastreia arquivos já lidos por pasta
- **Seleção Aleatória**: Modo tradicional de seleção totalmente aleatória
- **Suporte a arquivos ZIP**: Detecta e extrai arquivos de ZIPs automaticamente
- **Exclusão de arquivos lidos**: Ignora arquivos com prefixo configurável (padrão: `_L_`)
- **Filtragem por palavras-chave**: Busca arquivos que contenham ao menos uma palavra-chave

### Suporte a Cloud Storage
- Funciona com **Google Drive**, **OneDrive** e outras pastas de sincronização
- Ignora automaticamente pastas ocultas (prefixo `.`)
- Busca recursiva em todas as subpastas

## 📋 Requisitos

- Python 3.8 ou superior
- Poetry (gerenciador de dependências)

## 🚀 Instalação

### Com Poetry (recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/random-file-picker.git
cd random-file-picker

# Instale as dependências
poetry install

# Ative o ambiente virtual
poetry shell
```

### Instalação manual

```bash
pip install -e .
```

## 💻 Como usar

### Interface Gráfica

```bash
# Com Poetry
poetry run rfp-gui

# Ou se estiver no ambiente virtual ativado
rfp-gui
```

### Linha de Comando (CLI)

```bash
# Seleção básica
poetry run random-file-picker /caminho/pasta1 /caminho/pasta2

# Com opções avançadas
poetry run random-file-picker \
    --exclude-prefix "_LIDO_" \
    --keywords "marvel" "dc" \
    --open-folder \
    /caminho/pasta1 /caminho/pasta2

# Desativar modo sequencial (usar apenas aleatório)
poetry run random-file-picker --no-sequence /caminho/pasta

# Não processar arquivos ZIP
poetry run random-file-picker --no-zip /caminho/pasta
```

### Opções CLI

- `folders`: Pasta(s) para buscar arquivos (obrigatório)
- `--exclude-prefix`: Prefixo de arquivos a ignorar (padrão: `_L_`)
- `--keywords`: Palavras-chave para filtrar arquivos
- `--no-sequence`: Desativa seleção sequencial
- `--open-folder`: Abre a pasta do arquivo selecionado
- `--no-zip`: Não processa arquivos ZIP

## 🧪 Testes

```bash
# Executar todos os testes
poetry run pytest

# Com cobertura
poetry run pytest --cov

# Gerar relatório HTML de cobertura
poetry run pytest --cov --cov-report=html
```

## 🛠️ Desenvolvimento

### Configurar ambiente de desenvolvimento

```bash
# Instalar dependências de desenvolvimento
poetry install

# Instalar pre-commit hooks
poetry run pre-commit install

# Executar formatação
poetry run black src tests

# Executar linting
poetry run flake8 src tests

# Executar type checking
poetry run mypy src
```

### Estrutura do Projeto

```
random-file-picker/
├── src/
│   └── random_file_picker/
│       ├── __init__.py
│       ├── cli.py                 # CLI entry point
│       ├── core/                  # Core functionality
│       │   ├── __init__.py
│       │   ├── file_picker.py     # File selection logic
│       │   └── sequential_selector.py  # Sequential selection
│       ├── gui/                   # GUI module
│       │   ├── __init__.py
│       │   └── app.py             # Tkinter GUI application
│       └── utils/                 # Utility modules
│           ├── __init__.py
│           ├── system_utils.py
│           ├── system_utils_windows.py
│           └── system_utils_linux.py
├── tests/                         # Tests
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
├── config/                        # Configuration files
├── pyproject.toml                # Poetry configuration
├── README.md
└── .gitignore
```

## 📝 Configuração

O arquivo `config.json` é criado automaticamente na primeira execução e armazena:
- Lista de pastas para busca
- Prefixo de exclusão
- Preferências de abertura automática
- Histórico de arquivos
- Configurações de filtragem

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 🐛 Problemas Conhecidos

Consulte [BUG_FIX_REPORT.md](BUG_FIX_REPORT.md) para informações sobre problemas conhecidos e correções.

## ✨ Agradecimentos

- Comunidade Python
- Contribuidores do projeto

## 📧 Contato

Para questões e suporte, abra uma issue no GitHub.
