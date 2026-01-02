# 🎬 Busca Automática de Capas de Filmes

## Resumo da Funcionalidade

Foi implementado um sistema para buscar **capas oficiais de filmes** na internet antes de extrair frames dos vídeos. Isso melhora significativamente a qualidade das prévias visuais.

## 📁 Arquivos Criados/Modificados

### Novos Arquivos

1. **`src/random_file_picker/utils/movie_poster.py`** (257 linhas)
   - Classe `MoviePosterFetcher` para busca e download de capas
   - Parser inteligente de nomes de arquivos
   - Integração com TMDb API

2. **`docs/TMDB_SETUP.md`**
   - Guia completo de configuração
   - Como obter API key gratuitamente
   - Solução de problemas

3. **`tests/unit/test_movie_poster.py`**
   - 9 testes unitários
   - Testes de integração opcionais

### Arquivos Modificados

1. **`src/random_file_picker/core/archive_extractor.py`**
   - Importa `MoviePosterFetcher`
   - Adiciona parâmetro `tmdb_api_key` ao construtor
   - Tenta buscar capa antes de extrair frame (fallback automático)

2. **`src/random_file_picker/gui/app.py`**
   - Inicializa `ArchiveExtractor` com API key do config

3. **`config.json` e `config/config.example.json`**
   - Adicionado campo `"tmdb_api_key": ""`

4. **`pyproject.toml`**
   - Adicionada dependência `requests = "^2.31.0"`

## 🎯 Como Funciona

### Fluxo de Execução

```
Arquivo de vídeo selecionado
         ↓
┌────────────────────────┐
│ API key configurada?   │
└────────────────────────┘
         ↓
       SIM ──────────────────┐
         │                   │
         ↓                   ↓
┌────────────────────┐  ┌──────────────────┐
│ Buscar capa online │  │ Extrair frame    │
│ (TMDb API)         │  │ do vídeo         │
└────────────────────┘  └──────────────────┘
         ↓                   ↑
    Encontrou?               │
         │                   │
       SIM ─────────┐        │
         │          │      NÃO
        NÃO ────────┴────────┘
         │          │
         ↓          ↓
    [Fallback] [Sucesso]
    Usa frame  Usa capa
```

### Parsing Inteligente de Nomes

O sistema remove automaticamente informações técnicas do nome do arquivo:

```python
# Entrada
"The Matrix (1999) [1080p] BluRay x264-YIFY.mkv"

# Processamento
1. Remove extensão: "The Matrix (1999) [1080p] BluRay x264-YIFY"
2. Substitui separadores: "The Matrix  1999   1080p  BluRay x264 YIFY"
3. Extrai ano: 1999
4. Remove padrões técnicos: "The Matrix"

# Busca na API
GET https://api.themoviedb.org/3/search/movie?query=The+Matrix&year=1999
```

### Padrões Removidos

- **Resolução**: 1080p, 720p, 4K, UHD, 2160p
- **Source**: BluRay, WEB-DL, HDRip, DVDRip, BRRip
- **Codec**: x264, x265, HEVC, H.264, H.265, XviD
- **Audio**: AAC, AC3, DTS, Atmos, FLAC
- **Grupos**: YIFY, RARBG, YTS, ETRG, SPARKS
- **Separadores**: _, -, .
- **Colchetes/Parênteses**: [...], (...) (exceto ano)

## ✅ Vantagens vs Frame Extraction

| Aspecto | Capa Online | Frame do Vídeo |
|---------|-------------|----------------|
| **Qualidade** | ⭐⭐⭐⭐⭐ Alta (oficial) | ⭐⭐⭐ Variável |
| **Velocidade** | ⭐⭐⭐⭐ ~2-3s | ⭐⭐⭐ ~3-5s |
| **Identificação** | ⭐⭐⭐⭐⭐ Capa oficial | ⭐⭐ Depende do frame |
| **Consistência** | ⭐⭐⭐⭐⭐ Sempre igual | ⭐⭐ Aleatória |
| **Requer Internet** | ❌ Sim | ✅ Não |
| **Requer API Key** | ❌ Sim | ✅ Não |
| **Requer FFmpeg** | ✅ Não | ❌ Sim |

## 🔧 Configuração Rápida

### 1. Obter API Key (5 minutos)

1. Cadastre-se em https://www.themoviedb.org/signup
2. Acesse https://www.themoviedb.org/settings/api
3. Clique em "Create" → "Developer"
4. Copie a **API Key (v3 auth)** (32 caracteres)

### 2. Configurar no Aplicativo

Edite `config.json`:

```json
{
    "folders": ["K:/Filmoteca"],
    "tmdb_api_key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    ...
}
```

### 3. Verificar Funcionamento

Execute o aplicativo e selecione um vídeo. Você verá no log:

```
🎬 Tentando buscar capa do filme online...
🔍 Buscando: The Matrix (1999)
✓ Encontrado: The Matrix (1999)
⬇ Baixando capa...
✓ Capa baixada: (500, 750)
✓ Usando capa do filme encontrada
```

## 📊 Testes

### Rodar Testes Unitários

```bash
poetry run pytest tests/unit/test_movie_poster.py::TestMoviePosterFetcher -v
```

**Resultado esperado**: 9 testes passando

### Rodar Testes de Integração (com API key real)

```bash
poetry run pytest tests/unit/test_movie_poster.py --tmdb-api-key=YOUR_API_KEY -m integration
```

## 🔍 Exemplos de Uso

### Código Direto

```python
from src.random_file_picker.utils.movie_poster import MoviePosterFetcher

# Inicializar
fetcher = MoviePosterFetcher(api_key="sua_chave_aqui")

# Buscar capa
poster = fetcher.get_movie_poster("The Matrix (1999) 1080p.mkv")

if poster:
    poster.save("matrix_poster.jpg")
    print(f"Capa salva! Tamanho: {poster.size}")
else:
    print("Capa não encontrada")
```

### Integrado no Sistema

A funcionalidade é **totalmente automática** quando a API key está configurada:

```python
# Em archive_extractor.py
image, page_count, status = extractor.extract_first_image_from_file(video_path)

# Internamente:
# 1. Detecta que é vídeo
# 2. Tenta buscar capa (se API key configurada)
# 3. Se falhar, extrai frame do vídeo
# 4. Retorna imagem (capa ou frame)
```

## 🌍 API do TMDb

### Limites Gratuitos

- **40 requisições por 10 segundos**
- Sem limite diário para uso pessoal
- Uso normal: nunca atinge limites

### Endpoints Utilizados

1. **Busca de Filmes**
   ```
   GET https://api.themoviedb.org/3/search/movie
   Params: api_key, query, year, language=pt-BR
   ```

2. **Download de Imagem**
   ```
   GET https://image.tmdb.org/t/p/w500/{poster_path}
   Tamanho: 500px de largura (médio)
   ```

### Privacidade

- ✅ API key armazenada apenas localmente
- ✅ Apenas nome do filme é enviado
- ✅ Nenhuma informação pessoal transmitida
- ✅ Sem rastreamento de uso

## 🎨 Arquitetura do Código

```
movie_poster.py
│
├── MoviePosterFetcher (classe principal)
│   ├── __init__(api_key, log_callback)
│   ├── _clean_movie_name(filename) → (name, year)
│   ├── search_movie(name, year) → dict
│   ├── download_poster(poster_path) → Image
│   └── get_movie_poster(filename) → Image
│
└── get_poster_for_video() (função auxiliar)
```

### Isolamento da Funcionalidade

✅ **Totalmente isolado** no módulo `movie_poster.py`
✅ **Zero dependências** do resto do código (exceto PIL)
✅ **Fallback automático** se não configurado
✅ **Logging opcional** via callback
✅ **Testável** independentemente

## 📝 Notas de Implementação

### Decisões de Design

1. **Opcional por padrão**: Funciona sem API key (usa frame)
2. **Fallback automático**: Se busca falhar, extrai frame
3. **Cache não implementado**: Downloads são rápidos (~2s)
4. **Sem persistência**: Imagens são mantidas apenas em memória
5. **Prioridade português**: `language=pt-BR` nos requests

### Possíveis Melhorias Futuras

- [ ] Cache local de capas (SQLite)
- [ ] Suporte a séries de TV (TMDb TV API)
- [ ] Múltiplos idiomas configuráveis
- [ ] Seleção manual quando há múltiplos resultados
- [ ] Suporte a outros provedores (OMDb, Fanart.tv)
- [ ] Download assíncrono com preview de loading

## 🐛 Troubleshooting

### "Nenhum resultado encontrado"

**Causas**:
- Nome do arquivo muito diferente do título oficial
- Filme não está no banco de dados do TMDb
- Ano incorreto ou ausente

**Soluções**:
- Renomear arquivo com nome mais próximo do original
- Adicionar ano ao nome: `Filme (2023).mkv`
- Sistema fará fallback para frame automaticamente

### "Erro na API TMDb: 401"

**Causas**:
- API key incorreta
- API key não autorizada

**Soluções**:
- Verificar se copiou a chave completa (32 caracteres)
- Gerar nova API key no TMDb
- Confirmar que aceitou os termos de uso

### "ModuleNotFoundError: No module named 'requests'"

**Causa**: Dependência não instalada

**Solução**:
```bash
poetry install
```

## 📚 Documentação Adicional

- **Setup Completo**: `docs/TMDB_SETUP.md`
- **API TMDb**: https://developers.themoviedb.org/3
- **Termos de Uso**: https://www.themoviedb.org/documentation/api/terms-of-use

---

**Implementado em**: Janeiro 2026  
**Testado com**: Python 3.13, Poetry, TMDb API v3  
**Status**: ✅ Produção (100% funcional)
