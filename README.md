# wanmen

万门视频下载爬虫
支持购买过的视频下载



主要函数
download_wanmen_one_course_warp

参数
head 浏览器f12抓到的头信息文本 直接复制f12抓到的文本即可 程序自己会解析成dict
base_dir  下载目录 默认为当前路径下的wanmen_course文件夹 可以自行在代码修改 变量base_dir
link 课程链接 如 https://api.wanmen.org/4.0/content/v2/courses/60acbe86bf5ea22cc961b619

head失效会重新读区
程序运行路径下的head.txt文件

可以把自己最新的head信息手动
新建文本文件 重命名为head.txt 填入进去


需要如下头信息（举例 f12自己找）：
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


做了flask接口 会用多进程下载 可以post调用多个课程链接 批量下载  可自行修改
下载逻辑是先获取所有信息缓存 然后开始下载文件 
会下载课程下所有的章节视频 和资料


![image](https://user-images.githubusercontent.com/46922107/159587263-beaf33f4-8097-4819-80bd-f39f68b65364.png)
![image](https://user-images.githubusercontent.com/46922107/159587271-22dace99-f227-43de-b01d-25e4caac5d3d.png)
![image](https://user-images.githubusercontent.com/46922107/159587288-29ad550f-fa87-49b8-8b9c-e2ebde60c217.png)
![image](https://user-images.githubusercontent.com/46922107/159587307-372f7f33-7665-46b3-8ba0-e37f1405e785.png)



x-platform: web
