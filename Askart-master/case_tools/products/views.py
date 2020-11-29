from django.contrib.auth.decorators import login_required
from .forms import Userform, Loginform
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View
from django.views.generic import FormView
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.core.files import File
import json
from django.http import JsonResponse
import codecs
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os
from bs4 import BeautifulSoup
import requests
import time
import smtplib

def index(request):
    return HttpResponse("Hello world")


def error(request):
    return HttpResponse("Error!")


class UserFormView(View):
    form_class = Userform
    template_name = "products/signup.htm"

    def get(self, request):
        #username=request.user.get_full_name()
        form = self.form_class(None)
        
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        #username=request.user.get_full_name()
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('products:compare')
        else:
            return HttpResponse("Error")

        return render(request, self.template_name, {'form': form})


def display(request):
    return redirect('products:compare')
    
class AutoCompleteView(View):
    def get(self,request):
        name = request.GET.get("term","")
        word=name
        name=word[0].upper()+word[1:]
        print(name)        
        with codecs.open('products/amazon.json', 'r', 'utf-8') as data_file:
            data = json.load(data_file)
        prod_list1 = data["selection1"]
        prodstuff=[]
        print(name)
        if name:
            for p in prod_list1:
                if p["name"].startswith(name):
                    prodstuff.append(p)
        else:
            prodstuff=prod_list1
        i=0
        results = []
        for prods in prodstuff:
            if "selection2" in prods:
                user_json = {}
                user_json['id']=i
                user_json['label'] = prods["name"]
                user_json['value'] = prods["name"]
                results.append(user_json)
                i=i+1

        data = json.dumps(results[:10])
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)

def details(request,name):
    with codecs.open('products/amazon.json', 'r', 'utf-8') as amazon,\
            codecs.open('products/flipkart.json', 'r', 'utf-8') as flipkart:
        data1 = json.load(amazon)
        data2 = json.load(flipkart)
		
    prod_list1 = data1["selection1"]
    prod_list2 = data2["selection1"]

    prod_list=list()
    pics = os.listdir('products/static')

    for prods in prod_list1:
        if "selection2" in prods:
            prods["image"]=None

            for pic in pics:
                if prods["name"] in pic:
                    prods["image"]=pic
                    continue

            prod_list.append(prods)
    '''
    temp_list=list()
    for prods in prod_list:
        for p in prod_list2:
            if p["name"].split(',')[0].startswith(prods["name"].split(',')[0]
                                                  [:len(prods["name"].split(',')[0]) - 1]) \
                    and prods["name"] not in temp_list:
                temp_list.append(prods["name"])
    #print(temp_list)
    #file=open('products/a.txt','w')
    #file.write(str(temp_list))
    #print("length=" + str(len(temp_list)))
    '''
    temp=dict()
    new_list=list()
    p_list=list()
    #username=request.user.get_full_name()
    for prods in prod_list:
        if prods["name"]==name:
            temp=prods
            for p in prod_list2:
                if p["name"].split(',')[0].startswith(prods["name"].split(',')[0]
                                                      [:len(prods["name"].split(',')[0])-1])\
                        and prods["name"] not in new_list:
                    new_list.append((temp["name"]))
                    temp["f_url"]=p["url"]
                    temp["f_price"]=p["selection2"]
                    temp["f_price_url"]=p["selection2_url"]
					

    return render(request,"products/details.html",{"product":temp})


@login_required(login_url="/products/")
def compare_views(request):
    flag = 0
    flipkart=''
    amazon=''
    olx=''
    amazon_name=''
    olx_name=''
    flipkart_name=''
    flag_amazon = 1
    flag_olx = 1
    flag_flipkart = 1
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    if(request.method=="GET"):
        flag = 0
        return render(request, "products/price.html", {"flag": flag })
    elif(request.method=="POST"):
        flag = 1
        name = request.POST['phoneName']
        desired_price = request.POST['desiredPrice']
        print("Name: ", name)
        def flipkart(name):
            try:
                global flipkart1, flipkart_name, flipkart_price
                name1 = name.replace(" ","+")   #iphone x  -> iphone+x
                flipkart1=f'https://www.flipkart.com/search?q={name1}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off'
                res = requests.get(f'https://www.flipkart.com/search?q={name1}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off',headers=headers)
                soup = BeautifulSoup(res.text,'html.parser')
                flipkart_name = soup.select('._4rR01T')[0].getText().strip()
                flipkart_name = flipkart_name.upper()
                if name.upper() in flipkart_name:
                    flipkart_price = soup.select('._30jeq3')[0].getText().strip()
                    flipkart_name = soup.select('._4rR01T')[0].getText().strip()
                else:
                    flipkart_price='0'
                return flipkart_price 
            except:
                flipkart_price= '0'
            return flipkart_price 

        def amazon(name):
            try:
                global amazon1, amazon_price, amazon_name
                name1 = name.replace(" ","-")
                name2 = name.replace(" ","+")
                amazon1=f'https://www.amazon.in/{name1}/s?k={name2}'
                res = requests.get(f'https://www.amazon.in/{name1}/s?k={name2}',headers=headers)
                print("\nSearching in amazon:")
                soup = BeautifulSoup(res.text,'html.parser')
                amazon_page = soup.select('.a-color-base.a-text-normal')
                amazon_page_length = int(len(amazon_page))
                for i in range(0,amazon_page_length):
                    name = name.upper()
                    amazon_name = soup.select('.a-color-base.a-text-normal')[i].getText().strip().upper()
                    if name in amazon_name[0:20]:
                        amazon_name = soup.select('.a-color-base.a-text-normal')[i].getText().strip().upper()
                        amazon_price = soup.select('.a-price-whole')[i].getText().strip().upper()
                        break
                    else:
                        i+=1
                        i=int(i)
                        if i==amazon_page_length:
                            amazon_price = '0'
                            break
                return amazon_price
            except:
                amazon_price = '0'
            return amazon_price


        def olx(name):
            try:
                global olx1, olx_price, olx_name
                name1 = name.replace(" ","-")
                olx1=f'https://www.olx.in/items/q-{name1}?isSearchCall=true'
                res = requests.get(f'https://www.olx.in/items/q-{name1}?isSearchCall=true',headers=headers)
                print("\nSearching in OLX......")
                soup = BeautifulSoup(res.text,'html.parser')
                olx_name = soup.select('._2tW1I')
                olx_page_length = len(olx_name)
                for i in range(0,olx_page_length):
                    olx_name = soup.select('._2tW1I')[i].getText().strip()
                    name = name.upper()
                    olx_name = olx_name.upper()
                    if name in olx_name:
                        olx_price = soup.select('._89yzn')[i].getText().strip()
                        olx_name = soup.select('._2tW1I')[i].getText().strip()
                        olx_loc = soup.select('.tjgMj')[i].getText().strip()
                        try:
                            label = soup.select('._2Vp0i span')[i].getText().strip()
                        except:
                            label = "OLD"
                        break
                    else:
                        i+=1
                        i=int(i)
                        if i==olx_page_length:

                            olx_price = '0'
                            break
                return olx_price
            except:
                olx_price = '0'
            return olx_price

        def convert(a):
            b=a.replace(" ",'')
            c=b.replace("INR",'')
            d=c.replace(",",'')
            f=d.replace("₹",'')
            g=int(float(f))
            return g

        flipkart_price=flipkart(name)
        amazon_price=amazon(name)
        olx_price = olx(name)
        if flipkart_price=='0':
            print("No product found!")
            flipkart_price = int('0')
        else:
            print("\nFLipkart Price:",flipkart_price)
            flipkart_price=convert(flipkart_price)
        if amazon_price=='0':
            print("No Product found!")
            amazon_price = int(amazon_price)
        else:
            print("\namazon price: ₹",amazon_price)
            amazon_price=convert(amazon_price)
        if olx_price =='0':
            print("No product found!")
            olx_price = int(olx_price)
        else:
            print("\nOlx Price:",olx_price)
            olx_price=convert(olx_price)
        time.sleep(2)
        lst = [flipkart_price,amazon_price,olx_price]
        lst2=[]
        for j in range(0,len(lst)):
            if lst[j]>0:
                lst2.append(lst[j])
        min_price=min(lst2)
        global price

        price = {
            f'{amazon_price}':f'{amazon1}',
            f'{olx_price}':f"{olx1}",
            f'{flipkart_price}':f'{flipkart1}'
            
        }
        for key, value in price.items():
            if int(key)==min_price:
                min_link = price[key]
        
        if(min_price < int(desired_price)):
            username = request.user.username
            send_mail(min_link, username)
        if(amazon_name==""):
            amazon_name = "Null"
            flag_amazon = 0
        if(flipkart_name==""):
            flipkart_name = "Null"
            flag_flipkart = 0        
        if(olx_name==""):
            olx_name = "Null"
            flag_olx = 0
        return render(request, "products/price.html", {"flag":flag, "flipkart":flipkart1, "amazon":amazon1, "olx":olx1, "amazon_price": amazon_price, "flipkart_price": flipkart_price, "olx_price": olx_price, "amazon_name": amazon_name, "flipkart_name": flipkart_name, "olx_name": olx_name, "min_link": min_link, "flag_olx":flag_olx, "flag_flipkart":flag_flipkart, "flag_amazon":flag_amazon, "min_price": min_price})


def send_mail(min_link, reciever):
    print("Reciver: ", reciever)
    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.ehlo()
    sender_mail = 'pds146c@gmail.com'
    password = 'parisar2212'
    server.login(sender_mail, password)
    subject = "Price fell down!"
    body = f'Check the given link {min_link}'
    message = f"Subject: {subject}\n\n {body}"
    server.sendmail('sender_email_id', reciever, message)
    server.quit()


