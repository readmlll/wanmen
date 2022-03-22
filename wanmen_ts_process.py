import os
from multiprocessing import Pool
import json
import requests as requestsP
from requests.adapters import HTTPAdapter
import pickle
requests = requestsP.Session()
requests.mount('http://', HTTPAdapter(max_retries=3))
requests.mount('https://', HTTPAdapter(max_retries=3))
import glob
import re
import time
import logging
# 第一步，创建一个logger
logger = logging.getLogger()  # 定义对应的程序模块名name，默认是root
logger.setLevel(logging.INFO)  # 指定最低的日志级别 critical > error > warning > info > debug


# 第三步，再创建一个handler,用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)  # 输出到console的log等级的开关
# 第四步，定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(thread)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# 第五步，将logger添加到handler里面
logger.addHandler(ch)
log=logger

error_limit=1000000000000000
head_text_path='./head.txt'


class M3U8Info:
    def __init__(self):
        self.vd_url = ''
        self.vd_size =''
        self.vd_conetnt_json = ''
        self.vd_name = ''
        self.vd_media_id = ''
        self.vd_duration = ''
        self.vd_image = ''

        self.course_name=''
        self.course_files=[]
        self.chapter = ''
        self.section = ''
        self.chapter_name = ''
        self.section_title = ''
        self.m3u8_content_json=''
        self.chapterinfo_json=''
        self.course_info_json=''
        self.course_intr=''
        self.chapter_list=[]
        self.contents=[]

        self.ts_files=[]
        self.is_end=False
        self.key_method=''
        self.key_url=''
        self.key=''
        self.iv=''
        self.m3u8_text=''
        self.m3u8_file_name=''

    def __setitem__(self, k, v):
        self.k = v

def parse_heads_by_browser(head_str):
    if head_str is None:
        head_str='''
    Accept-Encoding: gzip, deflate, br
    Accept-Language: zh-CN,zh;q=0.9
    Cache-Control: no-cache
    Connection: keep-alive
    Pragma: no-cache
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
        '''
    try:
        heads={}
        hs = head_str.split("\n")
        hs = [h.strip() for h in hs if h.strip() != '']
        for h in hs:
            try:
                parts = h.split(": ")
                heads[parts[0].strip()] = parts[1].strip()
            except Exception as  ee:
                pass
        return heads
    except Exception as e:
        return {}

def get_new_head():
    try:
        log.error(f"需要获取新的head信息 head文件{head_text_path}")
        f = open(head_text_path, 'r')
        head = f.read()
        f.close()
        head = parse_heads_by_browser(head)
        return head
    except Exception as e:
        log.error(f"需要获取新的head信息 head文件{head_text_path} 获取异常")
        return {}


def process_dir_name(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def download_get_text(url,head=None,cookie=None,isJson=False):
    begin_time = time.time()
    res=None
    error = 0

    head_not = '''
                                      accept: */*
                                      accept-encoding: gzip, deflate, br
                                      accept-language: zh-CN,zh;q=0.9
                                      cache-control: no-cache
                                      origin: https://www.wanmen.org
                                      pragma: no-cache
                                      referer: https://www.wanmen.org/
                                      sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"
                                      sec-ch-ua-mobile: ?0
                                      sec-ch-ua-platform: "macOS"
                                      sec-fetch-dest: empty
                                      sec-fetch-mode: cors
                                      sec-fetch-site: same-site
                                      user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
                                      '''
    head_not = parse_heads_by_browser(head_not)


    while error<error_limit and not res:
        try:
            if error % 5 == 0 and error!=0:
                res = requests.get(url, timeout=60 * 4, headers=head_not, cookies=cookie)
            else:
                res = requests.get(url, timeout=60 * 4, headers=head, cookies=cookie)
            if "401 Authorization Required" in res.text and res.status_code != 200:
                log.error(f"访问401-{url}")
                raise Exception("访问401")
            elif res.status_code == 200:
                log.info(f"访问url-{url}-耗时 {time.time() - begin_time}")
                if isJson:
                    return json.loads(res.text)
                return res.text
            else:
                if "x-token" in head:
                    log.error(f"{url} {res.status_code}")
                    head = get_new_head()

            res=None
        except Exception as e:
            res = None
            if "x-token" in head:
                head = get_new_head()


        finally:
            error += 1





def download_file_or_get_bytes(url,save_file=None,head=None,cookie=None,isJson=False):
    begin_time = time.time()
    if save_file:
        save_dir=process_dir_name(os.path.dirname(save_file))
    save_file+="."+url.split(".")[-1]
    res=None
    error=0
    while error<error_limit and not res:
        try:
            res = requests.get(url, timeout=60 * 4, headers=head, cookies=cookie)
            if "401 Authorization Required" in res.text and res.status_code != 200:
                log.error(f"下载401-{url}")
                raise Exception("下载401")
            elif res.status_code == 200:
                if isJson:
                    return json.loads(res.text)
                byte_list = res.content
                if save_file:
                    with open(save_file, 'bw') as f:
                        f.write(byte_list)
                        f.flush()
                log.info(f"下载文件-{save_file}-耗时 {time.time() - begin_time}")
                return byte_list
            else:
                if "x-token" in head:
                    head = get_new_head()
            res=None
        except Exception as e:
            res=None
            if "x-token" in head:
                head=get_new_head()
        finally:
            error+=1



class UnitBlock():
    def __init__(self):
        self.name=''
        self.id=''
        self.type=''
        self.sons=[]
        self.m3u8_text=''
        self.content=''
        self.m3U8Info=None
        self.ts_name_base=''

def get_file_list_info(text,m3u8_file_name):
    strs=text.split("\n")
    tss=[]
    is_end=False
    key_method=''
    key_url=''
    for s in strs:
        if "EXT-X-KEY" in s:

            temps=s.split(",")
            for temp_str in temps:
                if "METHOD" in temp_str:
                    key_method=temp_str.split("=")[-1]
                    continue
                if "URI=" in temp_str:
                    key_url=temp_str.replace("URI=","").replace('"',"")
            continue
        if ".ts"  in s:
            tss.append('https://media.wanmen.org/'+s)
        if "EXT-X-ENDLIST" in s:
            is_end=True

    info=M3U8Info()
    info.m3u8_file_name=m3u8_file_name
    info.m3u8_text=text
    info.ts_files=tss
    info.is_end=is_end
    info.key_method=key_method
    info.key_url=key_url

    return info

def process_name(name):
    name=name.replace("\\", "_").replace(" ", "_")\
        .replace("*", "_").replace("?", "_").replace("/", "_").replace(":", "_").replace('：','_').strip()
    return name




def sort_ts_files(save_base_dir,m3u8_file_name):
    if save_base_dir[-1]=='/':
        save_base_dir=save_base_dir[0:-1]
    fs=glob.glob(save_base_dir+"/"+m3u8_file_name+"*.ts",recursive=True)
    fs_objs=[]
    for f in fs:
        if "_compose_ts" in f:
            continue
        num = int(re.findall(r"\d+\.?\d*", f.replace(m3u8_file_name, ''))[-1].replace(".", ""))
        fs_objs.append({
            'f':f,'num':num
        })
    fs_objs=sorted(fs_objs, key=lambda i: i['num'],reverse = False)
    fs_objs=[f['f'] for f in fs_objs]
    return fs_objs

def compose_ts(save_dir,m3u8_file_name):
    fs=sort_ts_files(save_dir,m3u8_file_name)
    save_dir=os.path.dirname(save_dir)
    compose_ts_file=os.path.join(save_dir,m3u8_file_name+'_compose_ts.ts')
    with open(compose_ts_file,'bw') as allf:
        for f in fs:
            if os.path.isdir(f):
                continue
            if f.split(".")[-1]!='ts':
                continue
            with open(f,'br') as onef:
                bys=onef.read()
                allf.write(bys)
                allf.flush()

class WanMen():

    def __init__(self,base_dir,header_str,mut_download_size=10):
        self.mut_download_size=mut_download_size
        self.base_dir=process_dir_name(base_dir)
        self.header_str=header_str

    def get_head(self):
        heads = parse_heads_by_browser(self.header_str)
        return heads


    def get_m3u8_url(self,presentationVideo):
        m3u8_file=None
        if 'pcHigh' in presentationVideo:
            m3u8_file=presentationVideo['pcHigh']
        if 'pcLow' in presentationVideo and not m3u8_file:
            m3u8_file=presentationVideo['pcLow']
        if 'pcMid' in presentationVideo and not m3u8_file:
            m3u8_file = presentationVideo['pcMid']
        if 'mobileMid' in presentationVideo and not m3u8_file:
            m3u8_file = presentationVideo['mobileMid']
        if m3u8_file:
            m3u8_file=m3u8_file.strip()
        return m3u8_file

    def download_chapter_content(self, chapter_list, course_name):
        for chapteridx, chapter in enumerate(chapter_list):
            chapter_dir = process_dir_name(
                os.path.join(self.base_dir, course_name, (str(chapteridx + 1) + chapter.name)))
            for sectionidx, section in enumerate(chapter.sons):
                if section.type != 'video':
                    break
                ts_file_path_base = os.path.join(chapter_dir, (str(sectionidx + 1) + section.name), "_ts_files_")
                for ts in section.m3U8Info.ts_files:
                    ts_name = ts.split(".")[-2].split("/")[-1]
                    ts_file_path = os.path.join(ts_file_path_base, ts_name)
                    head = '''
                     accept: */*
                     accept-encoding: gzip, deflate, br
                     accept-language: zh-CN,zh;q=0.9
                     cache-control: no-cache
                     origin: https://www.wanmen.org
                     pragma: no-cache
                     referer: https://www.wanmen.org/
                     sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"
                     sec-ch-ua-mobile: ?0
                     sec-ch-ua-platform: "macOS"
                     sec-fetch-dest: empty
                     sec-fetch-mode: cors
                     sec-fetch-site: same-site
                     user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
                     '''
                    download_file_or_get_bytes(ts, ts_file_path, parse_heads_by_browser(head), None)
                #     self.pool = Pool(self.mut_download_size)
                #     self.pool.apply_async(download_file_or_get_bytes, (ts, ts_file_path, parse_heads_by_browser(head), None,))  # 执行任务
                # self.pool.close()
                # self.pool.join()
                compose_ts(ts_file_path_base, section.ts_name_base)

    def get_chapter_content(self,chapter_list,course_name):
        for chapteridx,chapter in enumerate(chapter_list):
            chapter_dir=process_dir_name(os.path.join(self.base_dir,course_name,(str(chapteridx+1)+chapter.name)))
            for sectionidx,section in enumerate(chapter.sons):
                sid=section.id
                surl=f'https://api.wanmen.org/4.0/content/lectures/{sid}?routeId=main'
                error=0
                while error<5:
                    try:
                        if section.type!='video':
                            break
                        sectionContent = download_get_text(surl, self.get_head(), None, True)
                        hls = sectionContent['hls']
                        hls = self.get_m3u8_url(hls)
                        m3basename = hls.split("?")[0].split("/")[-1].split(".")[0]
                        section.content = sectionContent
                        section.m3u8_text = download_get_text(hls, self.get_head())
                        section.m3U8Info = get_file_list_info(section.m3u8_text, sid)
                        ts_name_base = m3basename
                        section.ts_name_base = ts_name_base
                        break
                    except Exception as e:
                        pass
                    finally:
                        error+=1


    def get_chapter_content_req(self,course_id):
        section_url = f'https://api.wanmen.org/4.0/content/courses/{course_id}/catalogue'
        lecturest = download_get_text(section_url,self.get_head(),None,True)
        charpter_content=lecturest['lectures']
        if len(charpter_content)<=0:
            phases=lecturest['phases']
            for ph in phases:
                for lecture in ph['lectures']:
                    charpter_content.append(lecture)
        chapter_list = []
        for chpter in charpter_content:
            block = UnitBlock()
            block.name = process_name(chpter['name'])
            block.id = chpter['_id'].strip()
            sections_content = chpter['children']
            for section in sections_content:
                sblock = UnitBlock()
                sblock.id = section['_id'].strip()
                sblock.name = process_name(section['name'])
                sblock.type = section['assetType'].strip()  # video
                sblock.sons = []
                block.sons.append(sblock)
            chapter_list.append(block)
        return chapter_list



    def get_course_content(self,link):
        link=link.replace("?routeId=main","")
        content_res=download_get_text(link,self.get_head(),None,True)
        info=M3U8Info()
        info.course_name=process_name(content_res['name'])
        info.course_files=[{'name':process_name(f['name']),'link':f['url'].strip()}for f in content_res['documents']]
        info.course_intr=content_res['description'].strip()
        info.course_info_json=json.dumps(content_res,ensure_ascii=False)

        course_base_dir = os.path.join(self.base_dir, info.course_name)
        course_base_dir=process_dir_name(course_base_dir)

        log.info(f"获取课程信息成功-{info.course_name}-开始解析章节")
        course_id=content_res['_id']
        info.chapter_list=self.get_chapter_content_req(course_id)
        old_info=None
        if os.path.exists(os.path.join(course_base_dir,'info.json')):
            try:
                with open(os.path.join(course_base_dir,'info.json'),'br') as of:
                    old_info=pickle.loads(of.read())
            except Exception as ee:
                old_info=None
                pass

        if not old_info:
            log.info(f"{info.course_name}-解析章节成功-开始获取各个视频信息")
            self.get_chapter_content(info.chapter_list,info.course_name)
            log.info(f"{info.course_name}-获取各个视频信息-成功")
            with open(os.path.join(course_base_dir, 'info.json'), 'bw') as f:
                pickle.dump(info, f, 0)
                f.flush()
        else:
            info=old_info
            log.info(f"{info.course_name}-从缓存获取各个视频信息-成功")

        log.info(f"{info.course_name}-解析章节成功-开始下载")
        self.download_chapter_content(info.chapter_list,info.course_name)
        log.info(f"{info.course_name}-视频下载成功")

        for file in info.course_files:
            file_path = os.path.join(course_base_dir, file['name'])
            download_file_or_get_bytes(file['link'], file_path, self.get_head(), None)
        log.info(f"{info.course_name}-文件下载成功")

def download_wanmen_one_course_warp(head,base_dir,link):
    wanmen = WanMen(base_dir, head)
    wanmen.get_course_content(link)


from flask import Flask,request as flask_request


if __name__ == '__main__':


    head = '''
    authorization: Bearer eyJhbGci
    cache-control: no-cache
    origin: https://www.wanmen.org
    pragma: no-cache
    referer: https://www.wanmen.org/
    user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    x-app: uni
    x-platform: web
    x-sa: 9e2f
    x-time: 623
    x-token: bbc8
                '''
    base_dir = './wanmen_course'
    my_book=True
    mut_download_size=2



    if my_book:
        l='https://api.wanmen.org/4.0/content/v2/courses/60acbe86bf5ea22cc961b619'
        download_wanmen_one_course_warp(head,base_dir,l)
    else:
        app = Flask(__name__)
        @app.route('/wanmen', methods=['GET', 'POST'])
        def xxxx():
            base_dir = './wanmen_course'
            link = flask_request.args.get('link')
            if not link:
                link = flask_request.form['link']
            pool = Pool(mut_download_size)
            pool.apply_async(download_wanmen_one_course_warp,
                                  (head, base_dir,link,))  # 执行任务
            pool.close()
            pool.join()
        app.run(host="0.0.0.0",port=60002)


