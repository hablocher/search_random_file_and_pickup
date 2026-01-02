import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import subprocess
import platform
import time
from pathlib import Path
import threading
from PIL import Image, ImageTk
import gc
import traceback

from random_file_picker.core.file_picker import pick_random_file, open_folder, pick_random_file_with_zip_support, cleanup_temp_dir
from random_file_picker.core.sequential_selector import (
    select_file_with_sequence_logic,
    SequentialFileTracker,
    analyze_folder_sequence,
    get_next_unread_file,
)
from random_file_picker.utils.system_utils import get_default_app_info, format_app_info_for_log

# Módulos refatorados (agora em core)
from random_file_picker.core.config_manager import ConfigManager
from random_file_picker.core.file_loader import FileLoader
from random_file_picker.core.archive_extractor import ArchiveExtractor
from random_file_picker.core.thumbnail_generator import ThumbnailGenerator
from random_file_picker.core.file_analyzer import FileAnalyzer


class RandomFilePickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Media Finder")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        
        # Aplica tema moderno
        self._apply_modern_theme()
        
        self.config_file = Path.cwd() / "config.json"
        self.is_running = False
        self.config_changed = False
        self.initial_config = {}
        self.file_history = []  # Lista dos últimos 5 arquivos
        self.last_opened_folder = None  # Última pasta aberta
        self.current_image = None  # Referência para imagem atual (evita garbage collection)
        self.file_data_buffer = None  # Buffer reutilizável para carregar arquivos (evita vazamento de memória)
        self.temp_directories = []  # Lista de diretórios temporários criados durante a sessão
        
        # Controle de animação
        self.loading_animation_running = False
        self.loading_animation_frames = []
        self.loading_animation_index = 0
        self.loading_animation_job = None
        
        # Controle de fonte do log
        self.log_font_size = 14  # Tamanho padrão de fonte do log
        
        # Imagens para o botão de seleção
        self.roulette_image_static = None
        self.spinning_animation_frames = []  # Frames da animação spinning.gif
        self.spinning_animation_index = 0
        self.spinning_animation_job = None
        
        # Inicializa variáveis de configuração antes de setup_ui
        self.exclude_prefix_var = tk.StringVar(value="_L_,_W_")
        self.history_limit_var = tk.IntVar(value=5)
        self.keywords_var = tk.StringVar(value="")
        self.keywords_match_all_var = tk.BooleanVar(value=False)
        self.ignored_extensions_var = tk.StringVar(value="srt,sub,txt,nfo")
        self.open_folder_var = tk.BooleanVar(value=False)
        self.open_file_var = tk.BooleanVar(value=False)
        self.use_sequence_var = tk.BooleanVar(value=True)
        self.process_zip_var = tk.BooleanVar(value=True)
        self.use_cache_var = tk.BooleanVar(value=True)
        self.enable_cloud_hydration_var = tk.BooleanVar(value=False)
        
        # Módulos refatorados
        self.config_manager = ConfigManager(self.config_file)
        self.file_loader = FileLoader(chunk_size=1024 * 1024)  # 1MB chunks
        # ArchiveExtractor será inicializado após carregar config (precisa da API key)
        self.archive_extractor = None
        self.thumbnail_generator = ThumbnailGenerator(max_size=(400, 600))
        self.file_analyzer = FileAnalyzer()
        
        self.setup_ui()
        self.load_config()
        
        # Inicializa ArchiveExtractor com API key do config
        tmdb_api_key = self.config_manager.get('tmdb_api_key')
        self.archive_extractor = ArchiveExtractor(
            log_callback=self.log_message,
            tmdb_api_key=tmdb_api_key
        )
        self.store_initial_config()
        self.setup_change_tracking()
        self.setup_keyboard_shortcuts()
        
        # Configura handler para fechar a janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _apply_modern_theme(self):
        """Aplica tema moderno Azure à interface."""
        try:
            style = ttk.Style()
            
            # Tenta usar tema Azure (moderno)
            available_themes = style.theme_names()
            if 'azure' in available_themes:
                style.theme_use('azure')
            elif 'clam' in available_themes:
                style.theme_use('clam')
            elif 'alt' in available_themes:
                style.theme_use('alt')
            
            # Cores modernas
            bg_color = '#f5f5f5'  # Cinza claro
            fg_color = '#2c3e50'  # Cinza escuro
            accent_color = '#3498db'  # Azul moderno
            success_color = '#27ae60'  # Verde
            
            # Configura estilos customizados
            style.configure('TFrame', background=bg_color)
            style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Segoe UI', 9))
            style.configure('TLabelframe', background=bg_color, foreground=fg_color, font=('Segoe UI', 9, 'bold'))
            style.configure('TLabelframe.Label', background=bg_color, foreground=accent_color, font=('Segoe UI', 10, 'bold'))
            style.configure('TButton', font=('Segoe UI', 9), padding=6)
            style.configure('TCheckbutton', background=bg_color, foreground=fg_color, font=('Segoe UI', 9))
            style.configure('TEntry', font=('Segoe UI', 9), padding=5)
            
            # Botão de ação principal
            style.configure('Accent.TButton', 
                          font=('Segoe UI', 11, 'bold'), 
                          padding=10,
                          foreground='white')
            
            # Botão de salvar
            style.configure('Success.TButton',
                          font=('Segoe UI', 9),
                          padding=6)
            
            # Configura fundo da janela principal
            self.root.configure(background=bg_color)
            
        except Exception as e:
            print(f"Erro ao aplicar tema: {e}")
        
    def setup_ui(self):
        """Configura a interface gráfica."""
        # Frame principal com padding maior
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)  # Log (esquerda) - peso reduzido
        main_frame.columnconfigure(1, weight=2)  # Preview (meio) - peso aumentado
        main_frame.columnconfigure(2, weight=2)  # Histórico (direita) - peso aumentado
        main_frame.rowconfigure(1, weight=0)  # Linha de pastas e botão
        main_frame.rowconfigure(2, weight=1)  # Linha de conteúdo principal
        
        # Título com estilo moderno e botão de engrenagem
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Container para título e botão de engrenagem
        title_container = ttk.Frame(title_frame)
        title_container.pack()
        
        title_label = ttk.Label(title_container, text="🎬 Media Finder", 
                               font=('Segoe UI', 16, 'bold'),
                               foreground='#2c3e50')
        title_label.grid(row=0, column=0, padx=(0, 10))
        
        # Botão de engrenagem para abrir opções avançadas
        settings_btn = ttk.Button(title_container, text="⚙️", 
                                 command=self.open_advanced_settings,
                                 width=3)
        settings_btn.grid(row=0, column=1)
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="Busca inteligente com detecção de sequências",
                                  font=('Segoe UI', 9, 'italic'),
                                  foreground='#7f8c8d')
        subtitle_label.pack()
        
        # Frame para pastas e botão de seleção (sem grupo "Configurações")
        top_frame = ttk.Frame(main_frame, padding="15")
        top_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N), pady=(0, 15))
        top_frame.columnconfigure(0, weight=1)
        
        # Subframe: Pastas para buscar
        folders_subframe = ttk.LabelFrame(top_frame, text="📁 Pastas para Buscar", padding="10")
        folders_subframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 15))
        folders_subframe.columnconfigure(0, weight=1)
        
        # Lista de pastas (Listbox com scrollbar para permitir seleção)
        folders_list_frame = ttk.Frame(folders_subframe)
        folders_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        folders_list_frame.columnconfigure(0, weight=1)
        
        folders_scrollbar = ttk.Scrollbar(folders_list_frame, orient="vertical")
        self.folders_listbox = tk.Listbox(
            folders_list_frame,
            height=6,
            width=50,
            font=('Segoe UI', 9),
            yscrollcommand=folders_scrollbar.set,
            selectmode=tk.SINGLE,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground='#bdc3c7',
            highlightcolor='#3498db'
        )
        folders_scrollbar.config(command=self.folders_listbox.yview)
        
        self.folders_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        folders_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame para botões de adicionar/remover/limpar pastas (inline)
        folders_buttons_inline = ttk.Frame(folders_subframe)
        folders_buttons_inline.grid(row=1, column=0, sticky=(tk.W), pady=(8, 0))
        
        self.add_folder_btn = ttk.Button(folders_buttons_inline, text="➕ Adicionar", 
                                         command=self.add_folder, width=15)
        self.add_folder_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.remove_folder_btn = ttk.Button(folders_buttons_inline, text="➖ Remover", 
                                           command=self.remove_selected_folder, width=15)
        self.remove_folder_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.clear_folders_btn = ttk.Button(folders_buttons_inline, text="🗑️ Limpar", 
                                           command=self.clear_folders, width=15)
        self.clear_folders_btn.grid(row=0, column=2)
        
        # Botão de seleção com imagem de dado
        dice_btn_frame = ttk.Frame(top_frame)
        dice_btn_frame.grid(row=0, column=1, sticky=(tk.N))
        
        # Carregar imagem estática do botão (roulette.png)
        try:
            assets_dir = Path.cwd() / "assets"
            roulette_path = assets_dir / "roulette.png"
            
            if roulette_path.exists():
                img = Image.open(roulette_path)
                img = img.resize((64, 64), Image.Resampling.LANCZOS)  # Aumentado de 48x48 para 64x64
                self.roulette_image_static = ImageTk.PhotoImage(img)
                print(f"✓ Imagem de roleta carregada: {roulette_path.name}")
            else:
                self.roulette_image_static = None
                print("⚠ roulette.png não encontrado, usando emoji 🎲 como fallback")
        except Exception as e:
            print(f"Erro ao carregar roulette.png: {e}")
            self.roulette_image_static = None
        
        # Carregar animação spinning.gif para usar durante a busca
        try:
            spinning_path = assets_dir / "spinning.gif"
            
            if spinning_path.exists():
                self.spinning_animation_frames = []
                gif = Image.open(spinning_path)
                
                # Carregar todos os frames do GIF
                try:
                    while True:
                        frame = gif.copy().convert("RGBA")
                        frame = frame.resize((64, 64), Image.Resampling.LANCZOS)  # Aumentado de 48x48 para 64x64
                        self.spinning_animation_frames.append(ImageTk.PhotoImage(frame))
                        gif.seek(len(self.spinning_animation_frames))
                except EOFError:
                    pass
                
                if self.spinning_animation_frames:
                    print(f"✓ Animação spinning carregada: {spinning_path.name} ({len(self.spinning_animation_frames)} frames)")
                else:
                    print("⚠ spinning.gif não possui frames válidos")
            else:
                print("⚠ spinning.gif não encontrado")
        except Exception as e:
            print(f"Erro ao carregar spinning.gif: {e}")
        
        # Botão de execução (principal) - usando tk.Button para remover padding
        if self.roulette_image_static:
            self.execute_btn = tk.Button(dice_btn_frame, image=self.roulette_image_static,
                                         command=self.execute_selection,
                                         relief=tk.RAISED, bd=2,
                                         cursor='hand2')
        else:
            self.execute_btn = tk.Button(dice_btn_frame, text="🎲",
                                         command=self.execute_selection,
                                         font=('Segoe UI', 24),
                                         relief=tk.RAISED, bd=2,
                                         cursor='hand2',
                                         width=3, height=1)
        self.execute_btn.grid(row=0, column=0, pady=(0, 10))
        
        # Botão de cancelar (inicialmente oculto)
        self.cancel_btn = tk.Button(dice_btn_frame, text="⏹️",
                                     command=self.cancel_file_loading, state='disabled',
                                     font=('Segoe UI', 20),
                                     relief=tk.RAISED, bd=2,
                                     cursor='hand2',
                                     width=3, height=1)
        self.cancel_btn.grid(row=1, column=0)
        self.cancel_btn.grid_remove()  # Oculta o botão
        
        # Frame para log/resultado com controles de fonte
        log_outer_frame = ttk.LabelFrame(main_frame, text="📋 Log de Execução", padding="10")
        log_outer_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_outer_frame.columnconfigure(0, weight=1)
        log_outer_frame.rowconfigure(1, weight=1)
        
        # Controles de fonte
        font_controls = ttk.Frame(log_outer_frame)
        font_controls.grid(row=0, column=0, sticky=(tk.W), pady=(0, 5))
        
        ttk.Label(font_controls, text="Tamanho da fonte:").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(font_controls, text="−", command=self.decrease_log_font, width=3).pack(side=tk.LEFT, padx=2)
        
        self.font_size_label = ttk.Label(font_controls, text="14pt", width=5)
        self.font_size_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(font_controls, text="+", command=self.increase_log_font, width=3).pack(side=tk.LEFT, padx=2)
        
        self.log_text = scrolledtext.ScrolledText(log_outer_frame, height=18, width=70, 
                                                  font=('Consolas', 14), state='disabled',
                                                  relief=tk.FLAT, borderwidth=1,
                                                  highlightthickness=1,
                                                  highlightbackground='#bdc3c7')
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para colorir o log
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("info", foreground="blue")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("highlight", foreground="blue", font=("Consolas", 10, "bold"))
        
        # Frame para miniatura da imagem (área aumentada)
        thumbnail_frame = ttk.LabelFrame(main_frame, text="🖼️ Prévia", padding="10")
        thumbnail_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(15, 0))
        thumbnail_frame.columnconfigure(0, weight=1)
        thumbnail_frame.rowconfigure(0, weight=1)
        
        # Label para exibir a imagem
        self.thumbnail_label = ttk.Label(thumbnail_frame, text="Nenhum arquivo\nselecionado", 
                                        anchor="center", background="#ecf0f1",
                                        font=('Segoe UI', 10, 'italic'),
                                        foreground='#95a5a6')
        self.thumbnail_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame para histórico de arquivos (área aumentada)
        history_frame = ttk.LabelFrame(main_frame, text="📚 Histórico", padding="10")
        history_frame.grid(row=2, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(15, 0))
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
        
        # Suporte a scroll com mouse wheel (apenas quando mouse estiver sobre o canvas)
        def on_mousewheel(event):
            self.history_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_enter(event):
            self.history_canvas.bind("<MouseWheel>", on_mousewheel)
        
        def on_leave(event):
            self.history_canvas.unbind("<MouseWheel>")
        
        self.history_canvas.bind("<Enter>", on_enter)
        self.history_canvas.bind("<Leave>", on_leave)
        
        self.history_buttons = []
        
        # Status bar moderno
        self.status_var = tk.StringVar(value="✅ Pronto para iniciar")
        status_frame = ttk.Frame(main_frame, relief=tk.FLAT, borderwidth=1)
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        status_bar = ttk.Label(status_frame, textvariable=self.status_var,
                              anchor=tk.W, font=('Segoe UI', 9),
                              foreground='#27ae60', padding=8)
        status_bar.pack(fill=tk.BOTH, expand=True)
    
    # ========== JANELA POPUP DE OPÇÕES AVANÇADAS ==========
    
    def open_advanced_settings(self):
        """Abre janela popup com opções avançadas."""
        popup = tk.Toplevel(self.root)
        popup.title("⚙️ Opções Avançadas")
        popup.geometry("650x550")
        popup.resizable(False, False)
        
        # Centralizar janela
        popup.transient(self.root)
        popup.grab_set()
        
        main_popup_frame = ttk.Frame(popup, padding="20")
        main_popup_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        popup.columnconfigure(0, weight=1)
        popup.rowconfigure(0, weight=1)
        
        # Canvas e scrollbar para as opções
        canvas = tk.Canvas(main_popup_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_popup_frame, orient="vertical", command=canvas.yview)
        options_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        canvas_frame = canvas.create_window((0, 0), window=options_frame, anchor="nw")
        
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_frame, width=event.width)
            update_scroll_region()
        
        options_frame.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Linha 0: Prefixos de arquivo
        ttk.Label(options_frame, text="📝 Prefixos:", 
                 font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 2))
        exclude_prefix_entry = ttk.Entry(options_frame, textvariable=self.exclude_prefix_var, 
                                             width=30, font=('Segoe UI', 9))
        exclude_prefix_entry.grid(row=0, column=1, sticky=tk.W, pady=(5, 2))
        
        info_label = ttk.Label(options_frame, 
                              text="   ℹ️ Ex: _L_,_W_ (separados por vírgula). Pastas com '.' são ignoradas automaticamente",
                              font=('Segoe UI', 8, 'italic'),
                              foreground='#7f8c8d')
        info_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(2, 8))
        
        # Linha 2: Limite de histórico
        ttk.Label(options_frame, text="📊 Histórico (1-50):",
                 font=('Segoe UI', 9)).grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 2))
        history_limit_spinbox = ttk.Spinbox(options_frame, from_=1, to=50, 
                                                 textvariable=self.history_limit_var, 
                                                 width=10, font=('Segoe UI', 9))
        history_limit_spinbox.grid(row=2, column=1, sticky=tk.W, pady=(5, 2))
        
        # Linha 3-5: Palavras-chave
        ttk.Label(options_frame, text="🔍 Palavras-chave (máx. 5, separadas por vírgula):",
                 font=('Segoe UI', 9, 'bold')).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(12, 3))
        keywords_entry = ttk.Entry(options_frame, textvariable=self.keywords_var, width=50,
                                       font=('Segoe UI', 9))
        keywords_entry.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 3))
        
        # Checkbox para escolher AND/OR
        keywords_match_all_check = ttk.Checkbutton(options_frame,
                                                        text="✅ TODAS as palavras (AND)",
                                                        variable=self.keywords_match_all_var,
                                                        command=self._on_keywords_match_changed)
        keywords_match_all_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(3, 0))
        
        self.keywords_info_popup = ttk.Label(options_frame,
                                 text="   ℹ️ Arquivo deve conter ao menos UMA palavra-chave",
                                 font=('Segoe UI', 8, 'italic'),
                                 foreground='#7f8c8d')
        self.keywords_info_popup.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))
        
        # Linha 6-7: Extensões ignoradas
        ttk.Label(options_frame, text="🚫 Ignorar extensões:",
                 font=('Segoe UI', 9, 'bold')).grid(
            row=7, column=0, columnspan=2, sticky=tk.W, pady=(12, 3))
        ignored_extensions_entry = ttk.Entry(options_frame, textvariable=self.ignored_extensions_var, 
                                                 width=50, font=('Segoe UI', 9))
        ignored_extensions_entry.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 3))
        
        ttk.Label(options_frame,
                  text="   ℹ️ Ex: srt,sub,txt - arquivos com estas extensões serão ignorados",
                  font=('Segoe UI', 8, 'italic'),
                  foreground='#7f8c8d').grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))
        
        # Checkboxes com emojis
        open_folder_check = ttk.Checkbutton(options_frame, 
                                                 text="📂 Abrir pasta após seleção",
                                                 variable=self.open_folder_var)
        open_folder_check.grid(row=10, column=0, columnspan=2, sticky=tk.W, pady=(8, 3))
        
        open_file_check = ttk.Checkbutton(options_frame, 
                                               text="📝 Abrir arquivo após seleção",
                                               variable=self.open_file_var)
        open_file_check.grid(row=11, column=0, columnspan=2, sticky=tk.W, pady=3)
        
        use_sequence_check = ttk.Checkbutton(options_frame, 
                                                  text="🔢 Seleção sequencial (detecta ordenação)",
                                                  variable=self.use_sequence_var)
        use_sequence_check.grid(row=12, column=0, columnspan=2, sticky=tk.W, pady=3)
        
        process_zip_check = ttk.Checkbutton(options_frame, 
                                                 text="📦 Processar arquivos ZIP/RAR",
                                                 variable=self.process_zip_var)
        process_zip_check.grid(row=13, column=0, columnspan=2, sticky=tk.W, pady=3)
        
        use_cache_check = ttk.Checkbutton(options_frame, 
                                               text="⚡ Cache de arquivos (busca instantânea)",
                                               variable=self.use_cache_var)
        use_cache_check.grid(row=14, column=0, columnspan=2, sticky=tk.W, pady=3)
        
        enable_cloud_hydration_check = ttk.Checkbutton(options_frame, 
                                                            text="☁️ Forçar download de nuvem (OneDrive/Google Drive)",
                                                            variable=self.enable_cloud_hydration_var)
        enable_cloud_hydration_check.grid(row=15, column=0, columnspan=2, sticky=tk.W, pady=3)
        
        # Botões no final
        buttons_frame = ttk.Frame(options_frame)
        buttons_frame.grid(row=16, column=0, columnspan=2, pady=(20, 0))
        
        save_btn = ttk.Button(buttons_frame, text="💾 Salvar e Fechar", 
                             command=lambda: self._save_and_close_popup(popup),
                             style='Success.TButton')
        save_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = ttk.Button(buttons_frame, text="Fechar", 
                              command=popup.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)
    
    def _save_and_close_popup(self, popup):
        """Salva a configuração e fecha o popup."""
        self.save_config()
        self.store_initial_config()
        self.log_message("Configuração salva com sucesso!", "success")
        popup.destroy()
    
    # ========== CONTROLE DE FONTE DO LOG ==========
    
    def increase_log_font(self):
        """Aumenta o tamanho da fonte do log."""
        if self.log_font_size < 24:
            self.log_font_size += 1
            self.log_text.configure(font=('Consolas', self.log_font_size))
            self.font_size_label.configure(text=f"{self.log_font_size}pt")
    
    def decrease_log_font(self):
        """Diminui o tamanho da fonte do log."""
        if self.log_font_size > 8:
            self.log_font_size -= 1
            self.log_text.configure(font=('Consolas', self.log_font_size))
            self.font_size_label.configure(text=f"{self.log_font_size}pt")
    
    # ========== ANIMAÇÃO DO DADO ==========
    
    def start_spinning_animation(self):
        """Inicia a animação do botão (spinning.gif) durante a busca."""
        if self.spinning_animation_frames and len(self.spinning_animation_frames) > 1:
            self.spinning_animation_index = 0
            self._animate_spinning()
    
    def stop_spinning_animation(self):
        """Para a animação da roleta."""
        if self.spinning_animation_job:
            self.root.after_cancel(self.spinning_animation_job)
            self.spinning_animation_job = None
        
        # Volta para a imagem estática
        if self.roulette_image_static and hasattr(self, 'execute_btn'):
            try:
                self.execute_btn.configure(image=self.roulette_image_static)
            except:
                pass
    
    def _animate_spinning(self):
        """Atualiza o frame da animação (spinning.gif) durante a busca."""
        if not hasattr(self, 'execute_btn'):
            return
        
        try:
            if self.spinning_animation_frames:
                frame = self.spinning_animation_frames[self.spinning_animation_index]
                self.execute_btn.configure(image=frame)
                self.spinning_animation_index = (self.spinning_animation_index + 1) % len(self.spinning_animation_frames)
                self.spinning_animation_job = self.root.after(50, self._animate_spinning)  # 50ms = ~20 FPS
        except Exception as e:
            print(f"Erro na animação: {e}")
            self.stop_spinning_animation()
    
    # ========== GERENCIAMENTO DE PASTAS ==========
    
    def add_folder(self):
        """Abre diálogo para adicionar uma pasta."""
        folder = filedialog.askdirectory(title="Selecione uma pasta para buscar")
        if folder:
            # Verifica se a pasta já está na lista
            current_folders = list(self.folders_listbox.get(0, tk.END))
            if folder not in current_folders:
                self.folders_listbox.insert(tk.END, folder)
                self.log_message(f"Pasta adicionada: {folder}", "info")
                self.check_config_changed()
            else:
                self.log_message(f"Pasta já existe na lista: {folder}", "warning")
            
    def remove_selected_folder(self):
        """Remove a pasta selecionada da lista."""
        selection = self.folders_listbox.curselection()
        if selection:
            index = selection[0]
            folder = self.folders_listbox.get(index)
            self.folders_listbox.delete(index)
            self.log_message(f"Pasta removida: {folder}", "info")
            self.check_config_changed()
        else:
            messagebox.showinfo("Aviso", "Selecione uma pasta para remover!")
    
    def clear_folders(self):
        """Limpa a lista de pastas."""
        self.folders_listbox.delete(0, tk.END)
        self.log_message("Lista de pastas limpa", "info")
        self.check_config_changed()
        
    def get_folders_list(self):
        """Retorna a lista de pastas como uma lista."""
        return list(self.folders_listbox.get(0, tk.END))
    
    def get_keywords_list(self):
        """Retorna a lista de palavras-chave (máximo 5)."""
        text = self.keywords_var.get().strip()
        if not text:
            return []
        # Separa por vírgula e limpa espaços
        keywords = [kw.strip().lower() for kw in text.split(",") if kw.strip()]
        # Limita a 5 palavras-chave
        return keywords[:5]
    
    def get_ignored_extensions_list(self):
        """Retorna a lista de extensões a ignorar."""
        text = self.ignored_extensions_var.get().strip()
        if not text:
            return []
        # Separa por vírgula e limpa espaços
        extensions = [ext.strip().lower().lstrip('.') for ext in text.split(",") if ext.strip()]
        return extensions
    
    # ========== GERENCIAMENTO DE CONFIGURAÇÃO ==========
    
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
            "keywords_match_all": self.keywords_match_all_var.get(),
            "process_zip": self.process_zip_var.get(),
            "use_cache": self.use_cache_var.get(),
            "ignored_extensions": self.get_ignored_extensions_list(),
            "enable_cloud_hydration": self.enable_cloud_hydration_var.get(),
            "last_opened_folder": self.last_opened_folder
        }
    
    def store_initial_config(self):
        """Armazena a configuração inicial para comparação."""
        self.config_manager.store_initial_config(self.get_current_config())
        self.config_changed = False
        self.update_save_button_state()
    
    def check_config_changed(self):
        """Verifica se a configuração foi alterada."""
        current = self.get_current_config()
        changed = self.config_manager.has_changed(current)
        if changed != self.config_changed:
            self.config_changed = changed
            self.update_save_button_state()
    
    def _on_use_cache_changed(self):
        """Callback quando a opção use_cache é alterada."""
        use_cache = self.use_cache_var.get()
        
        # Se cache foi desativado, remove a pasta de cache
        if not use_cache:
            from ..core.cache_manager import CacheManager
            cache_manager = CacheManager()
            
            try:
                cache_path = cache_manager.cache_file.parent
                if cache_path.exists():
                    import shutil
                    shutil.rmtree(cache_path)
                    print(f"Cache removido: {cache_path}")
                    self.log_message("Cache de arquivos removido.", "info")
            except Exception as e:
                print(f"Aviso: Não foi possível remover cache: {e}")
        
        # Marca configuração como alterada
        self.check_config_changed()
    
    def update_save_button_state(self):
        """Atualiza o estado do botão de salvar."""
        if self.config_changed:
            self.status_var.set("⚠️ Configuração alterada - não salva")
        else:
            if not self.is_running:
                self.status_var.set("✅ Pronto")
    
    def setup_change_tracking(self):
        """Configura rastreamento de mudanças."""
        # Listbox não tem evento Modified, rastrearemos via botões que modificam a lista
        # (add_folder, remove_selected_folder, clear_folders já chamam check_config_changed)
        
        # Rastreia mudanças nas variáveis
        self.exclude_prefix_var.trace_add('write', lambda *args: self.check_config_changed())
        self.open_folder_var.trace_add('write', lambda *args: self.check_config_changed())
        self.open_file_var.trace_add('write', lambda *args: self.check_config_changed())
        self.use_sequence_var.trace_add('write', lambda *args: self.check_config_changed())
        self.history_limit_var.trace_add('write', lambda *args: self._on_history_limit_changed())
        self.keywords_var.trace_add('write', lambda *args: self.check_config_changed())
        self.keywords_match_all_var.trace_add('write', lambda *args: self.check_config_changed())
        self.ignored_extensions_var.trace_add('write', lambda *args: self.check_config_changed())
        self.process_zip_var.trace_add('write', lambda *args: self.check_config_changed())
        self.use_cache_var.trace_add('write', lambda *args: self._on_use_cache_changed())
        self.enable_cloud_hydration_var.trace_add('write', lambda *args: self.check_config_changed())
    
    def setup_keyboard_shortcuts(self):
        """Configura atalhos de teclado."""
        # Bind Enter para executar a seleção
        self.root.bind('<Return>', lambda event: self.execute_selection())
        
        # Tab já funciona por padrão no tkinter para navegação entre campos
        # Mas vamos garantir que os widgets principais estejam na ordem correta de focus
        # A ordem natural é: folders_listbox -> exclude_prefix_entry -> history_limit_spinbox 
        # -> keywords_entry -> checkboxes -> execute_btn -> save_config_btn
    
    def manual_save_config(self):
        """Salva a configuração manualmente."""
        self.save_config()
        self.store_initial_config()
        self.log_message("Configuração salva com sucesso!", "success")
        messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
    
    def _on_keywords_match_changed(self):
        """Callback quando o modo de combinação de palavras-chave muda."""
        text = "   ℹ️ Arquivo deve conter TODAS as palavras-chave" if self.keywords_match_all_var.get() else "   ℹ️ Arquivo deve conter ao menos UMA palavra-chave"
        
        # Atualiza na janela principal se existir
        if hasattr(self, 'keywords_info'):
            self.keywords_info.configure(text=text)
        
        # Atualiza no popup se existir
        if hasattr(self, 'keywords_info_popup'):
            self.keywords_info_popup.configure(text=text)
        
        self.check_config_changed()
    
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
    
    # ========== CANCELAMENTO E FECHAMENTO ==========
    
    def cancel_file_loading(self):
        """Cancela o carregamento do arquivo."""
        self.file_loader.cancel()
        self.log_message("\n⚠ Cancelamento solicitado pelo usuário...", "warning")
    
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
        
        # Limpa todas as pastas temporárias antes de fechar
        self._cleanup_temp_directories()
        
        self.root.destroy()
    
    # ========== GERENCIAMENTO DE HISTÓRICO ==========
    
    def _cleanup_temp_directories(self):
        """Limpa todas as pastas temporárias criadas durante a sessão."""
        from ..core.file_picker import cleanup_temp_dir
        
        if not self.temp_directories:
            return
        
        print(f"[Limpeza] Removendo {len(self.temp_directories)} pasta(s) temporária(s)...")
        
        for temp_dir in self.temp_directories:
            try:
                cleanup_temp_dir(temp_dir)
                print(f"[Limpeza] ✓ Removida: {os.path.basename(temp_dir)}")
            except Exception as e:
                print(f"[Limpeza] ⚠ Não foi possível remover '{os.path.basename(temp_dir)}': {e}")
        
        self.temp_directories.clear()
        print(f"[Limpeza] Concluída!")
    
    def _register_temp_directory(self, temp_dir: str):
        """Registra um diretório temporário para limpeza posterior."""
        if temp_dir and temp_dir not in self.temp_directories:
            self.temp_directories.append(temp_dir)
    
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
        
        # Configura peso das colunas no frame
        self.history_buttons_frame.columnconfigure(0, weight=1)
        self.history_buttons_frame.columnconfigure(1, weight=0)
        
        # Cria novos botões
        for idx, file_path in enumerate(self.file_history):
            file_name = Path(file_path).name
            
            # Trunca nome se muito longo
            display_name = file_name if len(file_name) <= 40 else file_name[:37] + "..."
            
            # Botão principal (abre arquivo)
            btn = ttk.Button(
                self.history_buttons_frame,
                text=f"{idx + 1}. {display_name}",
                command=lambda fp=file_path: self.open_history_file(fp)
            )
            btn.grid(row=idx, column=0, sticky=(tk.W, tk.E), pady=2, padx=(0, 2))
            self.history_buttons.append(btn)
            
            # Botão '...' (abre pasta)
            folder_btn = ttk.Button(
                self.history_buttons_frame,
                text="...",
                command=lambda fp=file_path: self.open_history_folder(fp),
                width=3
            )
            folder_btn.grid(row=idx, column=1, sticky=tk.W, pady=2)
            self.history_buttons.append(folder_btn)
    
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
    
    def open_history_folder(self, file_path):
        """Abre a pasta onde está o arquivo do histórico."""
        try:
            folder_path = Path(file_path).parent
            if not folder_path.exists():
                messagebox.showerror("Erro", "Pasta não encontrada!")
                return
            
            open_folder(str(folder_path))
            self.log_message(f"Abrindo pasta: {folder_path}", "info")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir pasta: {e}")
    
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
    
    def _force_cloud_hydration(self, file_path):
        """Força hidratação completa de arquivo do Google Drive/OneDrive usando Cloud Files API.
        
        Retorna: True se conseguiu hidratar, False caso contrário
        """
        import ctypes
        from ctypes import wintypes
        import platform
        
        if platform.system() != "Windows":
            return True  # Não precisa em outros sistemas
        
        try:
            self.log_message("🔧 Verificando estado do arquivo na nuvem...", "info")
            
            # Carrega a DLL da Cloud Filter API
            try:
                cldapi = ctypes.WinDLL("CldApi.dll")
            except:
                self.log_message("   ⚠ CldApi.dll não disponível (Windows 10 1709+ necessário)", "warning")
                return True  # Continua sem a API
            
            # Verifica estado do arquivo
            CF_PLACEHOLDER_STATE_PLACEHOLDER = 0x00000001
            CF_PLACEHOLDER_STATE_PARTIALLY_ON_DISK = 0x00000020
            
            state = cldapi.CfGetPlaceholderStateFromFileInfo(
                wintypes.LPCWSTR(file_path),
                0  # FileBasicInfo
            )
            
            is_placeholder = (state & CF_PLACEHOLDER_STATE_PLACEHOLDER) or \
                           (state & CF_PLACEHOLDER_STATE_PARTIALLY_ON_DISK)
            
            if not is_placeholder and state != -1:
                self.log_message("   ✓ Arquivo já está local (não é placeholder)", "success")
                return True
            
            self.log_message("   📥 Arquivo é placeholder - forçando hidratação completa...", "info")
            
            # Abre o arquivo para obter handle
            GENERIC_READ = 0x80000000
            GENERIC_WRITE = 0x40000000
            FILE_SHARE_READ = 0x00000001
            OPEN_EXISTING = 3
            FILE_ATTRIBUTE_NORMAL = 0x00000080
            
            handle = ctypes.windll.kernel32.CreateFileW(
                wintypes.LPCWSTR(file_path),
                GENERIC_READ | GENERIC_WRITE,  # Precisa de escrita para hidratar
                FILE_SHARE_READ,  # Permite leitura simultânea
                None,  # lpSecurityAttributes
                OPEN_EXISTING,
                FILE_ATTRIBUTE_NORMAL,
                None  # hTemplateFile
            )
            
            if handle == -1 or handle == 0:
                error_code = ctypes.windll.kernel32.GetLastError()
                self.log_message(f"   ❌ Erro ao abrir arquivo (erro {error_code})", "error")
                return False
            
            try:
                # Força hidratação do arquivo inteiro
                # CfHydratePlaceholder(handle, startOffset, length, flags, overlapped)
                # length = -1 significa "arquivo inteiro"
                CF_HYDRATE_FLAG_NONE = 0x00000000
                
                result = cldapi.CfHydratePlaceholder(
                    handle,
                    ctypes.c_longlong(0),    # startOffset = 0 (início)
                    ctypes.c_longlong(-1),   # length = -1 (arquivo inteiro)
                    CF_HYDRATE_FLAG_NONE,    # flags = 0 (síncrono)
                    None  # overlapped = NULL
                )
                
                if result == 0:
                    self.log_message("   ✓ Hidratação iniciada com sucesso!", "success")
                    
                    # Aguarda a hidratação completar verificando o estado
                    import time
                    max_wait = 60  # Máximo 60 segundos
                    waited = 0
                    
                    while waited < max_wait:
                        time.sleep(2)
                        waited += 2
                        
                        # Verifica estado novamente
                        new_state = cldapi.CfGetPlaceholderStateFromFileInfo(
                            wintypes.LPCWSTR(file_path),
                            0
                        )
                        
                        # Se não é mais placeholder/partial, está pronto
                        is_still_placeholder = (new_state & CF_PLACEHOLDER_STATE_PLACEHOLDER) or \
                                             (new_state & CF_PLACEHOLDER_STATE_PARTIALLY_ON_DISK)
                        
                        if not is_still_placeholder or new_state == -1:
                            self.log_message(f"   ✓ Hidratação completa após {waited}s!", "success")
                            return True
                        
                        if waited % 10 == 0:
                            self.log_message(f"   ⏳ Aguardando hidratação... ({waited}s)", "info")
                    
                    self.log_message(f"   ⚠ Timeout aguardando hidratação (60s)", "warning")
                    return True  # Continua tentando mesmo assim
                    
                else:
                    error_code = ctypes.get_last_error()
                    self.log_message(f"   ⚠ CfHydratePlaceholder retornou {result} (erro {error_code})", "warning")
                    return False
                    
            finally:
                # Fecha o handle
                ctypes.windll.kernel32.CloseHandle(handle)
            
        except Exception as e:
            self.log_message(f"⚠ Erro ao forçar hidratação: {e}", "warning")
            return False
    
    def _force_file_download(self, file_path):
        """Força o download completo do arquivo da nuvem lendo-o progressivamente.
        
        Retorna: True se conseguiu ler o arquivo completo, False caso contrário
        """
        import os
        from pathlib import Path
        
        try:
            file_size = os.path.getsize(file_path)
            self.log_message(f"📥 Forçando download do arquivo ({file_size / (1024*1024):.1f} MB)...", "info")
            
            chunk_size = 1024 * 1024  # 1MB por chunk
            total_read = 0
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    total_read += len(chunk)
                    progress = (total_read / file_size) * 100
                    
                    # Atualiza progresso a cada 10MB
                    if total_read % (10 * 1024 * 1024) < chunk_size:
                        self.log_message(
                            f"⏳ Baixando: {progress:.1f}% ({total_read / (1024*1024):.1f} MB)",
                            "info"
                        )
            
            self.log_message(f"✓ Download completo: {total_read / (1024*1024):.1f} MB", "success")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Erro ao forçar download: {e}", "error")
            return False
    
    def _is_placeholder_file(self, file_path):
        """Verifica se o arquivo é um placeholder de nuvem.
        
        Retorna: True se é placeholder, False se é arquivo normal
        """
        import ctypes
        from ctypes import wintypes
        import platform
        
        if platform.system() != "Windows":
            return False
        
        try:
            # Tenta usar Cloud Files API para verificar
            try:
                cldapi = ctypes.WinDLL("CldApi.dll")
                
                CF_PLACEHOLDER_STATE_PLACEHOLDER = 0x00000001
                CF_PLACEHOLDER_STATE_PARTIALLY_ON_DISK = 0x00000020
                
                state = cldapi.CfGetPlaceholderStateFromFileInfo(
                    wintypes.LPCWSTR(file_path),
                    0
                )
                
                is_placeholder = (state & CF_PLACEHOLDER_STATE_PLACEHOLDER) or \
                               (state & CF_PLACEHOLDER_STATE_PARTIALLY_ON_DISK)
                
                if is_placeholder:
                    self.log_message("📋 Arquivo detectado como placeholder de nuvem", "info")
                    return True
                else:
                    self.log_message("✓ Arquivo já está local (não é placeholder)", "success")
                    return False
                    
            except:
                # API não disponível, tenta detecção manual
                pass
            
            # Fallback: tenta ler e validar conteúdo
            from pathlib import Path
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.rar', '.cbr']:
                import rarfile
                try:
                    with rarfile.RarFile(file_path) as rf:
                        file_list = rf.namelist()
                        for filename in sorted(file_list)[:1]:  # Apenas primeiro
                            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                                with rf.open(filename) as img_file:
                                    test_read = img_file.read(1024)
                                    if len(test_read) < 100:
                                        self.log_message("📋 Arquivo detectado como placeholder (leitura < 100 bytes)", "info")
                                        return True
                                break
                    self.log_message("✓ Arquivo validado como local", "success")
                    return False
                except:
                    # Se não conseguiu abrir, assume que é placeholder
                    self.log_message("⚠ Não foi possível validar - assumindo placeholder", "warning")
                    return True
            
            elif file_ext in ['.zip', '.cbz']:
                import zipfile
                try:
                    with zipfile.ZipFile(file_path) as zf:
                        file_list = zf.namelist()
                        for filename in sorted(file_list)[:1]:
                            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                                with zf.open(filename) as img_file:
                                    test_read = img_file.read(1024)
                                    if len(test_read) < 100:
                                        self.log_message("📋 Arquivo detectado como placeholder (leitura < 100 bytes)", "info")
                                        return True
                                break
                    self.log_message("✓ Arquivo validado como local", "success")
                    return False
                except:
                    self.log_message("⚠ Não foi possível validar - assumindo placeholder", "warning")
                    return True
            
            # Outros formatos: assume que está OK
            return False
            
        except Exception as e:
            self.log_message(f"⚠ Erro ao verificar placeholder: {e}", "warning")
            return False
    
    def _load_file_to_buffer(self, file_path):
        """Verifica se arquivo é placeholder e força hidratação se necessário.
        
        Retorna: True se arquivo está pronto, False se falhou
        """
        import time
        from pathlib import Path
        
        # VERIFICA SE HIDRATAÇÃO ESTÁ HABILITADA
        if not self.enable_cloud_hydration_var.get():
            # Hidratação desabilitada - não verifica placeholder
            self.log_message("ℹ Hidratação de nuvem desabilitada - processando arquivo diretamente", "info")
            return True
        
        # VERIFICA SE É PLACEHOLDER
        if not self._is_placeholder_file(file_path):
            # Arquivo já está local, não precisa hidratar
            self.log_message("✓ Arquivo local - pode extrair diretamente", "success")
            return True
        
        # É PLACEHOLDER - PRECISA HIDRATAR
        self.log_message("🔄 Arquivo é placeholder - iniciando hidratação...", "info")
        
        max_retries = 3  # 3 tentativas
        retry_delay = 10   # 10 segundos entre tentativas
        
        for attempt in range(1, max_retries + 1):
            try:
                self.log_message(f"🔍 Tentativa {attempt}/{max_retries}...", "info")
                
                # FASE ÚNICA: FORÇA HIDRATAÇÃO E AGUARDA
                if attempt == 1:
                    hydration_ok = self._force_cloud_hydration(file_path)
                    if not hydration_ok:
                        self.log_message("⚠ API de hidratação falhou - usando método alternativo...", "warning")
                        # Fallback: força download lendo o arquivo
                        self._force_file_download(file_path)
                
                # Aguarda progressivamente mais tempo
                wait_time = retry_delay * attempt  # 10s, 20s, 30s
                self.log_message(f"⏳ Aguardando hidratação completar ({wait_time}s)...", "info")
                time.sleep(wait_time)
                
                # Valida se o arquivo agora está hidratado tentando abrir como RAR
                file_ext = Path(file_path).suffix.lower()
                
                if file_ext in ['.rar', '.cbr']:
                    import rarfile
                    try:
                        with rarfile.RarFile(file_path) as rf:
                            file_list = rf.namelist()
                            # Tenta ler primeira imagem
                            for filename in sorted(file_list):
                                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                                    with rf.open(filename) as img_file:
                                        test_read = img_file.read(1024)
                                        if len(test_read) >= 100:
                                            self.log_message("✓ Arquivo hidratado e validado!", "success")
                                            return True
                                        else:
                                            self.log_message(f"⚠ Ainda placeholder (lidos {len(test_read)} bytes)", "warning")
                                            break
                                    break
                    except Exception as e:
                        self.log_message(f"⚠ Erro ao validar: {e}", "warning")
                
                elif file_ext in ['.zip', '.cbz']:
                    import zipfile
                    try:
                        with zipfile.ZipFile(file_path) as zf:
                            file_list = zf.namelist()
                            for filename in sorted(file_list):
                                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                                    with zf.open(filename) as img_file:
                                        test_read = img_file.read(1024)
                                        if len(test_read) >= 100:
                                            self.log_message("✓ Arquivo hidratado e validado!", "success")
                                            return True
                                        else:
                                            self.log_message(f"⚠ Ainda placeholder (lidos {len(test_read)} bytes)", "warning")
                                            break
                                    break
                    except Exception as e:
                        self.log_message(f"⚠ Erro ao validar: {e}", "warning")
                
                # Se não validou, tenta novamente
                if attempt < max_retries:
                    self.log_message("⚠ Arquivo ainda não está pronto - tentando novamente...", "warning")
                else:
                    self.log_message("❌ Arquivo não ficou pronto após todas as tentativas", "error")
                    return False
                    
            except Exception as e:
                self.log_message(f"❌ Erro: {e}", "error")
                if attempt >= max_retries:
                    return False
        
        return False
    
    # ========== EXTRAÇÃO DE IMAGENS ==========
    
    def _extract_first_image_from_zip(self, file_path):
        """Extrai a primeira imagem (jpg/png) de um arquivo compactado (ZIP/RAR/PDF).
        Lê diretamente do arquivo após hidratação (sem buffer na memória).
        
        Retorna:
            Tupla (PIL.Image, page_count) ou ("SYNCING", page_count) ou (None, 0)
        """
        try:
            # Verifica se o arquivo existe e tem tamanho razoável
            file_stat = Path(file_path).stat()
            if file_stat.st_size < 1000:
                self.log_message(f"Arquivo parece ser placeholder (tamanho: {file_stat.st_size} bytes)", "warning")
                return (None, 0)
            
            # FORÇA HIDRATAÇÃO DO ARQUIVO (aguarda estar pronto)
            if not self._load_file_to_buffer(file_path):
                # Hidratação falhou
                self.log_message("⚠ Não foi possível hidratar o arquivo", "warning")
                return ("SYNCING", 0)
            
            # Usa ArchiveExtractor para extrair imagem DIRETAMENTE DO ARQUIVO
            self.log_message(f"📖 Extraindo imagem diretamente do arquivo...", "info")
            image, page_count, status = self.archive_extractor.extract_first_image_from_file(file_path)
            
            self.log_message(f"Resultado: image={'presente' if image else 'None'}, pages={page_count}, status={status}", "info")
            
            # Trata status especiais
            if status == 'SYNCING':
                return ("SYNCING", page_count)
            elif status == '7Z_NOT_SUPPORTED':
                self.log_message("⚠ Arquivo é 7-Zip (.7z), formato não suportado ainda", "warning")
                self.log_message("Extraia manualmente ou converta para ZIP/RAR", "info")
                return (None, 0)
            elif status == 'VIDEO_ERROR':
                self.log_message("⚠ Erro ao extrair frame do vídeo", "warning")
                self.log_message("💡 Certifique-se de que o FFmpeg está instalado:", "info")
                self.log_message("   Windows: winget install Gyan.FFmpeg", "info")
                self.log_message("   Ou baixe em: https://www.gyan.dev/ffmpeg/builds/", "info")
                return (None, 0)
            elif status == 'AUDIO_FILE':
                self.log_message("ℹ Arquivo de áudio - sem prévia visual disponível", "info")
                return (None, 0)
            elif status == 'UNKNOWN_FORMAT':
                self.log_message("Não foi possível extrair imagem do arquivo", "warning")
                return (None, 0)
            
            return (image, page_count)
            
        except Exception as e:
            self.log_message(f"Erro ao extrair imagem do arquivo: {e}", "error")
            self.log_message(traceback.format_exc(), "error")
            return (None, 0)
    

    
    def _analyze_file_and_display_info(self, file_path):
        """Analisa arquivo e exibe tabela com informações."""
        try:
            # Usa FileAnalyzer para obter informações
            info = self.file_analyzer.analyze_file(file_path)
            
            # Formata e exibe a tabela
            table = self.file_analyzer.format_file_info_table(info)
            self.log_message("\n" + table, "info")
            
        except Exception as e:
            self.log_message(f"Erro ao analisar arquivo: {e}", "error")
    
    # ========== ANIMAÇÃO DE LOADING ==========
    
    def _create_loading_animation_frames(self):
        """Cria frames para animação de loading."""
        import math
        from PIL import ImageDraw
        
        frames = []
        size = (200, 280)
        num_frames = 12
        num_dots = 8
        
        for frame in range(num_frames):
            # Cria imagem de fundo
            img = Image.new('RGB', size, color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
            # Centro da imagem
            center_x = size[0] // 2
            center_y = size[1] // 2
            
            # Raio do círculo de pontos
            radius = 40
            dot_radius = 6
            
            # Desenha os pontos
            for i in range(num_dots):
                angle = (i / num_dots) * 2 * math.pi - (frame / num_frames) * 2 * math.pi
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                
                # Opacidade varia com a posição
                opacity = int(255 * (0.3 + 0.7 * (i / num_dots)))
                color = (100, 150, 200, opacity)
                
                # Desenha o ponto
                draw.ellipse(
                    [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                    fill=(100, 150, 200)
                )
            
            # Adiciona texto
            try:
                from PIL import ImageFont
                # Tenta usar fonte padrão
                font = ImageFont.truetype("arial.ttf", 14)
            except:
                font = None
            
            text = "Buscando arquivo..."
            # Calcula posição do texto
            if font:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:
                text_width = len(text) * 7
                text_height = 12
            
            text_x = center_x - text_width // 2
            text_y = center_y + radius + 30
            
            draw.text((text_x, text_y), text, fill='#333333', font=font)
            
            frames.append(img)
        
        return frames
    
    def _start_loading_animation(self):
        """Inicia a animação de loading."""
        if not self.loading_animation_frames:
            self.loading_animation_frames = self._create_loading_animation_frames()
        
        self.loading_animation_running = True
        self.loading_animation_index = 0
        self._animate_loading_frame()
    
    def _animate_loading_frame(self):
        """Atualiza um frame da animação."""
        if not self.loading_animation_running:
            return
        
        try:
            # Pega o frame atual
            frame = self.loading_animation_frames[self.loading_animation_index]
            photo = ImageTk.PhotoImage(frame)
            
            # Armazena referência
            self.current_image = photo
            
            # Atualiza label
            self.thumbnail_label.configure(image=photo, text="")
            
            # Avança para próximo frame
            self.loading_animation_index = (self.loading_animation_index + 1) % len(self.loading_animation_frames)
            
            # Agenda próximo frame (83ms = ~12 FPS)
            self.loading_animation_job = self.root.after(83, self._animate_loading_frame)
        except:
            self.loading_animation_running = False
    
    def _stop_loading_animation(self):
        """Para a animação de loading."""
        self.loading_animation_running = False
        if self.loading_animation_job:
            self.root.after_cancel(self.loading_animation_job)
            self.loading_animation_job = None
        
        # Para também a animação da roleta
        self.stop_spinning_animation()
    
    # ========== DISPLAY DE THUMBNAILS ==========
    
    def _display_thumbnail(self, file_path):
        """Exibe a miniatura do arquivo selecionado."""
        self.log_message(f"\n=== Carregando miniatura de: {Path(file_path).name}", "info")
        
        # Analisa e exibe informações do arquivo em tabela
        self._analyze_file_and_display_info(file_path)
        
        try:
            # Obtém informações do tipo de arquivo
            file_ext = Path(file_path).suffix.lower()
            file_formats = self.file_analyzer.analyze_file(file_path)
            
            # Determina se é um arquivo de vídeo
            is_video = file_formats.get('detected_format', '').lower() in [
                'mp4', 'avi', 'mkv', 'webm', 'flv', 'mov', 'wmv'
            ]
            
            # Tenta extrair imagem do arquivo (se for ZIP/RAR/PDF/VIDEO)
            result = self._extract_first_image_from_zip(file_path)
            
            # Desempacota o resultado (pode ser tupla ou valor único)
            if isinstance(result, tuple):
                image, page_count = result
            else:
                image = result
                page_count = 0
            
            # Usa ThumbnailGenerator para criar imagens
            if image == "SYNCING":
                # Arquivo está sincronizando do OneDrive
                self.log_message("Exibindo mensagem de sincronização", "info")
                image = self.thumbnail_generator.create_syncing_thumbnail()
            elif image is None:
                # Se não conseguiu, usa imagem padrão
                self.log_message("Usando imagem padrão (arquivo não é ZIP/RAR ou não contém imagens)", "info")
                image = self.thumbnail_generator.create_default_thumbnail()
            else:
                # Cria thumbnail da imagem extraída
                # Para vídeos, usa modo 'contain' para ajustar automaticamente
                if is_video:
                    image = self.thumbnail_generator.create_thumbnail(image, fit_mode='contain')
                else:
                    image = self.thumbnail_generator.create_thumbnail(image)
            
            # Converte para formato do Tkinter
            photo = ImageTk.PhotoImage(image)
            
            # Armazena referência para evitar garbage collection
            self.current_image = photo
            
            # Atualiza o label
            self.thumbnail_label.configure(image=photo, text="")
            
            # FORÇA a renderização imediata da miniatura (BLOQUEANTE)
            self.root.update_idletasks()
            self.root.update()
            
            self.log_message("Miniatura exibida com sucesso!", "success")
            
            # Libera o buffer de memória após uso
            self.file_data_buffer = None
            
        except Exception as e:
            # Em caso de erro, mostra imagem padrão
            self.log_message(f"Erro ao exibir miniatura: {e}", "error")
            
            # Libera o buffer mesmo em caso de erro
            self.file_data_buffer = None
            
            try:
                image = self.thumbnail_generator.create_error_thumbnail()
                photo = ImageTk.PhotoImage(image)
                self.current_image = photo
                self.thumbnail_label.configure(image=photo, text="")
                
                # FORÇA a renderização imediata
                self.root.update_idletasks()
                self.root.update()
            except:
                self.thumbnail_label.configure(image="", text="Erro ao carregar imagem")
                self.root.update_idletasks()
                self.root.update()
    
    # ========== LOGGING ==========
    
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
    
    # ========== EXECUÇÃO PRINCIPAL ==========
    
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
        if hasattr(self, 'save_config_btn'):
            self.save_config_btn.configure(state='disabled')
        self.status_var.set("Buscando arquivos...")
        self.clear_log()
        
        # Inicia animação da roleta
        self.start_spinning_animation()
        
        keywords = self.get_keywords_list()
        
        thread = threading.Thread(target=self._execute_selection_thread, 
                                 args=(folders, self.exclude_prefix_var.get(), 
                                       self.open_folder_var.get(), self.open_file_var.get(),
                                       self.use_sequence_var.get(), keywords, 
                                       self.process_zip_var.get(), self.use_cache_var.get()))
        thread.daemon = True
        thread.start()
        
    def _execute_selection_thread(self, folders, exclude_prefix, open_folder_after, 
                                  open_file_after, use_sequence, keywords, process_zip, use_cache):
        """Executa a seleção em uma thread separada."""
        temp_dir_to_cleanup = None
        try:
            # Limpa pastas temporárias de buscas anteriores
            self._cleanup_temp_directories()
            
            # Limpa o buffer de memória no início de cada busca
            self.file_data_buffer = None
            import gc
            gc.collect()  # Força coleta de lixo para liberar memória
            
            self.log_message("=" * 70)
            self.log_message("Iniciando busca de arquivos...", "info")
            self.log_message(f"Pastas: {len(folders)}", "info")
            self.log_message(f"Prefixos: {exclude_prefix}", "info")
            self.log_message(f"Ignorando pastas com prefixo: .", "info")
            self.log_message(f"Seleção sequencial: {'Ativada' if use_sequence else 'Desativada'}", "info")
            self.log_message(f"Processar arquivos ZIP: {'Ativado' if process_zip else 'Desativado'}", "info")
            
            # Obtém extensões ignoradas
            ignored_extensions = self.get_ignored_extensions_list()
            if ignored_extensions:
                self.log_message(f"Extensões ignoradas: {', '.join(ignored_extensions)}", "info")
            
            if keywords:
                mode = "AND (todas)" if self.keywords_match_all_var.get() else "OR (ao menos uma)"
                self.log_message(f"Palavras-chave: {', '.join(keywords)} [Modo: {mode}]", "info")
            else:
                self.log_message("Palavras-chave: Nenhuma (todos os arquivos são elegíveis)", "info")
            
            self.log_message("=" * 70)
            
            start_time = time.time()
            
            # Usa lógica sequencial ou aleatória conforme configuração
            if use_sequence:
                file_result, selection_info = select_file_with_sequence_logic(
                    folders, exclude_prefix, use_sequence=True, keywords=keywords,
                    keywords_match_all=self.keywords_match_all_var.get(),
                    process_zip=process_zip, use_cache=use_cache, ignored_extensions=ignored_extensions
                )
                
                # Log do total de arquivos encontrados
                total_found = selection_info.get('total_files_found', 0)
                self.log_message(f"\n✓ ARQUIVOS ENCONTRADOS: {total_found}", "success" if total_found > 0 else "warning")
                
                if not file_result or not file_result['file_path']:
                    if keywords:
                        raise ValueError(f"Nenhum arquivo válido encontrado com as palavras-chave: {', '.join(keywords)}")
                    raise ValueError("Nenhum arquivo válido encontrado nas pastas informadas.")
                
                selected_file = file_result['file_path']
                temp_dir_to_cleanup = file_result.get('temp_dir')
                
                # Registra pasta temporária para limpeza ao iniciar nova busca ou fechar programa
                if temp_dir_to_cleanup:
                    self._register_temp_directory(temp_dir_to_cleanup)
                    self.log_message(f"\n📁 Pasta temporária criada: {os.path.basename(temp_dir_to_cleanup)}", "info")
                    self.log_message("   (Será removida ao iniciar nova busca ou fechar o programa)", "info")
                
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
                file_result = pick_random_file_with_zip_support(
                    folders, exclude_prefix, check_accessibility=False, 
                    keywords=keywords, keywords_match_all=self.keywords_match_all_var.get(),
                    process_zip=process_zip, use_cache=use_cache, ignored_extensions=ignored_extensions
                )
                
                if not file_result or not file_result['file_path']:
                    if keywords:
                        raise ValueError(f"Nenhum arquivo válido encontrado com as palavras-chave: {', '.join(keywords)}")
                    raise ValueError("Nenhum arquivo válido encontrado nas pastas informadas.")
                
                selected_file = file_result['file_path']
                temp_dir_to_cleanup = file_result.get('temp_dir')
                
                # Registra pasta temporária para limpeza ao iniciar nova busca ou fechar programa
                if temp_dir_to_cleanup:
                    self._register_temp_directory(temp_dir_to_cleanup)
                    self.log_message(f"\n📁 Pasta temporária criada: {os.path.basename(temp_dir_to_cleanup)}", "info")
                    self.log_message("   (Será removida ao iniciar nova busca ou fechar o programa)", "info")
                
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
            # Para a animação do botão
            self.root.after(0, self.stop_spinning_animation)
            
            # NÃO remove arquivos temporários aqui - eles precisam permanecer
            # disponíveis para o aplicativo abrir o arquivo
            # Serão removidos apenas ao iniciar nova busca ou fechar o programa
            
            self.is_running = False
            self.root.after(0, lambda: self.execute_btn.configure(state='normal'))
            self.root.after(0, lambda: self.execute_btn.grid())  # Mostra o botão de execução
            self.root.after(0, lambda: self.cancel_btn.grid_remove())  # Esconde o botão de cancelar
            self.root.after(0, self.update_save_button_state)
    
    # ========== SALVAR E CARREGAR CONFIGURAÇÃO ==========
    
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
            "keywords_match_all": self.keywords_match_all_var.get(),
            "ignored_extensions": self.ignored_extensions_var.get(),
            "process_zip": self.process_zip_var.get(),
            "use_cache": self.use_cache_var.get(),
            "enable_cloud_hydration": self.enable_cloud_hydration_var.get(),
            "file_history": self.file_history,
            "last_opened_folder": self.last_opened_folder
        }
        
        success = self.config_manager.save_config(config)
        if not success:
            self.log_message("Erro ao salvar configuração", "error")
            
    def load_config(self):
        """Carrega a configuração salva."""
        try:
            config = self.config_manager.load_config()
            config = self.config_manager.validate_config(config)
            
            # Restaurar pastas
            folders = config.get("folders", [])
            if folders:
                self.folders_listbox.delete(0, tk.END)
                for folder in folders:
                    self.folders_listbox.insert(tk.END, folder)
                self.log_message(f"Configuração carregada: {len(folders)} pasta(s)", "success")
            
            # Restaurar outras configurações
            self.exclude_prefix_var.set(config.get("exclude_prefix", "_L_,_W_"))
            self.open_folder_var.set(config.get("open_folder", True))
            self.open_file_var.set(config.get("open_file", True))
            self.use_sequence_var.set(config.get("use_sequence", True))
            self.process_zip_var.set(config.get("process_zip", True))
            
            self.use_cache_var.set(config.get("use_cache", True))
            
            self.enable_cloud_hydration_var.set(config.get("enable_cloud_hydration", False))
            self.keywords_var.set(config.get("keywords", ""))
            self.keywords_match_all_var.set(config.get("keywords_match_all", False))
            self.history_limit_var.set(config.get("history_limit", 5))
            
            # Carregar extensões ignoradas
            ignored_ext = config.get("ignored_extensions", [])
            if isinstance(ignored_ext, list):
                self.ignored_extensions_var.set(",".join(ignored_ext))
            elif isinstance(ignored_ext, str):
                self.ignored_extensions_var.set(ignored_ext)
            else:
                self.ignored_extensions_var.set("srt,sub,txt,nfo")
            
            # Atualiza texto informativo baseado no modo
            self._on_keywords_match_changed()
            
            # Restaurar histórico e última pasta
            self.file_history = config.get("file_history", [])
            self.last_opened_folder = config.get("last_opened_folder", None)
            
            self.update_history_buttons()
            
            # Forçar atualização da UI para refletir os valores carregados
            self.root.update_idletasks()
            
        except Exception as e:
            self.log_message(f"Erro ao carregar configuração: {e}", "error")


def main():
    root = tk.Tk()
    app = RandomFilePickerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
