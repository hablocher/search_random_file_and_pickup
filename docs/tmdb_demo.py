"""
Exemplo demonstrando as melhorias do TMDb.

Este script mostra como a busca inteligente funciona na prática.
"""

from random_file_picker.utils.movie_poster import MoviePosterFetcher


def demo_clean_names():
    """Demonstra a limpeza de nomes de arquivos."""
    print("=" * 70)
    print("DEMO 1: LIMPEZA DE NOMES DE ARQUIVOS")
    print("=" * 70)
    
    fetcher = MoviePosterFetcher()
    
    test_files = [
        "O Poderoso Chefão (1972) Dual Audio 1080p BluRay.mkv",
        "Cidade de Deus 2002 Dublado Nacional.mp4",
        "Matrix.1999.4K.HDR10.HEVC.x265-RARBG.mkv",
        "Inception 2010 IMAX 1080p DDP5.1 Atmos x265.mp4",
        "Interstellar.2014.2160p.WEB-DL.DDP5.1.Atmos.mkv",
        "Avatar.2009.3D.BluRay.1080p.x264.DTS-HD.mkv",
        "Tropa de Elite (2007) Nacional PTBR 720p.avi",
    ]
    
    print("\nArquivo Original → Nome Limpo (Ano)\n")
    for filename in test_files:
        name, year = fetcher._clean_movie_name(filename)
        year_str = f"({year})" if year else "(sem ano)"
        print(f"✓ {filename}")
        print(f"  → {name} {year_str}\n")


def demo_relevance_scoring():
    """Demonstra o cálculo de score de relevância."""
    print("\n" + "=" * 70)
    print("DEMO 2: SISTEMA DE SCORE DE RELEVÂNCIA")
    print("=" * 70)
    
    fetcher = MoviePosterFetcher()
    
    # Simula resultados de busca para "Matrix"
    movies = [
        {
            'title': 'Matrix',
            'original_title': 'The Matrix',
            'popularity': 50.0,
            'release_date': '1999-03-31',
            'vote_average': 8.7,
            'vote_count': 20000
        },
        {
            'title': 'Matrix Reloaded',
            'original_title': 'The Matrix Reloaded',
            'popularity': 40.0,
            'release_date': '2003-05-15',
            'vote_average': 7.2,
            'vote_count': 15000
        },
        {
            'title': 'Matrix Revolutions',
            'original_title': 'The Matrix Revolutions',
            'popularity': 35.0,
            'release_date': '2003-11-05',
            'vote_average': 6.8,
            'vote_count': 14000
        },
    ]
    
    query = "Matrix"
    year = 1999
    
    print(f"\nBusca: '{query}' ({year})")
    print("\nResultados ordenados por relevância:\n")
    
    scored = []
    for movie in movies:
        score = fetcher._calculate_relevance_score(movie, query, year)
        scored.append((score, movie))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    
    for rank, (score, movie) in enumerate(scored, 1):
        title = movie['title']
        orig = movie['original_title']
        pop = movie['popularity']
        year_release = movie['release_date'][:4]
        rating = movie['vote_average']
        
        print(f"{rank}. {title} ({year_release})")
        print(f"   Original: {orig}")
        print(f"   Score: {score:.1f} pontos")
        print(f"   Popularidade: {pop} | Avaliação: {rating}/10")
        
        # Explica o score
        components = []
        
        # Popularidade
        pop_score = min(pop / 2, 50)
        components.append(f"Popularidade: +{pop_score:.1f}")
        
        # Match
        if query.lower() == title.lower() or query.lower() == orig.lower():
            components.append("Match exato: +100.0")
        elif query.lower() in title.lower() or query.lower() in orig.lower():
            components.append("Match parcial: +50.0")
        
        # Ano
        if year and str(year) in year_release:
            components.append("Ano correto: +30.0")
        
        # Rating
        if movie['vote_count'] > 100:
            rating_score = rating * 2
            components.append(f"Avaliação: +{rating_score:.1f}")
        
        print(f"   Componentes: {' | '.join(components)}")
        print()


def demo_bilingual_search():
    """Demonstra a busca bilíngue (requer API key)."""
    print("\n" + "=" * 70)
    print("DEMO 3: BUSCA BILÍNGUE")
    print("=" * 70)
    
    print("\nℹ Este demo requer uma API key do TMDb.")
    print("Configure em config.json: \"tmdb_api_key\": \"sua_chave\"")
    print("\nComo funciona:")
    print("1. Busca em português (pt-BR)")
    print("2. Busca em inglês (en-US)")
    print("3. Combina resultados (remove duplicatas)")
    print("4. Calcula score de relevância")
    print("5. Seleciona o melhor resultado")
    
    print("\nExemplos de buscas que se beneficiam:")
    examples = [
        ("Cidade de Deus", "Encontra 'City of God' (título original em inglês)"),
        ("Matrix", "Encontra 'The Matrix' (título em inglês e português)"),
        ("Tropa de Elite", "Encontra versões pt-BR e título internacional"),
        ("Avatar", "Encontra tanto o filme de 2009 quanto outros 'Avatar'"),
    ]
    
    print()
    for query, explanation in examples:
        print(f"✓ '{query}'")
        print(f"  → {explanation}\n")


def main():
    """Executa todas as demonstrações."""
    print("\n" + "🎬" * 35)
    print("DEMONSTRAÇÃO: MELHORIAS DO TMDb")
    print("🎬" * 35 + "\n")
    
    demo_clean_names()
    demo_relevance_scoring()
    demo_bilingual_search()
    
    print("\n" + "=" * 70)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA")
    print("=" * 70)
    print("\nPara mais informações, veja:")
    print("- docs/TMDB_IMPROVEMENTS.md - Documentação completa")
    print("- tests/unit/test_tmdb_improvements.py - Testes automatizados")
    print("\nPara usar com API real:")
    print("1. Obtenha API key: https://www.themoviedb.org/settings/api")
    print("2. Configure em config.json")
    print("3. Execute a aplicação GUI: poetry run rfp-gui")
    print()


if __name__ == '__main__':
    main()
