
import requests
import base64
import json
import PIL
try:
    import cookielib
except Exception as e:
    import http.cookiejar as cookielib

session = requests.Session()
session.cookies = cookielib.LWPCookieJar(filename='requests_coo.txt')

try:
    session.cookies.load(ignore_discard=True,ignore_expires=True)
    print('cookie信息加载成功')
except Exception as e:
    print("cookie信息加载失败")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
           'HOST': 'www.zhihu.com','Referer': 'https://www.zhihu.com/signin?next=%2F',
           'Authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'}


def zhihu_login(account,password,captcha):
    #登陆之前先拿验证码数据
    # is_captcha = parse_captcha()
    # if is_captcha:
    #     print '你有验证码，我不登陆'
    #     # is_captcha =parse_captcha()
    # else:
    #     print '没有验证码，我登陆'
    post_url='https://www.zhihu.com/api/v3/oauth/sign_in'
    post_data={
        'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
        'grant_type': 'password',
        'timestamp': '1515398025518',
        'source': 'com.zhihu.web',
        'signature': '30b129980d00e5efb09f16b0334bf4e8601b060b',
        'username': account,
        'password': password,
        'captcha': captcha,
        'lang': 'en',
        'ref_source': 'homepage',
        'utm_source': ''
    }





def parse_captcha():
    response = session.get('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',headers=headers,verify= False)
    show_captcha=response.json()['show_captcha']
    if show_captcha:
        print( '有验证码')
        #有验证码，就再一次向https://www.zhihu.com/api/v3/oauth/captcha?lang=en发送put请求，用于向服务器索引当前的验证码的图片地址
        response = session.put('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',headers=headers,verify=False)
        try:
            img=json.loads(response.content)['img_base64']
        except Exception as e:
            print('获取img_base64的值失败，原因:'%e)
        else:
            print( '成功获取加密后的图片地址')
            #将加密后的图片进行解密，同时保存到本地
            img = img.encode('utf-8')
            img_data = base64.b64decode(img)
        with open('zhihu_captcha.GIF','wb') as f:
            f.write(img_data)
        captcha = input('请输入识别的验证码:')
        #将验证码继续发送post请求和服务器端进行对比是否正确
        data = {'input_text':captcha}
        response = session.post('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',data = data,headers=headers,verify=False)
        try:
            yanzheng_result = json.loads(response.content)['success']
        except Exception as e:
            print('关于验证码的post请求响应失败，原因：{}'.format(e))
        else:
            if yanzheng_result:
                zhihu_login('18516157608','123qaz',captcha)
            else:
                print('是错误的验证码')
        # return True
    else:
        print( '没有验证码')
        zhihu_login('*****','******',captcha='')

parse_captcha()