import os
from typing import List

class ConfigManager:
    """配置文件管理类，负责读取和管理关键词配置"""
    
    def __init__(self, config_path: str = 'config.txt'):
        self.config_path = config_path
        self.keywords = []
        self.garbled_keywords = []
    
    def load_keywords(self) -> List[str]:
        """从配置文件加载关键词列表"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        # 检查是否包含 "keywords = " 前缀
                        if line.startswith('keywords ='):
                            # 移除 "keywords = " 前缀，然后按空格分割关键词
                            keywords_content = line[10:].strip()  # 移除 "keywords = " (10个字符)
                            self.keywords = [keyword.strip() for keyword in keywords_content.split() if keyword.strip()]
                            break
                    else:
                        # 如果没有找到 keywords = 行，设置为空列表
                        self.keywords = []
            else:
                print(f"配置文件不存在: {self.config_path}")
                self.keywords = []
        except Exception as e:
            print(f"读取配置文件时出错: {e}")
            self.keywords = []
        
        return self.keywords
    
    def load_garbled_keywords(self) -> List[str]:
        """从配置文件加载乱码检测关键词列表"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # 查找 "check_garbled = " 行
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line.startswith('check_garbled = '):
                                # 移除 "check_garbled = " 前缀，然后按空格分割关键词
                                garbled_content = line[16:].strip()  # 移除 "check_garbled = " (16个字符)
                                self.garbled_keywords = [keyword.strip() for keyword in garbled_content.split() if keyword.strip()]
                                break
                        else:
                            # 如果没有找到 check_garbled 行，设置为空列表
                            self.garbled_keywords = []
                    else:
                        self.garbled_keywords = []
            else:
                print(f"配置文件不存在: {self.config_path}")
                self.garbled_keywords = []
        except Exception as e:
            print(f"读取配置文件时出错: {e}")
            self.garbled_keywords = []
        
        return self.garbled_keywords
    
    def get_keywords(self) -> List[str]:
        """获取当前加载的关键词列表"""
        return self.keywords
    
    def get_garbled_keywords(self) -> List[str]:
        """获取当前加载的乱码检测关键词列表"""
        return self.garbled_keywords
    
    def set_config_path(self, path: str):
        """设置配置文件路径"""
        self.config_path = path
        self.load_keywords()
        self.load_garbled_keywords() 