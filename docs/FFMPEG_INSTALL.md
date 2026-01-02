# Instalação do FFmpeg para Suporte a Vídeos

O aplicativo usa o FFmpeg para extrair frames de arquivos de vídeo e gerar prévias visuais.

## Windows

### Opção 1: Usando winget (Recomendado)

```powershell
winget install Gyan.FFmpeg
```

### Opção 2: Download Manual

1. Baixe o FFmpeg em: https://www.gyan.dev/ffmpeg/builds/
2. Escolha "ffmpeg-release-essentials.zip"
3. Extraia o arquivo para uma pasta (ex: `C:\ffmpeg`)
4. Adicione o caminho do `bin` ao PATH do sistema:
   - Abra "Editar variáveis de ambiente do sistema"
   - Clique em "Variáveis de Ambiente"
   - Em "Variáveis do sistema", selecione "Path" e clique em "Editar"
   - Clique em "Novo" e adicione: `C:\ffmpeg\bin`
   - Clique em "OK" em todas as janelas
5. Reinicie o terminal/aplicativo

### Verificação

Abra um terminal e execute:

```bash
ffmpeg -version
```

Se mostrar a versão do FFmpeg, está instalado corretamente.

## Linux

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

### Fedora

```bash
sudo dnf install ffmpeg
```

### Arch Linux

```bash
sudo pacman -S ffmpeg
```

## macOS

### Usando Homebrew

```bash
brew install ffmpeg
```

## Formatos de Vídeo Suportados

Com o FFmpeg instalado, o aplicativo suporta:

- **MP4** (.mp4, .m4v, .m4a)
- **AVI** (.avi)
- **MKV** (.mkv)
- **WEBM** (.webm)
- **FLV** (.flv)
- **MOV** (.mov, .qt)
- **WMV** (.wmv)

## Extração de Frames

O aplicativo extrai automaticamente um frame aleatório da **metade do vídeo ±5 minutos** para criar a prévia visual.

Exemplo:
- Vídeo de 60 minutos → Frame extraído entre 25-35 minutos
- Vídeo de 20 minutos → Frame extraído entre 5-15 minutos

## Solução de Problemas

### "FFmpeg não encontrado no sistema"

- Certifique-se de que o FFmpeg está instalado
- Verifique se o executável `ffmpeg` está no PATH do sistema
- Reinicie o terminal e o aplicativo após a instalação

### "Erro ao extrair frame do vídeo"

- Verifique se o arquivo de vídeo não está corrompido
- Teste o vídeo com `ffmpeg -i arquivo.mp4` no terminal
- Alguns formatos podem não ser suportados dependendo da versão do FFmpeg

### Performance

A extração de frames é rápida (geralmente < 5 segundos), mas pode variar dependendo:
- Tamanho e resolução do vídeo
- Velocidade do disco (HDD vs SSD)
- Codec utilizado no vídeo
