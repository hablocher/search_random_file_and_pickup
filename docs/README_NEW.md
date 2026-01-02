# Random File Picker

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-managed-blue)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Programa Python com interface gráfica que seleciona arquivos de forma inteligente a partir de uma lista de pastas, com suporte a seleção sequencial e aleatória.

## 🎯 Funcionalidades

### Interface Gráfica
- **Interface completa em Tkinter** com todas as configurações acessíveis
- **Gerenciamento de pastas** com adição e remoção via interface
- **Log detalhado** de todas as operações realizadas
- **Histórico persistente** dos últimos arquivos selecionados (configurável de 1 a 50)
- **Filtragem por palavras-chave** (até 3 palavras, operação OR)
- **Atalhos de teclado** para produtividade

### Seleção Inteligente de Arquivos
- **Seleção Sequencial**: Detecta automaticamente arquivos numerados
- **Seleção Aleatória**: Modo tradicional de seleção totalmente aleatória
- **Suporte a arquivos ZIP**: Detecta e processa automaticamente
- **Exclusão de arquivos lidos**: Ignora arquivos com prefixo configurável (padrão: `_L_`)
- **Filtragem por palavras-chave**: Busca case-insensitive

### Suporte a Cloud Storage
- Funciona com **Google Drive**, **OneDrive** e outras pastas de sincronização
- Ignora automaticamente pastas ocultas (prefixo `.`)
- Busca recursiva em todas as subpastas

## 📦 Instalação

### Com Poetry (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/random-file-picker.git
cd random-file-picker

# Instale as dependências
poetry install

# Ative o ambiente virtual
poetry shell
```

### Instalação Manual

```bash
pip install -e .
```

## 🚀 Como Usar

### Interface Gráfica

```bash
# Com Poetry
poetry run rfp-gui

# Ou se estiver no shell do Poetry
rfp-gui
```

### Linha de Comando

```bash
# Seleção básica
poetry run random-file-picker /caminho/pasta1 /caminho/pasta2

# Com palavras-chave
poetry run random-file-picker /caminho/pasta --keywords importante documento

# Modo aleatório (sem sequencial)
poetry run random-file-picker /caminho/pasta --no-sequence

# Abrir pasta automaticamente
poetry run random-file-picker /caminho/pasta --open-folder

# Ajuda completa
poetry run random-file-picker --help
```

## 🧪 Testes

```bash
# Executar todos os testes
poetry run pytest

# Com cobertura
poetry run pytest --cov

# Testes específicos
poetry run pytest tests/unit/test_file_picker.py

# Ver relatório de cobertura HTML
poetry run pytest --cov --cov-report=html
open htmlcov/index.html  # ou start htmlcov\index.html no Windows
```

## 🛠️ Desenvolvimento

### Configurar Ambiente de Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
poetry install

# Instalar pre-commit hooks
poetry run pre-commit install

# Formatar código
poetry run black src/ tests/

# Verificar estilo
poetry run flake8 src/ tests/

# Type checking
poetry run mypy src/
```

### Estrutura do Projeto

```
random-file-picker/
├── src/
│   └── random_file_picker/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── core/               # Core functionality
│       │   ├── __init__.py
│       │   ├── file_picker.py
│       │   └── sequential_selector.py
│       ├── gui/                # GUI components
│       │   ├── __init__.py
│       │   └── app.py
│       └── utils/              # Utility functions
│           ├── __init__.py
│           ├── system_utils.py
│           ├── system_utils_windows.py
│           └── system_utils_linux.py
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── __init__.py
├── config/                     # Configuration files
├── pyproject.toml              # Poetry configuration
└── README.md
```

## 📝 Configuração

A aplicação GUI salva automaticamente as configurações em `config.json` incluindo:
- Pastas monitoradas
- Prefixo de exclusão
- Preferências de abertura
- Histórico de arquivos
- Palavras-chave

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## ✨ Recursos do Poetry

Este projeto usa Poetry para gerenciamento de dependências e oferece:

- ✅ Gerenciamento de dependências isolado
- ✅ Versionamento semântico automático
- ✅ Scripts de linha de comando configurados
- ✅ Suporte a ambientes virtuais
- ✅ Build e publicação simplificados
- ✅ Testes com pytest e coverage
- ✅ Code formatting com black e isort
- ✅ Type checking com mypy
