"""
Teste para reproduzir o bug no modo aleatório:
Quando um arquivo aleatório é selecionado e faz parte de uma sequência,
deve detectar e selecionar o primeiro não lido, não o arquivo aleatório.
"""
import os
import tempfile
import shutil
from pathlib import Path
from sequential_selector import (
    analyze_folder_sequence, 
    get_next_unread_file,
    SequentialFileTracker
)
from random_file_picker import pick_random_file


def test_random_mode_sequence_detection():
    """
    Reproduz o cenário: modo aleatório seleciona Volume 02,
    mas deveria detectar a sequência e selecionar Volume 01.
    """
    temp_dir = tempfile.mkdtemp(prefix="test_random_")
    
    try:
        # Cria arquivos de teste
        files = [
            "A Floresta - Volume 01.cbz",
            "A Floresta - Volume 02.cbz",
            "A Floresta - Volume 03.cbz",
        ]
        
        for file in files:
            file_path = Path(temp_dir) / file
            file_path.touch()
        
        print("=" * 80)
        print("TESTE: Detecção de Sequência no Modo Aleatório")
        print("=" * 80)
        print(f"Diretório de teste: {temp_dir}")
        print(f"Arquivos criados: {files}")
        
        # Simula o que acontece no modo aleatório da GUI
        print("\n--- PASSO 1: Seleção Aleatória ---")
        # Forçar seleção do Volume 02 (simula o "azar" do aleatório)
        selected_file = str(Path(temp_dir) / "A Floresta - Volume 02.cbz")
        print(f"Arquivo aleatório selecionado: {Path(selected_file).name}")
        
        print("\n--- PASSO 2: Detectar Sequência na Pasta ---")
        file_folder = Path(selected_file).parent
        sequences = analyze_folder_sequence(file_folder, exclude_prefix="_L_", keywords=None)
        
        if sequences:
            print(f"✓ Sequência detectada!")
            print(f"  Coleção: {sequences[0]['collection']}")
            print(f"  Total de arquivos: {sequences[0]['count']}")
            
            print("\n--- PASSO 3: Buscar Próximo Não Lido ---")
            tracker = SequentialFileTracker()
            result = get_next_unread_file(sequences, tracker, keywords=None)
            
            if result:
                next_file, selected_sequence, file_info = result
                actual = Path(next_file).name
                expected = "A Floresta - Volume 01.cbz"
                
                print(f"Arquivo substituído por: {actual}")
                print(f"Número: {file_info['number']}")
                
                if actual == expected:
                    print(f"\n✅ TESTE PASSOU: Volume 01 foi selecionado corretamente")
                    return True
                else:
                    print(f"\n❌ TESTE FALHOU!")
                    print(f"   Esperado: {expected}")
                    print(f"   Obtido: {actual}")
                    return False
            else:
                print("❌ Nenhum arquivo não lido encontrado")
                return False
        else:
            print("❌ Nenhuma sequência detectada")
            return False
            
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_random_with_complex_names():
    """
    Testa com nomes mais complexos que podem ter padrões confusos
    """
    temp_dir = tempfile.mkdtemp(prefix="test_complex_")
    
    try:
        # Nomes mais complexos
        files = [
            "A Floresta - Volume 01 - Capitulo 01.cbz",
            "A Floresta - Volume 02 - Capitulo 05.cbz",
            "A Floresta - Volume 03 - Final.cbz",
        ]
        
        for file in files:
            file_path = Path(temp_dir) / file
            file_path.touch()
        
        print("\n" + "=" * 80)
        print("TESTE: Nomes Complexos com Múltiplos Números")
        print("=" * 80)
        print(f"Arquivos: {files}")
        
        # Analisa sequências
        sequences = analyze_folder_sequence(Path(temp_dir), exclude_prefix="_L_", keywords=None)
        
        print(f"\nSequências detectadas: {len(sequences)}")
        for seq in sequences:
            print(f"  Tipo: {seq['type']}")
            print(f"  Arquivos: {[f['filename'] for f in seq['files']]}")
        
        if sequences:
            tracker = SequentialFileTracker()
            result = get_next_unread_file(sequences, tracker, keywords=None)
            
            if result:
                next_file, _, file_info = result
                actual = Path(next_file).name
                print(f"\nPrimeiro não lido: {actual}")
                
                # Deve selecionar Volume 01
                if "Volume 01" in actual:
                    print("✅ TESTE PASSOU: Volume 01 selecionado")
                    return True
                else:
                    print(f"❌ TESTE FALHOU: {actual} foi selecionado")
                    return False
            else:
                print("❌ Nenhum arquivo encontrado")
                return False
        else:
            print("❌ Nenhuma sequência detectada")
            return False
            
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_mixed_sequences():
    """
    Testa pasta com múltiplas séries misturadas
    """
    temp_dir = tempfile.mkdtemp(prefix="test_mixed_")
    
    try:
        files = [
            "A Floresta - Volume 01.cbz",
            "A Floresta - Volume 02.cbz",
            "Batman - Issue 001.cbz",
            "Batman - Issue 002.cbz",
            "Superman - Cap 1.cbz",
            "Superman - Cap 2.cbz",
        ]
        
        for file in files:
            file_path = Path(temp_dir) / file
            file_path.touch()
        
        print("\n" + "=" * 80)
        print("TESTE: Múltiplas Séries na Mesma Pasta")
        print("=" * 80)
        
        sequences = analyze_folder_sequence(Path(temp_dir), exclude_prefix="_L_", keywords=None)
        
        print(f"Sequências detectadas: {len(sequences)}")
        for i, seq in enumerate(sequences):
            print(f"\nSérie {i+1}: {seq['collection']}")
            print(f"  Tipo: {seq['type']}")
            print(f"  Arquivos: {seq['count']}")
        
        if len(sequences) == 3:
            print("\n✅ TESTE PASSOU: 3 sequências detectadas corretamente")
            return True
        else:
            print(f"\n❌ TESTE FALHOU: Esperado 3 sequências, encontrado {len(sequences)}")
            return False
            
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TESTES DE BUG NO MODO ALEATÓRIO")
    print("=" * 80)
    
    test1 = test_random_mode_sequence_detection()
    test2 = test_random_with_complex_names()
    test3 = test_mixed_sequences()
    
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    print(f"Teste 1 (Detecção Random): {'✅ PASSOU' if test1 else '❌ FALHOU'}")
    print(f"Teste 2 (Nomes Complexos): {'✅ PASSOU' if test2 else '❌ FALHOU'}")
    print(f"Teste 3 (Séries Mistas): {'✅ PASSOU' if test3 else '❌ FALHOU'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
