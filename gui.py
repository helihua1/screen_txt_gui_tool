import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Dict, List, Callable
import threading

class ParagraphDetailWindow:
    """段落详情窗口，用于显示段落的完整内容"""
    
    def __init__(self, parent, title: str, content: str):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("600x400")
        self.window.resizable(True, True)
        
        # 创建文本区域
        text_frame = ttk.Frame(self.window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文本显示区域
        self.text_widget = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 10)
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 插入内容
        self.text_widget.insert(tk.END, content)
        self.text_widget.config(state=tk.DISABLED)  # 设置为只读
        
        # 关闭按钮
        close_button = ttk.Button(
            self.window, 
            text="关闭", 
            command=self.window.destroy
        )
        close_button.pack(pady=10)

class MainGUI:
    """主GUI界面类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文本段落批量处理工具")
        self.root.geometry("1000x900")
        self.root.resizable(True, True)
        
        # 数据存储
        self.current_data = {}  # 当前显示的数据 {文件名: [段落列表]}
        self.selected_items = {}  # 用户选择的项目 {文件名: [段落列表]}
        self.processor = None  # 文本处理器
        self.callback_functions = {}  # 回调函数
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 路径选择区域
        self.setup_path_selection(main_frame)
        
        # 功能选择区域
        self.setup_function_selection(main_frame)
        
        # 信息展示区域
        self.setup_info_display(main_frame)
        
        # 操作按钮区域
        self.setup_action_buttons(main_frame)
    
    def setup_path_selection(self, parent):
        """设置路径选择区域"""
        path_frame = ttk.LabelFrame(parent, text="路径选择", padding=10)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 文件路径选择
        file_frame = ttk.Frame(path_frame)
        file_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(file_frame, text="待处理文件路径:").pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_path_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        
        ttk.Button(
            file_frame, 
            text="选择文件夹", 
            command=self.select_files_directory
        ).pack(side=tk.RIGHT)
        
        # 配置文件路径选择
        config_frame = ttk.Frame(path_frame)
        config_frame.pack(fill=tk.X)
        
        ttk.Label(config_frame, text="配置文件路径:").pack(side=tk.LEFT)
        self.config_path_var = tk.StringVar()
        self.config_path_entry = ttk.Entry(config_frame, textvariable=self.config_path_var, width=50)
        self.config_path_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        
        ttk.Button(
            config_frame, 
            text="选择文件夹", 
            command=self.select_config_directory
        ).pack(side=tk.RIGHT)
    
    def setup_function_selection(self, parent):
        """设置功能选择区域"""
        func_frame = ttk.LabelFrame(parent, text="功能选择", padding=10)
        func_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.function_var = tk.StringVar(value="keyword")
        
        ttk.Radiobutton(
            func_frame, 
            text="删除带有关键词的段落", 
            variable=self.function_var, 
            value="keyword",
            command=self.on_function_change
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            func_frame, 
            text="删除带有英文句的段落", 
            variable=self.function_var, 
            value="english",
            command=self.on_function_change
        ).pack(anchor=tk.W)
        
        # 关键词显示区域
        self.keywords_frame = ttk.LabelFrame(func_frame, text="目标删除关键词", padding=5)
        self.keywords_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.keywords_text = scrolledtext.ScrolledText(
            self.keywords_frame, 
            height=3, 
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.keywords_text.pack(fill=tk.X)
    
    def setup_info_display(self, parent):
        """设置信息展示区域"""
        info_frame = ttk.LabelFrame(parent, text="待删除段落预览", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview容器
        tree_frame = ttk.Frame(info_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ("选择", "文件名", "匹配关键词", "段落内容")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        self.tree.heading("选择", text="选择")
        self.tree.heading("文件名", text="文件名")
        self.tree.heading("匹配关键词", text="匹配关键词")
        self.tree.heading("段落内容", text="段落内容")
        
        self.tree.column("选择", width=50, anchor=tk.CENTER, stretch=False)
        self.tree.column("文件名", width=200, anchor=tk.W, stretch=True)
        self.tree.column("匹配关键词", width=120, anchor=tk.W, stretch=False)
        self.tree.column("段落内容", width=600, anchor=tk.W, stretch=True)
        
        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置网格权重
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定事件
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-1>", self.on_item_click)
        
        # 全选/取消全选按钮
        select_frame = ttk.Frame(info_frame)
        select_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            select_frame, 
            text="全选", 
            command=self.select_all
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            select_frame, 
            text="取消全选", 
            command=self.deselect_all
        ).pack(side=tk.LEFT)
    
    def setup_action_buttons(self, parent):
        """设置操作按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 分析按钮
        ttk.Button(
            button_frame, 
            text="分析文件", 
            command=self.analyze_files
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # 执行删除按钮
        ttk.Button(
            button_frame, 
            text="执行选中段落删除", 
            command=self.execute_deletion
        ).pack(side=tk.LEFT)
    
    def select_files_directory(self):
        """选择待处理文件目录"""
        directory = filedialog.askdirectory(title="选择待处理文件目录")
        if directory:
            self.file_path_var.set(directory)
    
    def select_config_directory(self):
        """选择配置文件目录"""
        directory = filedialog.askdirectory(title="选择配置文件目录")
        if directory:
            self.config_path_var.set(directory)
    
    def on_function_change(self):
        """功能选择改变时的处理"""
        # 清空当前显示
        self.clear_display()
        
        # 更新关键词显示
        if self.function_var.get() == "keyword":
            self.update_keywords_display()
    
    def update_keywords_display(self):
        """更新关键词显示"""
        if not self.processor:
            return
        
        keywords = self.processor.config_manager.get_keywords()
        if keywords:
            keywords_text = " ".join(keywords)
        else:
            keywords_text = "未加载到关键词"
        
        self.keywords_text.config(state=tk.NORMAL)
        self.keywords_text.delete(1.0, tk.END)
        self.keywords_text.insert(1.0, keywords_text)
        self.keywords_text.config(state=tk.DISABLED)
    
    def clear_display(self):
        """清空显示区域"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_data = {}
        self.selected_items = {}
    
    def analyze_files(self):
        """分析文件"""
        if not self.file_path_var.get():
            messagebox.showerror("错误", "请选择待处理文件目录")
            return
        
        if not self.config_path_var.get():
            messagebox.showerror("错误", "请选择配置文件目录")
            return
        
        # 初始化处理器
        if not self.processor:
            from processor import TextProcessor
            self.processor = TextProcessor()
        
        self.processor.set_files_directory(self.file_path_var.get())
        self.processor.set_config_directory(self.config_path_var.get())
        
        # 在新线程中执行分析
        def analyze_thread():
            try:
                if self.function_var.get() == "keyword":
                    data = self.processor.find_keyword_paragraphs()
                else:
                    data = self.processor.find_english_paragraphs()
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.update_display(data))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"分析文件时出错: {e}"))
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def update_display(self, data: Dict[str, List]):
        """更新显示区域"""
        self.clear_display()
        self.current_data = data
        
        if not data:
            messagebox.showinfo("提示", "没有找到符合条件的段落")
            return
        
        # 填充数据
        for filename, items in data.items():
            for item in items:
                if isinstance(item, tuple):
                    # 关键词匹配模式：item是(paragraph, keyword)元组
                    paragraph, keyword = item
                    display_text = paragraph[:100] + "..." if len(paragraph) > 100 else paragraph
                    item_values = ("✓", filename, keyword, display_text)
                else:
                    # 英文检测模式：item是paragraph字符串
                    paragraph = item
                    display_text = paragraph[:100] + "..." if len(paragraph) > 100 else paragraph
                    item_values = ("✓", filename, "英文段落", display_text)
                
                tree_item = self.tree.insert("", tk.END, values=item_values)
                
                # 使用item的tags存储完整内容用于双击查看
                self.tree.item(tree_item, tags=(paragraph,))
        
        # 默认全选
        self.select_all()
        
        messagebox.showinfo("完成", f"分析完成，找到 {len(data)} 个文件包含符合条件的段落")
    
    def on_item_click(self, event):
        """单击项目时的处理 - 切换选择状态"""
        item = self.tree.identify_row(event.y)
        if item:
            column = self.tree.identify_column(event.x)
            # 只在点击选择列时切换状态
            if column == "#1":  # 选择列
                current_value = self.tree.item(item, "values")[0]
                new_value = "" if current_value == "✓" else "✓"
                self.tree.set(item, "选择", new_value)
                self.update_selected_items()
    
    def on_item_double_click(self, event):
        """双击项目时的处理"""
        item = self.tree.identify_row(event.y)
        if item:
            filename = self.tree.item(item, "values")[1]  # 文件名列现在是第2列
            tags = self.tree.item(item, "tags")
            paragraph_full = tags[0] if tags else ""
            
            if paragraph_full:
                ParagraphDetailWindow(
                    self.root, 
                    f"段落详情 - {filename}", 
                    paragraph_full
                )
    
    def select_all(self):
        """全选"""
        for item in self.tree.get_children():
            self.tree.set(item, "选择", "✓")
        self.update_selected_items()
    
    def deselect_all(self):
        """取消全选"""
        for item in self.tree.get_children():
            self.tree.set(item, "选择", "")
        self.update_selected_items()
    
    def update_selected_items(self):
        """更新选中的项目"""
        self.selected_items = {}
        
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[0] == "✓":  # 被选中
                filename = values[1]  # 文件名列现在是第2列
                tags = self.tree.item(item, "tags")
                paragraph_full = tags[0] if tags else ""
                
                if filename not in self.selected_items:
                    self.selected_items[filename] = []
                
                if paragraph_full:
                    self.selected_items[filename].append(paragraph_full)
    
    def execute_deletion(self):
        """执行删除操作"""
        if not self.selected_items:
            messagebox.showwarning("警告", "没有选择要删除的段落")
            return
        
        # 确认删除
        result = messagebox.askyesno(
            "确认删除", 
            f"确定要删除选中的 {len(self.selected_items)} 个文件中的段落吗？\n此操作不可撤销！"
        )
        
        if not result:
            return
        
        # 在新线程中执行删除
        def delete_thread():
            try:
                if self.function_var.get() == "keyword":
                    success = self.processor.process_keyword_deletion(self.selected_items)
                else:
                    success = self.processor.process_english_deletion(self.selected_items)
                
                if success:
                    self.root.after(0, lambda: messagebox.showinfo("完成", "删除操作完成"))
                    self.root.after(0, self.analyze_files)  # 重新分析
                else:
                    self.root.after(0, lambda: messagebox.showerror("错误", "删除操作失败"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"删除时出错: {e}"))
        
        threading.Thread(target=delete_thread, daemon=True).start()
    
    def run(self):
        """运行GUI"""
        self.root.mainloop() 