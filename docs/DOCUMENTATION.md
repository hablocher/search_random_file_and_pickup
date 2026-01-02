# 📚 Documentação Completa - Random File Picker

## 📑 Índice

1. [Visão Geral](#visão-geral)
2. [Instalação e Configuração](#instalação-e-configuração)
3. [Funcionalidades](#funcionalidades)
4. [Guias de Uso](#guias-de-uso)
5. [Otimizações e Melhorias](#otimizações-e-melhorias)
6. [Correções de Bugs](#correções-de-bugs)
7. [Comandos e Atalhos](#comandos-e-atalhos)
8. [Troubleshooting](#troubleshooting)

---

## 1. Visão Geral

### O que é o Random File Picker?

Aplicação Python com interface gráfica moderna que seleciona arquivos de forma inteligente, com suporte a:
- ✅ Detecção automática de sequências (quadrinhos, séries, volumes)
- 🎲 Seleção aleatória ou sequencial
- 📦 Busca dentro de arquivos ZIP/RAR
- 🖼️ Prévia de thumbnails (imagens, PDFs, vídeos)
- 🎬 Busca de capas de filmes online (TMDb API)
- ⚡ Cache inteligente para buscas instantâneas
- ☁️ Suporte a OneDrive e Google Drive

---

## 2. Instalação e Configuração

### 2.1 Requisitos do Sistema

- **Python 3.6+**
- **Sistema Operacional**: Windows, Linux ou macOS

### 2.2 Instalação com Poetry (Recomendado)

```bash
# Clone o repositório
git clone <repository-url>
cd search_random_file_and_pickup

# Instale as dependências com Poetry
poetry install

# Execute a aplicação
poetry run rfp-gui
```

### 2.3 Instalação Manual

```bash
# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python -m random_file_picker.gui.app
```

### 2.4 Dependências Principais

| Biblioteca | Uso | Instalação |
|-----------|-----|------------|
| **Pillow** | Processamento de imagens | `pip install Pillow` |
| **rarfile** | Extração de RAR/CBR | `pip install rarfile` |
| **PyMuPDF** | Renderização de PDFs | `pip install PyMuPDF` |
| **ffmpeg-python** | Extração de frames de vídeos | `pip install ffmpeg-python` |
| **requests** | Busca de capas online | `pip install requests` |

### 2.5 Configuração Inicial

1. **Execute a aplicação** pela primeira vez
2. **Adicione pastas** para busca usando o botão "➕ Adicionar"
3. **Configure opções** conforme necessário:
   - Prefixo de arquivos lidos (padrão: `_L_`)
   - Limite de histórico (1-50)
   - Palavras-chave para filtrar
   - Extensões a ignorar
4. **Salve a configuração** (💾 Salvar Configuração)

### 2.6 Instalação do FFmpeg (Opcional)

O FFmpeg é necessário para extrair frames de vídeos. [Ver guia completo](FFMPEG_INSTALL.md)

**Windows:**
```powershell
winget install Gyan.FFmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 2.7 Configuração da API TMDb (Opcional)

Para buscar capas de filmes online:

1. Crie uma conta em [themoviedb.org](https://www.themoviedb.org)
2. Obtenha uma API Key em: Configurações → API
3. Adicione ao `config.json`:
```json
{
  "tmdb_api_key": "sua_api_key_aqui"
}
```

---

## 3. Funcionalidades

### 3.1 Interface Moderna

- 🎨 **Tema Azure** com cores suaves e design responsivo
- 📱 **Layout intuitivo** com emojis para identificação rápida
- 🖱️ **Atalhos de teclado** (Enter para buscar, Tab para navegar)
- 📊 **Status bar** com feedback visual
- 🔄 **Atualização em tempo real** durante processamento

### 3.2 Seleção Inteligente

#### Modo Sequencial (Recomendado)

Detecta automaticamente arquivos numerados e seleciona o próximo não lido:

**Formatos suportados:**
- Números decimais: `001`, `081`, `100`
- Com prefixo hash: `#001`, `#100`
- Padrão "X de Y": `01 de 10`, `1 of 10`
- Capítulo/Volume: `Cap 1`, `Vol 2`, `Part 3`
- Números romanos: `I`, `II`, `III`, `IX`, `X`
- Séries com volume: `Marvel Team-Up v1 081`

**Exemplos:**
```
✅ Detecta sequência:
   Serie 001.cbr, Serie 002.cbr, Serie 003.cbr
   
✅ Múltiplas coleções:
   Batman #001.cbr, Superman #001.cbr
   
✅ Volumes:
   Manga v1 001.cbz, Manga v1 002.cbz, Manga v2 001.cbz
```

#### Modo Aleatório

Seleção totalmente randômica, ideal para:
- Explorar biblioteca sem ordem
- Redescobrir arquivos esquecidos
- Variedade máxima

### 3.3 Processamento de ZIP/RAR

- 📦 **Detecção automática** de arquivos compactados
- 🔍 **Busca recursiva** dentro dos arquivos
- 🎯 **Aplicação de filtros** (palavras-chave, prefixo)
- 📂 **Extração inteligente** para pasta temporária
- 🧹 **Limpeza automática** após uso
- 🔢 **Detecção de sequência dentro de ZIPs**

**Exemplo de uso:**
```
Marvel Team-Up v1 81-100.zip
  ├─ Marvel Team-Up v1 081.cbz  ← Seleciona o primeiro não lido
  ├─ Marvel Team-Up v1 082.cbz
  └─ Marvel Team-Up v1 100.cbz
```

### 3.4 Sistema de Cache

#### Como Funciona

1. **Primeira busca**: Escaneia todas as pastas e cria `file_cache.json.gz`
2. **Buscas seguintes**: Carrega do cache (instantâneo)
3. **Validação automática**: Detecta mudanças por timestamp/hash
4. **Invalidação inteligente**: Recria cache quando necessário

#### Controle Manual

- ✅ **Ligado** (padrão): Usa cache para velocidade
- ❌ **Desligado**: Sempre recria (útil após mudanças massivas)

#### Benefícios

- ⚡ **10-100x mais rápido** em buscas subsequentes
- 💾 **Economia de I/O** no disco
- 🎯 **Cache por configuração** (pastas, keywords, etc.)

### 3.5 Prévia de Thumbnails

Suporta múltiplos formatos:

| Tipo | Formato | Como Funciona |
|------|---------|---------------|
| **Imagens** | JPG, PNG, GIF | Exibe diretamente |
| **Arquivos Compactados** | ZIP, RAR, CBZ, CBR | Extrai primeira imagem |
| **PDFs** | PDF | Renderiza primeira página |
| **Vídeos** | MP4, AVI, MKV, WEBM | Extrai frame ou busca capa online |
| **Áudio** | MP3, FLAC, OGG, WAV | Indica sem prévia |

#### Busca de Capas de Filmes

1. **Detecta nome do filme** no arquivo
2. **Busca na API TMDb** (se configurada)
3. **Fallback para FFmpeg** (extrai frame)
4. **Indica quando não encontrado**

### 3.6 Filtragem por Palavras-Chave

Configure até **5 palavras-chave** para filtrar arquivos:

**Modo OR (padrão):**
```
Keywords: "batman, superman"
✅ Match: "Batman Begins.cbr"
✅ Match: "Superman vs Batman.cbr"
❌ No match: "Wonder Woman.cbr"
```

**Modo AND:**
```
Keywords: "batman, dark"
✅ Match: "Batman The Dark Knight.cbr"
❌ No match: "Batman Begins.cbr"
```

### 3.7 Extensões Ignoradas

Ignore arquivos indesejados automaticamente:

```
Padrão: srt, sub, txt, nfo

✅ Ignora: legendas.srt, info.nfo
✅ Seleciona: filme.mp4, quadrinho.cbr
```

### 3.8 Histórico Persistente

- 📜 **Últimos arquivos** selecionados (configurável 1-50)
- 🔄 **Reabre arquivo** com um clique
- 📂 **Abre pasta** do arquivo com botão "..."
- 💾 **Persistência** entre sessões

---

## 4. Guias de Uso

### 4.1 Uso Básico

1. **Adicione pastas** para busca
2. **Configure opções** (opcional)
3. **Clique em "🎲 Selecionar Arquivo"**
4. **Visualize prévia** e informações
5. **Arquivo abre automaticamente** (se habilitado)

### 4.2 Trabalhar com Sequências

Para melhor experiência com quadrinhos/mangás:

1. ✅ **Ative "🔢 Seleção sequencial"**
2. 📝 **Configure prefixo** de lidos (`_L_` padrão)
3. 🎯 **Sistema detecta** automaticamente numeração
4. 📖 **Seleciona próximo** não lido
5. ✏️ **Marque como lido** renomeando com prefixo

### 4.3 Buscar Filmes Específicos

Use palavras-chave para filtrar:

1. 🔍 **Digite keywords**: `avengers, marvel`
2. ✅ **Escolha modo AND/OR**
3. 🎲 **Execute busca**
4. 🎬 **Prévia busca capa** automaticamente

### 4.4 Trabalhar com Cloud Storage

**OneDrive / Google Drive:**

1. ☁️ **Ative "Forçar download de nuvem"**
2. ⏳ **Sistema aguarda** hidratação completa
3. 📥 **Download forçado** se necessário
4. ✅ **Processa arquivo** quando pronto

**Importante:** Primeira busca pode demorar para baixar arquivos.

### 4.5 Otimizar Performance

**Para bibliotecas grandes (10.000+ arquivos):**

1. ⚡ **Ative cache** (padrão ligado)
2. 🎯 **Use palavras-chave** para filtrar
3. 📁 **Organize pastas** por categoria
4. 🚫 **Ignore extensões** desnecessárias

**Para mudanças frequentes:**

1. ❌ **Desative cache** temporariamente
2. 🔄 **Faça mudanças** nos arquivos
3. ✅ **Reative cache** para velocidade

---

## 5. Otimizações e Melhorias

### 5.1 Cache Inteligente

**Implementação:**
- Arquivo: `file_cache.json.gz` (compactado)
- Hash: SHA256 da configuração (pastas + filtros)
- Validação: Timestamp das pastas
- Invalidação: Automática quando necessário

**Performance:**
```
Sem cache: 15-30 segundos (10.000 arquivos)
Com cache: 0.1-0.5 segundos
Speedup: ~100x
```

### 5.2 Detecção de Sequências ZIP

**Correção Crítica:**

Arquivos dentro de ZIPs agora são detectados como sequência:

```python
# ANTES (bug):
"Marvel Team-Up v1 081.cbz" → Coleção: "Marvel Team-Up v1 081"
"Marvel Team-Up v1 100.cbz" → Coleção: "Marvel Team-Up v1 100"
# Resultado: 20 coleções separadas ❌

# DEPOIS (corrigido):
"Marvel Team-Up v1 081.cbz" → Coleção: "Marvel Team-Up v1", Número: 81
"Marvel Team-Up v1 100.cbz" → Coleção: "Marvel Team-Up v1", Número: 100
# Resultado: 1 coleção com 20 arquivos ✅
```

**Padrões Corrigidos:**
1. Regex de números romanos (evita match vazio)
2. Ordem de padrões (específicos antes de genéricos)
3. Extração de número (usa último número, não primeiro)

### 5.3 Carregamento de Arquivos Grandes

- 🔄 **Streaming em chunks** (1MB por vez)
- 📊 **Barra de progresso** com percentual
- ⏹️ **Cancelamento** a qualquer momento
- ⏱️ **Temporizador** de operação
- 💾 **Gestão de memória** eficiente

### 5.4 Interface Responsiva

- 🎨 **Tema moderno** Azure
- 📱 **Layout adaptativo** (1200x750 → 900x600 mínimo)
- 🖱️ **Componentes estilizados** com Segoe UI
- 🎭 **Emojis** para UX intuitiva
- 📊 **Feedback visual** em tempo real

---

## 6. Correções de Bugs

### 6.1 Bug: Seleção Errada em Sequências

**Problema:** Selecionava "Volume 02" quando "Volume 01" existia não lido.

**Causa:** Fallback aleatório não verificava se arquivo fazia parte de sequência.

**Solução:** Adicionada verificação de sequência no fallback:

```python
# Após seleção aleatória
selected_folder = Path(selected).parent
folder_sequences = analyze_folder_sequence(selected_folder, ...)

if folder_sequences:
    # Arquivo faz parte de sequência!
    result = get_next_unread_file(folder_sequences, tracker, ...)
    if result:
        next_file, sequence_info, file_info = result
        selected = next_file  # ← Usa primeiro não lido da sequência
```

### 6.2 Bug: Números Romanos com Match Vazio

**Problema:** Regex `(M{0,3}...)` matchava strings vazias.

**Solução:** Mudança para `(M{1,3}|CM|CD|...)` que requer pelo menos 1 caractere.

### 6.3 Bug: Extração de Número Errada

**Problema:** "Marvel Team-Up v1 081" extraía "1" (de "v1") em vez de "081".

**Solução:** Mudança de `numbers[0]` para `numbers[-1]` (último número).

### 6.4 Bug: Collection Name com Número

**Problema:** "Marvel Team-Up v1 081" → collection "Marvel Team-Up v1 081" (mantinha número).

**Solução:** Padrão `(v\d+)\s+\d+.*$` agora remove apenas número, preserva "v1".

---

## 7. Comandos e Atalhos

### 7.1 Interface Gráfica

| Ação | Atalho |
|------|--------|
| Selecionar arquivo | `Enter` |
| Navegar campos | `Tab` |
| Cancelar operação | `Esc` ou botão ⏹️ |
| Fechar aplicação | `Alt+F4` |

### 7.2 Poetry (Desenvolvimento)

```bash
# Executar GUI
poetry run rfp-gui

# Executar CLI
poetry run rfp-cli --folders "C:\Comics" --sequence

# Instalar dependências
poetry install

# Atualizar dependências
poetry update

# Executar testes
poetry run pytest

# Adicionar dependência
poetry add <package>
```

### 7.3 Linha de Comando (CLI)

```bash
# Seleção sequencial
python -m random_file_picker.cli --folders "C:\Comics" --sequence

# Seleção aleatória
python -m random_file_picker.cli --folders "C:\Comics" "D:\Manga"

# Com palavras-chave (OR)
python -m random_file_picker.cli --folders "C:\Comics" --keywords "batman,superman"

# Com palavras-chave (AND)
python -m random_file_picker.cli --folders "C:\Comics" --keywords "batman,dark" --match-all

# Sem abrir arquivo
python -m random_file_picker.cli --folders "C:\Comics" --no-open

# Desabilitar cache
python -m random_file_picker.cli --folders "C:\Comics" --no-cache
```

---

## 8. Troubleshooting

### 8.1 Problemas Comuns

#### Cache não invalida após mudanças

**Sintoma:** Arquivos novos não aparecem na busca.

**Solução:**
1. Desative "⚡ Cache de arquivos"
2. Execute busca (recria cache)
3. Reative cache

#### FFmpeg não encontrado

**Sintoma:** "Erro ao extrair frame do vídeo".

**Solução:**
```bash
# Verifique instalação
ffmpeg -version

# Windows: Reinstale
winget install Gyan.FFmpeg

# Linux: Reinstale
sudo apt install ffmpeg
```

#### UnRAR não encontrado (Windows)

**Sintoma:** "Cannot find working tool" ao processar RAR.

**Solução:**
1. Baixe UnRAR: https://www.rarlab.com/rar_add.htm
2. Extraia `UnRAR.exe`
3. Coloque na pasta do script ou no PATH

#### Thumbnails não aparecem

**Sintoma:** Prévia mostra "Nenhum arquivo selecionado".

**Solução:**
1. Verifique dependências: `pip list | grep -E "(Pillow|PyMuPDF|rarfile)"`
2. Reinstale se necessário
3. Para vídeos, instale FFmpeg

#### API TMDb não funciona

**Sintoma:** Não busca capas de filmes.

**Solução:**
1. Verifique `config.json` tem `tmdb_api_key`
2. Teste chave em: https://api.themoviedb.org/3/configuration?api_key=SUA_KEY
3. Verifique conexão internet

#### OneDrive/Google Drive demora muito

**Sintoma:** Carregamento travado em "Sincronizando...".

**Solução:**
1. Desative "☁️ Forçar download de nuvem"
2. Sincronize arquivos manualmente
3. Execute busca após sincronização completa

### 8.2 Performance Issues

#### Busca muito lenta

**Causas possíveis:**
- Cache desabilitado
- Muitas pastas/arquivos
- Disco lento (HDD)
- Cloud storage sincronizando

**Soluções:**
- ✅ Ative cache
- 🎯 Use palavras-chave para filtrar
- 📁 Divida bibliotecas grandes
- ☁️ Aguarde sincronização

#### Interface travando

**Causas possíveis:**
- Arquivo muito grande (5GB+)
- Operação demorada sem progresso
- Muitos thumbnails simultâneos

**Soluções:**
- ⏹️ Use botão cancelar
- 🔄 Reinicie aplicação
- 💾 Reduza limite de histórico

### 8.3 Logs e Debug

**Localização dos logs:**
- Interface gráfica: Painel "📋 Log de Execução"
- Console: Output padrão

**Logs importantes:**
```
[Análise de Sequência] → Detecção de sequências
[Cache] → Operações de cache
[Limpeza] → Pastas temporárias
```

**Modo verbose (desenvolvimento):**
```python
# Em app.py ou cli.py, adicione:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📝 Notas Finais

### Contribuindo

Contribuições são bem-vindas! Areas de melhoria:
- 🌐 Internacionalização (i18n)
- 🎨 Temas customizáveis
- 📊 Estatísticas de leitura
- 🔗 Integração com Calibre
- 📱 Interface mobile

### Licença

Este projeto é open source. Veja LICENSE para detalhes.

### Suporte

- 🐛 **Issues**: Reporte bugs via GitHub Issues
- 💬 **Discussões**: Use GitHub Discussions
- 📧 **Email**: [seu-email@exemplo.com]

---

**Última atualização:** Janeiro 2026  
**Versão:** 2.0.0  
**Autor:** [Seu Nome]
