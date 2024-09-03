import re

from bs4 import BeautifulSoup
from nltk import sent_tokenize, word_tokenize


class HtmlUtils:
    @staticmethod
    def replace_link_with_url(html_text):
        """清空html标签，将a标签替换为链接"""
        # 检查输入是否为字符串，如果不是则返回空字符串
        if not isinstance(html_text, str):
            return ''

        def replacer(match):
            a_tag = match.group()
            url_match = re.search(r'href="(.*?)"', a_tag)
            text_match = re.search(r'>(.*?)<', a_tag)
            if url_match and text_match:
                url = url_match.group(1)
                text = text_match.group(1)
                return f' {text} ({url}) '
            else:
                return ''

        html_text = re.sub(r'<a .*?>.*?</a>', replacer, html_text)
        html_text = re.sub(r'<.*?>|&nbsp;', ' ', html_text).replace('  ', '')
        return html_text.strip()

    @staticmethod
    def text2soup(text: str) -> BeautifulSoup:
        # 使用BeautifulSoup解析HTML文本
        soup = BeautifulSoup(text, 'html.parser')
        return soup

    @staticmethod
    def get_text_from_html(soup: BeautifulSoup) -> str:
        # 从HTML文本中提取纯文本
        text = soup.get_text()
        return text

    @staticmethod
    def cleat_text(text):  # 定义清理文本的方法
        text = text.strip().replace("\n\n", "").replace(" ", " ")
        # 多空格变成一个空格
        text = re.sub(r"\s+", " ", text)
        return text

class TextUtils:
    @staticmethod
    def split_text(paragraphs, chunk_size=300, overlap_size=100):
        '''按指定 chunk_size 和 overlap_size 交叠割文本'''
        sentences = [s.strip() for s in word_tokenize(paragraphs,language='zh')]
        chunks = []
        i = 0
        merged = False  # Add a flag to track whether a merge has occurred
        while i < len(sentences):
            chunk = sentences[i]
            overlap = ''
            prev_len = 0
            prev = i - 1
            # 向前计算重叠部分
            while prev >= 0 and len(sentences[prev]) + len(overlap) <= overlap_size:
                overlap = sentences[prev] + ' ' + overlap
                prev -= 1
            chunk = overlap + chunk
            next = i + 1
            # 向后计算当前chunk
            while next < len(sentences) and len(sentences[next]) + len(chunk) <= chunk_size:
                chunk = chunk + ' ' + sentences[next]
                next += 1
            # chunk 太小，合并到前一个 chunk
            if len(chunk) < chunk_size / 2:
                if not merged:  # Only merge if a merge has not already occurred
                    chunks[-1] += chunk
                    merged = True  # Set the flag to True after a merge
                else:
                    chunks.append(chunk)
                    merged = False  # Reset the flag when starting a new chunk
            else:
                chunks.append(chunk)
                merged = False  # Reset the flag when starting a new chunk
            i = next
        return chunks

    @staticmethod
    def split_text_str(paragraphs, chunk_size=300, overlap_size=100):
        # 分割字符串，chunk_size 为每个 chunk 的长度，overlap_size 为重叠部分的长度
        chunks = []
        start = 0
        while start < len(paragraphs):
            end = min(start + chunk_size, len(paragraphs))
            chunks.append(paragraphs[start:end])
            start = end - overlap_size
            # 如果最后一个 chunk 的长度小于 overlap_size的二分之一，则合并到前一个 chunk，并且删除最后一个 chunk，结束循环
            if len(chunks[-1]) < chunk_size:
                if len(chunks[-1]) < chunk_size / 2:
                    chunks[-2] += chunks[-1]
                    chunks.pop()
                break
        return chunks


if __name__ == '__main__':
    html_text = 'wang wen <a href="https://www.google.com">Google</a>&nbsp;&nbsp;&nbsp;&nbsp;kkkk'
    print(HtmlUtils.replace_link_with_url(html_text))  # Output: Google (https://www.google.com)
