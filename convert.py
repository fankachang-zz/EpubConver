#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from zipfile import ZipFile, ZIP_DEFLATED
from xml.dom.minidom import parse
import iniconfig

ini = iniconfig.IniConfig("config.ini")

sdir = ini['config']['sdir']
outdir = ini['config']['outdir']
tmpdir = ini['config']['tmpdir']
outlang = ini['config']['outlang']

if sdir == "":
    sdir = "./epubsource/"
if outdir == "":
    outdir = "./output/"
if tmpdir == "":
    tmpdir = "./tmp/"
if outlang == "":
    outlang = "T"

bookname = ""
bookcreator = ""
outbookname = ""
dic_char = {}
dic_word = {}
deldir_list = []

fw = ""


#====================================
#轉換字元庫讀取函式
#====================================
def char_conv_fw(fw1):
    f = open("./conv_char.txt", "r")
    svalues = f.readlines()
    f.close()

    char_svalues_len = len(svalues)

    for i in range(char_svalues_len):
        a = svalues[i].replace('\n', '')
        conv_char = a.split(',')
        outlang.upper()
        if outlang == "T":
            try:
                fw1 = fw1.replace(conv_char[0], conv_char[1]).strip()
            except:
                fw1 = fw1.strip()
        elif outlang == "S":
            try:
                fw1 = fw1.replace(conv_char[1], conv_char[0]).strip()
            except:
                fw1 = fw1.strip()
    return fw1

# ==  ==  ==  ==  ==  ==  ==  ==  == =
#轉換字詞庫讀取函式
# ==  ==  ==  ==  ==  ==  ==  ==  == =
def word_conv_fw(fw1):
    f = open("./conv_word.txt", "r")
    svalues = f.readlines()
    f.close()
    word_svalues_len = len(svalues)

    for j in range(word_svalues_len):
        b = svalues[j].replace("\n", "")
        conv_word = b.split(",")
        outlang.upper()
        if outlang == "T":
            fw1 = fw1.replace(conv_word[0], conv_word[1])
        elif outlang == "S":
            fw1 = fw1.replace(conv_word[1], conv_word[0])
    return fw1

# ==  ==  ==  ==  ==  ==  ==  ==  == =
#壓縮功能函式
#ƒ
def myzip(target_dir, outdir1, out_filenm):
    target_file = outdir1 + out_filenm
    target_file = char_conv_fw(target_file)
    target_file = word_conv_fw(target_file)
    # 壓縮所有文件，包含子目錄
    myzipfile = ZipFile(target_file, 'w')

    for root, dirs, files in os.walk(target_dir):
        for vfileName in files:
            filename = os.path.join(root, vfileName)
            #變更檔名編碼為繁體
            outfilename = filename.replace(target_dir, "")
            myzipfile.write(filename, outfilename, ZIP_DEFLATED)
     # 壓縮完成
    myzipfile.close()

# ================================================
#解壓縮功能函式
# ================================================
def unzip(target_dir, out_dir, filenm):
    target_name = filenm
    if ".DS_Store" not in target_name:
        print target_dir + target_name
        zipfiles = ZipFile(target_dir + target_name, 'r')
        zipfiles.extractall(os.path.join(out_dir, os.path.splitext(target_name)[0]))
        zipfiles.close()

# ================================================
#檔案繁簡轉換
# ================================================
def file_cn_tw_conv(filenm):
    #讀取檔案
    f = open(filenm, "r")
    svalues = f.read()
    f.close()

    #寫入原本檔案
    f1 = open(filenm, "w")
    f = char_conv_fw(svalues)
    f = word_conv_fw(f)
    f1.write(f)
    f1.close()

#=============================
#目錄內掃檔案名後進行檔案內容繁簡轉換
#=============================
def dirfile_epub(target_dir):

    for root, dirs, files in os.walk(target_dir):
        print("    |" + root + "目錄處理中...請等待!")
        for vfileName in files:
            filename = os.path.join(root, vfileName)
            b = filename[-3:]
            if b == 'htm' or b == 'tml' or b == 'opf' or b == 'ncx':
            #if(b == 'opf' or b == 'ncx'):
                #print("    |轉換 "+filename)
                #進行檔案內容繁簡轉換
                file_cn_tw_conv(filename)
                #pass


#=============================
#製作 epub 檔
#=============================
def zip_epub():
    ofile = os.listdir(tmpdir)
    outfile_temp = ""
    #取得目錄名稱
    for outfile in ofile:
        find_opffilename_dir = tmpdir + outfile
        # 對目錄內所有檔案查找opf檔，建立書名和作者名
        for root, dirs, files in os.walk(find_opffilename_dir):
            for vfileName in files:
                filename = os.path.join(root, vfileName)
                b = filename[-3:]
                if b == 'opf':
                    #print(filename)
                    #指定輸出名稱
                    #print("原版名："+filename)
                    outfile_temp = read_title_creator(filename)
                    outfile_temp = outfile_temp.replace("/", "")
                    #print(outfile_temp)
        #zip(来源目录,输出目录,档名）
        myzip(tmpdir + outfile, outdir, outfile_temp.replace("\n","") + ".epub")
        print "    |" + outfile_temp.replace("\n","") + ".epub END!"


#=============================
#解壓縮 epub
#=============================
def unzip_epub():
    sfile = os.listdir(sdir)
    #解壓縮
    for ssfile in sfile:
        #unzip(来源目录,目的地目录,档案名）
        print("    |解壓縮 " + ssfile)
        unzip(sdir, tmpdir, ssfile)


#=============================
#讀取 epub書名與作者
#=============================
def read_title_creator(filepath):
    global book_creator, book_name
    doc = parse(filepath)

    for ChildNodes in doc.getElementsByTagName("metadata")[0].childNodes:
        #print(ChildNodes.nodeValue)
        if ChildNodes.nodeName == 'dc:title':
            for chitext in ChildNodes.childNodes:
                book_name = chitext.nodeValue
                #print(chitext.nodeValue)
        if ChildNodes.nodeName == 'dc:creator':
            for chitext in ChildNodes.childNodes:
                book_creator = chitext.nodeValue
                #print(chitext.nodeValue)
    #《阿米．宇宙之心》
    out_book_name = book_creator.strip() + "-" + book_name.strip()
    out_book_name = char_conv_fw(char_conv_fw(out_book_name))
    return out_book_name
    #print(outbookname)

#=============================
#清除暫存區
#=============================
def clean_tmp(tmp_dir):
    #Delete All Files in any Dir
    for root, dirs, files in os.walk(tmp_dir):
        for dirname in dirs:
            deldir_list.append(os.path.join(root, dirname))
        for name in files:
            os.remove(os.path.join(root, name))
    #Delete Dir
    for i in deldir_list[::-1]:
        os.rmdir(i)

# ==  ==  ==  ==  ==  ==  ==  ==  == =
#主程式
# ==  ==  ==  ==  ==  ==  ==  ==  == =
def main():
    if outlang == "T":
        print("#=============================")
        print("        簡體轉正體 ")
        print("#=============================")
    elif outlang == "S":
        print("#=============================")
        print("        正體 轉簡體")
        print("#=============================")
    print("1 == =>解開 EPUB 檔案至暫存區......")
    unzip_epub()
    print("2 == =>檔案編碼轉換...............")
    dirfile_epub(tmpdir)
    print("3 == =>建立 EPUB ................")
    zip_epub()
    print("4 == =>Clean TempDIR ..........\n\nDone!")
    clean_tmp(tmpdir)

main()
