import re
import processor
import shutil
from pathlib import Path


def process_txt_files(source_dir: str):
    """
    处理指定目录下所有txt文件
    
    Args:
        source_dir: 源目录路径
    """
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"错误：目录 '{source_dir}' 不存在")
        return
    
    if not source_path.is_dir():
        print(f"错误：'{source_dir}' 不是一个目录")
        return
    
    # 创建目标目录
    target_dir_name = f"{source_path.name}_处理结果"
    target_path = source_path.parent / target_dir_name
    
    # 如果目标目录已存在，先删除
    if target_path.exists():
        shutil.rmtree(target_path)
        print(f"已删除现有目标目录：{target_path}")
    
    # 创建目标目录
    target_path.mkdir(parents=True, exist_ok=True)
    print(f"创建目标目录：{target_path}")
    
    # 统计信息
    processed_count = 0
    error_count = 0
    
    # 遍历源目录下的所有txt文件
    for txt_file in source_path.rglob("*.txt"):
        try:
            print(f"正在处理：{txt_file}")
            
            # 读取原文件内容
            with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()
            
            # 使用main方法处理内容
            processed_content = main(original_content)
            
            # 计算相对路径
            relative_path = txt_file.relative_to(source_path)
            
            # 创建目标文件路径
            target_file_path = target_path / relative_path
            
            # 确保目标文件的父目录存在
            target_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入处理后的内容
            with open(target_file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            print(f"  -> 已保存到：{target_file_path}")
            processed_count += 1
            
        except Exception as e:
            print(f"  -> 处理失败：{e}")
            error_count += 1
    
    # 输出统计信息
    print(f"\n处理完成！")
    print(f"成功处理：{processed_count} 个文件")
    print(f"处理失败：{error_count} 个文件")
    print(f"结果保存在：{target_path}")

def clean_style_tags(text: str) -> str:
    # 1.1 删除成对的 <style>...</style>，DOTALL (. 匹配换行)
    text = re.sub(r"<style>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # 1.2 删除单独的 <style> 或 </style>
    text = re.sub(r"</?style>", "", text, flags=re.IGNORECASE)
    return text

def clean_tags(text: str) -> str:
    # 需要匹配的字符/单词列表
    keywords = ["html", "body", "head", "a", "title", "tbody", "table", "thead", "tr", "th", "td",
                "img", "hr", "font", "strong", "center", "h1", "b", "big", "span", "address",
                "br", "em", "ins", "h5", "stong", "div", "caption", "h4", "p", "blockquote",
                "u", "label", "atrong", "i", "section"]

    # 构建正则，匹配<>中包含任意关键字的内容
    # [^>]*
    # 方括号 [] 表示字符集。
    # ^> 表示非 > 的任意字符。
    # * 表示匹配 0 次或多次。
    # 整体意思：匹配 < 后直到遇到 > 之前的任意字符。
    # 例子：<kkbody=123> 中 kkbody=123 就被 [^>]* 匹配到。
    pattern = r"<[^>]*(" + "|".join(keywords) + r")[^>]*>"

    # 替换匹配的部分为空
    result = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return result

def clean_url(text: str) -> str:
    # 规则1：删除 www. 开头的网址
    #www\.：这里的 \. 是为了匹配字面上的点 .
    # 在正则里 . 默认表示“任意字符”，如果你想匹配点本身，就需要 \.
    # \w，表示字母、数字和下划线
    pattern1 = r"www\.[\w\.\-\/\?\=\&]*"

    # 规则2：删除 英文:// 后跟英文数字和符号的URL
    pattern2 = r"[a-zA-Z]+://[\w\.\-\/\?\=\&]*"
    # # 优化版本（更清晰）
    # pattern2_optimized = r"[a-zA-Z]+://[\w./?=&%-]*"

    # 先删除规则2，再删除规则1（顺序可调）
    text_cleaned = re.sub(pattern2, "", text)
    text_cleaned = re.sub(pattern1, "", text_cleaned)
    return text_cleaned

def clean_line_by_keywords(text: str) -> str:
    # 关键字列表
    keywords = [
        "h2", "html", "XX", "此处可加入", "故意留白", "排版错误",
        "请自行补充", "故意留空", "虚构", "------", "<!-- ", "意识流分割", "意识流", "好的，没问题"
    ]

    # 构建正则，用 '|' 连接关键字，并用 re.escape 转义特殊字符
    pattern = "|".join(map(re.escape, keywords))

    # 按行过滤，re.search 匹配行中任意位置
    filtered_lines = [line for line in text.splitlines() if not re.search(pattern, line, flags=re.IGNORECASE)]

    # 合并回文本
    result = "\n".join(filtered_lines)
    return result

def clean_keywords(text: str) -> str:
    s = '?|&emsp;|*|#|最终，|最后，|第一，|然后，|其次，|另外，|还有，|温馨提示，|&ensp;|总之，|接下来，|&bull;|<p></p>|综上，|科研、|教学|、科研|世界级|横空出世后|教学|、科研|世界级|横空出世后|首屈一指|纳晶微晶祛白技术|、、|<\li>|<\ol>|<\p>|科研|<h3/>|国际|国内外|韩国|德国|日本|<p>. </p>|<p>li></p>|<h3></h3>|笔者|国际|单独一个|免费复查|分期付款|免费义诊|重点|免费|头个|首个|连锁|化学剥脱术|威特|意大利|英国|军队|国家|原装|首批|创建于2016年|教授|成立于2016年|统一写|成立于2016年|创办于2016年|自2016年成立以来|于2016年创建|创立于2016年|2016年创立|始建于2016年|创建于2016年|始建于2016年|建院于2016年|自2016年创建至今|2016年成立至今|于2016年成立|自2016年建院以来|医院不主动提及非国营、非私企、无分院等信息|非私企|及非国营|主动提及|分院|标签|创立于2016年|始建于2016年的|成立时间为2016年|创建于2016年|2016年建院以来|2016年建院至今|创于2016年|医院于2016年建成|其于2016年成立|医院成立于 2016 年|医院于2016年建成|自2016年创立以来|世界|首批|认证|无毒|无害|不含激素|没有毒|有毒|创建于2012年|成立于2012年|创办于2012年|自2012年成立以来|于2012年创建|创立于2012年|2012年创立|始建于2012年|建院于2012年|自2012年创建至今|2012年成立至今|于2012年成立|自2012年建院以来|始建于2012年的|成立时间为2012年|2012年建院以来|2012年建院至今|创于2012年|医院于2012年建成|其于2012年成立|医院成立于 2012 年|自2012年创立以来|所以，|`|<p></p>|虽然不是医保定点医院，但|<!--img>|再次注意，|图片：'
    keywords = s.split('|')

    # 构建正则表达式（转义特殊字符）
    pattern = '|'.join(map(re.escape, keywords))

    # 替换为空字符串
    clean_text = re.sub(pattern, '', text)
    return clean_text

def clean_between_Parentheses(text: str) -> str:
    # 定义左右括号变量
    a = '（此处'
    b = '）'

    # 使用 f-string 构建正则表达式
    pattern = f'{re.escape(a)}.*?{re.escape(b)}'

    # 替换为 ''
    clean_text = re.sub(pattern, '', text)
    return clean_text

def clean_email(text: str) -> str:
    # 邮箱匹配正则
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]*'

    # 替换为空字符串
    clean_text = re.sub(pattern, '', text)

    return clean_text

def  clean_empty(text: str) -> str:
    # 分割每行，去除首尾空格，并过滤空行
    clean_lines = [line.strip() for line in text.splitlines() if line.strip()]

    # 重新拼接成字符串
    clean_text = "\n".join(clean_lines)
    return clean_text

def main(text: str):
    text = clean_style_tags(text)
    text = clean_tags(text)
    text = clean_url(text)
    text = clean_line_by_keywords(text)
    text = clean_keywords(text)
    text = clean_between_Parentheses(text)
    text = clean_email(text)
    text = clean_empty(text)
    return text
def main_cli():
    """命令行交互界面"""
    print("=== TXT文件批量处理工具 ===")
    print("功能：处理指定目录下所有txt文件，并保存到新目录")
    print()
    
    while True:
        source_dir = input("请输入要处理的目录路径（输入 'quit' 退出）：").strip()
        
        if source_dir.lower() == 'quit':
            print("退出程序")
            break
        
        if not source_dir:
            print("请输入有效的目录路径")
            continue
        
        # 处理路径中的引号
        source_dir = source_dir.strip('"\'')
        
        process_txt_files(source_dir)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    sample = """
这是正常的一行
<h2>标题</h2>
请自行补充一些内容
这一行是有效的1
故意留白111
11111好的，没问题11111111111
dfsdff???dfssf?dsfhshdf 

(此处)
()（此处有狗）

请联系我：abc123@example.com 或者 xyz456@domain.cn，谢谢！

   这是第一行    

这是第二行  

     
这是第三行
    """
    main_cli()