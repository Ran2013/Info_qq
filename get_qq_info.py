import threading
import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter.filedialog
from tkinter import scrolledtext
import requests
from PIL import Image
import time
import re
import emoji
import json
import math
import os
import sys
import pandas as pd
from tkinter import messagebox
 

# generate source path of the files 
def resource_path(relative_path):
    if getattr(sys, 'frozen', False): #judge Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

icon_path = resource_path(os.path.join("res","favicon.ico"))

root = tk.Tk()

# Functions for login
def bkn(Skey):
    t = 5381
    n = 0
    o = len(Skey)
    while n < o:
        t += (t << 5) + ord(Skey[n])
        n += 1
    return t & 2147483647
 
def ptqrtoken(qrsig):
    n = len(qrsig)
    i = 0
    e = 0
    while n > i:
        e += (e << 5) + ord(qrsig[i])
        i += 1
    return 2147483647 & e
 
#  Functions for QR code
def QR():
    url = 'https://ssl.ptlogin2.qq.com/ptqrshow?appid=715030901&e=2&l=M&s=3&d=72&v=4&t=0.'+str(time.time())+'&daid=73&pt_3rd_aid=0'
    r = requests.get(url)
    qrsig = requests.utils.dict_from_cookiejar(r.cookies).get('qrsig')
    with open(r'QQ.png','wb') as f:
        f.write(r.content)
    im = Image.open(r'QQ.png')
    im = im.resize((350,350))
    im.show()
    return qrsig
 
# Functions for qq account cookies
def cookies(qrsig,ptqrtoken):
    while 1:
        url = 'https://ssl.ptlogin2.qq.com/ptqrlogin?u1=https%3A%2F%2Fqun.qq.com%2Fmanage.html%23click&ptqrtoken=' + str(ptqrtoken) + '&ptredirect=1&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-0-' + str(time.time()) + '&js_ver=20032614&js_type=1&login_sig=&pt_uistyle=40&aid=715030901&daid=73&'
        cookies = {'qrsig': qrsig}
        r = requests.get(url,cookies = cookies)
        r1 = r.text
        if '二维码未失效' in r1:

            pass
        elif '二维码认证中' in r1:

            pass
        elif '二维码已失效' in r1:

            pass
        else:

            cookies = requests.utils.dict_from_cookiejar(r.cookies)
            uin = requests.utils.dict_from_cookiejar(r.cookies).get('uin')
            regex = re.compile(r'ptsigx=(.*?)&')
            sigx = re.findall(regex,r.text)[0]
            url = 'https://ptlogin2.qun.qq.com/check_sig?pttype=1&uin=' + uin + '&service=ptqrlogin&nodirect=0&ptsigx=' + sigx + '&s_url=https%3A%2F%2Fqun.qq.com%2Fmanage.html&f_url=&ptlang=2052&ptredirect=101&aid=715030901&daid=73&j_later=0&low_login_hour=0&#174;master=0&pt_login_type=3&pt_aid=0&pt_aaid=16&pt_light=0&pt_3rd_aid=0'
            r2 = requests.get(url,cookies=cookies,allow_redirects=False)
            targetCookies = requests.utils.dict_from_cookiejar(r2.cookies)
            skey = requests.utils.dict_from_cookiejar(r2.cookies).get('skey')
            break
        time.sleep(3)
    return targetCookies,skey
join_qun = {}
create_qun = {}
manage_qun = {}

# get info from qq group
def qun(cookies,bkn,num):
    url = 'https://qun.qq.com/cgi-bin/qun_mgr/get_group_list'
    data = {'bkn':bkn}
    cookies = cookies
    # print(cookies)
    r = requests.post(url,data = data,cookies = cookies)

    res = r.text
    res = res.encode('utf-8', 'replace').decode()
    res1 = json.loads(res)
    global join_qun
    global create_qun
    global manage_qun
    if "create" in res1:
        create_qun = res1['create']
    else:
        create_qun = {}
    if "join" in res1:
        join_qun = res1['join']
    else:
        join_qun = {}
    if "manage" in res1:
        manage_qun = res1['manage']
    else:
        manage_qun = {}
 
    regex = re.compile(r'"gc":(\d+),"gn')
    r = re.findall(regex,r.text)
    return cookies 
 

# Functions for loading data , input the position for starting and ending
def load_data(st,end):
    url = 'https://qun.qq.com/cgi-bin/qun_mgr/search_group_members'
    def str_cookie(state):
        str1 = ''
        for i in state:
            str1 = str1 + i + '=' + state[i] + '; '
        return str1
    cookie = str_cookie(state)

    headers = {  
        "cookie": cookie
    }
    #get bkn from qq group
    def get_bkn():
        e = state['skey']
        t = 5381
        n = 0
        o = len(e)
        while n < o:
            t += (t << 5) + ord(e[n])
            n += 1
        return(2147483647 & t)

    global gc
    gc = show_qqqun_number()
    data = {
        "gc": gc, 
        "st": st,  
        "end": end, 
        "sort": "0",
        "bkn": get_bkn()
    }
     
    response = requests.post(url,data=data,headers=headers,verify=False )
    response = response.text
    response = response.encode('utf-8').decode("unicode_escape")
    return response

# Count qq group member
def get_qq_member_count():
    response = load_data(0,0)
    qq_member_count = json.loads(response)['count']
    return qq_member_count
 
# Function for get qq member list
qq_qun_info = []
def get_qq_member_list():
    global qq_qun_info
    global cft
    
    qq_qun_info = []
    count = math.ceil(get_qq_member_count()/21) 
    n = 0 
    j = 0 
    num = 1 
    while j < count:
        #load_data() numbers per page 1-20, 21-40 etc.
        response = load_data(n+j,n+20+j)
        
        response=filter_emoji(response,'')# handle the special character

        res = json.loads(response, strict=False)['mems']

        qq_name = ''
        qq_qun_name = ''
        qq_number = ''
        sex = ''
        qq_age = ''
        join_qun_time = ''
        last_speak_time = '' 
        for i in res:
            qq_name = i['nick']
            # replace the '\' character
            qq_name = filter_emoji(qq_name,'??????') # handle the special character
 
            qq_qun_name = i['card']
            
            qq_qun_name = filter_emoji(qq_qun_name,'??????') # handle the special character
             
            qq_number = str(i['uin'])
             
            sex = i['g'] #if ex = 0 male, sex = -1 nan, sex = 1 female
            if sex == 0:
                sex = '男'
            elif sex == 1:
                sex = '女'
            elif sex == -1:
                sex = '未知'
            else:
                sex = '错误'
             
            qq_age = i['qage']
            join_qun_time = i['join_time'] #这里返回的是10位整数
            last_speak_time = i['last_speak_time']
            # put all above into dict1
            dict1 = {}
            dict1['num'] = num
            dict1["qq_name"] = qq_name
            dict1["qq_qun_name"] = qq_qun_name
            dict1["qq_number"] = qq_number
            dict1["sex"] = sex
            dict1["qq_age"] = qq_age
            #change time structure of join group time
            join_qun_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(join_qun_time))
            dict1["join_qun_time"] = join_qun_time
            #change time structure of last speak time
            last_speak_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_speak_time))
            dict1["last_speak_time"] = last_speak_time
            # make dict1 join qq_qun_info
            qq_qun_info.append(dict1)
 
            if select_var.get() == 0:
                table.insert('', 'end', values=(num, qq_name, qq_qun_name, qq_number, sex,qq_age,join_qun_time,last_speak_time))
                # scroll to the bottom of the table                

                scroll.insert(END, "\n"+str(qq_qun_info[num-1]))
                scroll.see("end")
 
            num = num + 1 
        j = j + 1
        n += 20
    # print(qq_qun_info)
 
    member_count = get_qq_member_count()
    if member_count > 0:
        if(select_var.get() == 1): # choose
            messagebox.showinfo('提示','查询到'+str(member_count)+'个好友数据，正在扫描后四位信息，此过程可能会比较漫长，请耐心等待...')
            from_qq_get_info() # deep search
            messagebox.showinfo('提示','导入完成，一共导入'+str(member_count)+'个好友数据')
        else:
            messagebox.showinfo('提示','查询到'+str(member_count)+'个好友数据')
    else:
        messagebox.showinfo('提示','没有查询到任何好友数据')
     
    return qq_qun_info
    # print(qq_qun_info) #显示群成员列表
 
#digging for more info associated qq account, cost more times
def from_qq_get_info():
    time.sleep(2)
    global c_info
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    }
    for i in qq_qun_info:
        url = 'https://zy.xywlapi.cc/qqcx?qq='+i['qq_number']
        # url = 'https://qb-api.ltd/allcha.php?qq='+i['qq_number']  # 20220520 maybe need change interface
        
        response = requests.get(url,headers=headers)
        
        resp = response.text
        c_info = resp
        
        response=filter_emoji(resp,'')
        response = json.loads(response, strict=False)
        # print(response)
        if response['status'] == 200:
            qq_qun_info[qq_qun_info.index(i)]['phone'] = response['phone']
            qq_qun_info[qq_qun_info.index(i)]['diqu'] = response['phonediqu']
            qq_qun_info[qq_qun_info.index(i)]['lol'] = response['lol']
            qq_qun_info[qq_qun_info.index(i)]['wb'] = response['wb']
        else:
            qq_qun_info[qq_qun_info.index(i)]['phone'] = '未知'
            qq_qun_info[qq_qun_info.index(i)]['diqu'] = '未知'
            qq_qun_info[qq_qun_info.index(i)]['lol'] = '未知'
            qq_qun_info[qq_qun_info.index(i)]['wb'] = '未知'
 
        table.insert('', 'end', values=(i['num'], i['qq_name'], i['qq_qun_name'], i['qq_number'], i['sex'],i['qq_age'],i['join_qun_time'],i['last_speak_time'],i['phone'],i['diqu'],i['lol'],i['wb']))
        
        def log():
            scroll.insert(END, "\n"+str(qq_qun_info[qq_qun_info.index(i)]))
            scroll.see("end")

        threading.Thread(target = log).start()
 
# Function for save info to excel
def export_excel(export):
    #change dict to DataFrame
    pf = pd.DataFrame(list(export))
    
    if select_var.get() == 1:
        order = ['num','qq_name','qq_qun_name','qq_number','sex','qq_age','join_qun_time','last_speak_time','phone','diqu','lol','wb']
    else:
        order = ['num','qq_name','qq_qun_name','qq_number','sex','qq_age','join_qun_time','last_speak_time']
    pf = pf[order]

    columns_map = {
        'num':'序号',
        'qq_name':'qq昵称',
        'qq_qun_name':'qq群昵称',
        'qq_number':'qq号码',
        'sex':'性别',
        'qq_age':'Q龄',
        'join_qun_time':'入群时间',
        'last_speak_time':'最近发言时间',
        'phone':'手机号',
        'diqu':'地区',
        'lol':'lol',
        'wb':'微博UID'
    }
    pf.rename(columns = columns_map,inplace = True)

    file_path = pd.ExcelWriter(save_path+'.xlsx')

    pf.fillna(' ',inplace = True)

    pf.to_excel(file_path,encoding = 'utf-8',index = False)

    file_path.save()
 
# Function for fliter the special characters
def filter_emoji(desstr, restr=''):

   
    
    # 1. handle char like \x14 etc
    content = desstr 
    result = re.findall(r'\\x[a-f0-9]{2}', content)
    content = content.encode('unicode_escape').decode('utf-8').replace(' ', '')
    result = re.findall(r'\\x[a-f0-9]{2}', content)
    for x in result:

        content = content.replace(x, '')

    content = content.encode('utf-8').decode('unicode_escape')
    
    # 2 . handle emoji  
    res = re.compile(u'[\U00010000-\U0010ffff\\uD800-\\uDBFF\\uDC00-\\uDFFF]')
    
    return res.sub(restr, content)

 
# get  info of all qq groups
def get_allqun_list(group_name):
    if group_name == '我创建的群':

        return create_qun
    if group_name == '我加入的群':

        return join_qun
    if group_name == '我管理的群':

        return manage_qun

 
# GUI, powered with tkinter
label1 = tk.Label(root,text = 'QQ群号:')
label1.place(x = 150,y = 10)
label1.config(font = ('微软雅黑',12))

# Pick one group
qq_qun_gc = []
qq_qun_gn = []
def show_group(*arg):
    global qq_qun_gc
    global qq_qun_gn
    qq_qun_gc = []
    qq_qun_gn = []
    all_qun1 = get_allqun_list(value_group.get())
    # print(all_qun1)
    for i in all_qun1:
        qq_qun_gc.append(i['gc'])
        gn = emoji.demojize(i['gn'])
        gn = re.sub(emoji.get_emoji_regexp(), r"?", gn)
        gn = filter_emoji(gn,'?')
        qq_qun_gn.append(gn)

    xiala_list["values"] = qq_qun_gn
    xiala_list.current(0)
value_group = StringVar()


data_group = ["我创建的群","我管理的群","我加入的群"]
group_list = ttk.Combobox(root, width = 10, height = 10, textvariable = value_group, state="readonly")

# Font setting
group_list.config(font = ('微软雅黑',12))
group_list.bind("<<ComboboxSelected>>",show_group)  #事件的绑定
group_list.place(x = 230, y = 10)

group_list["values"] = data_group

# Pick the number of gourps
def show_qqqun_number(*arg):
    index1 = xiala_list.current()
    qq_qun_num = qq_qun_gc[index1]
    return qq_qun_num
     
value = StringVar()
# Create a drop-down list
xiala_list = ttk.Combobox(root, width = 13, height = 10, textvariable = value)

xiala_list.config(font = ('微软雅黑',12))
xiala_list.place(x = 360, y = 10)

 
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
width = 1000
height = 500
x = int((screenwidth - width) / 2)
y = int((screenheight - height) / 2)
root.geometry('{}x{}+{}+{}'.format(width, height, x, y))  # &#12068;&#12073;position
xscroll = Scrollbar(root, orient=HORIZONTAL)
yscroll = Scrollbar(root, orient=VERTICAL)
columns = ['序号', 'qq昵称', 'qq群昵称', 'qq号码', '性别', 'Q龄', '入群时间', '最近发言时间','手机号','地区','lol','微博UID']
table = ttk.Treeview(
        master=root,  # &#12119;容器
        height=20,  # 表格显&#12144;的&#12175;数,height&#12175;
        columns=columns,  # 显&#12144;的列
        show='headings',  # 隐藏&#12216;列
        xscrollcommand=xscroll.set,  # x轴滚动条
        yscrollcommand=yscroll.set,  # y轴滚动条
        )
xscroll.config(command=table.xview)
xscroll.pack(side=BOTTOM, fill=X)
yscroll.config(command=table.yview)
yscroll.pack(side=RIGHT, fill=Y)
table.pack(fill=BOTH, expand=True)
table.heading(column='序号', text='序号', anchor='w',
                  command=lambda: print('序号'))  # 定义表头
table.heading('qq昵称', text='qq昵称', )  # 定义表头
table.heading('qq群昵称', text='qq群昵称', )  # 定义表头
table.heading('qq号码', text='qq号码', )  # 定义表头
table.heading('性别', text='性别', )  # 定义表头
table.heading('Q龄', text='Q龄', )  # 定义表头
table.heading('入群时间', text='入群时间', )  # 定义表头
table.heading('最近发言时间', text='最近发言时间', )  # 定义表头
table.heading('手机号', text='手机号', )  # 定义表头
table.heading('地区', text='地区', )  # 定义表头
table.heading('lol', text='lol', )  # 定义表头
table.heading('微博UID', text='微博UID', )  # 定义表头
table.column('序号', width=50, minwidth=50, anchor=S, )  # 定义列
table.column('qq昵称', width=100, minwidth=100, anchor=S)  # 定义列
table.column('qq群昵称', width=100, minwidth=100, anchor=S)  # 定义列
table.column('qq号码', width=100, minwidth=100, anchor=S)  # 定义列
table.column('性别', width=50, minwidth=50, anchor=S)  # 定义列
table.column('Q龄', width=50, minwidth=50, anchor=S)  # 定义列
table.column('入群时间', width=150, minwidth=150, anchor=S)  # 定义列
table.column('最近发言时间', width=150, minwidth=150, anchor=S)  # 定义列
table.column('手机号', width=100, minwidth=100, anchor=S)  # 定义列
table.column('地区', width=100, minwidth=100, anchor=S)  # 定义列
table.column('lol', width=100, minwidth=100, anchor=S)  # 定义列
table.column('微博UID', width=100, minwidth=100, anchor=S)  # 定义列
table.place(x = 10,y = 50)
 
#Add a command output box for log
scroll=scrolledtext.ScrolledText(root,width=164,height=14,font=('黑体',10))
def Scroll(root):
    scroll.place(x=10,y=480)
Scroll(root)
 
#Add a check box
select_var = IntVar()
select = Checkbutton(root, text='查询后四位数据(耗时)', variable=select_var)
select.place(x = 520, y = 10)
 
def chaxun():
    #clear the info in Scroll
    scroll.delete(1.0,END)
    #clear the info in Table
    table.delete(*table.get_children())
    # set threading
    threading.Thread(target=get_qq_member_list).start()
     
#Add a check button btn1
btn1 = tk.Button(root,text = '查询',command = chaxun)
btn1.config(font = ('微软雅黑',9))
btn1.config(width = 8)
btn1.place(x = 680,y = 10)
     
def save():
    export_excel(qq_qun_info)
    messagebox.showinfo('提示','保存成功')
save_path =''
def FileSave():
    global save_path
    save_path = tkinter.filedialog.asksaveasfilename(title='保存',initialfile=value.get(),filetypes=[('excel', '*.xlsx')])
    #return the save_path name
    if save_path:
        save()
    else:
        messagebox.showinfo('提示','取消保存')
 
#Add a check button btn2
btn2 = tk.Button(root,text = '保存表格',command = FileSave)
btn2.config(font = ('微软雅黑',9))
btn2.config(width = 8)
btn2.place(x = 770,y = 10)
 
 
if __name__ == '__main__':

    global state
    qrsig = QR()
    ptqrtoken = ptqrtoken(qrsig)
    cookie = cookies(qrsig,ptqrtoken)
    skey = cookie[1]
    bkn = bkn(skey)
    ck = cookie[0]
    state = qun(ck, bkn,'434252251')

    root.iconbitmap(icon_path)
    root.geometry('1190x700')
    root.title("QQ群信息爬取")
    root.resizable(False, False)
    root.mainloop()
