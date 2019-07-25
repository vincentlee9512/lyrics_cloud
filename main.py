"""
歌词词云：Python 数据可视化例子
概括：根据提供的歌手 id，从网易云音乐获取其人气前 50 名的歌曲的歌词，用最高频的词作出词云图片

Author：李文轩
Email：wenxuanli2015@163.com

1. 准备阶段
    - Python 爬虫获取歌词列表
    - 获取每首歌歌词
    - 获取歌词文本

2. 词云分析
    - 设置词云模型
    - 通过歌词生成词云
    - 词云可视化
"""
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import requests
import re
from lxml import etree
from nltk.tokenize import word_tokenize
import jieba


# 设置请求的headers，避免反爬虫
headers = {
        'Referer': 'http://music.163.com',
        'Host': 'music.163.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent': 'Chrome/10'
}


def remove_stop_words(f):
    """
    在所有歌词中，去掉没有意义的单词
    :param f: 需要被过滤的歌词
    :return: 已经过滤的歌词
    """
    stop_words = ['hey', 'yo', 've', '作词', '作曲', '编曲', 'Arranger', '录音', '混音', '人声', 'Vocal', '弦乐', 'Keyboard', '键盘', '编辑', '助理', 'Assistants', 'Mixing', 'Editing', 'Recording', '音乐', '制作', 'Producer', '发行', 'produced', 'and', 'distributed', '监制', '李纤', 'Studio', 'Drum', 'Matbou']
    for stop_word in stop_words:
        f = f.replace(stop_word, '')
    return f


def generate_lyrics_cloud(artist_name, f, lang):
    """
    使用 wordCloud 生成词云
    :param artist_name: 歌手名字，用做命名词云图片
    :param f: 所有歌词
    :param lang: 歌词的主要语言，根据语言选择切词工具和字形字体；只支持英文和中文
    """

    print('-----根据词频，开始生成词云-----')

    # 过滤歌词
    f = remove_stop_words(f)

    # 根据语言设置切词工具和字形字体
    if lang == 'en':
        word_list = ' '.join(word_tokenize(f))
        font_path = './font/MYRIADAT.TTF'
    if lang == 'cn':
        word_list = ' '.join(list(set(jieba.cut(f, cut_all=False, HMM=True))))
        font_path = './font/SimHei.ttf'

    lc = WordCloud(
        font_path=font_path,
        max_words=100,
        width=2000,
        height=1200
    )

    lyrics_cloud = lc.generate(word_list)

    # 写词云图片
    lyrics_cloud.to_file('{}_lyrics_cloud.jpg'.format(artist_name))

    # 显示词云文件
    plt.imshow(lyrics_cloud)
    plt.axis('off')
    plt.show()


def song_lyrics(headers, lyric_url):
    """
    获得一首歌的歌词
    :param headers: global 变量，请求的headers
    :param lyric_url: 歌词的url
    :return: 去掉标点符号的歌词
    """
    res = requests.request('GET', lyric_url, headers=headers)

    if 'lrc' in res.json():
        lyric = res.json()['lrc']['lyric']
        new_lyric = re.sub(r'[\d:.[\]]', '', lyric)
        return new_lyric
    else:
        print(res.json())
        return ''

def songs(artist_id):
    """
    根据歌手的网易云音乐id，抓取歌单
    :param artist_id: 歌手的网易云音乐id
    :return: 歌的id列表 和 歌名列表
    """
    songs_ids, songs_names = [], []

    page_url = 'https://music.163.com/artist?id=' + artist_id

    # 获得HTML
    res = requests.request('GET', page_url, headers=headers)

    # 使用 XPath 解析
    html = etree.HTML(res.text)

    href_xpath = "//*[@id='hotsong-list']//a/@href"
    hrefs = html.xpath(href_xpath)

    name_xpath = "//*[@id='hotsong-list']//a/text()"
    names = html.xpath(name_xpath)

    for href, name in zip(hrefs, names):
        songs_ids.append(href[9:])
        songs_names.append(name)
        # print("{} {}".format(href, name))

    return songs_ids, songs_names


def main():
    """
    这个项目的 main 函数

    - 执行程序前，请先把 artist_name, artist_id, lang 改到想要生成词语的歌手资料
    - 执行程序后，会在同目录生成词云图片
    """

    """
    # Artist: Passenger
    # 网易云音乐里，他的id是70840
    artist_name = 'Passenger'
    artist_id = '70840'

    # 根据语言，选择不同切词工具； cn 或者 en
    lang = 'en'
    """

    artist_name = '房东的猫'
    artist_id = '1050282'
    lang = 'cn'

    # 通过 songs() 函数获得人气前 50 名的歌曲的歌名和 id
    songs_ids, songs_names = songs(artist_id)

    # 词集
    all_words = ''

    # 通过循环和 song_lyrics() 函数，获取人气前 50 名的歌曲的歌词
    for(song_id, song_name) in zip(songs_ids, songs_names):
        # 网易歌词 API URL
        lyric_url = 'http://music.163.com/api/song/lyric?os=pc&id=' + song_id + '&lv=-1&kv=-1&tv=-1'
        lyric = song_lyrics(headers, lyric_url)

        # 减除歌词提供者
        new_lyric = re.sub(r'\bby\w+\b', '', lyric)

        # 加进词集
        all_words = all_words + ' ' + new_lyric

    # 通过 generate_lyrics_cloud() 函数，生成词云图片和显示词云图片
    generate_lyrics_cloud(artist_name, all_words, lang)


if __name__ == '__main__':
    main()
