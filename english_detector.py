import re
from typing import List, Tuple

class EnglishDetector:
    """英文句子检测器，用于检测段落中是否包含英文句子"""
    
    def __init__(self):
        # 英文字母的正则表达式
        self.english_letter_pattern = re.compile(r'[a-zA-Z]')
        # 检测英文句子的模式：字母 + 空格 + 字母（至少两个单词）
        self.english_sentence_pattern = re.compile(r'[a-zA-Z]+\s+[a-zA-Z]+')
        # HTML标签模式，用于排除HTML标签内的英文
        self.html_tag_pattern = re.compile(r'<[^>]*>')
    
    def contains_english_sentence(self, text: str) -> bool:
        """
        检测文本中是否包含英文句子
        
        判定方法：
        1. 首先排除HTML标签内的内容
        2. 检测是否包含连续两个英文单词（字母+空格+字母）
        3. 确保不是HTML标签内的英文
        
        Args:
            text: 要检测的文本
            
        Returns:
            bool: 是否包含英文句子
        """
        if not text or not text.strip():
            return False
        
        # 移除HTML标签，避免误判
        text_without_tags = self.html_tag_pattern.sub('', text)
        
        # 检测是否包含英文句子模式
        if self.english_sentence_pattern.search(text_without_tags):
            return True
        
        return False
    
    def find_english_sentences_in_paragraphs(self, paragraphs: List[str]) -> List[Tuple[int, str]]:
        """
        在段落列表中查找包含英文句子的段落
        
        Args:
            paragraphs: 段落列表
            
        Returns:
            List[Tuple[int, str]]: 包含(段落索引, 段落内容)的列表
        """
        english_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            if self.contains_english_sentence(paragraph):
                english_paragraphs.append((i, paragraph))
        
        return english_paragraphs
    
    def extract_paragraphs_from_text(self, text: str) -> List[str]:
        """
        从文本中提取段落（按换行符分割）
        
        Args:
            text: 原始文本
            
        Returns:
            List[str]: 段落列表
        """
        if not text:
            return []
        
        # 按换行符分割，并过滤空段落
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        return paragraphs 