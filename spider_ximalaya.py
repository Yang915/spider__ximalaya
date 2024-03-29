import json
import os

import execjs
import requests

'''爬取喜马拉雅服务器系统时间戳，用于生成xm-sign'''
def getxmtime():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Accept': 'text/html,application/xhtml+ xml,application/xml;q = 0.9,image/webp,image/apng,*/*;q=0.8, application/signe-exchange;v = b3',
        'Host': 'www.ximalaya.com'
    }
    url = "https://www.ximalaya.com/revision/time"
    response = requests.get(url, headers=headers)
    print(response)
    html = response.text
    return html
# print(getxmtime())

'''生成xm-sign'''
def exec_js():
    # 获取喜马拉雅系统时间戳
    time = getxmtime()

    # 读取同一路径下的js文件
    with open('xmSign.js', encoding='utf-8') as f:
        js = f.read()

    # 通过compile命令转成一个js对象
    docjs = execjs.compile(js)
    # 调用js的function
    res = docjs.call('python', time)
    # res = docjs.call('getnow')
    return res
# print(exec_js())

def spider_list(albumId):
    all_list = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Accept':'text/html,application/xhtml+ xml,application/xml;q = 0.9,image/webp,image/apng,*/*;q=0.8, application/signe-exchange;v = b3',
        'Host': 'www.ximalaya.com'
    }
    sign = exec_js()
    #加入xm-sign到header中
    headers['xm-sign'] = sign
    # 音频地址(pageNum参数设置页码)
    page=1
    data_url =f'https://www.ximalaya.com/revision/play/album?albumId={albumId}&pageNum={page}&sort=-1&pageSize=30'
    # print(data_url)
    response = requests.get(data_url, headers=headers)
    py_dict = json.loads(response.content.decode())
    # print(py_dict)
    song_list = py_dict['data']['tracksAudioPlay']
    for song in song_list:
        # print('-----------------------------------')
        # print(song)
        # 获取每段音频的名称和地址
        list = {}
        list['title'] = song['trackName']
        list['albumName'] = song['albumName']
        list['music_src'] = song['src']
        list['cover_src']='https:'+song['trackCoverPath']
        # 打印list
        # print(list)
        all_list.append(list)
    # 返回字典
    return all_list
# print(spider_list(24943257))



def spider_songs(list):
    '''保存音频（字典）'''
    for i in list:
        dir = "ximalaya/{}/".format(i['albumName'])
        if not os.path.exists(dir):
            print("创建目录:.%s" % dir)
            os.makedirs(dir)
        i['title'] = i['title'].replace("?", "").replace('"', "")
        # 在目录下创建一个喜马拉雅的文件夹
        with open(r'{}/{}.jpg'.format(dir, i['title']), 'ab')as f:
            r = requests.get(i['cover_src'])
            print("正在下载:{}.jpg...".format(i['title']), end="")
            f.write(r.content)
            print("\t下载完成！")

        with open(r'{}/{}.mp3'.format(dir, i['title']), 'ab')as f:
            r = requests.get(i['music_src'])
            print("正在下载:{}.mp3...".format(i['title']), end="")
            f.write(r.content)
            print("\t下载完成！")

def spider_ximalaya(albumId):
    all_list = spider_list(albumId)
    spider_songs(all_list)


if __name__ =='__main__':
    spider_ximalaya(15046153)