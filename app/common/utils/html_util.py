import re


class HtmlUtils:
    @staticmethod
    def replace_link_with_url(html_text):
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
