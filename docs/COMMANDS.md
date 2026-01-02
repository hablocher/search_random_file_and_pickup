# Comandos Úteis - Random File Picker

## 🚀 Instalação e Setup

```bash
# Instalar Poetry (Windows PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Instalar Poetry (Linux/macOS)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependências do projeto
poetry install

# Ativar ambiente virtual
poetry shell
```

## 💻 Executar Aplicação

```bash
# Interface Gráfica
poetry run rfp-gui

# CLI - Básico
poetry run random-file-picker C:\Pasta1 D:\Pasta2

# CLI - Com palavras-chave
poetry run random-file-picker --keywords "marvel" "dc" C:\Comics

# CLI - Modo aleatório (sem sequência)
poetry run random-file-picker --no-sequence C:\Pasta

# CLI - Não processar ZIPs
poetry run random-file-picker --no-zip C:\Pasta

# CLI - Abrir pasta automaticamente
poetry run random-file-picker --open-folder C:\Pasta

# CLI - Ver ajuda
poetry run random-file-picker --help
```

## 🧪 Testes

```bash
# Executar todos os testes
poetry run pytest

# Testes com verbose
poetry run pytest -v

# Testes com cobertura
poetry run pytest --cov

# Testes com cobertura e relatório HTML
poetry run pytest --cov --cov-report=html
# Abrir: htmlcov/index.html

# Executar teste específico
poetry run pytest tests/unit/test_file_picker.py

# Executar apenas testes que contenham "sequential"
poetry run pytest -k sequential

# Executar com mais detalhes
poetry run pytest -vv

# Parar no primeiro erro
poetry run pytest -x
```

## 🎨 Formatação e Linting

```bash
# Formatar código com Black
poetry run black src tests

# Ordenar imports com isort
poetry run isort src tests

# Verificar estilo com Flake8
poetry run flake8 src tests

# Type checking com mypy
poetry run mypy src

# Executar todos juntos (usando tasks.py)
poetry run python tasks.py format
poetry run python tasks.py lint
```

## 🛠️ Desenvolvimento

```bash
# Adicionar nova dependência
poetry add nome-do-pacote

# Adicionar dependência de desenvolvimento
poetry add --group dev nome-do-pacote

# Atualizar dependências
poetry update

# Ver dependências instaladas
poetry show

# Ver apenas dependências diretas
poetry show --tree

# Remover dependência
poetry remove nome-do-pacote

# Criar novo ambiente virtual
poetry env use python3.11

# Ver ambientes virtuais
poetry env list

# Remover ambiente virtual
poetry env remove python3.11
```

## 📦 Build e Distribuição

```bash
# Criar pacote para distribuição
poetry build

# Publicar no PyPI (requer configuração)
poetry publish

# Publicar no Test PyPI
poetry publish -r testpypi

# Instalar localmente em modo editável
poetry install

# Instalar apenas dependências de produção
poetry install --only main
```

## 🧹 Limpeza

```bash
# Limpar cache do Poetry
poetry cache clear . --all

# Limpar arquivos temporários (usando tasks.py)
poetry run python tasks.py clean

# Remover ambiente virtual e reinstalar
poetry env remove python
poetry install
```

## 🔍 Informações

```bash
# Ver versão do Poetry
poetry --version

# Ver informações do projeto
poetry show --tree

# Ver path do ambiente virtual
poetry env info --path

# Ver configuração do Poetry
poetry config --list

# Ver dependências desatualizadas
poetry show --outdated
```

## 📝 Git

```bash
# Inicializar repositório (se novo)
git init
git add .
git commit -m "Initial commit com Poetry"

# Adicionar mudanças
git add .
git commit -m "Descrição das mudanças"

# Ver status
git status

# Ver histórico
git log --oneline

# Criar branch
git checkout -b feature/nova-feature

# Push
git push origin main
```

## 🔧 Configuração do Poetry

```bash
# Criar virtualenv dentro do projeto
poetry config virtualenvs.in-project true

# Usar Python do sistema
poetry config virtualenvs.prefer-active-python true

# Ver configuração
poetry config --list

# Resetar configuração
poetry config virtualenvs.in-project --unset
```

## 📊 Pre-commit Hooks

```bash
# Instalar hooks
poetry run pre-commit install

# Executar manualmente
poetry run pre-commit run --all-files

# Atualizar hooks
poetry run pre-commit autoupdate

# Desinstalar hooks
poetry run pre-commit uninstall
```

## 🐛 Debug

```bash
# Executar com mais informações
poetry run python -v random_file_picker/cli.py

# Ver traceback completo
poetry run pytest --tb=long

# Debugger interativo (adicione ao código)
# import pdb; pdb.set_trace()

# Ver variáveis de ambiente
poetry run python -c "import sys; print(sys.path)"
```

## 📚 Documentação

```bash
# Gerar documentação com Sphinx (se configurado)
poetry run sphinx-build -b html docs/ docs/_build/

# Servidor local para docs
poetry run python -m http.server 8000 -d docs/_build/
```

## ⚡ Atalhos Úteis

```bash
# Executar CLI rapidamente (após poetry shell)
alias rfp='random-file-picker'
alias rfpg='rfp-gui'

# Windows (PowerShell)
Set-Alias rfp 'random-file-picker'
Set-Alias rfpg 'rfp-gui'

# Depois pode usar:
rfp C:\Comics --keywords "marvel"
rfpg
```

## 🎯 Workflow Típico de Desenvolvimento

```bash
# 1. Clonar/entrar no projeto
cd random-file-picker

# 2. Instalar dependências
poetry install

# 3. Ativar ambiente
poetry shell

# 4. Criar branch
git checkout -b feature/minha-feature

# 5. Desenvolver e testar
# ... fazer mudanças no código ...
poetry run pytest

# 6. Formatar código
poetry run black src tests
poetry run isort src tests

# 7. Verificar qualidade
poetry run flake8 src tests
poetry run mypy src

# 8. Commit
git add .
git commit -m "Adiciona nova feature"

# 9. Push
git push origin feature/minha-feature
```

## 📱 Scripts Personalizados (tasks.py)

```bash
# Executar testes
poetry run python tasks.py test

# Testes com cobertura
poetry run python tasks.py test-cov

# Linting completo
poetry run python tasks.py lint

# Type checking
poetry run python tasks.py type-check

# Formatar código
poetry run python tasks.py format

# Limpar cache e temporários
poetry run python tasks.py clean
```

## 🌐 URLs Úteis

- Poetry: https://python-poetry.org/docs/
- pytest: https://docs.pytest.org/
- Black: https://black.readthedocs.io/
- Flake8: https://flake8.pycqa.org/
- mypy: https://mypy.readthedocs.io/
- isort: https://pycqa.github.io/isort/
