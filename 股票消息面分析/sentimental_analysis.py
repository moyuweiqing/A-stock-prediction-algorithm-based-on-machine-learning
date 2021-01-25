from snownlp import SnowNLP
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import jieba

def word_cut(word):     # 使用jieba库进行分词处理
    cut_word_list = ''
    cut_words = jieba.cut(word)
    for cut_word in cut_words:
        cut_word_list += cut_word
        cut_word_list += '，'
    return cut_word_list

def build_sentimental_analysis(file_name):
    info_table = pd.DataFrame(columns=['股票名称', '股票代码', '总分词数量', '正面占比', '中立占比', '负面占比', '平均分'])

    excel = pd.read_csv('sina_message/' + file_name, encoding='gb18030')

    for stock in range(0, len(excel)):
        alist = []
        alist.append(excel['股票名称'].iloc[stock])
        alist.append(str(excel['股票代码'].iloc[stock]))

        s1 = excel['公告信息'].iloc[stock]

        # 切词
        word_list = word_cut(s1)

        #建立情感分析
        sn1 = SnowNLP(word_list)
        sentimentslist = []
        pos_word_cnt = 0  # 初始化情感分组数量
        nag_word_cnt = 0
        mid_word_cnt = 0

        for i in sn1.sentences:
            j = SnowNLP(i)
            if j.sentiments >= 0.65:                         # 阈值设置，大于0.65为正向情感
                pos_word_cnt += 1
            elif j.sentiments < 0.65 and j.sentiments > 0.35: # 阈值设置，大于0.35小于0.65为中立情感
                mid_word_cnt += 1
            else:                                           # 阈值设置，小于0.35为负向情感
                nag_word_cnt += 1

            sentimentslist.append(j.sentiments)
        alist.append(len(sentimentslist))
        alist.append(round(pos_word_cnt / len(sentimentslist), 2))
        alist.append(round(mid_word_cnt / len(sentimentslist), 2))
        alist.append(round(nag_word_cnt / len(sentimentslist), 2))
        alist.append(round(sum(sentimentslist) / len(sentimentslist), 3))
        info_table.loc[stock] = alist

    info_table.to_csv('analysis_result/'+file_name)
    print('完成', file_name)

def read_file():
    file_list = []
    #将当前目录下的所有文件名称读取进来
    a = os.listdir('./sina_message')
    for j in a:
        if os.path.splitext(j)[1] == '.csv':
            file_list.append(j)

    for file in file_list:
        build_sentimental_analysis(file)

if __name__ == '__main__':
    read_file()
