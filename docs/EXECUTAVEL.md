# 🚀 Como Usar o Media Finder (Executável)

## Após o Build

1. **Localização do Executável**
   - O arquivo estará em: `dist/MediaFinder.exe`
   - Tamanho aproximado: 50-80 MB

2. **Executando pela Primeira Vez**
   - Duplo clique em `MediaFinder.exe`
   - Não precisa instalar Python ou dependências
   - O programa criará automaticamente:
     - `config.json` (suas configurações)
     - `read_files_tracker.json` (cache de arquivos)

3. **Distribuindo para Outros Computadores**
   - Copie apenas o arquivo `MediaFinder.exe`
   - Funciona em qualquer Windows 10/11
   - Não precisa instalar nada adicional

## Antivírus

Alguns antivírus podem alertar sobre executáveis criados com PyInstaller. Isso é um **falso positivo** comum. Motivos:
- PyInstaller empacota Python inteiro no executável
- Executáveis auto-extraíveis são frequentemente sinalizados
- É seguro adicionar à lista de exceções

## Configuração

Ao executar pela primeira vez:
1. Clique no botão ⚙️ (engrenagem) para configurar
2. Adicione as pastas que deseja pesquisar
3. Configure prefixos, palavras-chave, etc
4. Clique em "Salvar e Fechar"

## Recursos

✅ Seleção sequencial e aleatória de arquivos
✅ Suporte a ZIP/RAR
✅ Preview de vídeos e imagens
✅ Histórico de arquivos
✅ Cache para buscas rápidas
✅ Filtros por palavras-chave
✅ Integração com OneDrive/Cloud

## Problemas Comuns

**"Windows protegeu seu PC"**
- Clique em "Mais informações" → "Executar assim mesmo"
- Isso acontece porque o executável não tem assinatura digital

**Demora na primeira execução**
- Normal! O executável se descompacta na primeira vez
- Execuções seguintes serão mais rápidas

**Erro ao carregar assets**
- Os assets (roulette.png, spinning.gif) estão embutidos
- Se houver erro, recompile com `build_exe.bat`

## Desenvolvedor

Para recompilar o executável:
```batch
build_exe.bat
```

O executável será recriado em `dist/MediaFinder.exe`
