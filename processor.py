import os
import glob
from typing import Dict, List, Tuple
from config_manager import ConfigManager
from english_detector import EnglishDetector

class TextProcessor:
    """文本处理核心类，负责文件读取、内容处理和文件写入"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.english_detector = EnglishDetector()
        self.files_directory = ""
        self.config_directory = ""
    
    def set_files_directory(self, directory: str):
        """设置待处理文件目录"""
        self.files_directory = directory
    
    def set_config_directory(self, directory: str):
        """设置配置文件目录"""
        self.config_directory = directory
        self.config_manager.set_config_path(os.path.join(directory, 'config.txt'))
    
    def get_txt_files(self) -> List[str]:
        """获取目录下所有txt文件"""
        if not self.files_directory or not os.path.exists(self.files_directory):
            return []
        
        pattern = os.path.join(self.files_directory, "*.txt")
        return glob.glob(pattern)
    
    def read_file_content(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
            return ""
    
    def write_file_content(self, file_path: str, content: str):
        """写入文件内容"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件 {file_path} 时出错: {e}")
            return False
    
    def find_keyword_paragraphs(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        查找包含关键词的段落
        
        Returns:
            Dict[str, List[Tuple[str, str]]]: {文件名: [(段落内容, 匹配的关键词)]}
        """
        result = {}
        keywords = self.config_manager.load_keywords()
        
        if not keywords:
            print("没有加载到关键词")
            return result
        
        txt_files = self.get_txt_files()
        
        for file_path in txt_files:
            filename = os.path.basename(file_path)
            content = self.read_file_content(file_path)
            
            if not content:
                continue
            
            # 提取段落
            paragraphs = self.english_detector.extract_paragraphs_from_text(content)
            matching_paragraphs = []
            
            # 检查每个段落是否包含关键词
            for paragraph in paragraphs:
                for keyword in keywords:
                    if keyword in paragraph:
                        matching_paragraphs.append((paragraph, keyword))
                        break  # 找到一个关键词就够了
            
            if matching_paragraphs:
                result[filename] = matching_paragraphs
        
        return result
    
    def find_english_paragraphs(self) -> Dict[str, List[str]]:
        """
        查找包含英文句子的段落
        
        Returns:
            Dict[str, List[str]]: {文件名: [段落内容列表]}
        """
        result = {}
        txt_files = self.get_txt_files()
        
        for file_path in txt_files:
            filename = os.path.basename(file_path)
            content = self.read_file_content(file_path)
            
            if not content:
                continue
            
            # 提取段落
            paragraphs = self.english_detector.extract_paragraphs_from_text(content)
            english_paragraphs = []
            
            # 检查每个段落是否包含英文句子
            for paragraph in paragraphs:
                if self.english_detector.contains_english_sentence(paragraph):
                    english_paragraphs.append(paragraph)
            
            if english_paragraphs:
                result[filename] = english_paragraphs
        
        return result
    
    def remove_paragraphs_from_file(self, file_path: str, paragraphs_to_remove: List[str]) -> bool:
        """
        从文件中删除指定段落
        
        Args:
            file_path: 文件路径
            paragraphs_to_remove: 要删除的段落列表
            
        Returns:
            bool: 是否成功删除
        """
        try:
            content = self.read_file_content(file_path)
            if not content:
                return False
            
            # 提取所有段落
            all_paragraphs = self.english_detector.extract_paragraphs_from_text(content)
            
            # 过滤掉要删除的段落
            remaining_paragraphs = []
            for paragraph in all_paragraphs:
                if paragraph not in paragraphs_to_remove:
                    remaining_paragraphs.append(paragraph)
            
            # 重新组合内容
            new_content = '\n'.join(remaining_paragraphs)
            
            # 写入文件
            return self.write_file_content(file_path, new_content)
            
        except Exception as e:
            print(f"删除段落时出错: {e}")
            return False
    
    def process_keyword_deletion(self, selected_items: Dict[str, List[str]]) -> bool:
        """
        处理关键词删除
        
        Args:
            selected_items: 用户选择的要删除的项目 {文件名: [段落列表]}
            
        Returns:
            bool: 是否成功处理
        """
        success_count = 0
        total_count = len(selected_items)
        
        for filename, paragraphs in selected_items.items():
            file_path = os.path.join(self.files_directory, filename)
            if os.path.exists(file_path):
                if self.remove_paragraphs_from_file(file_path, paragraphs):
                    success_count += 1
                    print(f"成功处理文件: {filename}")
                else:
                    print(f"处理文件失败: {filename}")
            else:
                print(f"文件不存在: {filename}")
        
        print(f"关键词删除完成: {success_count}/{total_count} 个文件处理成功")
        return success_count == total_count
    
    def process_english_deletion(self, selected_items: Dict[str, List[str]]) -> bool:
        """
        处理英文句子删除
        
        Args:
            selected_items: 用户选择的要删除的项目 {文件名: [段落列表]}
            
        Returns:
            bool: 是否成功处理
        """
        success_count = 0
        total_count = len(selected_items)
        
        for filename, paragraphs in selected_items.items():
            file_path = os.path.join(self.files_directory, filename)
            if os.path.exists(file_path):
                if self.remove_paragraphs_from_file(file_path, paragraphs):
                    success_count += 1
                    print(f"成功处理文件: {filename}")
                else:
                    print(f"处理文件失败: {filename}")
            else:
                print(f"文件不存在: {filename}")
        
        print(f"英文句子删除完成: {success_count}/{total_count} 个文件处理成功")
        return success_count == total_count 