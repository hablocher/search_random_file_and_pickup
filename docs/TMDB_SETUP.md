# Configuração da API TMDb para Capas de Filmes

O aplicativo pode buscar automaticamente capas de filmes online usando a API do **The Movie Database (TMDb)**, melhorando significativamente a qualidade das prévias visuais de vídeos.

## 🎬 O que é TMDb?

O Movie Database (TMDb) é um banco de dados comunitário de filmes e séries, similar ao IMDb, com uma API gratuita e bem documentada. Possui capas (posters) de alta qualidade para milhares de filmes.

Site oficial: https://www.themoviedb.org

## 📋 Como Funciona

Quando você seleciona um arquivo de vídeo:

1. **Primeiro**: O app tenta buscar a capa do filme online (se a API key estiver configurada)
2. **Fallback**: Se não encontrar a capa ou a API não estiver configurada, extrai um frame do vídeo

### Vantagens da Capa vs Frame

- ✅ **Qualidade**: Imagens oficiais em alta resolução
- ✅ **Velocidade**: Mais rápido que extrair frame do vídeo
- ✅ **Identificação**: Capa oficial facilita reconhecer o filme
- ✅ **Consistência**: Sempre mostra a melhor imagem do filme

## 🔑 Como Obter sua API Key (Gratuita)

### Passo 1: Criar Conta

1. Acesse: https://www.themoviedb.org/signup
2. Preencha o formulário de cadastro
3. Confirme seu email

### Passo 2: Solicitar API Key

1. Faça login em https://www.themoviedb.org
2. Clique no seu avatar (canto superior direito)
3. Vá em **Configurações** (Settings)
4. No menu lateral, clique em **API**
5. Clique em **Create` ou **Request an API Key**
6. Selecione **Developer** (não comercial)
7. Aceite os termos de uso
8. Preencha o formulário:
   - **Type of Use**: Personal
   - **Application Name**: Random File Picker (ou qualquer nome)
   - **Application URL**: Pode deixar vazio ou usar https://github.com/
   - **Application Summary**: Descrição breve (ex: "Personal file organizer")
9. Clique em **Submit**

Você receberá duas chaves:
- **API Key (v3 auth)** ← Use esta! (32 caracteres alfanuméricos)
- **API Read Access Token** (não usar)

### Passo 3: Configurar no Aplicativo

Abra o arquivo `config.json` na raiz do projeto e adicione sua chave:

```json
{
    "folders": ["K:/Filmoteca"],
    "tmdb_api_key": "sua_chave_de_32_caracteres_aqui",
    ...
}
```

**Exemplo**:
```json
{
    "folders": ["K:/Filmoteca"],
    "tmdb_api_key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    ...
}
```

Salve o arquivo e reinicie o aplicativo.

## ✅ Como Verificar se Está Funcionando

Após configurar:

1. Execute o aplicativo
2. Selecione um arquivo de vídeo
3. No log, você verá mensagens como:
   ```
   🎬 Tentando buscar capa do filme online...
   🔍 Buscando: The Matrix (1999)
   ✓ Encontrado: The Matrix (1999)
   ⬇ Baixando capa...
   ✓ Capa baixada: (500, 750)
   ✓ Usando capa do filme encontrada
   ```

Se a API key não estiver configurada ou a capa não for encontrada, o log mostrará:
```
⚠ Capa não encontrada, extraindo frame do vídeo...
```

## 🎯 Formatos de Nome Suportados

O aplicativo é inteligente e remove automaticamente informações técnicas do nome do arquivo para melhorar a busca:

### ✅ Funciona Bem

```
The Matrix (1999).mkv
Avatar.2009.1080p.BluRay.x264.mp4
Inception [2010] 720p WEB-DL.avi
Interstellar.2014.4K.UHD.HEVC-YIFY.mkv
```

### ❌ Pode Não Funcionar

```
film123.mp4                    # Sem nome reconhecível
meu_video_legal.avi            # Nome genérico
The.Matrix.Resurrections.mp4   # Sem ano (pode buscar filme errado)
```

**Dica**: Para melhores resultados, inclua o ano no nome do arquivo.

## 🔧 Solução de Problemas

### "API key não configurada"

- Verifique se adicionou a chave no `config.json`
- Certifique-se de que a chave está entre aspas
- Confirme que salvou o arquivo
- Reinicie o aplicativo

### "Nenhum resultado encontrado"

- Verifique se o nome do arquivo é reconhecível
- Adicione o ano ao nome do arquivo: `Filme (2023).mp4`
- Tente renomear o arquivo para um nome mais próximo do título oficial
- Alguns filmes podem não estar no banco de dados do TMDb

### "Erro na API TMDb"

- Verifique sua conexão com a internet
- Confirme que a API key está correta (32 caracteres)
- Verifique se sua conta TMDb está ativa
- Aguarde alguns minutos e tente novamente

### API Key Inválida

Se você ver "Erro na API TMDb: 401":
- Sua API key está incorreta ou expirou
- Gere uma nova chave seguindo os passos acima
- Verifique se copiou a chave completa (32 caracteres)

## 📊 Limites da API Gratuita

A API gratuita do TMDb tem os seguintes limites:

- **40 requisições por 10 segundos**
- **Sem limite diário para uso pessoal**

Para uso normal do aplicativo (selecionar alguns filmes por vez), você nunca atingirá esses limites.

## 🔒 Privacidade

- A API key é armazenada apenas localmente no seu `config.json`
- Nenhuma informação pessoal é enviada ao TMDb
- Apenas o nome do filme é enviado para busca
- Não rastreamos ou armazenamos suas buscas

## 🌐 Alternativas

Se você preferir **não usar** a API do TMDb:

1. Deixe o campo `tmdb_api_key` vazio no `config.json`
2. O aplicativo continuará funcionando normalmente
3. Frames serão extraídos dos vídeos (método anterior)

## 📚 Recursos Adicionais

- **Documentação da API**: https://developers.themoviedb.org/3
- **Status da API**: https://status.themoviedb.org/
- **Fórum de Suporte**: https://www.themoviedb.org/talk
- **Política de Uso**: https://www.themoviedb.org/documentation/api/terms-of-use

## 🆘 Suporte

Se encontrar problemas:

1. Verifique o log do aplicativo para mensagens de erro detalhadas
2. Confirme que seguiu todos os passos de configuração
3. Teste com um arquivo de vídeo com nome claro (ex: "The Matrix 1999.mp4")
4. Verifique sua conexão com a internet

---

**Nota**: A funcionalidade de busca de capas é **opcional**. O aplicativo funciona perfeitamente sem ela, extraindo frames dos vídeos como fallback.
