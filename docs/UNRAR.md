# 📦 Como Corrigir Erro "Cannot find working tool" (RAR)

## O Problema

Você viu este erro no log:
```
✗ Erro ao extrair arquivo.png: Cannot find working tool
```

Isso significa que o **UnRAR** não está instalado no seu sistema.

## Solução (Windows)

### Opção 1: Instalar WinRAR (Recomendado)

1. **Download**: https://www.win-rar.com/download.html
2. Baixe a versão de **64 bits** para Windows
3. Instale normalmente
4. Reinicie o Media Finder

O WinRAR instala automaticamente o UnRAR.exe necessário.

### Opção 2: UnRAR Standalone

1. **Download**: https://www.rarlab.com/rar_add.htm
2. Procure por "UnRAR for Windows"
3. Extraia `UnRAR.exe` para uma destas pastas:
   - `C:\Program Files\WinRAR\`
   - `C:\Windows\System32\`
   - Qualquer pasta que esteja no PATH do sistema

## Verificação

Após instalar, o Media Finder detectará automaticamente o UnRAR nos seguintes locais:
- `C:\Program Files\WinRAR\UnRAR.exe`
- `C:\Program Files (x86)\WinRAR\UnRAR.exe`
- PATH do sistema

## Por Que Preciso Disso?

Arquivos `.cbr` (Comic Book RAR) são arquivos RAR compactados. Para extrair as imagens e gerar previews, o Python precisa do programa UnRAR instalado no sistema.

## Alternativa: Usar CBZ (ZIP)

Se não quiser instalar UnRAR:
- Arquivos `.cbz` (Comic Book ZIP) funcionam sem instalação adicional
- Muitos leitores de quadrinhos permitem converter CBR → CBZ

## Ainda Com Problemas?

Se mesmo após instalar o WinRAR o erro persistir:

1. Verifique se o UnRAR.exe existe em:
   ```
   C:\Program Files\WinRAR\UnRAR.exe
   ```

2. Teste manualmente no PowerShell:
   ```powershell
   & "C:\Program Files\WinRAR\UnRAR.exe" -?
   ```

3. Se não funcionar, adicione ao PATH ou reinstale o WinRAR.
