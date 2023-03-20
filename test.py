# 5555555555555555
import requests
from lxml import etree
import re 

requests.packages.urllib3.disable_warnings()

url = "https://jypx.gzsi.gzhrlss:9500/gdld_gz/action/MainAction"

header = {
    "Accept":"image/gif, image/jpeg, image/pjpeg, application/x-ms-application, application/xaml+xml, application/x-ms-xbap, */*",
    "Referer":"https://jypx.gzsi.gzhrlss:9500/gdld_gz/action/MainAction",
    "Accept-Language":"zh-Hans-CN,zh-Hans;q=0.5",
    "User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)",
    "Content-Type":"application/x-www-form-urlencoded",
    "Accept-Encoding":"gzip, deflate",
    "Host":"jypx.gzsi.gzhrlss:9500",
    "Content-Length":"468",
    "Connection":"Keep-Alive",
    "Cache-Control":"no-cache",
    "Cookie": "JSESSIONID=zMP84yiOcfq9BUWaXUpRkFbp0kh1GHsM2S8eTHBEqiiOVwW2zez-!289051377;ORA_OTD_JROUTE=WjEE-ZH4egjJ1aEV;SUFS=24651",
}

姓名 = str(姓名.encode('GBK')).replace("\\x", "%").split('\'')[1]
json_str_gaoxiao = f"ActionType=ggsjgl_bgxbys_xlcx_p&AAC003={姓名}&AAC002={证件号}"
data = requests.post(url, data=json_str_gaoxiao, headers=header, verify=False)

pattern = re.compile("aform.bbsjxh_xlcx.value = '(.*?)';", re.S)

sgin = re.findall(pattern, data.content.decode())[0]


# 6666666666666

json_strbb = f"ActionType=ggsjgl_bgxbys_xlcx_q&AAC002={证件号}&AAC003={姓名}&bbsjxh_xlcx={sgin}&isQuery=true"
data = requests.post(url, data=json_strbb, headers=header, verify=False)

html = etree.HTML(data.content.decode("uft-8"),parser=etree.HTMLParser(encoding='utf-8'))
list_all = []

#title = html.xpath('//tr[@class="list_table_thead_tr_title"]/td[@class="list_table_thead_td_title"]/text()')
#title = [i.replace(" ", "") for i in title]
#list_all.append(title)

num = 0
while True:
    list_data = html.xpath("//tbody/tr[@id='TR{}']/td/text()".format(num))
    list_data = [i.replace(" ", "") for i in list_data]
    if len(list_data) == 0:
        break
    num = num + 1
    list_all.append(list_data)
if list_all != []:
    def takeSecond(ele):
        return ele[7]
    list_all.sort(key=takeSecond)
    if list_all[-1][8]=="*":
        文化程度 = list_all[0][5]
        毕业时间 = list_all[0][7]
        毕业时间 = 毕业时间[0:4] + "-" + 毕业时间[4:6] + "-" + 毕业时间[6:8]
        毕业院校 = list_all[0][3]
        专业 = list_all[0][4]
        学习形式 = list_all[0][8]
    else:
        文化程度 = list_all[-1][5]
        毕业时间 = list_all[-1][7]
        毕业时间 = 毕业时间[0:4] + "-" + 毕业时间[4:6] + "-" + 毕业时间[6:8]
        毕业院校 = list_all[-1][3]
        专业 = list_all[-1][4]
        学习形式 = list_all[-1][8]
print(list_all)
print(毕业时间 +"\n"+ 学习形式)