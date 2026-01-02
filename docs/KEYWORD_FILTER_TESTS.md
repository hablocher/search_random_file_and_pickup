# Teste de Validação - Filtro de Keywords AND/OR

## 🎯 Objetivo
Validar que o filtro de keywords está funcionando corretamente nos modos AND e OR.

## 📝 Cenários de Teste

### Teste 1: Modo OR (Padrão)
**Comportamento esperado**: Encontra arquivos que contenham **PELO MENOS UMA** das palavras-chave.

**Exemplo com `john, wick`**:
- ✅ Deve encontrar: "John Wick Chapter 1.mkv"
- ✅ Deve encontrar: "John Rambo.mkv" (tem "john")
- ✅ Deve encontrar: "Keanu Wick.mkv" (tem "wick")
- ❌ NÃO deve encontrar: "Matrix.mkv" (não tem nenhuma)

**Passos**:
1. Digite as palavras-chave: `john, wick`
2. **Desmarque** o checkbox "TODAS as palavras (AND)"
3. Clique em "Buscar Arquivo Aleatório"
4. Verifique se o arquivo retornado contém "john" OU "wick" no nome

### Teste 2: Modo AND
**Comportamento esperado**: Encontra arquivos que contenham **TODAS** as palavras-chave.

**Exemplo com `john, wick`**:
- ✅ Deve encontrar: "John Wick Chapter 1.mkv"
- ✅ Deve encontrar: "John.Wick.2014.mkv"
- ❌ NÃO deve encontrar: "John Rambo.mkv" (falta "wick")
- ❌ NÃO deve encontrar: "Keanu Wick.mkv" (falta "john")
- ❌ NÃO deve encontrar: "Matrix.mkv" (falta ambas)

**Passos**:
1. Digite as palavras-chave: `john, wick`
2. **Marque** o checkbox "TODAS as palavras (AND)"
3. Clique em "Buscar Arquivo Aleatório"
4. Verifique se o arquivo retornado contém "john" E "wick" no nome

### Teste 3: Três Keywords - OR
**Exemplo com `batman, superman, wonder`**:
- ✅ Deve encontrar: "Batman vs Superman.mkv" (tem 2)
- ✅ Deve encontrar: "Batman Begins.mkv" (tem 1)
- ✅ Deve encontrar: "Wonder Woman.mkv" (tem 1)
- ❌ NÃO deve encontrar: "Aquaman.mkv" (não tem nenhuma)

### Teste 4: Três Keywords - AND
**Exemplo com `batman, vs, superman`**:
- ✅ Deve encontrar: "Batman vs Superman.mkv"
- ❌ NÃO deve encontrar: "Batman Begins.mkv" (falta "vs" e "superman")
- ❌ NÃO deve encontrar: "Superman Returns.mkv" (falta "batman" e "vs")

### Teste 5: Case-Insensitive
**Comportamento esperado**: Deve funcionar independente de maiúsculas/minúsculas.

**Exemplo com `JOHN, WICK`** (maiúsculas):
- ✅ Deve encontrar: "john wick.mkv" (minúsculas)
- ✅ Deve encontrar: "John Wick.mkv" (capitalized)
- ✅ Deve encontrar: "JOHN WICK.mkv" (maiúsculas)

### Teste 6: Substring Match
**Comportamento esperado**: Aceita correspondência parcial.

**Exemplo com `bat, man`** (AND):
- ✅ Deve encontrar: "Batman.mkv" (contém ambas as substrings)
- ✅ Deve encontrar: "Batman vs Superman.mkv" (contém ambas)

**Exemplo com `2024`**:
- ✅ Deve encontrar: "Movie 2024.mkv"
- ✅ Deve encontrar: "Film.2024.1080p.mkv"

### Teste 7: Arquivos dentro de ZIP/RAR
**Comportamento esperado**: Mesma lógica deve funcionar dentro de arquivos compactados.

**Com processamento de ZIP ativado**:
- Se o arquivo compactado se chama "John Wick Collection.cbr"
- E dentro tem "Chapter 01.jpg", "Chapter 02.jpg"
- Buscar `john, wick` (OR) → deve encontrar o arquivo compactado
- Buscar `john, wick, collection` (AND) → deve encontrar o arquivo compactado

## ✅ Checklist de Validação

Marque cada item após testar:

**Modo OR**:
- [ ] Encontra arquivos com apenas uma keyword
- [ ] Encontra arquivos com todas as keywords
- [ ] NÃO encontra arquivos sem nenhuma keyword

**Modo AND**:
- [ ] Encontra APENAS arquivos com todas as keywords
- [ ] NÃO encontra arquivos com apenas uma keyword
- [ ] NÃO encontra arquivos sem nenhuma keyword

**Recursos Gerais**:
- [ ] Case-insensitive funciona
- [ ] Substring match funciona
- [ ] Funciona dentro de arquivos ZIP/RAR
- [ ] Cache mantém filtro funcionando
- [ ] Índice de keywords acelera busca

## 🐛 Problemas Conhecidos (Corrigidos)

### ❌ BUG ANTERIOR:
```
Busca: "john, wick" (AND)
Esperado: Apenas arquivos com ambas as palavras
Resultado: Retornava arquivos com apenas "john"
```

### ✅ CORREÇÃO:
- Adicionada conversão `.lower()` consistente em todas as comparações
- Validação de lógica AND/OR em testes unitários
- 5 testes criados, todos passando

## 📊 Logs para Debug

Se ainda encontrar problemas, verifique:

1. **Console da aplicação**: Mostra quantos arquivos foram encontrados
2. **Cache info**: "Índice: X palavras indexadas"
3. **Teste unitário**: `poetry run python tests/unit/test_keyword_filtering.py`

## 🔧 Como Reportar Problemas

Se encontrar um comportamento incorreto:

1. Anote as keywords usadas
2. Anote se AND ou OR estava ativado
3. Anote o nome do arquivo retornado
4. Verifique manualmente se o nome contém as keywords
5. Reporte com essas informações

---

**Status**: ✅ Corrigido e testado
**Data**: 2026-01-02
