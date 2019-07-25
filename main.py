"""
歌词词云：Python 数据可视化例子

Author：李文轩
Email：wenxuanli2015@163.com


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
    stop_words = ['hey', 'yo', 've', '作词', '作曲', '编曲', 'Arranger', '录音', '混音', '人声', 'Vocal', '弦乐', 'Keyboard', '键盘', '编辑', '助理', 'Assistants', 'Mixing', 'Editing', 'Recording', '音乐', '制作', 'Producer', '发行', 'produced', 'and', 'distributed', '监制', '李纤', 'Studio', 'Drum', 'Matbou']
    for stop_word in stop_words:
        f = f.replace(stop_word, '')
    return f


def generate_lyrics_cloud(artist_name, f, lang):
    print('-----根据词频，开始生成词云-----')

    f = remove_stop_words(f)

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

# 获得一首歌的歌词
def song_lyrics(headers, lyric_url):
    res = requests.request('GET', lyric_url, headers=headers)

    if 'lrc' in res.json():
        lyric = res.json()['lrc']['lyric']
        new_lyric = re.sub(r'[\d:.[\]]', '', lyric)
        return new_lyric
    else:
        print(res.json())
        return ''

def songs(artist_id):
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

    songs_ids, songs_names = songs(artist_id)

    # 词集
    all_words = ''

    for(song_id, song_name) in zip(songs_ids, songs_names):
        # 网易歌词 API URL
        lyric_url = 'http://music.163.com/api/song/lyric?os=pc&id=' + song_id + '&lv=-1&kv=-1&tv=-1'
        lyric = song_lyrics(headers, lyric_url)

        # 减除歌词提供者
        new_lyric = re.sub(r'\bby\w+\b', '', lyric)

        # 加进词集
        all_words = all_words + ' ' + new_lyric

    generate_lyrics_cloud(artist_name, all_words, lang)

if __name__ == '__main__':
    main()
