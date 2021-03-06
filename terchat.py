#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import itchat
from itchat.content import *
import zlog
import random
import time, datetime
import configparser
import re

'''
print( random.randint(1,10) )        # 产生 1 到 10 的一个整数型随机数  
print( random.random() )             # 产生 0 到 1 之间的随机浮点数
print( random.uniform(1.1,5.4) )     # 产生  1.1 到 5.4 之间的随机浮点数，区间可以不是整数
print( random.choice('tomorrow') )   # 从序列中随机选取一个元素
print( random.randrange(1,100,2) )   # 生成从1到100的间隔为2的随机整数

a=[1,3,5,6,7]                # 将序列a中的元素顺序打乱
random.shuffle(a)
print(a)
----
import time
import datetime

t = time.time()

print (t)                       #原始时间数据
print (int(t))                  #秒级时间戳
print (int(round(t * 1000)))    #毫秒级时间戳

nowTime = lambda:int(round(t * 1000))
print (nowTime());              #毫秒级时间戳，基于lambda

print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))   #日期格式化
----
1499825149.26
1499825149
1499825149257
1499825149257
2017-07-12 10:05:49
----
'''

__doc__ = 'wechat module'

#if __name__ == "__main__":
#    print(__doc__)

#__name__ = "wechat"
groupChatInterval = 0
instance = itchat.new_instance()
# todo: instance 的接口应该封装一个异常捕获的头 在函数执行前
@instance.msg_register([TEXT, PICTURE, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def group_replay(msg):
    FromUser = instance.search_chatrooms(userName=msg['FromUserName'])
    ToUser = instance.search_chatrooms(userName=msg['ToUserName'])
    # print(msg)
    # print("::::::::::::::::::::::::::::")
    # print(FromUser)
    # print("::::::::::::::::::::::::::::")
    # print(ToUser)
    # print("::::::::::::::::::::::::::::")
    chatroom = (((not FromUser) or (FromUser['NickName'] == 'A.Zirpon')) and ToUser) or FromUser
    chatroomName = chatroom['NickName']
    chatroomUserName = chatroom['UserName']
    senderName = msg['ActualNickName']
    senderUserName = msg['ActualUserName']
    if senderName == '' :
        senderName = instance.search_chatrooms(userName=senderUserName)['NickName'] or "Empty senderName"

    # print("\n\n+++++++++++++++ Group %s(%s) Chat +++++++++++++++++++++++" % (chatroomName, chatroomUserName))
    # print(chatroomName)
    # print(chatroom)
    # print("::::::::::::::::::::::::::::")
    # print("::::::::::::::::::::::::::::")
    # print("GroupChat[%s]:member[%s] send [%s]" % (chatroomName, senderName, msg['Text']))
    # todo: 这里其实应该拉个线程/协程 来写日志的
    chatRoomLog = zlog.getLogger("Group",chatroomName)
    if msg['Type'] == 'Text':
        if chatRoomLog :
            chatRoomLog.debug("(%s)member[%s](%s) send [%s]" % (chatroomUserName, senderName, senderUserName, msg['Text']))
    elif msg['Type'] == 'Recording' or msg['Type'] == 'Picture' or msg['Type'] == 'Video':
        if chatRoomLog :
            chatRoomLog.debug("(%s)member[%s](%s) send ![file](%s)" % (chatroomUserName, senderName, senderUserName, '../resource/'+msg['FileName']))
    elif msg['Type'] == 'Map':
        x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
        if location is None:
            msg_content = "纬度->" + x.__str__() + " 经度->" + y.__str__()     #内容为详细的地址
        else:
            msg_content = location
        if chatRoomLog :
            chatRoomLog.debug("(%s)member[%s](%s) send location:%s" % (chatroomUserName, senderName, senderUserName, msg_content))
    elif msg['Type'] == 'Sharing':
        #如果消息为分享的音乐或者文章，详细的内容为文章的标题或者是分享的名字
        msg_content = msg['Text']
        msg_share_url = msg['Url']
        if chatRoomLog :
            chatRoomLog.debug("(%s)member[%s](%s) share content:%s, url:%s" % (chatroomUserName, senderName, senderUserName, msg_content, msg_share_url))
    #msg.download(msg['FileName'])   #这个同样是下载文件的方式
    #msg['Text'](msg['FileName'])    #下载文件
    # if not msg['FileName'].endswith(".gif"):
        msg["Text"]('./resource/'+msg['FileName'])
    #将下载的文件发送给发送者
    #itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil', msg["FileName"]), msg["FromUserName"])
    #itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil', './resource/'+msg['FileName']))
    
    # print("\n\n")
    # send to group
    # msg.user.send(u'@%s\u2005 I receuved: %s' % (senderName, msg['Text']))
    # send to phone
    # instance.send_msg("GroupChat:Dear %s\u2005,I am a robot,got your msg %s,My master will reply you soon,thanks" % (senderName, msg['Text']))
    IGroupChatAutoReply(chatroomName, chatroomUserName, msg, senderName)

#@instance.msg_register([FRIENDS, CARD, MAP, SHARING], isGroupChat=True)
#def download_files(msg):

@instance.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True)
def friend_replay(msg):
    friend = instance.search_friends(userName=msg['FromUserName'])
    if friend is None:
        friends = instance.get_friends(update=True)
        bingo = False
        for f in range(0,len(friends)):
            if msg['FromUserName'] in friends[f]['UserName']:
                bingo = True
                friend = friends[f]
                break
        if friend is None:
            return

    nickname = friend['NickName']
    username = friend['UserName']
    remarkname = friend['RemarkName']
    #print("\n\n+++++++++++++++ Friend %s(%s,%s) Chat +++++++++++++++++++++++" % (nickname,username,remarkname))
    # print(msg)
    # print("::::::::::::::::::::::::::::")
    # print("FriendChat:friend[%s] send [%s]" % (nickname, msg['Text']))
    # print("\n\n")

    friendLog = zlog.getLogger("Friend",nickname)
    if friendLog :
        if msg['Type'] == 'Text':
            friendLog.debug("(%s) send [%s]" % (username, msg['Text']))
        elif msg['Type'] == 'Recording' or msg['Type'] == 'Picture' or msg['Type'] == 'Video':
            friendLog.debug("(%s) send ![file](%s)" % (username, '../resource/'+msg['FileName']))
            msg["Text"]('./resource/'+msg['FileName'])
        elif msg['Type'] == 'Map':
            #如果消息为分享的位置信息
            x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
            if location is None:
                msg_content = "纬度->" + x.__str__() + " 经度->" + y.__str__()     #内容为详细的地址
            else:
                msg_content = location
            friendLog.debug("(%s) send location:%s" % (username, msg_content))
        elif msg['Type'] == 'Sharing':
            #如果消息为分享的音乐或者文章，详细的内容为文章的标题或者是分享的名字
            msg_content = msg['Text']
            msg_share_url = msg['Url']
            friendLog.debug("(%s) share content:%s, url:%s" % (username, msg_content, msg_share_url))
        else:
            friendLog.debug("(%s) send ![file](%s)" % (username, '../resource/'+msg['FileName']))
    IFriendChatAutoReply(nickname, remarkname, msg)

def IGroupChatAutoReply(chatroomName, chatroomUserName, msg, senderName):
    cf = configparser.ConfigParser()
    cf.read("test.conf", encoding="utf-8")

    flag = False
    matchList = cf.get("GroupChatParam", "AutoReplyGroupList").split('|')
    for groupname in matchList:
        if groupname in chatroomName:
            flag = True

    if flag == True:
        if msg['Type'] == 'Text':
            szTmp = ("%s" % msg['Text'])
            szTmp = szTmp.strip("吗?？"+"!")
        elif msg['Type'] == 'Recording':
            szTmp = "你声音真好听"
        elif msg['Type'] == 'Picture':
            szTmp = "这图片真好看"
        elif msg['Type'] == 'Video':
            szTmp = "这视频真刺激"
        else:
            szTmp = None
        szDefault = cf.options("AutoReplyGroupDefaultMsg")
        maxIndex = len(szDefault)
        index = random.randint(0, maxIndex+cf.getint("GroupChatParam", "msgListRandomRange"))
        #print("\n\n+++++++++++++++ Group %s(%s) Chat (%d, %d) +++++++++++++++++++++++" % (chatroomName, chatroomUserName, index, maxIndex))
        curTime = time.time()
        global groupChatInterval
        if groupChatInterval == 0 or curTime > groupChatInterval:
            if (msg['Type'] == 'Recording' or msg['Type'] == 'Picture' or msg['Type'] == 'Video') and szTmp is not None and szTmp != "": 
                msg.user.send("%s" % (szTmp))
            elif szTmp is None or szTmp == "" or index < maxIndex:
                #msg.user.send("%s, %s" % (senderName,szDefault[index]))
                msg.user.send("%s" % (szDefault[index]))
            else:
                msg.user.send("%s" % (szTmp))
            groupChatInterval = curTime + cf.getint("GroupChatParam", "groupChatInterval")

def IFriendChatAutoReply(nickname, remarkname, msg):
    cf = configparser.ConfigParser()
    cf.read("test.conf", encoding="utf-8")

    matchList = cf.get("FriendChatParam", "AutoReplyFriendList").split('|')
    # matchList 为空会匹配到任意的好友 bug
    for index in range(0,len(matchList)):
        if matchList[index] in nickname or matchList[index] in remarkname:
            if msg['Type'] == 'Text':
                szTmp = ("%s" % msg['Text'])
                szTmp = szTmp.strip("吗?？"+"!")
            elif msg['Type'] == 'Recording':
                szTmp = "你声音真好听"
            elif msg['Type'] == 'Picture':
                szTmp = "这图片真好看"
            elif msg['Type'] == 'Video':
                szTmp = "这视频真刺激"
            else:
                szTmp = None
            szDefault = cf.options("AutoReplyFriendDefaultMsg")
            maxIndex = len(szDefault)
            index = random.randint(0, maxIndex+cf.getint("FriendChatParam", "msgListRandomRange"))
            if (msg['Type'] == 'Recording' or msg['Type'] == 'Picture' or msg['Type'] == 'Video') and szTmp is not None and szTmp != "": 
                instance.send_msg("%s" % (szTmp), toUserName=msg['FromUserName'])
            elif szTmp is None or szTmp == "" or index < maxIndex:
                instance.send_msg("%s, %s" % (nickname, szDefault[index]), toUserName=msg['FromUserName'])
            else:
                instance.send_msg("%s" % (szTmp), toUserName=msg['FromUserName'])
                #instance.send_msg("FriendChat:Dear %s\u2005,I am a robot,got your msg %s,My master will reply you soon,thanks" % (nickname, msg['Text']))
                #instance.send_msg("Dear %s\u2005,I am a robot,got your msg %s,My master will reply you soon" % (nickname, msg['Text']), toUserName=msg['FromUserName'])

def start():
    instance.auto_login(hotReload=True, statusStorageDir='newInstance.pkl', enableCmdQR=2)
    instance.run(False, False)
    '''
    def coRecv():
        newInstance.auto_login(hotReload=True, statusStorageDir='newInstance.pkl') # enableCmdQR=True,
        newInstance.run()
    # EventLoop:
    loop = asyncio.get_event_loop()
    # coroutine
    loop.run_until_complete(coRecv())
    loop.close()
    '''

def send_msg(content,username):
    return instance.send_msg("terchat:%s" % content,toUserName=username)

def get_friends(remarkName=None, nickName=None, flag=False):
    friends = instance.get_friends(update=flag)
    bingo = False
    for f in range(0,len(friends)):
        if remarkName is not None and remarkName in friends[f]['RemarkName']:
            bingo = True
            print("remarkName:",f,"--", friends[f])
        elif nickName is not None and nickName in friends[f]['NickName']:
            bingo = True
            print("nickName",f,"--", friends[f])
        elif remarkName is None and nickName is None:
            print(f,"--", friends[f])

def printConfig(section=None):
    cf = configparser.ConfigParser()
    cf.read("test.conf", encoding="utf-8")

    #return all section
    secs = cf.sections()
    print ('sections:', secs, type(secs))
    if section is not None and section != "":
        opts = cf.options(section)
        print ('options:', opts, type(opts))
        kvs = cf.items(section)
        print ('kvs:', kvs)
        for key,value in kvs:
            print(key)
            print(value.split('|'))
    cf.get("FriendChatParam", "AutoReplyFriendList").split('|')

def end():
    instance.logout()
