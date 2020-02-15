#coding: utf-8
from lxml import etree
from pathlib import Path
import re
import zipfile
import os
import html
from os.path import dirname,basename,join

class Epub2Html():
    def __init__(self,epubpath):
        self.epubpath = epubpath 
        self.template =Path("./index.html").read_text()
        self.filedir = join(dirname(self.epubpath),basename(self.epubpath).split(".")[0])
        self.absfiledir = os.path.abspath(self.filedir)
        self.textdir = os.path.join(self.filedir ,"text")

    
    def parseDiv(self,dom,depth=0):
        titles=  dom.xpath("./a/text()")
        if len(titles)>0:
            print(depth* "---",titles[0])

        divs2=  dom.xpath("./div")
        if len(divs2)>0:
            for d in divs2:
                self.parseDiv(d,depth+1)

    def genMenuTree(self,filepath):
        contents =Path(filepath).read_text()
        contents = contents.encode('utf-8')
        dom = etree.HTML(contents)
        divs = dom.xpath("./body/div")
        for d in divs:
            self.parseDiv(d)

    def unzip(self):
        tokens =self.epubpath.split(".")

        only_name = self.epubpath+".unzip"
        if len(tokens)>0:
            only_name= tokens[-2] 
        else:
            print("can`t extract name!")

        with zipfile.ZipFile(self.epubpath,'r') as zip_ref:
            zip_ref.extractall(f"./{only_name}")


    def genContent(self):
        content_list = []
        for text in  self.traverse(self.textdir):
            if text in  ["part0000.html","part0001.html"]:
                continue
            text = os.path.join(self.textdir,text)
            print(text)
            raw_menu = Path(text).read_text()
            raw_menu = raw_menu.encode('utf-8')
            raw_menu_dom = etree.HTML(raw_menu)
            parts = raw_menu_dom.xpath("//body/*")
            for p in parts:
                raw_menu = etree.tostring(p,pretty_print=True).decode('utf-8')
                content_list.append(raw_menu)

        full_content = "".join(content_list)
        return full_content
        
    def traverse(self,rootdir):
        for cdirname, dirnames, filenames in os.walk(rootdir):
            if rootdir ==  cdirname:
                return filenames 


    def genMenu(self):
        # self.genMenuTree("./a/text/part0000.html")
        raw_menu =Path(join(self.textdir,"part0000.html")).read_text()
        raw_menu = raw_menu.encode('utf-8')
        raw_menu_dom = etree.HTML(raw_menu)
        parts = raw_menu_dom.xpath("//body/*")
        raw_menus = []
        for p in parts:
            raw_menu = etree.tostring(p,pretty_print=True).decode('utf-8')
            raw_menus.append(raw_menu)
        raw_menus = "".join(raw_menus)
        raw_menu=re.sub(r"part\w+\.html","",raw_menus)
        return raw_menu

    
    def gen(self):
        full_content = self.genContent()
        menu = self.genMenu()
        self.template = self.template.replace("${menu}$",menu)

        self.template = self.template.replace("${content}$",full_content)

        Path(join(self.filedir,"index.html")).write_text(self.template)
        self.copyJs()

    def copyJs(self):
        import shutil
        dest = join(self.absfiledir,"jquery.min.js")
        print("dest:",dest)
        shutil.copy("/Users/zk/git/jsPrj/epubViewer/jquery.min.js",dest)


if __name__ == "__main__":
    e = Epub2Html("./a.epub")
    e.gen()
