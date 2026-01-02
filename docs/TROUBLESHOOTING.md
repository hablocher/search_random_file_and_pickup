# 🐛 Troubleshooting

Este documento lista problemas comuns e suas soluções, além de um histórico de bugs corrigidos.

## 📑 Índice

- [Problemas Comuns](#-problemas-comuns)
- [Histórico de Bugs Corrigidos](#-histórico-de-bugs-corrigidos)

---

## 🔧 Problemas Comuns

### Erro "Cannot find working tool" ao processar arquivos RAR

**Causa**: O UnRAR, ferramenta necessária para extrair arquivos `.rar` e `.cbr`, não está instalado ou não foi encontrado.

**Solução**:
1. **Instale o WinRAR**: A forma mais fácil de resolver é instalando o [WinRAR](https://www.win-rar.com/download.html). A instalação inclui o `UnRAR.exe`.
2. **Verifique a instalação**: Certifique-se de que o `UnRAR.exe` está em `C:\ Program Files\WinRAR\`.
3. **Consulte o guia completo**: [UNRAR.md](UNRAR.md).

### FFmpeg não encontrado

**Causa**: O FFmpeg, necessário para gerar pré-visualizações (thumbnails) de vídeos, não está instalado.

**Solução**:
- **Windows**: Use o `winget install Gyan.FFmpeg`.
- **Linux/macOS**: Use o gerenciador de pacotes da sua distribuição (`apt`, `brew`, etc.).
- **Consulte o guia completo**: [FFMPEG_INSTALL.md](FFMPEG_INSTALL.md).

### Cache não atualiza após mudanças nos arquivos

**Causa**: O sistema de cache pode não ter detectado as alterações.

**Solução**:
1. Na interface, desative a opção "⚡ Cache de arquivos".
2. Execute uma busca para forçar a recriação do cache.
3. Reative a opção de cache.

### A busca de capas de filmes (TMDb) não funciona

**Causa**: A chave da API do TMDb não está configurada ou é inválida.

**Solução**:
1. Obtenha uma chave de API gratuita no [site do TMDb](https://www.themoviedb.org/settings/api).
2. Adicione a chave ao arquivo `config.json`.
3. **Consulte o guia completo**: [TMDB_SETUP.md](TMDB_SETUP.md).

### A interface trava durante uma busca

**Causa**: A busca pode estar demorando muito, especialmente em pastas grandes ou em HDDs lentos.

**Solução**:
- Aguarde a conclusão da busca. A interface deve voltar a responder.
- Em casos extremos, feche e reabra a aplicação.

---

## 🐞 Histórico de Bugs Corrigidos

### Seleção incorreta no modo sequencial
- **Sintoma**: O programa selecionava "Volume 02" de uma série mesmo quando "Volume 01" estava disponível e não lido.
- **Causa**: O modo de "fallback" para seleção aleatória não verificava se o arquivo escolhido fazia parte de uma sequência.
- **Solução**: Foi adicionada uma verificação de sequência ao fallback, garantindo que o primeiro arquivo não lido de uma série seja sempre priorizado.

### Nomes de coleção incorretos com números
- **Sintoma**: Um arquivo chamado "Série v1 081" era identificado como parte da coleção "Série v1 081" em vez de "Série v1".
- **Causa**: A lógica de extração do nome da coleção não removia o número do arquivo corretamente.
- **Solução**: A extração do nome da coleção foi aprimorada para remover corretamente os números de episódio/volume.
