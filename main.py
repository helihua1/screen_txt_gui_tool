#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本段落批量处理工具 - 主程序入口

功能：
1. 删除包含指定关键词的段落
2. 删除包含英文句子的段落

作者：AI Assistant
版本：1.0
"""

if __name__ == "__main__":
    try:
        from gui import MainGUI
        
        # 创建并运行GUI
        app = MainGUI()
        app.run()
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...") 