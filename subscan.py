import requests
import re
import base64
import inspect
import sys
import socket
from time import sleep
from multiprocessing.dummy import Pool as ThreadPool

class SubDomain:
    def __init__(self,url):
        self.url = url
        self.subs_filtered = []
        self.subs_filtered_domain = []
        self.ports = []
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
            'Referer':'http://www.baidu.com/',
        }
        socket.setdefaulttimeout(0.5)
        self.subs = self._get_all()
        self._save()
        
    #查询啦接口，容易被封，TMD
    def chaxunla(self):
        print('[+] 正在使用 '+inspect.stack()[0][3]+' 接口')
        sub = []
        res = requests.get('http://api.chaxun.la/toolsAPI/getDomain/?k={}&action=moreson'.format(self.url),headers=self.headers)
        res = res.json()
        if "status" in res and res['status']==3:
            print('[+] 查询啦接口可能出现问题!')
            print('[+] '+res['message'])
        else: 
            while True:
                page = 1
                res = requests.get('http://api.chaxun.la/toolsAPI/getDomain/?k={}&action=moreson&page={}'.format(self.url,page),headers=self.headers)
                res = res.json()
                if(res['status']==-2):
                    break
                for i in res['data']:
                    sub.append(i['domain'])
                if len(res['data'<100]):
                    break
                page += 1
                sleep(1)
        print('[+] '+inspect.stack()[0][3]+' 接口查询完毕: 共 '+str(len(sub))+' 条')
        return sub
    #chinaz
    def chinaz(self):
        print('[+] 正在使用 '+inspect.stack()[0][3]+' 接口')
        subs = []
        res = requests.get('http://tool.chinaz.com/subdomain?domain='+self.url,headers=self.headers)
        p = re.compile(r'<span class="col-gray02">[\u4e00-\u9fa5](\d)[\u4e00-\u9fa5]')
        #print(res.text)
        #获取页数
        if len(p.findall(res.text))>=1:
            page = int(p.findall(res.text)[0])
            #获取子域名
            for i in range(1,page+1):
                res = requests.get('http://tool.chinaz.com/subdomain?domain={}&page={}'.format(self.url,i),headers=self.headers)
                p = re.compile(r'target="_blank">(.*?)</a></div>')
                sub = p.findall(res.text)
                subs.extend(sub)
                sleep(0.5)
        if(len(subs)==0):
            print('[+] chinaz接口可能出现问题!')
        print('[+] '+inspect.stack()[0][3]+' 接口查询完毕: 共 '+str(len(subs))+' 条')
        return subs
    #ip138接口
    def ip138(self):
        print('[+] 正在使用 '+inspect.stack()[0][3]+' 接口')
        res = requests.get('http://site.ip138.com/{}/domain.htm'.format(self.url),headers=self.headers)
        p = re.compile(r'target="_blank">(.*?)</a></p>')
        sub = p.findall(res.text)
        #print(res.text)
        if(len(sub)==0):
            print('[+] ip138接口可能出现问题!')
        print('[+] '+inspect.stack()[0][3]+' 接口查询完毕: 共 '+str(len(sub))+' 条')
        return sub
    #fofa api，要钱的
    def fofa_api(self):
        print('[+] 正在使用 '+inspect.stack()[0][3]+' 接口')
        email = '1157799274@qq.com'
        key = '36e9d7c4f23a45a5f0b3e6650157e6f0'
        size = 50
        s = 'domain=\"{}\"'.format(self.url)
        s = base64.b64encode(s.encode())
        res = requests.get('https://fofa.so/api/v1/search/all?email={}&key={}&qbase64={}&size={}'.format(email,key,s,size))
        res = res.json()
        if "error" in res and res["error"]==True:
            print('[+] fofa api可能出现问题!')
            return res["errmsg"]
        else:
            return res
    #百度云观测接口,暂时只爬取子域名
    def baidu(self):
        print('[+] 正在使用 '+inspect.stack()[0][3]+' 接口')
        sub = []
        res = requests.get('http://ce.baidu.com/index/getRelatedSites?site_address='+self.url,headers=self.headers)
        res = res.json()
        for i in res['data']:
            sub.append(i['domain'])
        print('[+] '+inspect.stack()[0][3]+' 接口查询完毕: 共 '+str(len(sub))+' 条')
        return sub
    #汇总并去重，暂时没有fofa api，因为我没钱
    def _get_all(self):
        subs = []
        #sub = self.chaxunla()
        #subs.extend(sub)
        sub = self.chinaz()
        subs.extend(sub)
        sub = self.ip138()
        subs.extend(sub)
        sub = self.baidu()
        subs.extend(sub)
        #去重
        subs = list(set(subs))
        print('[+] 去重完毕: 共 '+str(len(subs))+' 条')
        return subs
    #save the results
    def _save(self):
        filename = self.url + '.txt'
        with open(filename,'w') as f:
            for i in self.subs:
                f.write(i+'\n')
        print('[+] 运行完毕，结果保存至 '+filename)
    def filter(self):
        print('[+] 正在过滤无法访问的子域名...')
        filename = self.url+'(filtered).txt'
        scan_pool = ThreadPool(processes = 16)
        scan_pool.map(self.is_use,self.subs)
        scan_pool.close()
        scan_pool.join()
        with open(filename,'w',encoding='utf-8') as f:
            for i in self.subs_filtered_domain:
                f.write(i+'\n')
        print('[+] 过滤后还剩: '+str(len(self.subs_filtered)))
        print('[+] 结果保存至 '+filename)
    def is_use(self,site):
        p = re.compile(r'<title>(.*?)</title>')
        try:
            res = requests.get('http://'+site,timeout=3,headers=self.headers)
            #print(res.encoding)
            res.encoding='utf-8'
            title = p.findall(res.text)[0]
            print(site,res.status_code,title)
            self.subs_filtered.append(site+'\t'+str(res.status_code)+'\t'+title+'\n')
            self.subs_filtered_domain.append(site)
        except Exception as e:
            print(e)
    def scan_port(self):
        print('[+] 正在扫描端口...')
        filename = self.url+'-ports.txt'
        scan_pool = ThreadPool(processes = 16)
        scan_pool.map(self.is_open,self.subs_filtered_domain)
        scan_pool.close()
        scan_pool.join()
        print('[+] End!')
    def is_open(self,site):
        for port in self.ports:
            try:
                s = socket.socket(2,1)
                res = s.connect_ex((site,port))
                if res == 0:
                    print('Site: {}  Port {}: OPEN'.format(site,port))
            except Exception as e:
                print(e)
                s.close()
        

if __name__=='__main__':
    if len(sys.argv)==1:
        print('[+] 使用方法: python '+sys.argv[0]+' baidu.com')
        print('[+] 可选参数:\n[1] -f\n\t加了之后会过滤无法访问的子域名，如果加必须加在末尾')
    elif len(sys.argv)==2:
        t = SubDomain(sys.argv[1])
    elif len(sys.argv)==3 and sys.argv[2]=='-f':
        t = SubDomain(sys.argv[1])
        print(t.subs)
        t.filter()
    elif len(sys.argv)==3 and sys.argv[2]=='-p':
        t = SubDomain(sys.argv[1])
        print(t.subs)
        t.filter()
        t.scan_port()
    else:
        print('参数错误!')