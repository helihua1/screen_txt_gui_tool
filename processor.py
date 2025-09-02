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
        """获取目录下所有txt文件（包括子目录）"""
        if not self.files_directory or not os.path.exists(self.files_directory):
            return []
        
        txt_files = []
        # 使用os.walk递归遍历目录及其所有子目录
        for root, dirs, files in os.walk(self.files_directory):
            for file in files:
                if file.lower().endswith('.txt'):
                    txt_files.append(os.path.join(root, file))
        
        return txt_files
    
    def read_file_content(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        # 如果所有编码都失败，尝试用错误处理方式读取
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
            return "格式错误，可能包含乱码€ ╋ ╅  ソ ュ等"
    
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
            Dict[str, List[Tuple[str, str]]]: {相对路径: [(段落内容, 匹配的关键词)]}
        """
        result = {}
        keywords = self.config_manager.load_keywords()
        
        if not keywords:
            print("没有加载到关键词")
            return result
        
        txt_files = self.get_txt_files()
        
        for file_path in txt_files:
            # 获取相对于files_directory的相对路径
            rel_path = os.path.relpath(file_path, self.files_directory)
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
                result[rel_path] = matching_paragraphs
        
        return result
    
    def find_english_paragraphs(self) -> Dict[str, List[str]]:
        """
        查找包含英文句子的段落
        
        Returns:
            Dict[str, List[str]]: {相对路径: [段落内容列表]}
        """
        result = {}
        txt_files = self.get_txt_files()
        
        for file_path in txt_files:
            # 获取相对于files_directory的相对路径
            rel_path = os.path.relpath(file_path, self.files_directory)
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
                result[rel_path] = english_paragraphs
        
        return result
    
    def find_garbled_files(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        查找包含乱码关键词的文件
        
        Returns:
            Dict[str, List[Tuple[str, str]]]: {相对路径: [(文件内容, 匹配的关键词)]}
        """
        result = {}
        garbled_keywords = self.config_manager.load_garbled_keywords()
        
        if not garbled_keywords:
            print("没有加载到乱码检测关键词")
            return result
        
        txt_files = self.get_txt_files()
        
        for file_path in txt_files:
            # 获取相对于files_directory的相对路径
            rel_path = os.path.relpath(file_path, self.files_directory)
            content = self.read_file_content(file_path)
            
            if not content:
                continue
            
            # 检查整个文件内容是否包含乱码关键词
            for keyword in garbled_keywords:
                if keyword in content:
                    result[rel_path] = [(content, keyword)]
                    break  # 找到一个关键词就够了
        
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
    
    def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 要删除的文件路径
            
        Returns:
            bool: 是否成功删除
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            else:
                print(f"文件不存在: {file_path}")
                return False
        except Exception as e:
            print(f"删除文件时出错: {e}")
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
    
    def process_garbled_deletion(self, selected_items: Dict[str, List[str]]) -> bool:
        """
        处理乱码文件删除
        
        Args:
            selected_items: 用户选择的要删除的项目 {文件名: [文件内容列表]}
            
        Returns:
            bool: 是否成功处理
        """
        success_count = 0
        total_count = len(selected_items)
        
        for filename, _ in selected_items.items():
            file_path = os.path.join(self.files_directory, filename)
            if os.path.exists(file_path):
                if self.delete_file(file_path):
                    success_count += 1
                    print(f"成功删除文件: {filename}")
                else:
                    print(f"删除文件失败: {filename}")
            else:
                print(f"文件不存在: {filename}")
        
        print(f"乱码文件删除完成: {success_count}/{total_count} 个文件删除成功")
        return success_count == total_count 