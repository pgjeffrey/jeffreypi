#!/usr/bin/python
# coding:utf-8
import os, sys
import filecmp
import re
import shutil
import datetime
import logging


'''
    校验源与备份目录的差异
'''

holderlist = []

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.DEBUG)
handler = logging.FileHandler(os.path.dirname(sys.argv[0])+"/filesync.log")
handler.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(ch)

def compareme(dir1, dir2):  # 递归获取更新项函数
    if not os.path.exists(dir1):
        return
    if not os.path.exists(dir2):
        os.makedirs(dir2)
    dircomp = filecmp.dircmp(dir1, dir2)
    only_in_one = dircomp.left_only  # 源目录新文件或目录
    diff_in_one = dircomp.diff_files  # 不匹配文件，源目录文件已发生变化
    dirpath = os.path.abspath(dir1)  # 定义源目录绝对路径

    [holderlist.append(x) for x in only_in_one]
    [holderlist.append(x) for x in diff_in_one]

    for x in holderlist:
        f1 = os.path.abspath(os.path.join(dir1, x))
        f2 = os.path.abspath(os.path.join(dir2, x))
        if os.path.isfile(f1) and (not os.path.basename(f1)[0] == "."):  # 判断是否为文件，是则进行复制操作，不是隐藏文件
            #print "%s\t[info]复制文件：%s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f1),
            logger.info("%s\t[info]复制文件：%s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f1))
            shutil.copyfile(f1, f2)
        if os.path.isdir(f1) and (not os.path.basename(f1)[0] == "."):  # 如果差异路径为目录且不存在，则在备份目录中创建，不是隐藏目录
            if not os.path.exists(f2) :
                logger.info("%s\t[info]创建目录：%s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f2))
                os.makedirs(f2)
                compareme(f1, f2)

    if len(dircomp.common_dirs) > 0:  # 判断是否存在相同子目录，以便递归
        for item in dircomp.common_dirs:  # 递归子目录
            d1 = os.path.abspath(os.path.join(dir1, item))
            d2 = os.path.abspath(os.path.join(dir2, item))
            compareme(d1, d2)

XiaoMiPATH = "/home/pi/xiaomi/"
PiPATH = "/media/pi/data/sync_xiaomi/"
ISDEBUG = False

if __name__ == '__main__':
    if len(sys.argv) > 2:  # 输入源目录与备份目录
        dir1 = sys.argv[1]
        dir2 = sys.argv[2]
        compareme(dir1, dir2)
    elif len(sys.argv) == 2:
        XiaoMiPATH = "/Volumes/XiaoMi/"
        PiPATH = "/Users/icecream/Documents/sync_xiaomi/"
        print os.path.dirname(sys.argv[0])

        with open(os.path.dirname(sys.argv[0])+"/filesync.ini", 'r') as f:
            dirs = f.readlines()
        for d in dirs:
            compareme(XiaoMiPATH + d.strip(), PiPATH + d.strip())
    elif len(sys.argv) == 1:
        try:
            with open(os.path.dirname(sys.argv[0]) + "/filesync.ini", 'r') as f:
                dirs = f.readlines()
            for d in dirs:
                compareme(XiaoMiPATH + d.strip(), PiPATH + d.strip())
        except Exception, e:
            logger.error('Failed！', exc_info=True)
    else:
        print('Usage:', sys.argv[0], 'datadir backdir')
        sys.exit()
