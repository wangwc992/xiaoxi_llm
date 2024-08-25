import re


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


if __name__ == '__main__':
    html_text = 'wang wen <a href="https://www.google.com">Google</a>&nbsp;&nbsp;&nbsp;&nbsp;kkkk'
    print(HtmlUtils.replace_link_with_url(html_text))  # Output: Google (https://www.google.com)
