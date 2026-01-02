# Guia de Migração para Poetry

## 📦 O que foi feito?

Este projeto foi completamente reorganizado e migrado para usar **Poetry** como gerenciador de dependências e build system. A estrutura foi profissionalizada seguindo as melhores práticas Python.

## 🗂️ Nova Estrutura

```
random-file-picker/
├── src/
│   └── random_file_picker/          # Código-fonte organizado
│       ├── __init__.py              # Exports principais
│       ├── cli.py                   # Interface de linha de comando
│       ├── core/                    # Lógica principal
│       │   ├── file_picker.py       # Seleção de arquivos
│       │   └── sequential_selector.py  # Seleção sequencial
│       ├── gui/                     # Interface gráfica
│       │   └── app.py               # Aplicação Tkinter
│       └── utils/                   # Utilitários
│           ├── system_utils.py
│           ├── system_utils_windows.py
│           └── system_utils_linux.py
├── tests/                           # Testes
│   ├── conftest.py                  # Fixtures do pytest
│   ├── unit/                        # Testes unitários
│   │   ├── test_file_picker.py
│   │   └── test_sequential_selector.py
│   └── integration/                 # Testes de integração
├── config/                          # Arquivos de configuração
│   └── config.example.json
├── pyproject.toml                   # Configuração do Poetry
├── README_POETRY.md                 # Documentação atualizada
├── LICENSE                          # Licença MIT
├── .gitignore                       # Arquivos ignorados pelo Git
└── tasks.py                         # Scripts de desenvolvimento
```

## 🚀 Como usar o novo projeto

### 1. Instalar Poetry (se necessário)

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Linux/macOS
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Instalar dependências

```bash
cd random-file-picker
poetry install
```

### 3. Executar a aplicação

#### Interface Gráfica (recomendado)
```bash
poetry run rfp-gui
```

#### Linha de Comando
```bash
# Exemplo básico
poetry run random-file-picker C:\Pasta1 D:\Pasta2

# Com opções
poetry run random-file-picker --keywords "marvel" "dc" --open-folder C:\Comics
```

### 4. Ativar ambiente virtual

```bash
# Ativar shell do Poetry
poetry shell

# Agora você pode usar diretamente
rfp-gui
random-file-picker --help
```

## 🔄 Mudanças de Imports

Se você tinha código que importava os módulos antigos, atualize assim:

### Antes:
```python
from random_file_picker import pick_random_file, open_folder
from sequential_selector import SequentialFileTracker
from system_utils import get_default_app_info
```

### Depois:
```python
from random_file_picker import pick_random_file, open_folder
from random_file_picker import SequentialFileTracker
from random_file_picker.utils import get_default_app_info
```

Ou de forma mais específica:
```python
from random_file_picker.core.file_picker import pick_random_file, open_folder
from random_file_picker.core.sequential_selector import SequentialFileTracker
from random_file_picker.utils.system_utils import get_default_app_info
```

## 🧪 Executar Testes

```bash
# Todos os testes
poetry run pytest

# Com cobertura
poetry run pytest --cov

# Gerar relatório HTML
poetry run pytest --cov --cov-report=html
# Abra htmlcov/index.html no navegador
```

## 🛠️ Comandos de Desenvolvimento

### Formatação de código
```bash
poetry run black src tests
poetry run isort src tests
```

### Linting
```bash
poetry run flake8 src tests
```

### Type checking
```bash
poetry run mypy src
```

### Scripts auxiliares
```bash
# Usar o arquivo tasks.py
poetry run python tasks.py format     # Formata código
poetry run python tasks.py lint       # Linting completo
poetry run python tasks.py test       # Executa testes
poetry run python tasks.py test-cov   # Testes com cobertura
poetry run python tasks.py clean      # Limpa arquivos temporários
```

## 📝 Arquivos Antigos

Os arquivos originais ainda estão na raiz do projeto:
- `random_file_picker.py` → agora em `src/random_file_picker/core/file_picker.py`
- `random_file_picker_gui.py` → agora em `src/random_file_picker/gui/app.py`
- `sequential_selector.py` → agora em `src/random_file_picker/core/sequential_selector.py`
- `system_utils*.py` → agora em `src/random_file_picker/utils/`
- `test_*.py` → agora em `tests/unit/`

**Você pode deletar os arquivos antigos da raiz** se quiser, pois a nova estrutura já está funcionando.

## 📦 Distribuição

### Criar pacote para distribuição
```bash
poetry build
# Gera arquivos em dist/ (.tar.gz e .whl)
```

### Publicar no PyPI (quando estiver pronto)
```bash
poetry publish
```

### Instalar a partir do código fonte
```bash
poetry install
# ou
pip install -e .
```

## ✨ Novos Recursos

1. **CLI aprimorado**: Agora com `argparse` e opções mais claras
2. **Testes automatizados**: Suite completa de testes unitários
3. **Cobertura de código**: Relatórios de cobertura integrados
4. **Linting e formatação**: Black, Flake8, isort configurados
5. **Type hints**: Suporte a mypy para verificação de tipos
6. **Pre-commit hooks**: Validações automáticas antes de commits
7. **Documentação melhorada**: README mais completo e profissional

## 🆘 Problemas Comuns

### Poetry não encontrado
Certifique-se que o diretório de scripts do Poetry está no PATH:
- Windows: `%APPDATA%\Python\Scripts`
- Linux/macOS: `~/.local/bin`

### Módulo não encontrado
```bash
# Reinstale as dependências
poetry install

# Ou ative o ambiente virtual
poetry shell
```

### Testes falhando
```bash
# Limpe o cache
poetry run python tasks.py clean

# Reinstale
poetry install

# Execute os testes novamente
poetry run pytest -v
```

## 📚 Próximos Passos

1. ✅ Estrutura do projeto organizada
2. ✅ Poetry configurado
3. ✅ Testes unitários criados
4. ✅ CLI e GUI funcionando
5. ⏭️ Adicionar mais testes de integração
6. ⏭️ Configurar CI/CD (GitHub Actions)
7. ⏭️ Publicar no PyPI
8. ⏭️ Criar documentação com Sphinx

## 🤝 Contribuindo

Agora é muito mais fácil contribuir! Basta:

1. Fork o projeto
2. Clone: `git clone sua-url`
3. Instale: `poetry install`
4. Crie uma branch: `git checkout -b feature/nova-feature`
5. Desenvolva e teste: `poetry run pytest`
6. Formate: `poetry run python tasks.py format`
7. Commit e push
8. Abra um Pull Request

## 📞 Suporte

Se encontrar problemas ou tiver dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação do Poetry: https://python-poetry.org/docs/
- Veja exemplos em `README_POETRY.md`
