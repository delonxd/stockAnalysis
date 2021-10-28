import itchat
from itchat.content import *


@itchat.msg_register([TEXT])
def text_reply(msg):
    print(msg.text)


if __name__ == '__main__':
    itchat.auto_login()
    itchat.run()
    #     time_str = time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime(time.time()))
    #     itchat.send(time_str)
    #     itchat.logout()
    #     # itchat.send('123')
    #
    # import itchat
    #
    # from itchat.content import TEXT

    # if itchat.load_login_status(fileDir='..\\test\\wechat_login_status'):
    #
    #     itchat.run()
    #     itchat.dump_login_status()
    #
    # else:
    #     itchat.auto_login()
    #     itchat.dump_login_status(fileDir='..\\test\\wechat_login_status')
    #     print('Config stored, so exit.')