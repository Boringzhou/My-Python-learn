#coding=utf-8
import urllib.request as request


def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html
    pass

html = getHtml("http://tieba.baidu.com/p/2738151262")

#print(dir(urllib))
print(html)