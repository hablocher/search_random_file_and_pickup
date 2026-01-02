# 🧪 Testes

Este documento descreve como executar os testes do projeto e detalha alguns dos cenários de teste implementados.

## 📑 Índice

- [Como Executar os Testes](#-como-executar-os-testes)
- [Cenários de Teste](#-cenários-de-teste)

---

## 🚀 Como Executar os Testes

### Requisitos
- [Poetry](https://python-poetry.org/) instalado.
- Dependências de desenvolvimento instaladas (`poetry install`).

### Comandos
- **Executar todos os testes**:
  ```bash
  poetry run pytest
  ```

- **Executar testes com mais detalhes (verbose)**:
  ```bash
  poetry run pytest -v
  ```

- **Gerar relatório de cobertura de código**:
  ```bash
  poetry run pytest --cov
  ```

- **Gerar relatório de cobertura em HTML**:
  ```bash
  poetry run pytest --cov --cov-report=html
  ```
  O relatório será gerado na pasta `htmlcov`. Abra o arquivo `index.html` para visualizar.

---

## 🔬 Cenários de Teste

### Filtro de Palavras-chave

O sistema de filtro por palavras-chave foi testado para garantir que os modos "AND" e "OR" funcionam corretamente.

- **Modo OR (padrão)**: A busca deve retornar arquivos que contenham **pelo menos uma** das palavras-chave.
  - **Exemplo**: `john, wick`
    - **Encontra**: "John Wick Chapter 1.mkv", "John Rambo.mkv"
    - **Não encontra**: "Matrix.mkv"

- **Modo AND**: A busca deve retornar apenas arquivos que contenham **todas** as palavras-chave.
  - **Exemplo**: `john, wick`
    - **Encontra**: "John Wick Chapter 1.mkv"
    - **Não encontra**: "John Rambo.mkv"

Os testes também validam:
- **Case-insensitivity**: A busca não diferencia maiúsculas de minúsculas.
- **Busca em arquivos compactados**: A filtragem funciona para arquivos dentro de `.zip` e `.rar`.

### Detecção de Sequência

Os testes garantem que a detecção de sequência funciona para diversos padrões de numeração:
- **Numeração simples**: `001`, `002`, `003`
- **Com prefixo**: `#1`, `#2`, `#3`
- **Capítulos/Volumes**: `Cap 1`, `Vol 2`
- **Números romanos**: `I`, `II`, `III`

### Correções de Bugs

Foram criados testes específicos para validar a correção de bugs, como:
- **Seleção incorreta no modo sequencial**: Garante que "Volume 01" seja sempre selecionado antes de "Volume 02".
- **Nomes de coleção incorretos**: Valida que o número do arquivo é removido corretamente ao identificar a coleção.
