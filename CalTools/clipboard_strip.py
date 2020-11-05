import win32clipboard
import win32con
import re

seq = '''
The limited supply of fossil fuels and the negative impact of
carbon dioxide emissions on the global climate change dictate the
increasing usage of renewable energy sources. The concentrated
solar power (CSP) technology is increasingly being one of the most
likely candidates for providing the majority of this renewable energy
[1e4]. Along the main four commercially available CSP technologies,
i.e., solar tower or central receiver system, parabolic
'''


# 整理文本（去换行、去无用的数字等）
def reform_text(text):
    text = re.sub('\[[^]]*?\d[^[]*?\]', '', text)
    text = re.sub('et al\.', 'et al', text)
    ts = text.replace('\r', '\n').split('\n')
    text = ' '.join(ts)
    return text


# 取得剪切板的内容
def get_clipboard():
    win32clipboard.OpenClipboard()
    st = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    return st


# 整理剪切板的内容
def clipboard(text='', print_text=True):
    if not text:
        text = get_clipboard()
    st = reform_text(text)
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, st)
    win32clipboard.CloseClipboard()
    if print_text:
        print(st)
    return st


if __name__ == '__main__':
    clipboard()
