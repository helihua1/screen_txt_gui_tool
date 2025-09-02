import os
from typing import List

class ConfigManager:
    """配置文件管理类，负责读取和管理关键词配置"""
    
    def __init__(self, config_path: str = 'config.txt'):
        self.config_path = config_path
        self.keywords = []
    
    def load_keywords(self) -> List[str]:
        """从配置文件加载关键词列表"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # 检查是否包含 "keywords = " 前缀
                        if content.startswith('keywords = '):
                            # 移除 "keywords = " 前缀，然后按空格分割关键词
                            keywords_content = content[10:].strip()  # 移除 "keywords = " (10个字符)
                            self.keywords = [keyword.strip() for keyword in keywords_content.split() if keyword.strip()]
                        else:
                            # 兼容旧格式，直接按空格分割
                            self.keywords = [keyword.strip() for keyword in content.split() if keyword.strip()]
                    else:
                        self.keywords = []
            else:
                print(f"配置文件不存在: {self.config_path}")
                self.keywords = []
        except Exception as e:
            print(f"读取配置文件时出错: {e}")
            self.keywords = []
        
        return self.keywords
    
    def get_keywords(self) -> List[str]:
        """获取当前加载的关键词列表"""
        return self.keywords
    
    def set_config_path(self, path: str):
        """设置配置文件路径"""
        self.config_path = path
        self.load_keywords() 