from bs4 import BeautifulSoup as bs
import pandas as pd
import requests, re
import lxml
import time
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    'Host': 'finance.sina.com.cn'
}

def savemessage(df, name, code, message, row):      # 信息处理
   alist = []
   alist.append(name)
   alist.append(code)
   alist.append(message)
   df.loc[row] = alist

   return df

def getnameandcode(message):
    code = re.findall('company(.*?)nc', str(message))
    name = re.findall('target="_blank">(.*?)<', str(message))

    return code[0][3:9], name[0]

def getdaymessage(url):     # 涨停板早知道具体内容信息
    info_table = pd.DataFrame(columns=['股票名称', '股票代码', '公告信息'])

    res = requests.get(url=url, headers=headers)
    res.encoding = 'utf-8'
    html_text = bs(res.text, 'lxml')
    ps = html_text.find_all('p')

    news_link = []
    date = str(html_text.find('span', class_ = 'date').text)[:11]

    row = 1
    for i in range(0, len(ps)):
        if 'strong' in str(ps[i])[:20] and 'span' in str(ps[i])[:25]:       # 硬核找符合条件的新闻信息
            code, name = getnameandcode(str(ps[i]))
            message = ps[i+1].text
            info_table = savemessage(info_table, name, code, message, row)
            row += 1

    info_table.to_csv('sina_message/' + date + '.csv', encoding='gb18030')
    if len(info_table) == 0:
        print(date, 'error!')

    print('完成了', date)

def if_zaozhidao(html_text):
    link_list = []
    date_list = []

    html_text = bs(html_text, 'lxml')
    uls = html_text.find_all('ul', class_ = 'list_009')

    for ul in uls:
        messages = ul.find_all('a')
        for message in messages:
            if '涨停板早知道' in str(message):
                link_list.append(re.findall('href="(.*?)"', str(message))[0])

    for i in range(0, len(link_list)):
        getdaymessage(link_list[i])
        time.sleep(2)
    pass

if __name__ == '__main__':
    urlhead = 'https://finance.sina.com.cn/roll/index.d.html?cid=56588&page='
    for page in range(1, 22):
        url = urlhead + str(page)
        res = requests.get(url=url, headers=headers)
        res.encoding = 'utf-8'
        if_zaozhidao(res.text)
        print('     完成了', page, '页')
        time.sleep(2)