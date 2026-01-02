import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import subprocess
import platform
import mimetypes
from pathlib import Path
import threading
import zipfile
import rarfile
import io
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from random_file_picker.core.file_picker import pick_random_file, open_folder, pick_random_file_with_zip_support, cleanup_temp_dir
from random_file_picker.core.sequential_selector import (
    select_file_with_sequence_logic,
    SequentialFileTracker,
    analyze_folder_sequence,
    get_next_unread_file,
)
from random_file_picker.utils.system_utils import get_default_app_info, format_app_info_for_log
import time


class RandomFilePickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Selecionador Aleatório de Arquivos")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.config_file = Path(__file__).parent / "config.json"
        self.is_running = False
        self.config_changed = False
        self.initial_config = {}
        self.file_history = []  # Lista dos últimos 5 arquivos
        self.last_opened_folder = None  # Última pasta aberta
        self.current_image = None  # Referência para imagem atual (evita garbage collection)
        self.file_data_buffer = None  # Buffer reutilizável para carregar arquivos (evita vazamento de memória)
        self.cancel_loading = False  # Flag para cancelar carregamento
        self.loading_start_time = None  # Tempo de início do carregamento
        
        self.setup_ui()
        self.load_config()
        self.store_initial_config()
        self.setup_change_tracking()
        self.setup_keyboard_shortcuts()
        
        # Configura handler para fechar a janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Configura a interface gráfica."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Selecionador Aleatório de Arquivos", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Frame para lista de pastas
        folders_frame = ttk.LabelFrame(main_frame, text="Pastas para buscar", padding="5")
        folders_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        folders_frame.columnconfigure(0, weight=1)
        folders_frame.rowconfigure(0, weight=1)
        
        # Lista de pastas (ScrolledText) - Read-only
        self.folders_text = scrolledtext.ScrolledText(folders_frame, height=8, width=60, 
                                                      font=('Consolas', 9), takefocus=0,
                                                      state='disabled', cursor='arrow')
        self.folders_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Frame para botões de pastas
        folders_buttons_frame = ttk.Frame(folders_frame)
        folders_buttons_frame.grid(row=0, column=1, sticky=(tk.N))
        
        self.add_folder_btn = ttk.Button(folders_buttons_frame, text="Adicionar Pasta", 
                                         command=self.add_folder)
        self.add_folder_btn.grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.clear_folders_btn = ttk.Button(folders_buttons_frame, text="Limpar Tudo", 
                                           command=self.clear_folders)
        self.clear_folders_btn.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Frame para opções com scroll
        options_outer_frame = ttk.LabelFrame(main_frame, text="Opções", padding="5")
        options_outer_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        options_outer_frame.columnconfigure(0, weight=1)
        
        options_container = tk.Frame(options_outer_frame)
        options_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        options_canvas = tk.Canvas(options_container, height=120, borderwidth=0, highlightthickness=0)
        options_scrollbar = ttk.Scrollbar(options_container, orient="vertical", command=options_canvas.yview)
        options_frame = ttk.Frame(options_canvas)
        
        options_canvas.configure(yscrollcommand=options_scrollbar.set)
        options_scrollbar.pack(side="right", fill="y")
        options_canvas.pack(side="left", fill="both", expand=True)
        
        options_canvas_frame = options_canvas.create_window((0, 0), window=options_frame, anchor="nw")
        options_frame.bind("<Configure>", lambda e: options_canvas.configure(scrollregion=options_canvas.bbox("all")))
        
        # Ajusta a largura do frame interno quando o canvas é redimensionado
        def on_canvas_configure(event):
            options_canvas.itemconfig(options_canvas_frame, width=event.width)
        options_canvas.bind("<Configure>", on_canvas_configure)
        
        ttk.Label(options_frame, text="Prefixo de arquivo lido:").grid(row=0, column=0, 
                                                                            sticky=tk.W, padx=(0, 5))
        self.exclude_prefix_var = tk.StringVar(value="_L_")
        self.exclude_prefix_entry = ttk.Entry(options_frame, textvariable=self.exclude_prefix_var, 
                                             width=15)
        self.exclude_prefix_entry.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(options_frame, text="Limite de histórico (1-50):").grid(row=0, column=2, 
                                                                            sticky=tk.W, padx=(20, 5))
        self.history_limit_var = tk.IntVar(value=5)
        self.history_limit_spinbox = ttk.Spinbox(options_frame, from_=1, to=50, 
                                                 textvariable=self.history_limit_var, 
                                                 width=10)
        self.history_limit_spinbox.grid(row=0, column=3, sticky=tk.W)
        
        info_label = ttk.Label(options_frame, 
                              text="(Pastas com '.' são ignoradas automaticamente)",
                              font=('Arial', 8, 'italic'))
        info_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Campo para palavras-chave
        ttk.Label(options_frame, text="Palavras-chave (máx. 3, separadas por vírgula):").grid(
            row=1, column=2, columnspan=2, sticky=tk.W, padx=(20, 5), pady=(5, 0))
        self.keywords_var = tk.StringVar(value="")
        self.keywords_entry = ttk.Entry(options_frame, textvariable=self.keywords_var, width=40)
        self.keywords_entry.grid(row=2, column=2, columnspan=2, sticky=(tk.W, tk.E), padx=(20, 0))
        
        keywords_info = ttk.Label(options_frame,
                                 text="(Arquivo deve conter ao menos UMA das palavras-chave no nome)",
                                 font=('Arial', 8, 'italic'))
        keywords_info.grid(row=3, column=2, columnspan=2, sticky=tk.W, padx=(20, 0))
        
        # Checkbox para abrir pasta
        self.open_folder_var = tk.BooleanVar(value=True)
        self.open_folder_check = ttk.Checkbutton(options_frame, 
                                                 text="Abrir pasta automaticamente após seleção",
                                                 variable=self.open_folder_var)
        self.open_folder_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Checkbox para abrir arquivo
        self.open_file_var = tk.BooleanVar(value=True)
        self.open_file_check = ttk.Checkbutton(options_frame, 
                                               text="Abrir arquivo automaticamente após seleção",
                                               variable=self.open_file_var)
        self.open_file_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))
        
        # Checkbox para usar seleção sequencial
        self.use_sequence_var = tk.BooleanVar(value=True)
        self.use_sequence_check = ttk.Checkbutton(options_frame, 
                                                  text="Usar seleção sequencial (detecta ordenação em pastas)",
                                                  variable=self.use_sequence_var)
        self.use_sequence_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))
        
        # Checkbox para processar arquivos ZIP
        self.process_zip_var = tk.BooleanVar(value=True)
        self.process_zip_check = ttk.Checkbutton(options_frame, 
                                                 text="Processar arquivos ZIP (buscar dentro de arquivos compactados)",
                                                 variable=self.process_zip_var)
        self.process_zip_check.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))
        
        # Botão de execução
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.execute_btn = ttk.Button(button_frame, text="Selecionar Arquivo Aleatório", 
                                      command=self.execute_selection, style='Accent.TButton')
        self.execute_btn.grid(row=0, column=0, padx=5)
        
        # Botão de cancelar (inicialmente oculto)
        self.cancel_btn = ttk.Button(button_frame, text="Cancelar Carregamento",
                                     command=self.cancel_file_loading, state='disabled')
        self.cancel_btn.grid(row=1, column=0, padx=5, pady=(5, 0))
        self.cancel_btn.grid_remove()  # Oculta o botão
        
        # Botão de salvar configuração
        self.save_config_btn = ttk.Button(button_frame, text="Salvar Configuração", 
                                         command=self.manual_save_config, state='disabled')
        self.save_config_btn.grid(row=0, column=1, padx=5)
        
        # Botão de abrir última pasta
        self.last_folder_btn = ttk.Button(button_frame, text="Última Pasta Aberta", 
                                         command=self.open_last_folder, state='disabled')
        self.last_folder_btn.grid(row=0, column=2, padx=5)
        
        # Configurar estilo do botão (se disponível)
        try:
            style = ttk.Style()
            style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        except:
            pass
        
        # Frame para log/resultado
        log_frame = ttk.LabelFrame(main_frame, text="Log / Resultado", padding="5")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=60, 
                                                  font=('Consolas', 9), state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para colorir o log
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("info", foreground="blue")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("highlight", foreground="blue", font=("Consolas", 10, "bold"))
        
        # Frame para miniatura da imagem
        thumbnail_frame = ttk.LabelFrame(main_frame, text="Prévia do Arquivo", padding="5")
        thumbnail_frame.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0), pady=(0, 10))
        thumbnail_frame.columnconfigure(0, weight=1)
        thumbnail_frame.rowconfigure(0, weight=1)
        
        # Label para exibir a imagem
        self.thumbnail_label = ttk.Label(thumbnail_frame, text="Nenhum arquivo selecionado", 
                                        anchor="center", background="#f0f0f0")
        self.thumbnail_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame para histórico de arquivos
        history_frame = ttk.LabelFrame(main_frame, text="Últimos Arquivos Selecionados", padding="5")
        history_frame.grid(row=4, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Container com Canvas e Scrollbar para histórico
        self.history_container = tk.Frame(history_frame)
        self.history_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.history_container.columnconfigure(0, weight=1)
        self.history_container.rowconfigure(0, weight=1)
        
        self.history_canvas = tk.Canvas(self.history_container, borderwidth=0, highlightthickness=0)
        self.history_scrollbar = ttk.Scrollbar(self.history_container, orient="vertical", 
                                               command=self.history_canvas.yview)
        self.history_buttons_frame = ttk.Frame(self.history_canvas)
        
        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)
        
        self.history_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.history_canvas_frame = self.history_canvas.create_window((0, 0), 
                                                                       window=self.history_buttons_frame, 
                                                                       anchor="nw")
        
        # Configura o scroll do canvas
        def on_history_configure(event):
            self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
            # Ajusta largura do frame interno
            canvas_width = event.width
            self.history_canvas.itemconfig(self.history_canvas_frame, width=canvas_width)
        
        self.history_buttons_frame.bind("<Configure>", on_history_configure)
        self.history_canvas.bind("<Configure>", lambda e: self.history_canvas.itemconfig(
            self.history_canvas_frame, width=e.width))
        
        # Suporte a scroll com mouse wheel
        def on_mousewheel(event):
            self.history_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.history_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        self.history_buttons = []
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, 
                              anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def add_folder(self):
        """Abre diálogo para adicionar uma pasta."""
        folder = filedialog.askdirectory(title="Selecione uma pasta para buscar")
        if folder:
            self.folders_text.config(state='normal')
            current_text = self.folders_text.get("1.0", tk.END).strip()
            if current_text:
                self.folders_text.insert(tk.END, "\n" + folder)
            else:
                self.folders_text.insert(tk.END, folder)
            self.folders_text.config(state='disabled')
            self.log_message(f"Pasta adicionada: {folder}", "info")
            
    def clear_folders(self):
        """Limpa a lista de pastas."""
        self.folders_text.config(state='normal')
        self.folders_text.delete("1.0", tk.END)
        self.folders_text.config(state='disabled')
        self.log_message("Lista de pastas limpa", "info")
        
    def get_folders_list(self):
        """Retorna a lista de pastas como uma lista."""
        text = self.folders_text.get("1.0", tk.END).strip()
        if not text:
            return []
        folders = [line.strip() for line in text.split("\n") if line.strip()]
        return folders
    
    def get_keywords_list(self):
        """Retorna a lista de palavras-chave (máximo 3)."""
        text = self.keywords_var.get().strip()
        if not text:
            return []
        # Separa por vírgula e limpa espaços
        keywords = [kw.strip().lower() for kw in text.split(",") if kw.strip()]
        # Limita a 3 palavras-chave
        return keywords[:3]
    
    def get_current_config(self):
        """Retorna a configuração atual."""
        return {
            "folders": self.get_folders_list(),
            "exclude_prefix": self.exclude_prefix_var.get(),
            "open_folder": self.open_folder_var.get(),
            "open_file": self.open_file_var.get(),
            "use_sequence": self.use_sequence_var.get(),
            "history_limit": self.history_limit_var.get(),
            "keywords": self.get_keywords_list(),
            "process_zip": self.process_zip_var.get(),
            "last_opened_folder": self.last_opened_folder
        }
    
    def store_initial_config(self):
        """Armazena a configuração inicial para comparação."""
        self.initial_config = self.get_current_config()
        self.config_changed = False
        self.update_save_button_state()
    
    def check_config_changed(self):
        """Verifica se a configuração foi alterada."""
        current = self.get_current_config()
        changed = current != self.initial_config
        if changed != self.config_changed:
            self.config_changed = changed
            self.update_save_button_state()
    
    def update_save_button_state(self):
        """Atualiza o estado do botão de salvar."""
        if self.config_changed:
            self.save_config_btn.configure(state='normal')
            self.status_var.set("Configuração alterada - não salva")
        else:
            self.save_config_btn.configure(state='disabled')
            if not self.is_running:
                self.status_var.set("Pronto")
    
    def setup_change_tracking(self):
        """Configura rastreamento de mudanças."""
        # Rastreia mudanças no texto de pastas
        self.folders_text.bind('<<Modified>>', self._on_folders_modified)
        
        # Rastreia mudanças nas variáveis
        self.exclude_prefix_var.trace_add('write', lambda *args: self.check_config_changed())
        self.open_folder_var.trace_add('write', lambda *args: self.check_config_changed())
        self.open_file_var.trace_add('write', lambda *args: self.check_config_changed())
        self.use_sequence_var.trace_add('write', lambda *args: self.check_config_changed())
        self.history_limit_var.trace_add('write', lambda *args: self._on_history_limit_changed())
        self.keywords_var.trace_add('write', lambda *args: self.check_config_changed())
        self.process_zip_var.trace_add('write', lambda *args: self.check_config_changed())
    
    def setup_keyboard_shortcuts(self):
        """Configura atalhos de teclado."""
        # Bind Enter para executar a seleção
        self.root.bind('<Return>', lambda event: self.execute_selection())
        
        # Tab já funciona por padrão no tkinter para navegação entre campos
        # Mas vamos garantir que os widgets principais estejam na ordem correta de focus
        # A ordem natural é: folders_text -> exclude_prefix_entry -> history_limit_spinbox 
        # -> keywords_entry -> checkboxes -> execute_btn -> save_config_btn
    
    def _on_folders_modified(self, event):
        """Callback para quando o texto de pastas é modificado."""
        if self.folders_text.edit_modified():
            self.folders_text.edit_modified(False)
            self.check_config_changed()
    
    def manual_save_config(self):
        """Salva a configuração manualmente."""
        self.save_config()
        self.store_initial_config()
        self.log_message("Configuração salva com sucesso!", "success")
        messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
    
    def _on_history_limit_changed(self):
        """Callback quando o limite de histórico muda."""
        self.check_config_changed()
        # Atualiza a exibição do histórico para refletir o novo limite
        try:
            new_limit = int(self.history_limit_var.get())
            if 1 <= new_limit <= 50:
                self.file_history = self.file_history[:new_limit]
                self.update_history_buttons()
        except ValueError:
            pass
    
    def cancel_file_loading(self):
        """Cancela o carregamento do arquivo."""
        self.cancel_loading = True
        self.log_message("\n⚠ Cancelamento solicitado pelo usuário...", "warning")
    
    def show_cancel_button(self):
        """Mostra o botão de cancelar."""
        self.cancel_btn.grid()
        self.cancel_btn.configure(state='normal')
    
    def hide_cancel_button(self):
        """Oculta o botão de cancelar."""
        self.cancel_btn.grid_remove()
        self.cancel_btn.configure(text="Cancelar Carregamento")
    
    def update_cancel_button_time(self, elapsed):
        """Atualiza o texto do botão com tempo decorrido."""
        self.cancel_btn.configure(text=f"Cancelar ({elapsed:.0f}s)")
    
    def on_closing(self):
        """Handler para quando o usuário tenta fechar a janela."""
        if self.config_changed:
            response = messagebox.askyesnocancel(
                "Configuração não salva",
                "Há alterações não salvas. Deseja salvar antes de sair?"
            )
            
            if response is None:  # Cancelar
                return
            elif response:  # Sim
                self.save_config()
        
        self.root.destroy()
    
    def add_to_history(self, file_path):
        """Adiciona um arquivo ao histórico (máximo configurado)."""
        # Remove o arquivo se já existe no histórico
        if file_path in self.file_history:
            self.file_history.remove(file_path)
        
        # Adiciona no início da lista
        self.file_history.insert(0, file_path)
        
        # Mantém apenas o limite configurado
        try:
            limit = int(self.history_limit_var.get())
            if 1 <= limit <= 50:
                self.file_history = self.file_history[:limit]
            else:
                self.file_history = self.file_history[:5]
        except (ValueError, tk.TclError):
            self.file_history = self.file_history[:5]
        
        # Atualiza a interface
        self.update_history_buttons()
        
        # Salva a configuração automaticamente para persistir o histórico
        self.save_config()
    
    def update_history_buttons(self):
        """Atualiza os botões do histórico."""
        # Remove botões antigos
        for btn in self.history_buttons:
            btn.destroy()
        self.history_buttons.clear()
        
        # Cria novos botões
        for idx, file_path in enumerate(self.file_history):
            file_name = Path(file_path).name
            
            # Trunca nome se muito longo
            display_name = file_name if len(file_name) <= 40 else file_name[:37] + "..."
            
            btn = ttk.Button(
                self.history_buttons_frame,
                text=f"{idx + 1}. {display_name}",
                command=lambda fp=file_path: self.open_history_file(fp)
            )
            btn.grid(row=idx, column=0, sticky=(tk.W, tk.E), pady=2)
            self.history_buttons.append(btn)
    
    def open_history_file(self, file_path):
        """Abre um arquivo do histórico."""
        try:
            if not Path(file_path).exists():
                messagebox.showerror("Erro", "Arquivo não encontrado!")
                return
            
            self._open_file(file_path)
            self.log_message(f"Abrindo arquivo do histórico: {Path(file_path).name}", "info")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir arquivo: {e}")
    
    def open_last_folder(self):
        """Abre a última pasta que foi aberta."""
        if not self.last_opened_folder:
            messagebox.showinfo("Informação", "Nenhuma pasta foi aberta ainda.")
            return
        
        try:
            if not Path(self.last_opened_folder).exists():
                messagebox.showerror("Erro", "A pasta não existe mais!")
                self.last_opened_folder = None
                self.update_last_folder_button_state()
                return
            
            open_folder(self.last_opened_folder)
            self.log_message(f"Abrindo última pasta: {self.last_opened_folder}", "info")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir pasta: {e}")
    
    def update_last_folder_button_state(self):
        """Atualiza o estado do botão de última pasta."""
        if self.last_opened_folder and Path(self.last_opened_folder).exists():
            self.last_folder_btn.config(state='normal')
        else:
            self.last_folder_btn.config(state='disabled')
    
    def _get_default_app(self, file_path):
        """Obtém o aplicativo padrão que abrirá o arquivo."""
        try:
            app_info = get_default_app_info(file_path)
            return app_info.get('display_name', 'Desconhecido')
        except Exception as e:
            file_ext = Path(file_path).suffix.lower()
            return f"Aplicativo padrão para {file_ext if file_ext else 'este tipo de arquivo'}"
    
    def _open_file(self, file_path):
        """Abre o arquivo com o aplicativo padrão do sistema."""
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(['open', file_path])
            elif system == "Linux":
                subprocess.run(['xdg-open', file_path])
            else:
                self.log_message(f"Sistema '{system}' não suportado para abrir arquivos.", "warning")
        except Exception as e:
            self.log_message(f"Erro ao abrir arquivo: {e}", "error")
    
    def _load_file_to_buffer(self, file_path):
        """Carrega arquivo completo no buffer com chunks, progresso e cancelamento.
        
        Retorna: True se sucesso, False se cancelado
        """
        try:
            self.log_message("Carregando arquivo completo na memória...", "info")
            self.log_message("(Arquivos grandes podem levar alguns minutos)", "warning")
            
            # Mostra botão de cancelar
            self.root.after(0, self.show_cancel_button)
            self.loading_start_time = time.time()
            self.cancel_loading = False
            
            # Lê o arquivo em chunks para poder cancelar
            chunk_size = 1024 * 1024  # 1MB por chunk
            chunks = []
            file_size = os.path.getsize(file_path)
            bytes_read = 0
            
            with open(file_path, 'rb') as f:
                while True:
                    # Verifica cancelamento
                    if self.cancel_loading:
                        self.log_message("❌ Carregamento cancelado pelo usuário", "error")
                        self.root.after(0, self.hide_cancel_button)
                        return False
                    
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    chunks.append(chunk)
                    bytes_read += len(chunk)
                    
                    # Atualiza tempo a cada 0.5s
                    elapsed = time.time() - self.loading_start_time
                    if int(elapsed * 2) % 1 == 0:  # A cada 0.5s
                        progress = (bytes_read / file_size * 100) if file_size > 0 else 0
                        self.root.after(0, lambda e=elapsed: self.update_cancel_button_time(e))
                        self.log_message(f"⏳ Carregando: {progress:.1f}% ({bytes_read / (1024*1024):.1f} MB)", "info")
            
            # Junta todos os chunks
            self.file_data_buffer = b''.join(chunks)
            elapsed_total = time.time() - self.loading_start_time
            
            # Oculta botão de cancelar
            self.root.after(0, self.hide_cancel_button)
            
            self.log_message(f"✓ Arquivo carregado: {len(self.file_data_buffer)} bytes em {elapsed_total:.1f}s", "success")
            return True
            
        except Exception as e:
            self.log_message(f"Erro ao carregar arquivo: {e}", "error")
            self.root.after(0, self.hide_cancel_button)
            return False
    
    def _detect_archive_format(self, file_path):
        """Detecta o formato do arquivo pela assinatura (magic bytes).
        
        Retorna: 'zip', 'rar', '7z', ou None
        """
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(10)
                
                # ZIP: 50 4B (PK)
                if magic[:2] == b'PK':
                    return 'zip'
                # RAR 1.5-4.x: 52 61 72 21 1A 07 (Rar!)
                elif magic[:4] == b'Rar!':
                    return 'rar'
                # RAR 5+: 52 61 72 21 1A 07 01 00
                elif magic[:8] == b'Rar!\x1a\x07\x01\x00':
                    return 'rar5'
                # 7-Zip: 37 7A BC AF 27 1C
                elif magic[:6] == b'7z\xbc\xaf\x27\x1c':
                    return '7z'
                
                return None
        except Exception as e:
            self.log_message(f"Erro ao detectar formato: {e}", "error")
            return None
    
    def _try_extract_from_zip(self, file_path):
        """Tenta extrair imagem de arquivo ZIP (usa buffer já carregado)."""
        try:
            if not self.file_data_buffer:
                self.log_message("⚠ Buffer não carregado, pulando extração ZIP", "warning")
                return (None, 0)
            
            # Processa o ZIP da memória (buffer já carregado)
            self.log_message("Processando arquivo ZIP...", "info")
            with zipfile.ZipFile(io.BytesIO(self.file_data_buffer), 'r') as zip_file:
                file_list = zip_file.namelist()
                page_count = len([f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                self.log_message(f"✓ Arquivo ZIP aberto! Arquivos encontrados: {len(file_list)}", "success")
                
                # Procura pela primeira imagem
                for filename in sorted(file_list):
                    lower_name = filename.lower()
                    if lower_name.endswith(('.jpg', '.jpeg', '.png')) and not filename.startswith('__MACOSX'):
                        self.log_message(f"Extraindo imagem: {filename}", "info")
                        
                        try:
                            with zip_file.open(filename) as image_file:
                                image_data = image_file.read()
                                image = Image.open(io.BytesIO(image_data))
                                self.log_message(f"✓ Imagem carregada: {image.size} {image.format}", "success")
                                return (image, page_count)
                        except Exception as e:
                            self.log_message(f"Erro ao ler imagem do ZIP: {e}", "warning")
                            continue
                
                self.log_message("Nenhuma imagem JPG/PNG encontrada no ZIP", "warning")
                return (None, 0)
                
        except zipfile.BadZipFile:
            self.log_message("✗ Não é um arquivo ZIP válido", "warning")
            return (None, 0)
        except Exception as e:
            self.log_message(f"✗ Erro ao processar ZIP: {e}", "error")
            return (None, 0)
    
    def _try_extract_from_rar(self, file_path):
        """Tenta extrair imagem de arquivo RAR (usa buffer já carregado)."""
        try:
            if not self.file_data_buffer:
                self.log_message("⚠ Buffer não carregado, pulando extração RAR", "warning")
                return (None, 0)
            
            # Processa o RAR da memória (buffer já carregado)
            self.log_message("Processando arquivo RAR...", "info")
            archive_file = rarfile.RarFile(io.BytesIO(self.file_data_buffer), 'r')
            file_list = archive_file.namelist()
            page_count = len([f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            self.log_message(f"✓ Arquivo RAR aberto! Arquivos encontrados: {len(file_list)}", "success")
            
            # Procura pela primeira imagem
            for filename in sorted(file_list):
                lower_name = filename.lower()
                if lower_name.endswith(('.jpg', '.jpeg', '.png')) and not filename.startswith('__MACOSX'):
                    self.log_message(f"Extraindo imagem: {filename}", "info")
                    
                    try:
                        with archive_file.open(filename) as image_file:
                            image_data = image_file.read()
                            image = Image.open(io.BytesIO(image_data))
                            self.log_message(f"✓ Imagem carregada: {image.size} {image.format}", "success")
                            archive_file.close()
                            return (image, page_count)
                            
                    except rarfile.BadRarFile as e:
                        # Arquivo está parcialmente sincronizado
                        error_msg = str(e)
                        self.log_message(f"⚠ Erro de sincronização: {error_msg}", "warning")
                        self.log_message("⚠ O arquivo pode estar em nuvem e ainda não foi completamente baixado", "warning")
                        self.log_message("💡 Dica: Abra o arquivo uma vez no explorador para forçar download completo", "info")
                        archive_file.close()
                        return ("SYNCING", page_count)
                        
                    except Exception as e:
                        self.log_message(f"Erro ao ler imagem do RAR: {e}", "warning")
                        continue
            
            # Se chegou aqui, não encontrou imagens
            self.log_message("Nenhuma imagem JPG/PNG encontrada no RAR", "warning")
            archive_file.close()
            return (None, 0)
            
        except rarfile.BadRarFile as e:
            self.log_message(f"✗ Não é um arquivo RAR válido: {e}", "warning")
            self.root.after(0, self.hide_cancel_button)
            return (None, 0)
        except Exception as e:
            self.log_message(f"✗ Erro ao processar RAR: {e}", "error")
            self.root.after(0, self.hide_cancel_button)
            return (None, 0)
    
    def _try_extract_from_pdf(self, file_path):
        """Tenta extrair primeira página de arquivo PDF como imagem (usa buffer já carregado)."""
        try:
            if not self.file_data_buffer:
                self.log_message("⚠ Buffer não carregado, pulando extração PDF", "warning")
                return (None, 0)
            
            # Processa o PDF da memória (buffer já carregado)
            self.log_message("Processando arquivo PDF...", "info")
            doc = fitz.open(stream=self.file_data_buffer, filetype="pdf")
            
            if len(doc) == 0:
                self.log_message("✗ PDF não contém páginas", "warning")
                doc.close()
                return (None, 0)
            
            self.log_message(f"✓ Arquivo PDF aberto! Páginas encontradas: {len(doc)}", "success")
            page_count = len(doc)
            
            # Pega a primeira página
            page = doc[0]
            
            # Renderiza a página como imagem
            # zoom = 2 para melhor qualidade
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            
            # Converte pixmap para PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            
            self.log_message(f"✓ Primeira página extraída: {image.size}", "success")
            
            doc.close()
            return image
            
        except Exception as e:
            self.log_message(f"✗ Erro ao processar PDF: {e}", "error")
            return (None, 0)
    
    def _extract_first_image_from_zip(self, file_path):
        """Extrai a primeira imagem (jpg/png) de um arquivo compactado (ZIP/RAR).
        
        Retorna:
            PIL.Image, "SYNCING" (se sincronizando), ou None
        """
        try:
            # Verifica se o arquivo existe e tem tamanho razoável
            file_stat = Path(file_path).stat()
            if file_stat.st_size < 1000:
                self.log_message(f"Arquivo parece ser placeholder (tamanho: {file_stat.st_size} bytes)", "warning")
                return (None, 0)
            
            # CARREGA O ARQUIVO NO BUFFER PRIMEIRO (com chunks e cancelamento)
            if not self._load_file_to_buffer(file_path):
                # Carregamento cancelado
                return (None, 0)
            
            # Detecta formato pela assinatura do arquivo
            detected_format = self._detect_archive_format(file_path)
            if detected_format:
                self.log_message(f"Formato detectado pela assinatura: {detected_format.upper()}", "info")
            
            # Tenta extrair baseado na extensão e formato detectado
            file_ext = Path(file_path).suffix.lower()
            
            # PDF - verifica primeiro se é PDF
            if file_ext == '.pdf':
                result = self._try_extract_from_pdf(file_path)
                if result is not None:
                    return result
            
            # Prioriza RAR se extensão ou detecção indicar
            if file_ext in ['.rar', '.cbr'] or detected_format in ['rar', 'rar5']:
                result = self._try_extract_from_rar(file_path)
                if result is not None:
                    return result
                # Se falhou, tenta ZIP como fallback
                result = self._try_extract_from_zip(file_path)
                if result is not None:
                    return result
            
            # Prioriza ZIP se extensão ou detecção indicar
            elif file_ext in ['.zip', '.cbz'] or detected_format == 'zip':
                result = self._try_extract_from_zip(file_path)
                if result is not None:
                    return result
                # Se falhou, tenta RAR como fallback
                result = self._try_extract_from_rar(file_path)
                if result is not None:
                    return result
            
            # Se não tem extensão conhecida, tenta ambos
            else:
                # Tenta ZIP primeiro
                result = self._try_extract_from_zip(file_path)
                if result is not None:
                    return result
                # Depois tenta RAR
                result = self._try_extract_from_rar(file_path)
                if result is not None:
                    return result
            
            # Se chegou aqui, não conseguiu extrair
            if detected_format == '7z':
                self.log_message("⚠ Arquivo é 7-Zip (.7z), formato não suportado ainda", "warning")
                self.log_message("Extraia manualmente ou converta para ZIP/RAR", "info")
            else:
                self.log_message("Não foi possível extrair imagem do arquivo", "warning")
            
            return (None, 0)
            
        except Exception as e:
            # Outro erro
            self.log_message(f"Erro ao extrair imagem do arquivo: {e}", "error")
            import traceback
            self.log_message(traceback.format_exc(), "error")
            return (None, 0)
    
    def _create_default_thumbnail(self, message="Prévia não disponível"):
        """Cria uma imagem padrão quando não é possível extrair a miniatura."""
        from PIL import ImageDraw, ImageFont
        
        # Cria uma imagem cinza com texto
        img = Image.new('RGB', (200, 280), color='#e0e0e0')
        draw = ImageDraw.Draw(img)
        
        # Adiciona borda
        draw.rectangle([0, 0, 199, 279], outline='#999999', width=2)
        
        # Adiciona texto no centro
        # Usa fonte padrão (pequena)
        text = message
        
        # Calcula posição central
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (200 - text_width) // 2
        y = (280 - text_height) // 2
        
        draw.text((x, y), text, fill='#666666')
        
        return img
    
    def _analyze_file_and_display_info(self, file_path):
        """Analisa arquivo e exibe tabela com informações."""
        try:
            file_name = Path(file_path).name
            folder_path = str(Path(file_path).parent)
            file_size = os.path.getsize(file_path)
            file_ext = Path(file_path).suffix.lower()
            
            # Detecta formato
            detected_format = self._detect_archive_format(file_path)
            format_name = "Desconhecido"
            page_count = 0
            
            # Carrega arquivo na memória e analisa
            if file_ext == '.pdf' or detected_format == 'pdf':
                format_name = "PDF"
                try:
                    with open(file_path, 'rb') as f:
                        pdf_data = f.read()
                    doc = fitz.open(stream=pdf_data, filetype="pdf")
                    page_count = len(doc)
                    doc.close()
                except:
                    pass
            elif file_ext in ['.rar', '.cbr'] or detected_format in ['rar', 'rar5']:
                format_name = "RAR"
                try:
                    with open(file_path, 'rb') as f:
                        rar_data = f.read()
                    archive = rarfile.RarFile(io.BytesIO(rar_data), 'r')
                    file_list = archive.namelist()
                    page_count = len([f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                    archive.close()
                except:
                    pass
            elif file_ext in ['.zip', '.cbz'] or detected_format == 'zip':
                format_name = "ZIP"
                try:
                    with open(file_path, 'rb') as f:
                        zip_data = f.read()
                    archive = zipfile.ZipFile(io.BytesIO(zip_data), 'r')
                    file_list = archive.namelist()
                    page_count = len([f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                    archive.close()
                except:
                    pass
            elif detected_format == '7z':
                format_name = "7-Zip"
            
            # Cria tabela formatada
            self.log_message("\n" + "=" * 70, "info")
            self.log_message("INFORMAÇÕES DO ARQUIVO", "info")
            self.log_message("=" * 70, "info")
            self.log_message(f"Nome:        {file_name}", "success")
            self.log_message(f"Pasta:       {folder_path}", "info")
            self.log_message(f"Formato:     {format_name}", "info")
            if page_count > 0:
                page_label = "Páginas" if format_name == "PDF" else "Imagens"
                self.log_message(f"{page_label}:     {page_count}", "info")
            self.log_message(f"Tamanho:     {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)", "info")
            self.log_message("=" * 70 + "\n", "info")
            
        except Exception as e:
            self.log_message(f"Erro ao analisar arquivo: {e}", "error")
    
    def _display_thumbnail(self, file_path):
        """Exibe a miniatura do arquivo selecionado."""
        self.log_message(f"\n=== Carregando miniatura de: {Path(file_path).name}", "info")
        
        # Analisa e exibe informações do arquivo em tabela
        self._analyze_file_and_display_info(file_path)
        
        try:
            # Tenta extrair imagem do arquivo (se for ZIP/RAR/PDF)
            result = self._extract_first_image_from_zip(file_path)
            
            # Desempacota o resultado (pode ser tupla ou valor único)
            if isinstance(result, tuple):
                image, page_count = result
            else:
                image = result
                page_count = 0
            
            if image == "SYNCING":
                # Arquivo está sincronizando do OneDrive
                self.log_message("Exibindo mensagem de sincronização", "info")
                image = self._create_default_thumbnail("Sincronizando\ndo OneDrive...\n\nTente novamente\nem alguns minutos")
            elif image is None:
                # Se não conseguiu, usa imagem padrão
                self.log_message("Usando imagem padrão (arquivo não é ZIP/RAR ou não contém imagens)", "info")
                image = self._create_default_thumbnail("Prévia não\ndisponível")
            
            # Redimensiona mantendo proporção
            # Tamanho máximo: 200x280
            image.thumbnail((200, 280), Image.Resampling.LANCZOS)
            
            # Converte para formato do Tkinter
            photo = ImageTk.PhotoImage(image)
            
            # Armazena referência para evitar garbage collection
            self.current_image = photo
            
            # Atualiza o label
            self.thumbnail_label.configure(image=photo, text="")
            self.log_message("Miniatura exibida com sucesso!", "success")
            
            # Libera o buffer de memória após uso
            self.file_data_buffer = None
            
        except Exception as e:
            # Em caso de erro, mostra imagem padrão
            self.log_message(f"Erro ao exibir miniatura: {e}", "error")
            
            # Libera o buffer mesmo em caso de erro
            self.file_data_buffer = None
            
            try:
                image = self._create_default_thumbnail("Erro ao\ncarregar")
                image.thumbnail((200, 280), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.current_image = photo
                self.thumbnail_label.configure(image=photo, text="")
            except:
                self.thumbnail_label.configure(image="", text="Erro ao carregar imagem")
    
    def _display_thumbnail_async(self, file_path):
        """Wrapper para exibir miniatura em thread separada (evita travar interface)."""
        try:
            # Mostra mensagem de carregamento
            self.root.after(0, lambda: self.thumbnail_label.configure(text="Carregando..."))
            
            # Executa o processamento da imagem
            self._display_thumbnail(file_path)
        except Exception as e:
            # Em caso de erro, atualiza na thread principal
            self.root.after(0, lambda: self.thumbnail_label.configure(image="", text="Erro ao carregar"))
        
    def log_message(self, message, tag=None):
        """Adiciona uma mensagem ao log."""
        self.log_text.configure(state='normal')
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        if tag:
            self.log_text.insert(tk.END, formatted_message, tag)
        else:
            self.log_text.insert(tk.END, formatted_message)
        
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()
        
    def clear_log(self):
        """Limpa o log."""
        self.log_text.configure(state='normal')
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state='disabled')
        
    def execute_selection(self):
        """Executa a seleção de arquivo aleatório."""
        if self.is_running:
            messagebox.showwarning("Aviso", "Já existe uma busca em andamento!")
            return
            
        folders = self.get_folders_list()
        if not folders:
            messagebox.showerror("Erro", "Por favor, adicione pelo menos uma pasta!")
            return
        
        # Salvar configuração automaticamente ao executar
        if self.config_changed:
            self.save_config()
            self.store_initial_config()
        
        # Executar em thread separada para não travar a UI
        self.is_running = True
        self.execute_btn.configure(state='disabled')
        self.save_config_btn.configure(state='disabled')
        self.status_var.set("Buscando arquivos...")
        self.clear_log()
        
        keywords = self.get_keywords_list()
        
        thread = threading.Thread(target=self._execute_selection_thread, 
                                 args=(folders, self.exclude_prefix_var.get(), 
                                       self.open_folder_var.get(), self.open_file_var.get(),
                                       self.use_sequence_var.get(), keywords, 
                                       self.process_zip_var.get()))
        thread.daemon = True
        thread.start()
        
    def _execute_selection_thread(self, folders, exclude_prefix, open_folder_after, 
                                  open_file_after, use_sequence, keywords, process_zip):
        """Executa a seleção em uma thread separada."""
        temp_dir_to_cleanup = None
        try:
            # Limpa o buffer de memória no início de cada busca
            self.file_data_buffer = None
            import gc
            gc.collect()  # Força coleta de lixo para liberar memória
            
            self.log_message("=" * 70)
            self.log_message("Iniciando busca de arquivos...", "info")
            self.log_message(f"Pastas: {len(folders)}", "info")
            self.log_message(f"Prefixo de arquivo lido: {exclude_prefix}", "info")
            self.log_message(f"Ignorando pastas com prefixo: .", "info")
            self.log_message(f"Seleção sequencial: {'Ativada' if use_sequence else 'Desativada'}", "info")
            self.log_message(f"Processar arquivos ZIP: {'Ativado' if process_zip else 'Desativado'}", "info")
            
            if keywords:
                self.log_message(f"Palavras-chave: {', '.join(keywords)}", "info")
            else:
                self.log_message("Palavras-chave: Nenhuma (todos os arquivos são elegíveis)", "info")
            
            self.log_message("=" * 70)
            
            start_time = time.time()
            
            # Usa lógica sequencial ou aleatória conforme configuração
            if use_sequence:
                file_result, selection_info = select_file_with_sequence_logic(
                    folders, exclude_prefix, use_sequence=True, keywords=keywords, process_zip=process_zip
                )
                
                if not file_result or not file_result['file_path']:
                    if keywords:
                        raise ValueError(f"Nenhum arquivo válido encontrado com as palavras-chave: {', '.join(keywords)}")
                    raise ValueError("Nenhum arquivo válido encontrado nas pastas informadas.")
                
                selected_file = file_result['file_path']
                temp_dir_to_cleanup = file_result.get('temp_dir')
                
                # Log informações sobre ZIP se aplicável
                if file_result['is_from_zip']:
                    self.log_message(f"\n✓ Arquivo extraído de ZIP!", "success")
                    self.log_message(f"  ZIP origem: {os.path.basename(file_result['zip_path'])}", "info")
                    self.log_message(f"  Arquivo no ZIP: {os.path.basename(file_result['file_in_zip'])}", "info")
                
                # Log informações sobre a seleção
                if selection_info['sequence_detected']:
                    self.log_message(f"\n✓ Sequência detectada na pasta!", "success")
                    self.log_message(f"  Método: Seleção Sequencial", "info")
                    self.log_message(f"  Coleção: {selection_info['sequence_info']['collection']}", "info")
                    self.log_message(f"  Tipo de ordenação: {selection_info['sequence_info']['type']}", "info")
                    self.log_message(f"  Total de arquivos na sequência: {selection_info['sequence_info']['total_files']}", "info")
                    if selection_info['sequence_info']['file_number']:
                        self.log_message(f"  Número do arquivo: {selection_info['sequence_info']['file_number']}", "info")
                else:
                    self.log_message(f"\nNenhuma sequência detectada - seleção aleatória", "info")
            else:
                # Modo aleatório tradicional com suporte a ZIP
                file_result = pick_random_file_with_zip_support(folders, exclude_prefix, check_accessibility=False, keywords=keywords, process_zip=process_zip)
                
                if not file_result or not file_result['file_path']:
                    if keywords:
                        raise ValueError(f"Nenhum arquivo válido encontrado com as palavras-chave: {', '.join(keywords)}")
                    raise ValueError("Nenhum arquivo válido encontrado nas pastas informadas.")
                
                selected_file = file_result['file_path']
                temp_dir_to_cleanup = file_result.get('temp_dir')
                
                self.log_message(f"\nMétodo: Seleção Aleatória", "info")
                
                # Log informações sobre ZIP se aplicável
                if file_result['is_from_zip']:
                    self.log_message(f"\n✓ Arquivo extraído de ZIP!", "success")
                    self.log_message(f"  ZIP origem: {os.path.basename(file_result['zip_path'])}", "info")
                    self.log_message(f"  Arquivo no ZIP: {os.path.basename(file_result['file_in_zip'])}", "info")
                
                # Verifica se o arquivo aleatório faz parte de uma sequência
                # (mas só se não veio de um ZIP, pois ZIPs já foram processados)
                if not file_result['is_from_zip']:
                    file_folder = Path(selected_file).parent
                    sequences = analyze_folder_sequence(file_folder, exclude_prefix, keywords)
                    
                    if sequences:
                        # Arquivo faz parte de uma sequência
                        tracker = SequentialFileTracker()
                        result = get_next_unread_file(sequences, tracker, keywords)
                        
                        if result:
                            next_file, selected_sequence, file_info = result
                            self.log_message(f"\n✓ Arquivo aleatório faz parte de uma sequência!", "success")
                            self.log_message(f"  Selecionando primeiro arquivo não lido da sequência", "info")
                            self.log_message(f"  Coleção: {selected_sequence['collection']}", "info")
                            self.log_message(f"  Tipo de ordenação: {selected_sequence['type']}", "info")
                            self.log_message(f"  Total de arquivos na sequência: {selected_sequence['count']}", "info")
                            if file_info['number']:
                                self.log_message(f"  Número do arquivo: {file_info['number']}", "info")
                            
                            # Substitui pelo primeiro não lido da sequência
                            selected_file = next_file
                            tracker.mark_as_read(selected_file)
                        else:
                            self.log_message(f"\nArquivo faz parte de sequência, mas todos já foram lidos", "info")
                    else:
                        self.log_message(f"\nArquivo isolado (não faz parte de sequência)", "info")
            
            elapsed_time = time.time() - start_time
            
            # Exibe contagem de arquivos encontrados
            if selection_info.get('total_files_found', 0) > 0:
                # Tag especial para azul negrito
                self.log_message(f"\n✓ ARQUIVOS ENCONTRADOS: {selection_info['total_files_found']}", "highlight")
            
            self.log_message(f"\nTempo de busca: {elapsed_time:.2f} segundos", "success")
            
            # Obtém informações do arquivo
            file_path = Path(selected_file)
            
            try:
                file_size = file_path.stat().st_size
                size_str = f"{file_size / (1024*1024):.2f} MB" if file_size > 0 else "Não sincronizado"
            except:
                size_str = "Não sincronizado"
            
            self.log_message("\nArquivo selecionado:", "success")
            self.log_message(f"  Nome: {file_path.name}", "success")
            self.log_message(f"  Caminho: {selected_file}", "success")
            self.log_message(f"  Tamanho: {size_str}", "success")
            
            # Identifica o aplicativo padrão que abrirá o arquivo
            try:
                app_info = get_default_app_info(selected_file)
                self.log_message("\nInformações do aplicativo padrão:", "info")
                self.log_message(format_app_info_for_log(app_info), "info")
            except Exception as e:
                default_app = self._get_default_app(selected_file)
                self.log_message(f"\nAplicativo padrão: {default_app}", "info")
            
            # Adiciona ao histórico (usa o arquivo original do ZIP se aplicável)
            history_file = file_result.get('zip_path') if file_result.get('is_from_zip') else selected_file
            self.root.after(0, lambda: self.add_to_history(history_file))
            
            # Exibe a miniatura ANTES de abrir pasta/arquivo (BLOQUEANTE)
            # Força o download completo do arquivo da nuvem antes de prosseguir
            # Usa o arquivo do ZIP se aplicável, pois a miniatura está dentro do ZIP
            thumbnail_file = file_result.get('zip_path') if file_result.get('is_from_zip') else selected_file
            self.log_message("\n=== Carregando e extraindo miniatura (aguarde)...", "info")
            self._display_thumbnail(thumbnail_file)
            self.log_message("=== Miniatura processada, prosseguindo com ações\n", "success")
            
            status_parts = []
            
            # Abre a pasta apenas se a opção estiver marcada
            if open_folder_after:
                self.log_message("\nAbrindo pasta no explorador...", "info")
                # Se veio de ZIP, abre a pasta do ZIP, não a temporária
                folder_to_open = file_result.get('zip_path', selected_file) if file_result.get('is_from_zip') else selected_file
                open_folder(folder_to_open)
                # Salva a última pasta aberta
                folder_path = os.path.dirname(folder_to_open)
                self.last_opened_folder = folder_path
                self.update_last_folder_button_state()
                status_parts.append("pasta aberta")
            else:
                self.log_message("\nPasta não aberta (opção desmarcada)", "info")
            
            # Abre o arquivo apenas se a opção estiver marcada
            if open_file_after:
                try:
                    app_info = get_default_app_info(selected_file)
                    app_name = app_info.get('display_name', 'aplicativo padrão')
                except:
                    app_name = 'aplicativo padrão'
                    
                self.log_message(f"Abrindo arquivo com {app_name}...", "info")
                self._open_file(selected_file)
                status_parts.append("arquivo aberto")
            else:
                self.log_message("Arquivo não aberto (opção desmarcada)", "info")
            
            # Monta mensagem de status
            if status_parts:
                status_msg = f"Arquivo selecionado! ({', '.join(status_parts)})"
            else:
                status_msg = "Arquivo selecionado!"
            
            self.log_message("=" * 70)
            self.log_message("Concluído!", "success")
            
            self.root.after(0, lambda: self.status_var.set(status_msg))
            
        except ValueError as e:
            self.log_message(f"\nErro: {e}", "error")
            self.log_message("\nDicas:", "warning")
            self.log_message("  - Verifique se as pastas existem e estão acessíveis", "warning")
            self.log_message("  - Certifique-se de que há arquivos nas pastas informadas", "warning")
            self.log_message(f"  - Verifique se há arquivos não lidos (sem o prefixo {exclude_prefix})", "warning")
            self.root.after(0, lambda: self.status_var.set("Erro na seleção"))
            
        except Exception as e:
            self.log_message(f"\nErro inesperado: {e}", "error")
            self.root.after(0, lambda: self.status_var.set("Erro inesperado"))
            
        finally:
            # Limpa diretório temporário se foi criado
            if temp_dir_to_cleanup:
                self.log_message("\nLimpando arquivos temporários...", "info")
                cleanup_temp_dir(temp_dir_to_cleanup)
            
            self.is_running = False
            self.root.after(0, lambda: self.execute_btn.configure(state='normal'))
            self.root.after(0, self.update_save_button_state)
            
    def save_config(self):
        """Salva a configuração atual em um arquivo JSON."""
        config = {
            "folders": self.get_folders_list(),
            "exclude_prefix": self.exclude_prefix_var.get(),
            "open_folder": self.open_folder_var.get(),
            "open_file": self.open_file_var.get(),
            "use_sequence": self.use_sequence_var.get(),
            "history_limit": int(self.history_limit_var.get()),
            "keywords": self.keywords_var.get(),
            "file_history": self.file_history
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_message(f"Erro ao salvar configuração: {e}", "error")
            
    def load_config(self):
        """Carrega a configuração salva."""
        if not self.config_file.exists():
            self.log_message("Nenhuma configuração anterior encontrada. Use os valores padrão.", "info")
            return
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Restaurar pastas
            folders = config.get("folders", [])
            if folders:
                self.folders_text.config(state='normal')
                self.folders_text.insert("1.0", "\n".join(folders))
                self.folders_text.config(state='disabled')
                self.log_message(f"Configuração carregada: {len(folders)} pasta(s)", "success")
                
            # Restaurar prefixo
            exclude_prefix = config.get("exclude_prefix", "_L_")
            self.exclude_prefix_var.set(exclude_prefix)
            
            # Restaurar preferência de abrir pasta
            open_folder = config.get("open_folder", True)
            self.open_folder_var.set(open_folder)
            
            # Restaurar preferência de abrir arquivo
            open_file = config.get("open_file", False)
            self.open_file_var.set(open_file)
            
            # Restaurar preferência de seleção sequencial
            use_sequence = config.get("use_sequence", True)
            self.use_sequence_var.set(use_sequence)
            
            # Restaurar preferência de processar ZIP
            process_zip = config.get("process_zip", True)
            self.process_zip_var.set(process_zip)
            
            # Restaurar palavras-chave
            keywords = config.get("keywords", "")
            self.keywords_var.set(keywords)
            
            # Restaurar histórico de arquivos
            self.file_history = config.get("file_history", [])
            
            # Restaurar limite de histórico
            history_limit = config.get("history_limit", 5)
            self.history_limit_var.set(history_limit)
            
            # Restaurar última pasta aberta
            self.last_opened_folder = config.get("last_opened_folder", None)
            self.update_last_folder_button_state()
            
            self.update_history_buttons()
            
        except Exception as e:
            self.log_message(f"Erro ao carregar configuração: {e}", "error")


def main():
    root = tk.Tk()
    app = RandomFilePickerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
