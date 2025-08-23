import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import pyperclip
import ctypes


class RoundedButton(tk.Canvas):
    """自定义圆角按钮"""
    def __init__(self, parent, text="", command=None, bg_color="#25ADF3", 
                 text_color="white", hover_color=None, width=120, height=40, 
                 font=("Microsoft YaHei UI", 10, "bold"), **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color or self._darken_color(bg_color)
        self.font = font
        self.width = width
        self.height = height
        self.is_pressed = False
        
        # 设置画布背景色，兼容不同父组件类型
        try:
            if hasattr(parent, 'cget'):
                parent_bg = parent.cget('bg')
            else:
                parent_bg = parent['bg'] if 'bg' in parent else '#2d2d2d'
            self.configure(bg=parent_bg)
        except:
            self.configure(bg='#2d2d2d')
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        self._draw_button()
    
    def _darken_color(self, color, factor=0.9):
        """使颜色变暗"""
        if color.startswith('#'):
            color = color[1:]
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(int(c * factor) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _draw_button(self, state="normal"):
        """绘制圆角按钮"""
        self.delete("all")
        
        # 选择颜色
        if state == "pressed":
            current_color = self._darken_color(self.bg_color, 0.8)
        elif state == "hover":
            current_color = self.hover_color
        else:
            current_color = self.bg_color
        
        # 计算圆角半径
        radius = min(self.width, self.height) // 2
        
        # 绘制圆角矩形（胶囊形状）
        self.create_oval(0, 0, radius*2, self.height, fill=current_color, outline="")
        self.create_oval(self.width-radius*2, 0, self.width, self.height, fill=current_color, outline="")
        self.create_rectangle(radius, 0, self.width-radius, self.height, fill=current_color, outline="")
        
        # 绘制文字
        self.create_text(self.width//2, self.height//2, text=self.text, 
                        fill=self.text_color, font=self.font, anchor="center")
    
    def _on_click(self, event):
        self.is_pressed = True
        self._draw_button("pressed")
    
    def _on_release(self, event):
        if self.is_pressed and self.command:
            self.command()
        self.is_pressed = False
        self._draw_button("hover")
    
    def _on_enter(self, event):
        if not self.is_pressed:
            self._draw_button("hover")
    
    def _on_leave(self, event):
        self.is_pressed = False
        self._draw_button("normal")
    
    def config_text(self, text):
        """更新按钮文字"""
        self.text = text
        self._draw_button()
    
    def config_colors(self, bg_color=None, text_color=None, hover_color=None):
        """更新按钮颜色"""
        if bg_color:
            self.bg_color = bg_color
        if text_color:
            self.text_color = text_color
        if hover_color:
            self.hover_color = hover_color
        else:
            self.hover_color = self._darken_color(self.bg_color)
        self._draw_button()


class AsymmetricChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("非对称加/解密器")
        self.root.geometry("1508x1080")
        
        # 配色方案
        self._init_color_schemes()
        
        self.root.configure(bg=self.colors['bg_main'])
        
        # 公钥输入框列表
        self.pubkey_entries = []
        self.encrypted_result_boxes = []
        
        self._setup_styles()
        self._create_layout()

    def _init_color_schemes(self):
        """初始化配色方案"""
        self.dark_colors = {
            'primary': '#25ADF3',    # 蓝色
            'secondary': '#A477D8',  # 紫色
            'accent': '#FF6C37',     # 橙色
            'bg_main': '#1a1a1a',    # 深色背景
            'bg_light': '#2d2d2d',   # 浅色背景
            'text_light': '#ffffff', # 白色文字
            'text_dark': '#333333',  # 深色文字
            'border': '#4a4a4a',     # 边框色
            'success': '#4CAF50',    # 成功色
            'warning': '#FFC107',    # 警告色
            'error': '#F44336'       # 错误色
        }
        
        self.colors = self.dark_colors

    def _setup_styles(self):
        """设置自定义样式"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # 主要标签样式
        style.configure("Title.TLabel", 
                       font=("Microsoft YaHei UI", 12, "bold"),
                       foreground=self.colors['text_light'],
                       background=self.colors['bg_main'])
        
        style.configure("Subtitle.TLabel",
                       font=("Microsoft YaHei UI", 10),
                       foreground=self.colors['text_light'],
                       background=self.colors['bg_light'])
        
        # 胶囊形状按钮样式 - 蓝色
        style.configure("Primary.TButton",
                       font=("Microsoft YaHei UI", 10, "bold"),
                       foreground="white",
                       background=self.colors['primary'],
                       borderwidth=0,
                       focuscolor="none",
                       padding=(20, 12),
                       relief="flat")
        
        style.map("Primary.TButton",
                 background=[('active', self._darken_color(self.colors['primary'])),
                           ('pressed', self._darken_color(self.colors['primary'], 0.8))])
        
        # 复制按钮样式 - 小型圆形
        style.configure("Copy.TButton",
                       font=("Microsoft YaHei UI", 8),
                       foreground="white",
                       background=self.colors['secondary'],
                       borderwidth=0,
                       focuscolor="none",
                       padding=(8, 8),
                       relief="flat")
        
        style.map("Copy.TButton",
                 background=[('active', self._darken_color(self.colors['secondary'])),
                           ('pressed', self._darken_color(self.colors['secondary'], 0.8))])
        
        # 加密按钮样式 - 橙色胶囊
        style.configure("Encrypt.TButton",
                       font=("Microsoft YaHei UI", 10, "bold"),
                       foreground="white",
                       background=self.colors['accent'],
                       borderwidth=0,
                       focuscolor="none",
                       padding=(20, 12),
                       relief="flat")
        
        style.map("Encrypt.TButton",
                 background=[('active', self._darken_color(self.colors['accent'])),
                           ('pressed', self._darken_color(self.colors['accent'], 0.8))])
        
        # 解密按钮样式 - 紫色胶囊
        style.configure("Decrypt.TButton",
                       font=("Microsoft YaHei UI", 10, "bold"),
                       foreground="white",
                       background=self.colors['secondary'],
                       borderwidth=0,
                       focuscolor="none",
                       padding=(20, 12),
                       relief="flat")
        
        style.map("Decrypt.TButton",
                 background=[('active', self._darken_color(self.colors['secondary'])),
                           ('pressed', self._darken_color(self.colors['secondary'], 0.8))])
        
        # 小按钮样式 - 用于+/-按钮
        style.configure("Small.TButton",
                       font=("Microsoft YaHei UI", 8, "bold"),
                       foreground="white",
                       background=self.colors['primary'],
                       borderwidth=0,
                       focuscolor="none",
                       padding=(8, 6),
                       relief="flat")
        
        style.map("Small.TButton",
                 background=[('active', self._darken_color(self.colors['primary'])),
                           ('pressed', self._darken_color(self.colors['primary'], 0.8))])
        
        # 主题切换按钮样式
        style.configure("Theme.TButton",
                       font=("Microsoft YaHei UI", 9),
                       foreground=self.colors['text_light'],
                       background=self.colors['bg_light'],
                       borderwidth=1,
                       focuscolor="none",
                       padding=(10, 6),
                       relief="solid",
                       bordercolor=self.colors['border'])
        
        style.map("Theme.TButton",
                 background=[('active', self.colors['border']),
                           ('pressed', self._darken_color(self.colors['border']))])
        
        # 框架样式
        style.configure("Keys.TLabelframe",
                       background=self.colors['bg_light'],
                       borderwidth=2,
                       relief="solid",
                       bordercolor=self.colors['primary'])
        
        style.configure("Keys.TLabelframe.Label",
                       font=("Microsoft YaHei UI", 12, "bold"),
                       foreground=self.colors['primary'],
                       background=self.colors['bg_light'])
        
        style.configure("Encrypt.TLabelframe",
                       background=self.colors['bg_light'],
                       borderwidth=2,
                       relief="solid",
                       bordercolor=self.colors['accent'])
        
        style.configure("Encrypt.TLabelframe.Label",
                       font=("Microsoft YaHei UI", 12, "bold"),
                       foreground=self.colors['accent'],
                       background=self.colors['bg_light'])
        
        style.configure("Decrypt.TLabelframe",
                       background=self.colors['bg_light'],
                       borderwidth=2,
                       relief="solid",
                       bordercolor=self.colors['secondary'])
        
        style.configure("Decrypt.TLabelframe.Label",
                       font=("Microsoft YaHei UI", 12, "bold"),
                       foreground=self.colors['secondary'],
                       background=self.colors['bg_light'])
        
        # 复选框样式
        style.configure("Custom.TCheckbutton",
                       font=("Microsoft YaHei UI", 9),
                       foreground=self.colors['text_light'],
                       background=self.colors['bg_light'],
                       focuscolor="none")

    def _update_custom_buttons(self):
        """更新自定义按钮颜色"""
        for button_info in self.custom_buttons:
            button = button_info['button']
            button_type = button_info['type']
            
            if button_type == 'primary':
                button.config_colors(bg_color=self.colors['primary'])
            elif button_type == 'encrypt':
                button.config_colors(bg_color=self.colors['accent'])
            elif button_type == 'decrypt':
                button.config_colors(bg_color=self.colors['secondary'])
            elif button_type == 'small':
                button.config_colors(bg_color=self.colors['primary'])
            elif button_type == 'theme':
                button.config_colors(
                    bg_color=self.colors['bg_light'], 
                    text_color=self.colors['text_light']
                )
            elif button_type == 'copy':
                button.config_colors(bg_color=self.colors['secondary'])
            
            # 更新按钮背景以匹配父容器
            try:
                if hasattr(button.master, 'cget'):
                    parent_bg = button.master.cget('bg')
                    if parent_bg:
                        button.configure(bg=parent_bg)
                    else:
                        button.configure(bg=self.colors['bg_light'])
                else:
                    button.configure(bg=self.colors['bg_light'])
            except Exception:
                button.configure(bg=self.colors['bg_light'])

    def _update_frame_colors(self):
        """更新所有Frame组件的背景色"""
        # 更新公钥输入控制框架
        if hasattr(self, 'pubkey_control_frame'):
            self.pubkey_control_frame.configure(bg=self.colors['bg_light'])
        
        if hasattr(self, 'keys_btn_frame'):
            self.keys_btn_frame.configure(bg=self.colors['bg_light'])
            
        if hasattr(self, 'encrypt_btn_frame'):
            self.encrypt_btn_frame.configure(bg=self.colors['bg_light'])

        if hasattr(self, 'decrypt_btn_frame'):
            self.decrypt_btn_frame.configure(bg=self.colors['bg_light'])

        if hasattr(self, 'guide_frame'):
            self.guide_frame.configure(style="Keys.TLabelframe")
            self.guide_label.configure(background=self.colors['bg_light'], foreground=self.colors['text_light'])

        # 更新公钥输入框架
        if hasattr(self, 'pubkey_entries_frame'):
            self.pubkey_entries_frame.configure(bg=self.colors['bg_light'])
        
        # 更新加密结果框架
        if hasattr(self, 'encrypted_results_frame'):
            self.encrypted_results_frame.configure(bg=self.colors['bg_light'])
            # 同时更新Canvas和外部容器
            if hasattr(self, 'results_canvas'):
                self.results_canvas.configure(bg=self.colors['bg_light'])
            if hasattr(self, 'results_container'):
                self.results_container.configure(bg=self.colors['bg_light'])
        
        # 更新所有公钥输入框的Frame
        for entry_data in self.pubkey_entries:
            if 'frame' in entry_data:
                entry_data['frame'].configure(bg=self.colors['bg_light'])
                # 更新标签
                if 'label' in entry_data:
                    entry_data['label'].configure(
                        fg=self.colors['text_light'], 
                        bg=self.colors['bg_light']
                    )
        
        # 更新加密结果框架中的子Frame
        for result_box in self.encrypted_result_boxes:
            if hasattr(result_box, 'configure'):
                try:
                    result_box.configure(bg=self.colors['bg_light'])
                    # 更新子组件
                    for child in result_box.winfo_children():
                        if hasattr(child, 'configure'):
                            try:
                                if 'Label' in str(type(child)):
                                    child.configure(
                                        fg=self.colors['text_light'], 
                                        bg=self.colors['bg_light']
                                    )
                                elif 'Frame' in str(type(child)):
                                    child.configure(bg=self.colors['bg_light'])
                                    # 确保Frame内的孙子组件也能更新背景
                                    for grandchild in child.winfo_children():
                                        if isinstance(grandchild, RoundedButton):
                                            grandchild.configure(bg=self.colors['bg_light'])
                            except:
                                pass
                except:
                    pass

    def _darken_color(self, color, factor=0.9):
        """使颜色变暗"""
        if color.startswith('#'):
            color = color[1:]
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(int(c * factor) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def _create_layout(self):
        """创建主要布局"""
        # 添加顶部标题和主题切换
        self.title_frame = tk.Frame(self.root, bg=self.colors['bg_main'], height=80)
        self.title_frame.pack(fill="x", padx=20, pady=(20, 10))
        self.title_frame.pack_propagate(False)
        
        self.title_label = tk.Label(self.title_frame, 
                              text="🔐 非对称加密解密器",
                              font=("Microsoft YaHei UI", 18, "bold"),
                              fg=self.colors['primary'],
                              bg=self.colors['bg_main'])
        self.title_label.pack(side="left", expand=True)
        
        # 关于按钮
        btn_about = RoundedButton(self.title_frame, text="关于",
                                command=self._show_about_window,
                                bg_color=self.colors['bg_light'],
                                text_color=self.colors['text_light'],
                                width=90, height=35,
                                font=("Microsoft YaHei UI", 10))
        btn_about.pack(side="right", padx=(0, 10))
        
        # 主要内容区域
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 三栏布局
        self.frame_keys = ttk.LabelFrame(self.main_frame, text="🔑 密钥对产生栏", 
                                        style="Keys.TLabelframe", padding=20)
        self.frame_keys.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")

        self.frame_encrypt = ttk.LabelFrame(self.main_frame, text="🔒 加密栏", 
                                           style="Encrypt.TLabelframe", padding=20)
        self.frame_encrypt.grid(row=0, column=1, padx=5, pady=0, sticky="nsew")

        self.frame_decrypt = ttk.LabelFrame(self.main_frame, text="🔓 解密栏", 
                                           style="Decrypt.TLabelframe", padding=20)
        self.frame_decrypt.grid(row=0, column=2, padx=(10, 0), pady=0, sticky="nsew")

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0) # 为指南区域预留空间

        self._build_keys_frame()
        self._build_encrypt_frame()
        self._build_decrypt_frame()
        self._build_guide_frame()

    def _create_textbox_with_copy(self, parent, height=5, width=50, key_type=None):
        """创建带复制按钮的文本框"""
        container = tk.Frame(parent, bg=self.colors['bg_light'])
        
        textbox = scrolledtext.ScrolledText(
            container,
            height=height, 
            width=width, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=self.colors['bg_main'],
            fg=self.colors['text_light'],
            insertbackground=self.colors['primary'],
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=self.colors['primary'],
            highlightbackground=self.colors['border']
        )
        textbox.pack(side="left", fill="both", expand=True)
        
        # 复制按钮镶嵌在右上角
        copy_btn = RoundedButton(container, text="📋", 
                               command=None, # 稍后设置
                               bg_color=self.colors['secondary'],
                               width=35, height=35,
                               font=("Microsoft YaHei UI", 11))
        copy_btn.command = lambda: self._copy_textbox_content(textbox, copy_btn, key_type)
        copy_btn.pack(side="right", anchor="ne", padx=(5, 0))
        
        return container, textbox

    def _create_textbox(self, parent, height=5, width=50):
        """创建普通文本框"""
        textbox = scrolledtext.ScrolledText(
            parent, 
            height=height, 
            width=width, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=self.colors['bg_main'],
            fg=self.colors['text_light'],
            insertbackground=self.colors['primary'],
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=self.colors['primary'],
            highlightbackground=self.colors['border']
        )
        return textbox

    def _copy_textbox_content(self, textbox, copy_btn, key_type=None):
        """复制文本框内容到剪贴板"""
        if key_type == 'privkey':
            proceed = messagebox.askokcancel("安全警告", 
                "您正在复制私钥。\n\n私钥是您的绝密凭证，请勿以任何形式泄露给任何人或在不安全的网络环境中传输！\n\n确定要继续复制吗？"
            )
            if not proceed:
                return

        content = textbox.get(1.0, tk.END).strip()
        if content:
            try:
                pyperclip.copy(content)
                original_text = copy_btn.text
                copy_btn.config_text("✓")
                copy_btn.config_colors(bg_color=self.colors['success'])
                self.root.after(2000, lambda: (
                    copy_btn.config_text(original_text),
                    copy_btn.config_colors(bg_color=self.colors['secondary'])
                ))
            except Exception as e:
                self._show_error_message("错误", f"❌ 复制失败: {str(e)}")
        else:
            self._show_warning_message("警告", "⚠️ 没有内容可复制")

    def _build_keys_frame(self):
        # 公钥标签
        pubkey_label = ttk.Label(self.frame_keys, text="🔐 公钥:", style="Subtitle.TLabel")
        pubkey_label.pack(anchor="w", pady=(0, 5))
        
        # 公钥文本框和复制按钮
        pubkey_container, self.pubkey_box = self._create_textbox_with_copy(self.frame_keys, height=6, key_type='pubkey')
        pubkey_container.pack(fill="x", pady=(0, 15))

        # 私钥标签
        privkey_label = ttk.Label(self.frame_keys, text="🔒 私钥:", style="Subtitle.TLabel")
        privkey_label.pack(anchor="w", pady=(0, 5))
        
        privkey_container, self.privkey_box = self._create_textbox_with_copy(self.frame_keys, height=6, key_type='privkey')
        privkey_container.pack(fill="x", pady=(0, 15))

        # 自动填充私钥到解密栏的选择框
        self.auto_fill_privkey = tk.BooleanVar(value=True)
        chk_auto_fill = ttk.Checkbutton(self.frame_keys, text="自动填充私钥到解密栏", 
                                       variable=self.auto_fill_privkey,
                                       style="Custom.TCheckbutton")
        chk_auto_fill.pack(anchor="w", pady=(0, 20))

        # 按钮容器
        self.keys_btn_frame = tk.Frame(self.frame_keys, bg=self.colors['bg_light'])
        self.keys_btn_frame.pack(fill="x", pady=5)

        # 生成密钥对按钮
        btn_gen_key = RoundedButton(self.keys_btn_frame, text="🎲 生成", 
                                   command=self.generate_keys,
                                   bg_color=self.colors['primary'],
                                   width=110, height=45)
        btn_gen_key.pack(side="left", expand=True, padx=2)

        # 保存密钥按钮
        btn_save_key = RoundedButton(self.keys_btn_frame, text="💾 保存",
                                     command=self._save_key_pair,
                                     bg_color=self.colors['primary'],
                                     width=110, height=45)
        btn_save_key.pack(side="left", expand=True, padx=2)
        
        # 加载密钥按钮
        btn_load_key = RoundedButton(self.keys_btn_frame, text="📂 加载",
                                     command=self._load_private_key,
                                     bg_color=self.colors['primary'],
                                     width=110, height=45)
        btn_load_key.pack(side="left", expand=True, padx=2)

        # 清空按钮
        btn_clear_keys = RoundedButton(self.keys_btn_frame, text="清空",
                                       command=self._clear_keys_frame_content,
                                       bg_color=self.colors['secondary'],
                                       width=110, height=45)
        btn_clear_keys.pack(side="left", expand=True, padx=2)

    def _build_encrypt_frame(self):
        # 输入消息标签
        msg_label = ttk.Label(self.frame_encrypt, text="💬 输入要发送的信息:", style="Subtitle.TLabel")
        msg_label.pack(anchor="w", pady=(0, 5))
        
        self.msg_to_encrypt = self._create_textbox(self.frame_encrypt, height=4)
        self.msg_to_encrypt.pack(fill="x", pady=(0, 15))

        # 公钥输入区域
        pubkeys_label = ttk.Label(self.frame_encrypt, text="🔑 接收方公钥:", style="Subtitle.TLabel")
        pubkeys_label.pack(anchor="w", pady=(0, 5))
        
        # 公钥输入控制框架
        self.pubkey_control_frame = tk.Frame(self.frame_encrypt, bg=self.colors['bg_light'])
        self.pubkey_control_frame.pack(fill="x", pady=(0, 5))
        
        # +/- 按钮
        btn_add_pubkey = RoundedButton(self.pubkey_control_frame, text="➕ 添加接收方", 
                                      command=self.add_pubkey_entry,
                                      bg_color=self.colors['primary'],
                                      width=160, height=45,
                                      font=("Microsoft YaHei UI", 10, "bold"))
        btn_add_pubkey.pack(side="left", padx=(0, 5))

        btn_remove_pubkey = RoundedButton(self.pubkey_control_frame, text="➖ 删除接收方", 
                                         command=self.remove_pubkey_entry,
                                         bg_color=self.colors['primary'],
                                         width=160, height=45,
                                         font=("Microsoft YaHei UI", 10, "bold"))
        btn_remove_pubkey.pack(side="left")
        
        # 公钥输入框容器
        self.pubkey_entries_frame = tk.Frame(self.frame_encrypt, bg=self.colors['bg_light'])
        self.pubkey_entries_frame.pack(fill="x", pady=(0, 15))
        
        # 初始化一个公钥输入框
        self.add_pubkey_entry()

        # 按钮容器
        self.encrypt_btn_frame = tk.Frame(self.frame_encrypt, bg=self.colors['bg_light'])
        self.encrypt_btn_frame.pack(pady=(0, 15))

        # 加密按钮
        btn_encrypt = RoundedButton(self.encrypt_btn_frame, text="🔒 加密!", 
                                   command=self.encrypt_message,
                                   bg_color=self.colors['accent'],
                                   width=220, height=45)
        btn_encrypt.pack(side="left", padx=(0, 10))
        
        # 清空加密栏按钮
        btn_clear_encrypt = RoundedButton(self.encrypt_btn_frame, text="清空",
                                          command=self._clear_encrypt_frame_content,
                                          bg_color=self.colors['secondary'],
                                          width=110, height=45)
        btn_clear_encrypt.pack(side="left")

        # 加密结果标签
        result_label = ttk.Label(self.frame_encrypt, text="📄 加密结果:", style="Subtitle.TLabel")
        result_label.pack(anchor="w", pady=(0, 5))
        
        # 加密结果容器
        self._create_scrollable_results_area()

    def _create_scrollable_results_area(self):
        """创建可滚动的加密结果区域"""
        container = tk.Frame(self.frame_encrypt, bg=self.colors['bg_light'])
        container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(container, bg=self.colors['bg_light'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        self.encrypted_results_frame = tk.Frame(canvas, bg=self.colors['bg_light'])
        
        self.encrypted_results_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.encrypted_results_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 保存对canvas和container的引用，以便在主题切换时更新颜色
        self.results_canvas = canvas
        self.results_container = container

    def add_pubkey_entry(self):
        """添加公钥输入框"""
        entry_frame = tk.Frame(self.pubkey_entries_frame, bg=self.colors['bg_light'])
        entry_frame.pack(fill="x", pady=(0, 5))
        
        label = tk.Label(entry_frame, text=f"公钥 {len(self.pubkey_entries) + 1}:", 
                        font=("Microsoft YaHei UI", 9),
                        fg=self.colors['text_light'], bg=self.colors['bg_light'])
        label.pack(anchor="w")
        
        textbox = self._create_textbox(entry_frame, height=3)
        textbox.pack(fill="x", pady=(2, 0))
        
        entry_data = {
            'frame': entry_frame,
            'label': label,
            'textbox': textbox
        }
        
        self.pubkey_entries.append(entry_data)
        self._update_pubkey_labels()

    def remove_pubkey_entry(self):
        """删除公钥输入框"""
        if len(self.pubkey_entries) > 1:  # 至少保留一个
            entry_data = self.pubkey_entries.pop()
            entry_data['frame'].destroy()
            self._update_pubkey_labels()

    def _update_pubkey_labels(self):
        """更新公钥标签编号"""
        for i, entry_data in enumerate(self.pubkey_entries):
            entry_data['label'].config(text=f"公钥 {i + 1}:")

    def _build_decrypt_frame(self):
        # 加密消息标签
        encrypted_msg_label = ttk.Label(self.frame_decrypt, text="📨 输入加密的消息:", style="Subtitle.TLabel")
        encrypted_msg_label.pack(anchor="w", pady=(0, 5))
        
        self.msg_to_decrypt = self._create_textbox(self.frame_decrypt, height=5)
        self.msg_to_decrypt.pack(fill="x", pady=(0, 15))

        # 私钥输入标签
        privkey_input_label = ttk.Label(self.frame_decrypt, text="🔐 输入私钥:", style="Subtitle.TLabel")
        privkey_input_label.pack(anchor="w", pady=(0, 5))
        
        self.privkey_input = self._create_textbox(self.frame_decrypt, height=5)
        self.privkey_input.pack(fill="x", pady=(0, 20))

        # 按钮容器
        self.decrypt_btn_frame = tk.Frame(self.frame_decrypt, bg=self.colors['bg_light'])
        self.decrypt_btn_frame.pack(pady=(0, 15))

        # 解密按钮 - 使用紫色
        btn_decrypt = RoundedButton(self.decrypt_btn_frame, text="🔓 解密！", 
                                   command=self.decrypt_message,
                                   bg_color=self.colors['secondary'],
                                   width=220, height=45)
        btn_decrypt.pack(side="left", padx=(0, 10))

        # 清空解密栏按钮
        btn_clear_decrypt = RoundedButton(self.decrypt_btn_frame, text="清空",
                                          command=self._clear_decrypt_frame_content,
                                          bg_color=self.colors['secondary'],
                                          width=110, height=45)
        btn_clear_decrypt.pack(side="left")

        # 解密结果标签
        result_label = ttk.Label(self.frame_decrypt, text="📝 解密结果:", style="Subtitle.TLabel")
        result_label.pack(anchor="w", pady=(0, 5))
        
        decrypt_container, self.decrypted_output = self._create_textbox_with_copy(self.frame_decrypt, height=5, key_type='decrypted')
        decrypt_container.pack(fill="both", expand=True)

    def _build_guide_frame(self):
        """创建使用指南区域"""
        guide_frame = ttk.LabelFrame(self.main_frame, text="💡 使用指南", 
                                     style="Keys.TLabelframe", padding=15)
        guide_frame.grid(row=1, column=0, columnspan=3, padx=0, pady=(10, 0), sticky="ew")

        # 标题和折叠按钮
        title_bar = tk.Frame(guide_frame, bg=self.colors['bg_light'])
        title_bar.pack(fill="x")

        guide_title_label = ttk.Label(title_bar, text="💡 使用指南", style="Subtitle.TLabel")
        guide_title_label.pack(side="left", pady=(0, 5))

        self.toggle_guide_btn = RoundedButton(title_bar, text="显示", 
                                             command=self._toggle_guide,
                                             bg_color=self.colors['primary'],
                                             width=100, height=30,
                                             font=("Microsoft YaHei UI", 9, "bold"))
        self.toggle_guide_btn.pack(side="left", padx=10)

        guide_text = """
💬冬雪莲：
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvttuUCcvHFuKHmW9vcm6
-----END PUBLIC KEY-----这是我的公钥
💬孙笑川：
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsoFhXJ6iJ2nZV9nqGqMS
-----END PUBLIC KEY-----这是我的公钥
^ 注：两人把自己的公钥给对方，私钥自己保管，不要泄露

💬冬雪莲：WQ_HJlpPGq…………gSdxQZCvkMv-PzUjDWg_OM6cQoJtkXCJU88htXypEg==
💬孙笑川：收到
^ 注：东雪莲用孙笑川提供的公钥加密“我是罕见”，然后发送给孙笑川，孙笑川收到后解密得到冬雪莲发送的“我是罕见”
^ 该过程中，除了东雪莲和孙笑川，其他人(包括QQ/微信/tg后台)都无法解密

Q: 这安全吗？
A: 安全, 软件本身是开源且不需要联网的(这意味着所有人都可以审查代码来确保软件本身没有作妖)，除非某一天超级计算机被发明或者你作死泄露了私钥。
不过，请注意其他可能窃取你聊天记录的方式(尤其是输入法)
        """

        self.guide_label = ttk.Label(guide_frame, text=guide_text.strip(), 
                                style="Subtitle.TLabel", justify="left")
        
        self.guide_frame = guide_frame
        self.guide_collapsed = True # 默认折叠

    def _toggle_guide(self):
        """切换使用指南的可见性"""
        if self.guide_collapsed:
            # 展开
            self.guide_label.pack(fill="x", pady=(10, 0))
            self.toggle_guide_btn.config_text("隐藏")
            self.guide_collapsed = False
        else:
            # 折叠
            self.guide_label.pack_forget()
            self.toggle_guide_btn.config_text("显示")
            self.guide_collapsed = True

    def _show_about_window(self):
        """显示关于窗口"""
        about_win = tk.Toplevel(self.root)
        about_win.title("关于 非对称加密聊天器")
        about_win.geometry("1280x720")
        about_win.configure(bg=self.colors['bg_main'])
        about_win.transient(self.root)
        about_win.grab_set()

        # 使窗口居中
        win_x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
        win_y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (300 // 2)
        about_win.geometry(f"+{win_x}+{win_y}")

        about_frame = tk.Frame(about_win, bg=self.colors['bg_light'], padx=20, pady=20)
        about_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ttk.Label(about_frame, text="关于应用",
                                style="Title.TLabel",
                                font=("Microsoft YaHei UI", 16, "bold"),
                                foreground=self.colors['primary'],
                                background=self.colors['bg_light'])
        title_label.pack(pady=(0, 15))

        # 在这里替换成你的关于文本
        about_text = """
【关于「Deeptalk」】
----------------------------------------------------
【简介】
为了对抗无处不在的网络审查以及应用后台对个人隐私的泄漏，我开发了这款非对称加/解密器。
它是一个完全在您本地电脑上运行的非对称加密聊天辅助工具。
理论上，只要您不泄露私钥，您的聊天记录将无法被任何人破译。
【安全性】
非对称加密是一种端对端加密，理论上，除非您泄露私钥，否则您的聊天记录无法被任何人破译。
不过，请注意其他可能窃取你聊天记录的方式(尤其是输入法)
【技术】
- 加密标准： RSA-2048 位非对称加密+PKCS1_OAEP。
- 开源可信：本应用完全开源，所有代码均可被公开审查，以证明其不含任何后门。你也可以自行构建
- 本地运行：所有密钥的生成、加密和解密过程，均在本地完成。
【开源协议】
本应用基于 MIT 协议开源，您可以自由地使用、修改和分发本应用。
----------------------------------------------------
本人编程水平有限，代码简单，请见谅。
项目地址: https://github.com/
相关链接：
- RSA 加密算法： https://www.bilibili.com/video/BV1Eo4y1y7Dh/
- 非对称加密： https://zh.wikipedia.org/wiki/非对称加密
"""
        
        text_widget = tk.Text(about_frame, wrap=tk.WORD,
                              bg=self.colors['bg_light'],
                              fg=self.colors['text_light'],
                              font=("Microsoft YaHei UI", 10),
                              relief="flat",
                              highlightthickness=0)
        text_widget.insert(tk.END, about_text)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True)

        ok_button = RoundedButton(about_frame, text="确定",
                                  command=about_win.destroy,
                                  bg_color=self.colors['primary'],
                                  width=100, height=35)
        ok_button.pack(pady=(15, 0))
        
        # 确保圆角按钮在Toplevel中也能正确显示背景色
        ok_button.configure(bg=self.colors['bg_light'])

    def _clear_keys_frame_content(self):
        """清空密钥栏内容"""
        self.pubkey_box.delete(1.0, tk.END)
        self.privkey_box.delete(1.0, tk.END)
        # 如果自动填充开启，也清空解密栏的私钥
        if self.auto_fill_privkey.get():
            self.privkey_input.delete(1.0, tk.END)

    def _clear_encrypt_frame_content(self):
        """清空加密栏内容"""
        self.msg_to_encrypt.delete(1.0, tk.END)
        # 移除所有公钥输入框
        while len(self.pubkey_entries) > 0:
            entry_data = self.pubkey_entries.pop()
            entry_data['frame'].destroy()
        # 再重新添加一个
        self.add_pubkey_entry()
        # 清空结果
        self._clear_encrypted_results()

    def _clear_decrypt_frame_content(self):
        """清空解密栏内容"""
        self.msg_to_decrypt.delete(1.0, tk.END)
        self.privkey_input.delete(1.0, tk.END)
        self.decrypted_output.delete(1.0, tk.END)

    def _save_key_pair(self):
        """保存密钥对到文件"""
        privkey_str = self.privkey_box.get(1.0, tk.END).strip()
        pubkey_str = self.pubkey_box.get(1.0, tk.END).strip()

        if not privkey_str or not pubkey_str:
            self._show_warning_message("警告", "⚠️ 密钥为空，无法保存")
            return

        filename = filedialog.asksaveasfilename(
            title="保存私钥",
            defaultextension=".pem",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(privkey_str)
                
                # 自动保存公钥
                pubkey_filename = filename.replace(".pem", "_pub.pem")
                with open(pubkey_filename, 'w') as f:
                    f.write(pubkey_str)
                
                self._show_success_message("成功", f"✅ 私钥已保存到: {filename}\n✅ 公钥已保存到: {pubkey_filename}")
            except Exception as e:
                self._show_error_message("错误", f"❌ 保存失败: {str(e)}")

    def _load_private_key(self):
        """从文件加载私钥，并派生公钥"""
        filename = filedialog.askopenfilename(
            title="选择私钥文件",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    privkey_str = f.read()
                
                # 导入私钥并派生公钥
                key = RSA.import_key(privkey_str)
                pubkey_str = key.publickey().export_key().decode()

                # 清空并填充
                self.privkey_box.delete(1.0, tk.END)
                self.privkey_box.insert(tk.END, privkey_str)
                self.pubkey_box.delete(1.0, tk.END)
                self.pubkey_box.insert(tk.END, pubkey_str)

                if self.auto_fill_privkey.get():
                    self.privkey_input.delete(1.0, tk.END)
                    self.privkey_input.insert(tk.END, privkey_str)
                
                self._show_success_message("成功", "✅ 密钥加载成功！")

            except Exception as e:
                self._show_error_message("错误", f"❌ 加载失败: {str(e)}")

    def generate_keys(self):
        """生成密钥对"""
        try:
            key = RSA.generate(2048)
            private_key = key.export_key().decode()
            public_key = key.publickey().export_key().decode()

            self.pubkey_box.delete(1.0, tk.END)
            self.pubkey_box.insert(tk.END, public_key)
            self.privkey_box.delete(1.0, tk.END)
            self.privkey_box.insert(tk.END, private_key)
            
            # 修复自动填充私钥功能
            if self.auto_fill_privkey.get():
                self.privkey_input.delete(1.0, tk.END)
                self.privkey_input.insert(tk.END, private_key)
                
            self._show_success_message("成功", "密钥对生成成功！")
        except Exception as e:
            self._show_error_message("错误", f"❌ 密钥生成失败: {str(e)}")

    def _clear_encrypted_results(self):
        """清空加密结果显示区域"""
        for box in self.encrypted_result_boxes:
            box.destroy()
        self.encrypted_result_boxes.clear()

    def encrypt_message(self):
        """加密消息"""
        message = self.msg_to_encrypt.get(1.0, tk.END).strip()
        if not message:
            self._show_warning_message("警告", "⚠️ 请输入要加密的消息")
            return

        # 获取所有公钥
        pubkeys = []
        for entry_data in self.pubkey_entries:
            pubkey_text = entry_data['textbox'].get(1.0, tk.END).strip()
            if pubkey_text:
                pubkeys.append(pubkey_text)

        if not pubkeys:
            self._show_warning_message("警告", "⚠️ 请至少输入一个公钥")
            return

        # 清空之前的结果
        self._clear_encrypted_results()

        # 对每个公钥进行加密
        for i, pubkey_str in enumerate(pubkeys):
            try:
                pubkey = RSA.import_key(pubkey_str)
                cipher = PKCS1_OAEP.new(pubkey)
                chunk_size = pubkey.size_in_bytes() - 42

                chunks = [message.encode()[i:i + chunk_size] for i in range(0, len(message.encode()), chunk_size)]
                encrypted_chunks = []
                for chunk in chunks:
                    encrypted = cipher.encrypt(chunk)
                    encoded = base64.urlsafe_b64encode(encrypted).decode()
                    encrypted_chunks.append(encoded)

                result = "::".join(encrypted_chunks)
                
                # 创建结果显示框
                self._create_encrypted_result_box(i + 1, result)
                
            except (ValueError, TypeError, IndexError) as e:
                error_msg = "❌ 公钥格式错误，请确保其为有效的 PEM 格式。"
                self._create_encrypted_result_box(i + 1, error_msg, is_error=True)
            except Exception as e:
                self._create_encrypted_result_box(i + 1, f"[❌ 未知错误] {str(e)}", is_error=True)

    def _create_encrypted_result_box(self, index, content, is_error=False):
        """创建加密结果显示框"""
        result_frame = tk.Frame(self.encrypted_results_frame, bg=self.colors['bg_light'])
        result_frame.pack(fill="x", pady=(0, 10))
        
        label_text = f"接收方 {index} 的加密结果:"
        if is_error:
            label_text = f"接收方 {index} 加密失败:"
            
        label = tk.Label(result_frame, text=label_text,
                        font=("Microsoft YaHei UI", 9),
                        fg=self.colors['error'] if is_error else self.colors['text_light'],
                        bg=self.colors['bg_light'])
        label.pack(anchor="w")
        
        if not is_error:
            container, textbox = self._create_textbox_with_copy(result_frame, height=4, key_type='encrypted')
            container.pack(fill="x", pady=(2, 0))
            textbox.insert(tk.END, content)
            textbox.config(state="disabled")  # 只读
            self.encrypted_result_boxes.append(result_frame)
        else:
            error_label = tk.Label(result_frame, text=content,
                                  font=("Consolas", 9),
                                  fg=self.colors['error'],
                                  bg=self.colors['bg_light'],
                                  wraplength=300,
                                  justify="left")
            error_label.pack(anchor="w", pady=(2, 0))
            self.encrypted_result_boxes.append(result_frame)

    def decrypt_message(self):
        """解密消息"""
        encrypted_text = self.msg_to_decrypt.get(1.0, tk.END).strip()
        privkey_str = self.privkey_input.get(1.0, tk.END).strip()
        if not encrypted_text or not privkey_str:
            self._show_warning_message("警告", "⚠️ 请输入加密消息和私钥")
            return

        try:
            privkey = RSA.import_key(privkey_str)
            cipher = PKCS1_OAEP.new(privkey)

            encrypted_chunks = encrypted_text.split("::")
            decrypted_bytes = b""
            for enc_chunk in encrypted_chunks:
                decoded = base64.urlsafe_b64decode(enc_chunk)
                decrypted_bytes += cipher.decrypt(decoded)

            decrypted = decrypted_bytes.decode()
            self.decrypted_output.delete(1.0, tk.END)
            self.decrypted_output.insert(tk.END, decrypted)
            self._show_success_message("成功", "✅ 解密成功！")
        except (ValueError, TypeError, IndexError) as e:
            error_msg = (
                "❌ 解密失败，发生了值错误、类型错误或索引错误。\n\n"
                "可能的原因：\n"
                "1. 私钥格式不正确或已损坏。\n"
                "2. 加密消息的格式不正确（例如，不是有效的Base64编码）。\n"
                "3. 消息在传输过程中被篡改。\n\n"
                f"详细信息: {str(e)}"
            )
            self._show_error_message("解密错误", error_msg)
        except Exception as e:
            self._show_error_message("未知错误", f"❌ 发生未知错误: {str(e)}")
    
    def _show_success_message(self, title, message):
        """显示成功消息"""
        messagebox.showinfo(title, message)
    
    def _show_error_message(self, title, message):
        """显示错误消息"""
        messagebox.showerror(title, message)
    
    def _show_warning_message(self, title, message):
        """显示警告消息"""
        messagebox.showwarning(title, message)


if __name__ == "__main__":
    try:
        # 提升应用在高分屏下的清晰度 (仅Windows)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    app = AsymmetricChatApp(root)
    root.mainloop()

