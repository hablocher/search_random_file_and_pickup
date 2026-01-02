# Análise de Sequência em Arquivos ZIP - Documentação

## Resumo das Mudanças

A lógica de busca de sequência agora funciona também para arquivos extraídos de ZIPs, aplicando a análise de sequência aos arquivos dentro de arquivos compactados.

## Como Funciona

### Exemplo 1: Sequência Detectada
```
ZIP: "colecao.cbr" contém:
  - _L_teste 001.cbr  (já lido - prefixo _L_)
  - teste 002.cbr
  - teste 003.cbr
  - teste 004.cbr

PROCESSO:
1. ZIP é selecionado aleatoriamente
2. TODO o conteúdo é extraído para pasta temporária
3. Análise de sequência é aplicada aos arquivos extraídos
4. Sequência detectada: "teste" (001-004)
5. Primeiro arquivo não lido é selecionado: "teste 002.cbr"

RESULTADO: "teste 002.cbr" é retornado
```

### Exemplo 2: Arquivo Isolado
```
ZIP: "arquivo.cbz" contém:
  - arquivo_normal.cbr

PROCESSO:
1. ZIP é selecionado aleatoriamente
2. TODO o conteúdo é extraído
3. Análise de sequência é aplicada
4. Nenhuma sequência detectada (apenas 1 arquivo)
5. Arquivo é selecionado: "arquivo_normal.cbr"

RESULTADO: "arquivo_normal.cbr" é retornado
```

### Exemplo 3: Múltiplas Sequências
```
ZIP: "grande_colecao.cbz" contém:
  - Serie A 01.cbr
  - Serie A 02.cbr
  - Serie A 03.cbr
  - Serie B 01.cbr
  - Serie B 02.cbr

PROCESSO:
1. ZIP é extraído
2. Análise detecta 2 sequências: "Serie A" e "Serie B"
3. Uma sequência é escolhida aleatoriamente
4. Primeiro arquivo não lido da sequência escolhida é selecionado

RESULTADO: Por exemplo, "Serie A 01.cbr" ou "Serie B 01.cbr"
```

## Mudanças no Código

### Arquivo: `file_picker.py`

**Função modificada:** `pick_random_file_with_zip_support()`

**O que mudou:**
- Após extrair o ZIP, agora aplica `analyze_folder_sequence()` na pasta temporária
- Se sequências são detectadas, usa `get_next_unread_file()` para selecionar o próximo não lido
- Se não há sequências, continua com seleção aleatória (comportamento anterior)

**Código adicionado:**
```python
# Analisa se há sequências dentro do ZIP extraído
sequences = analyze_folder_sequence(
    Path(temp_dir), 
    exclude_prefix, 
    keywords, 
    keywords_match_all, 
    ignored_extensions
)

file_from_sequence = None

if sequences:
    # Há sequências detectadas dentro do ZIP
    print(f"✓ Sequência detectada dentro do ZIP!")
    tracker = SequentialFileTracker()
    seq_result = get_next_unread_file(sequences, tracker, keywords, keywords_match_all)
    
    if seq_result:
        next_file, selected_sequence, file_info = seq_result
        file_from_sequence = next_file
        tracker.mark_as_read(next_file)

if not file_from_sequence:
    # Sem sequência - seleção aleatória
    result = pick_random_file_with_zip_support(...)
else:
    # Com sequência - usa arquivo selecionado
    result = {'file_path': file_from_sequence, ...}
```

## Comportamento em Diferentes Modos

### Modo Aleatório (`use_sequence=False`)
- Ao selecionar um ZIP aleatoriamente
- ZIP é extraído completamente
- **NOVO:** Análise de sequência é aplicada aos arquivos extraídos
- Se houver sequência, retorna o primeiro não lido
- Se não houver sequência, retorna arquivo aleatório

### Modo Sequencial (`use_sequence=True`)
- Já funcionava corretamente (código em `sequential_selector.py`)
- Detecta sequências nas pastas configuradas
- Se um ZIP fizer parte de uma sequência, é processado
- Dentro do ZIP, também aplica análise de sequência

## Recursão em ZIPs Aninhados

A análise de sequência funciona até 3 níveis de profundidade:

```
Nível 1: pasta/arquivo.zip
  Nível 2: arquivo.zip contém outro_arquivo.rar
    Nível 3: outro_arquivo.rar contém final.cbr
```

Em cada nível, a análise de sequência é aplicada.

## Palavras-Chave Aumentadas

O limite de palavras-chave foi aumentado de 3 para 5:
- Interface: "Palavras-chave (máx. 5, separadas por vírgula):"
- Método `get_keywords_list()`: retorna `keywords[:5]`

## Logs Exibidos

Quando sequência é detectada em ZIP:
```
✓ ZIP extraído completamente
Iniciando busca recursiva dentro do ZIP (aplicando todas as regras)...
✓ Sequência detectada dentro do ZIP!
Selecionando próximo arquivo não lido: 'teste 002.cbr'
  Coleção: teste
  Tipo de ordenação: decimal
  Total de arquivos na sequência: 4
  Número do arquivo: 2.0
```

Quando não há sequência:
```
✓ ZIP extraído completamente
Iniciando busca recursiva dentro do ZIP (aplicando todas as regras)...
Nenhuma sequência detectada - seleção aleatória dentro do ZIP
```

## Compatibilidade

- ✅ ZIP (.zip, .cbz)
- ✅ RAR (.rar, .cbr) - requer biblioteca `rarfile`
- ✅ ZIPs aninhados (até 3 níveis)
- ✅ Todas as regras de filtragem (keywords, extensões, prefixo)
- ✅ Cache de arquivos

## Teste

Execute o script de teste:
```bash
python test_zip_sequence.py
```

Ou teste diretamente na GUI:
1. Configure uma pasta que contém ZIPs
2. Habilite "Processar arquivos ZIP"
3. Execute a busca
4. Observe os logs para ver se sequências foram detectadas
