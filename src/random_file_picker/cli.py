"""CLI entry point for random file picker."""

import argparse
import sys
from pathlib import Path
from random_file_picker.core.file_picker import pick_random_file, open_folder
from random_file_picker.core.sequential_selector import select_file_with_sequence_logic


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Random File Picker - Seleção inteligente de arquivos"
    )
    parser.add_argument(
        "folders",
        nargs="+",
        help="Pasta(s) para buscar arquivos",
    )
    parser.add_argument(
        "--exclude-prefix",
        default="_L_",
        help="Prefixo de arquivos a ignorar (padrão: _L_)",
    )
    parser.add_argument(
        "--keywords",
        nargs="*",
        help="Palavras-chave para filtrar arquivos",
    )
    parser.add_argument(
        "--no-sequence",
        action="store_true",
        help="Desativa seleção sequencial",
    )
    parser.add_argument(
        "--open-folder",
        action="store_true",
        help="Abre a pasta do arquivo selecionado",
    )
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="Não processa arquivos ZIP",
    )
    
    args = parser.parse_args()
    
    # Converte keywords para lista
    keywords = [kw.lower() for kw in args.keywords] if args.keywords else None
    
    # Valida pastas
    for folder in args.folders:
        if not Path(folder).exists():
            print(f"Erro: Pasta não encontrada: {folder}", file=sys.stderr)
            sys.exit(1)
    
    print("=" * 70)
    print("RANDOM FILE PICKER")
    print("=" * 70)
    print(f"\nPastas: {len(args.folders)}")
    print(f"Prefixo de exclusão: {args.exclude_prefix}")
    print(f"Seleção sequencial: {'Não' if args.no_sequence else 'Sim'}")
    print(f"Processar ZIP: {'Não' if args.no_zip else 'Sim'}")
    
    if keywords:
        print(f"Palavras-chave: {', '.join(keywords)}")
    
    print("\nBuscando...\n")
    
    try:
        if args.no_sequence:
            # Modo aleatório
            from random_file_picker.core.file_picker import pick_random_file_with_zip_support
            result = pick_random_file_with_zip_support(
                args.folders,
                args.exclude_prefix,
                keywords=keywords,
                process_zip=not args.no_zip,
            )
            selected_file = result['file_path']
            
            if result['is_from_zip']:
                print(f"✓ Arquivo extraído de ZIP:")
                print(f"  ZIP: {result['zip_path']}")
                print(f"  Arquivo: {result['file_in_zip']}")
        else:
            # Modo sequencial
            result, info = select_file_with_sequence_logic(
                args.folders,
                args.exclude_prefix,
                use_sequence=True,
                keywords=keywords,
                process_zip=not args.no_zip,
            )
            
            if not result or not result['file_path']:
                raise ValueError("Nenhum arquivo encontrado")
            
            selected_file = result['file_path']
            
            if result['is_from_zip']:
                print(f"✓ Arquivo extraído de ZIP:")
                print(f"  ZIP: {result['zip_path']}")
                print(f"  Arquivo: {result['file_in_zip']}")
            
            if info['sequence_detected']:
                print(f"✓ Sequência detectada!")
                print(f"  Método: Sequencial")
                print(f"  Coleção: {info['sequence_info']['collection']}")
        
        print(f"\n{'='*70}")
        print("Arquivo selecionado:")
        print(f"  {selected_file}")
        print(f"{'='*70}\n")
        
        if args.open_folder:
            folder_to_open = result.get('zip_path', selected_file) if result.get('is_from_zip') else selected_file
            open_folder(folder_to_open)
            print("Pasta aberta no explorador.")
        
    except ValueError as e:
        print(f"\nErro: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro inesperado: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
