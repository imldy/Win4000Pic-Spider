import os
from lxml import etree
import requests


class PicPackage(object):
    # 图包
    def __init__(self, titile, url):
        self.titile = titile
        self.url = url
        self.picList = None
        self.category1 = None
        self.category2 = None

    def creatDirectory(self):
        self.path = dir + "/{}.{}/{}".format(self.category1, self.category2, self.titile)
        if not os.path.exists(self.path):
            os.mkdir(self.path)


class Pic(object):
    # 图
    def __init__(self, url):
        self.url = url
        self.name = os.path.basename(self.url)
        self.path = None


class User(object):
    def __init__(self):
        self.session = requests.session()
        self.target = {
            # 网页头部的分类
            "category1_list": ["wallpaper"],
            # 网页中部的分类
            "category2_list": ["191", "2357"],
        }
        self.currentCategoryUrl = ""

    def getCategoryWeb(self):
        res = self.session.get(url=self.currentCategoryUrl)
        return res

    def extraPicPackageList(self, res):
        # 提取图包，返回图包对象的列表
        HTML = etree.HTML(res.text)
        picPackages = HTML.xpath('//div[@class="list_cont Left_list_cont"]//div[@class="tab_box"]/div/ul/li')
        picPackageList = []
        for picPackage in picPackages:
            titile = picPackage.xpath('./a/@title')[0]
            url = picPackage.xpath('./a/@href')[0]
            picPackageList.append(PicPackage(titile, url))
        return picPackageList

    def getPicPackageWeb(self, picPackage):
        res = self.session.get(url=picPackage.url)
        return res

    def extraPicList(self, res):
        HTML = etree.HTML(res.text)
        # pics懒得全称了
        pics = HTML.xpath('//div[@class="scroll-img-cont"]/ul/li')
        picList = []
        for pic in pics:
            url = pic.xpath('./a/img/@data-original')[0]
            picList.append(Pic(url.replace("_120_80", "")))
        return picList

    def downloadPicPackage(self, picPackage):
        for pic in picPackage.picList:
            pic.path = "{}/{}".format(picPackage.path, pic.name)
            with open(pic.path, "wb") as f:
                print(pic.url, pic.path)
                f.write(self.session.get(url=pic.url).content)

    def start(self):
        # 循环大类别
        for category1 in self.target["category1_list"]:
            # 循环小类别
            for category2 in self.target["category2_list"]:
                # 开始请求第一页
                self.currentCategoryUrl = "http://www.win4000.com/{}_{}_0_0_1.html".format(category1, category2)
                res = self.getCategoryWeb()
                picPackageList = self.extraPicPackageList(res)
                # 遍历第一页所有图包
                for picPackage in picPackageList:
                    res = self.getPicPackageWeb(picPackage)
                    # 获取当前图包的所有图片
                    picList = self.extraPicList(res)
                    # 给当前图包添加上自己的图片
                    picPackage.picList = picList
                    # 给图包设定迟来的两个分类
                    picPackage.category1 = category1
                    picPackage.category2 = category2
                    picPackage.creatDirectory()
                    print("开始下载图包: {}".format(picPackage.titile))
                    self.downloadPicPackage(picPackage)


if __name__ == '__main__':
    dir = "pic"
    if not os.path.exists(dir):
        os.mkdir(dir)
    user = User()
    user.start()
