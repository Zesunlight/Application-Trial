# coding:utf-8
import requests
import json
import jieba
import re
from collections import defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


def url_get_json(url):
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64)' 
                           'AppleWebKit/537.36 (KHTML, like Gecko)' 
                           'Chrome/74.0.3729.169 Safari/537.36',
             }
    response = requests.get(url, headers=header)
    response.encoding = "UTF-8"
    return json.loads(response.text)

def artist_music(artist_id, page):
    url = f"http://www.kuwo.cn/api/www/artist/artistMusic?artistid={artist_id}&pn={page}&rn=30"
    music_json = url_get_json(url)
    return music_json


def artist_album(artist_id, page):
    url = f"http://www.kuwo.cn/api/www/artist/artistAlbum?artistid={artist_id}&pn={page}&rn=30"
    album_json = url_get_json(url)
    return album_json


def find_music_id(music_json, music_id, album=False):
    if album:
        music_list = music_json["data"]["musicList"]
    else:
        music_list = music_json["data"]["list"]
    
    for m in music_list:
        music_id[m["name"]] = m["rid"]

    return None


def album_music(album_id):
    url = f"http://www.kuwo.cn/api/www/album/albumInfo?albumId={album_id}&pn=1&rn=30"
    album_music_json = url_get_json(url)
    return album_music_json


def music_lyric(music_id):
    url = f"http://m.kuwo.cn/newh5/singles/songinfoandlrc?musicId={music_id}"
    lyric_json = url_get_json(url)
    return lyric_json


def extract_lyric(lyric_json, lyric_segment):
    lyric_list = lyric_json["data"]["lrclist"]
    if lyric_list is None:
        return None

    music_name_singer = lyric_list[0]["lineLyric"]
    lyric_writer = lyric_list[1]["lineLyric"]
    composer = lyric_list[2]["lineLyric"]
    print(f"{music_name_singer}_{lyric_writer}_{composer}")

    for line in lyric_list[1:]:
        # 跳过歌名 作词 作曲
        lyric = line["lineLyric"]
        lyric = re.sub('[():：,./。～-]', ' ', lyric)
        segment = jieba.lcut_for_search(lyric)

        for i in segment:
            # len(i) > 1
            # if i in {'的', '我', '周杰伦', '在', '你', '词', '曲', '了', '是', '不', 'Jay', 
            #         'Chou', '着', '都', '说', '就', '有', '方文山', '那', '让','却', '很', 
            #         '这', '编曲', '再', '会', '也', '谁', '要', '对', '还', '没有', '上', 
            #         '我们', '人', '像', '走', '去', '被', '给', '里', '只', '跟', '没', 
            #         '怎么', '来', '到', '等', '什么', '看', '而', '好', '又','将', '为', 
            #         '可以', '才', '把', '他', '听', '过', '用', '已', '多', '能', '一起', 
            #         '一直', '不是', '它', '自己',  '一个', '如果', '已经', '不会', '太', 
            #         '不要', '因为', '还是', '只是','但', '叫', '不到', '中', '和', '当', '后', 
            #         '真的', '想要', '请', '可', '不能', '我会','啊', '比', '林迈', '与', '找', 
            #         '一点', '吧', '该','下','更', '别', '得', '我用','这样', '写', '一', '就是', 
            #         '个', '地','黄俊郎', '呢', '成','应该', '不过', '有些','是不是','不了',
            #         '一种','有点', '她', '我要', '一样', '跟着','不用', '只有', '靠', '这么',
            #         '还有', '拿', '为了','制作','一定', '从','连','做','钟兴民','站', '一遍',
            #         '只能','一句', '这里','掉', '比较', '那么','向', '无法','这个','啦', '如',
            #         '吗', '有人', '也许','哪里','起来'}:
            # if i in {'的', '我', '在', '你', '和', '是', '也', '过', '会', '为'}:
            if len(i) == 1 or i in {'Live', 'Cheer', 'Chen', '陈绮贞'}:
                continue
            else:
                lyric_segment[i] += 1

    return None


def generate_lyric_segment(artist_id, music_range, album=False, album_range=1):
    music_id = defaultdict(int)
    if album:
        # get lyric segment from album content
        for p in range(1, album_range+1):
            album_json = artist_album(artist_id, p)
            for a in album_json["data"]["albumList"]:
                album_music_json = album_music(a["albumid"])
                find_music_id(album_music_json, music_id, album=True)
    else:
        # get lyric segment from music content
        for p in range(1, music_range+1):
            music_json = artist_music(artist_id, p)
            find_music_id(music_json, music_id)

    lyric_segment = defaultdict(int)
    for name, id in music_id.items():
        lyric_json = music_lyric(id)
        if lyric_json is not None:
            extract_lyric(lyric_json, lyric_segment)
        else:
            print(f"{name} not fund lyric")

    return lyric_segment


def word_cloud(lyric_segment):
    font = r"C:\Windows\Fonts\simhei.ttf"
    jay_mask = np.array(Image.open(r'C:\Users\DF\Desktop\female.jpeg'))
    wc = WordCloud(font_path=font,
                   background_color="white",
                   max_words=300,
                   mask=jay_mask,
                   contour_color="steelblue",
                   max_font_size=1000
                   )
    wc.generate_from_frequencies(lyric_segment)
    wc.to_file(r"C:\Users\DF\Desktop\Cheerego.png")
    # plt.figure()
    # plt.imshow(wc)
    # plt.axis("off")
    # plt.show()

if __name__ == '__main__':
    lyric_segment = generate_lyric_segment(artist_id=7, 
                                           music_range=8, 
                                           album=False, 
                                           album_range=1
                                           )
    word_cloud(lyric_segment)
