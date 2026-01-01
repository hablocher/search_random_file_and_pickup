"""
Teste final para verificar a correção do bug:
No modo sequencial, quando cai no fallback aleatório, deve verificar se 
o arquivo aleatório faz parte de uma sequência.
"""
import os
import tempfile
import shutil
from pathlib import Path
from sequential_selector import (
    select_file_with_sequence_logic,
    SequentialFileTracker
)


def test_sequential_mode_fallback_to_random():
    """
    Testa o cenário exato do bug:
    - Modo sequencial está ATIVADO
    - Programa não encontra sequências não lidas nas iterações iniciais
    - Cai no fallback aleatório
    - Arquivo aleatório é 'Volume 02'
    - MAS existe 'Volume 01' sem prefixo na mesma pasta
    - Deve detectar e selecionar 'Volume 01'
    """
    temp_base = tempfile.mkdtemp(prefix="test_bug_fix_")
    
    try:
        # Cria duas pastas
        folder1 = Path(temp_base) / "Series1"
        folder2 = Path(temp_base) / "Series2_Com_Floresta"
        folder1.mkdir()
        folder2.mkdir()
        
        # Folder 1: Série completamente lida
        files_folder1 = [
            "_L_Batman - Issue 001.cbz",
            "_L_Batman - Issue 002.cbz",
            "_L_Batman - Issue 003.cbz",
        ]
        
        for file in files_folder1:
            (folder1 / file).touch()
        
        # Folder 2: A Floresta - aqui está o bug!
        files_folder2 = [
            "A Floresta - Volume 01.cbz",  # SEM PREFIXO!
            "A Floresta - Volume 02.cbz",
            "A Floresta - Volume 03.cbz",
        ]
        
        for file in files_folder2:
            (folder2 / file).touch()
        
        print("=" * 80)
        print("TESTE CORREÇÃO DO BUG - Fallback Aleatório no Modo Sequencial")
        print("=" * 80)
        print(f"\nPasta 1 (todos lidos): {folder1.name}")
        for f in files_folder1:
            print(f"  - {f}")
        
        print(f"\nPasta 2 (nenhum lido): {folder2.name}")
        for f in files_folder2:
            print(f"  - {f}")
        
        # Marca toda a série 1 como lida
        tracker = SequentialFileTracker()
        for file in files_folder1:
            tracker.mark_as_read(str(folder1 / file))
        
        print("\n--- Executando Seleção Sequencial ---")
        folders = [str(folder1), str(folder2)]
        
        # Executa a seleção sequencial
        file_result, selection_info = select_file_with_sequence_logic(
            folders, 
            exclude_prefix="_L_", 
            use_sequence=True, 
            keywords=None,
            process_zip=False
        )
        
        if file_result and file_result['file_path']:
            selected_file = Path(file_result['file_path']).name
            print(f"\nArquivo selecionado: {selected_file}")
            print(f"Método: {selection_info['method']}")
            print(f"Sequência detectada: {selection_info['sequence_detected']}")
            
            if selection_info['sequence_detected']:
                print(f"Coleção: {selection_info['sequence_info']['collection']}")
                print(f"Número: {selection_info['sequence_info']['file_number']}")
            
            expected = "A Floresta - Volume 01.cbz"
            
            if selected_file == expected:
                print(f"\n✅ TESTE PASSOU!")
                print(f"   Correção funcionou: {selected_file} foi selecionado")
                print(f"   Mesmo quando caiu no fallback aleatório")
                return True
            else:
                print(f"\n❌ TESTE FALHOU!")
                print(f"   Esperado: {expected}")
                print(f"   Obtido: {selected_file}")
                print(f"   BUG AINDA PRESENTE!")
                return False
        else:
            print("\n❌ TESTE FALHOU: Nenhum arquivo foi selecionado")
            return False
            
    finally:
        shutil.rmtree(temp_base, ignore_errors=True)


def test_multiple_folders_with_sequences():
    """
    Testa com múltiplas pastas onde algumas têm sequências
    """
    temp_base = tempfile.mkdtemp(prefix="test_multi_")
    
    try:
        folders = []
        
        # Pasta 1: Sequência completa e lida
        f1 = Path(temp_base) / "Completa"
        f1.mkdir()
        for i in range(1, 4):
            (f1 / f"_L_Serie A - Vol {i:02d}.cbz").touch()
        folders.append(str(f1))
        
        # Pasta 2: Sequência parcialmente lida
        f2 = Path(temp_base) / "Parcial"
        f2.mkdir()
        (f2 / "_L_Serie B - Vol 01.cbz").touch()
        (f2 / "Serie B - Vol 02.cbz").touch()
        (f2 / "Serie B - Vol 03.cbz").touch()
        folders.append(str(f2))
        
        # Pasta 3: Sem sequência
        f3 = Path(temp_base) / "Isolados"
        f3.mkdir()
        (f3 / "Arquivo Qualquer.pdf").touch()
        (f3 / "Outro Documento.txt").touch()
        folders.append(str(f3))
        
        print("\n" + "=" * 80)
        print("TESTE: Múltiplas Pastas com Diferentes Estados")
        print("=" * 80)
        
        file_result, selection_info = select_file_with_sequence_logic(
            folders,
            exclude_prefix="_L_",
            use_sequence=True,
            keywords=None,
            process_zip=False
        )
        
        if file_result and file_result['file_path']:
            selected = Path(file_result['file_path']).name
            print(f"\nArquivo selecionado: {selected}")
            
            # Deve selecionar "Serie B - Vol 02.cbz" da pasta parcial
            if "Serie B - Vol 02" in selected:
                print("✅ TESTE PASSOU: Sequência parcial detectada corretamente")
                return True
            else:
                print(f"❌ TESTE FALHOU: Arquivo inesperado selecionado")
                return False
        else:
            print("❌ TESTE FALHOU: Nenhum arquivo selecionado")
            return False
            
    finally:
        shutil.rmtree(temp_base, ignore_errors=True)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TESTE FINAL DA CORREÇÃO DO BUG")
    print("=" * 80)
    
    test1 = test_sequential_mode_fallback_to_random()
    test2 = test_multiple_folders_with_sequences()
    
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    print(f"Teste 1 (Bug Corrigido): {'✅ PASSOU' if test1 else '❌ FALHOU'}")
    print(f"Teste 2 (Múltiplas Pastas): {'✅ PASSOU' if test2 else '❌ FALHOU'}")
    
    if all([test1, test2]):
        print("\n🎉 BUG CORRIGIDO COM SUCESSO!")
    else:
        print("\n⚠️  BUG AINDA PRESENTE - CORREÇÃO NECESSÁRIA")
