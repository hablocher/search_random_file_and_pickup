# 📦 Build do Media Finder

## Como gerar o executável

### Windows

1. Execute o script de build:
   ```batch
   build_exe.bat
   ```

2. O executável será criado em: `dist/MediaFinder.exe`

### Manual (qualquer plataforma)

```bash
# Construir usando o arquivo spec
poetry run pyinstaller MediaFinder.spec --clean

# OU construir diretamente (sem assets otimizados)
poetry run pyinstaller --name MediaFinder --windowed --onefile src/random_file_picker/gui/app.py
```

## Estrutura do Build

O arquivo `MediaFinder.spec` define:
- **Entrada**: `src/random_file_picker/gui/app.py`
- **Assets incluídos**: 
  - `assets/roulette.png`
  - `assets/spinning.gif`
- **Modo**: Single file (--onefile) sem console
- **Nome**: MediaFinder.exe

## Requisitos

- Python 3.9+
- Poetry
- PyInstaller 6.x

## Distribuição

Após o build, você pode distribuir apenas o arquivo `dist/MediaFinder.exe`. Ele contém:
- Todas as dependências Python
- Assets (imagens)
- Runtime Python embutido

Não precisa instalar Python ou dependências na máquina de destino!

## Configuração

O executável criará automaticamente um arquivo `config.json` no diretório onde for executado.

## Tamanho

O executável tem aproximadamente 50-80MB devido ao Python embutido e todas as bibliotecas (PIL, tkinter, etc).

## Notas

- **Antivírus**: Alguns antivírus podem alertar sobre executáveis PyInstaller. Isso é um falso positivo comum.
- **Primeira execução**: Pode demorar um pouco mais devido à descompactação inicial.
- **Cache**: O programa cria um arquivo `read_files_tracker.json` para cache de arquivos.
