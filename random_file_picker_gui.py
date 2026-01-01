import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import subprocess
import platform
import mimetypes
from pathlib import Path
import threading
from random_file_picker import pick_random_file, open_folder
from sequential_selector import select_file_with_sequence_logic, SequentialFileTracker, analyze_folder_sequence, get_next_unread_file
from system_utils import get_default_app_info, format_app_info_for_log
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
        self.open_file_var = tk.BooleanVar(value=False)
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
        
        # Botão de execução
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.execute_btn = ttk.Button(button_frame, text="Selecionar Arquivo Aleatório", 
                                      command=self.execute_selection, style='Accent.TButton')
        self.execute_btn.grid(row=0, column=0, padx=5)
        
        # Botão de salvar configuração
        self.save_config_btn = ttk.Button(button_frame, text="Salvar Configuração", 
                                         command=self.manual_save_config, state='disabled')
        self.save_config_btn.grid(row=0, column=1, padx=5)
        
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
            "keywords": self.get_keywords_list()
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
                                       self.use_sequence_var.get(), keywords))
        thread.daemon = True
        thread.start()
        
    def _execute_selection_thread(self, folders, exclude_prefix, open_folder_after, 
                                  open_file_after, use_sequence, keywords):
        """Executa a seleção em uma thread separada."""
        try:
            self.log_message("=" * 70)
            self.log_message("Iniciando busca de arquivos...", "info")
            self.log_message(f"Pastas: {len(folders)}", "info")
            self.log_message(f"Prefixo de arquivo lido: {exclude_prefix}", "info")
            self.log_message(f"Ignorando pastas com prefixo: .", "info")
            self.log_message(f"Seleção sequencial: {'Ativada' if use_sequence else 'Desativada'}", "info")
            
            if keywords:
                self.log_message(f"Palavras-chave: {', '.join(keywords)}", "info")
            else:
                self.log_message("Palavras-chave: Nenhuma (todos os arquivos são elegíveis)", "info")
            
            self.log_message("=" * 70)
            
            start_time = time.time()
            
            # Usa lógica sequencial ou aleatória conforme configuração
            if use_sequence:
                selected_file, selection_info = select_file_with_sequence_logic(
                    folders, exclude_prefix, use_sequence=True, keywords=keywords
                )
                
                if not selected_file:
                    if keywords:
                        raise ValueError(f"Nenhum arquivo válido encontrado com as palavras-chave: {', '.join(keywords)}")
                    raise ValueError("Nenhum arquivo válido encontrado nas pastas informadas.")
                
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
                # Modo aleatório tradicional - mas verifica se faz parte de sequência
                selected_file = pick_random_file(folders, exclude_prefix, check_accessibility=False, keywords=keywords)
                self.log_message(f"\nMétodo: Seleção Aleatória", "info")
                
                # Verifica se o arquivo aleatório faz parte de uma sequência
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
            
            # Adiciona ao histórico
            self.root.after(0, lambda: self.add_to_history(selected_file))
            
            status_parts = []
            
            # Abre a pasta apenas se a opção estiver marcada
            if open_folder_after:
                self.log_message("\nAbrindo pasta no explorador...", "info")
                open_folder(selected_file)
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
            
            # Restaurar palavras-chave
            keywords = config.get("keywords", "")
            self.keywords_var.set(keywords)
            
            # Restaurar histórico de arquivos
            self.file_history = config.get("file_history", [])
            
            # Restaurar limite de histórico
            history_limit = config.get("history_limit", 5)
            self.history_limit_var.set(history_limit)
            
            self.update_history_buttons()
            
        except Exception as e:
            self.log_message(f"Erro ao carregar configuração: {e}", "error")


def main():
    root = tk.Tk()
    app = RandomFilePickerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
