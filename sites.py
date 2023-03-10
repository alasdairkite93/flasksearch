import json
import multiprocessing
from os.path import exists
import math
import requests
import re
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request
import os
import random
import threading
from time import sleep
import sys
from seleniumwire import webdriver
from selenium_stealth import stealth
import time
from selenium.webdriver.common.by import By

from os import path


class Proxies:

    def createProxyList(self):

        print("Creating proxies")

        url = 'https://free-proxy-list.net/'

        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find("table", {"class": "table table-striped table-bordered"})
        tbody = table.find("tbody")

        proxies = []
        li_ip = []

        for tr in tbody:
            if len(proxies) > 10:
                break
            else:
                cells = tr.findAll("td")
                ip = cells[0].text + ":" + cells[1].text
                li_ip.append(ip)

        with open('/home/alasdairkite/flasksearch/flasksearch/static/proxies.txt', 'w') as p:
            for proxy in li_ip:
                p.write(proxy)
                p.write("\n")
            p.close()

    def is_bad_proxy(self, pip):
        try:
            proxy_handler = urllib.request.ProxyHandler({'http': pip})
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            sock = urllib.request.urlopen('https://www.ebay.co.uk/', timeout=1)
        except urllib.error.HTTPError as e:
            print('Error code: ', e.code)
            return 0
        except Exception as detail:

            print("ERROR:", detail)
            return 0
        return 1

    def getProxy(self):

        prox_list = ['185.199.229.156:7492',
                    '185.199.228.220:7300',
                    '185.199.231.45:8382',
                    '188.74.210.207:6286',
                    '188.74.183.10:8279',
                    '188.74.210.21:6100',
                    '45.155.68.129:8133',
                    '154.95.36.199:6893',
                    '45.94.47.66:8110',
                    '144.168.217.88:8780']

        proxlen = len(prox_list)-1
        print("proxlen: ", proxlen)
        proxy = prox_list[random.randint(0, proxlen)]
        print(proxy)
        return proxy


class Utility:

    def find_json_objects(self, text: str, decoder=json.JSONDecoder()):
        pos = 0
        while True:
            match = text.find("{", pos)
            if match == -1:
                break
            try:
                result, index = decoder.raw_decode(text[match:])
                yield result
                pos = match + index
            except ValueError:
                pos = match + 1

class Zoopla:

    def __init__(self, query, channel, beds, minprice, maxprice):
        self.searchquery = query
        self.channel = channel
        self.beds = beds
        self.price_min = minprice
        self.price_max = maxprice

    def requests(self):

        util = Utility()
        proxy = Proxies()

        searchurl = f'https://www.zoopla.co.uk/{self.channel}/property/{self.searchquery}/?q={self.searchquery}&results_sort=newest_listings&search_source={self.channel}&beds_max={self.beds}&price_min={self.price_min}&price_max={self.price_max}'

        baseurl = 'https://www.zoopla.co.uk/'

        zoop_l = []

        with open('zoopla.json', 'r') as r:
            data = json.loads(r.read())
            listings = data['props']['pageProps']['regularListingsFormatted']

            for listing in listings:
                li = []
                li.append(listing['address'])
                li.append(listing['branch']['name'])
                li.append(listing['features'][0]['content'])
                li.append(listing['price'])
                li.append('http://www.zoopla.co.uk' + listing['listingUris']['detail'])
                try:
                    li.append(listing['image']['src'])
                except KeyError:
                    li.append(" ")
                li.append("zoopla")
                zoop_l.append(li)

        return zoop_l

class Rightmove:

    def __init__(self, query, channel, radius, bedrooms, minprice, maxprice, page, maxrooms, type):
        self.pcode = query
        self.channel = channel
        self.radius = radius
        self.bedrooms = bedrooms
        self.minprice = minprice
        self.maxprice = maxprice
        self.page = page
        self.maxrooms = maxrooms
        self.type = type

    def requestScrape(self):

        utils = Utility()
        json_data =[]



        # Function to postcode

        rent = 'property-to-rent'
        sales = 'property-for-sale'

        if self.channel == "SALE":
            search_url = f'https://www.rightmove.co.uk/{sales}/search.html?searchLocation='

        else:
            search_url = f'https://www.rightmove.co.uk/{rent}/search.html?searchLocation='
        x = requests.get(search_url + self.pcode)

        soup = BeautifulSoup(x.text, 'html.parser')
        results = soup.find('input', {'id': 'locationIdentifier'}).get('value')
        txt = results
        x = re.findall("[^^]*$", txt)
        code = x[0]

        properties = []
        print(type(self.page))
        urls = []

        for ind in range(3):
            ind = ind*24
            if len(self.pcode) > 4 and self.channel == 'SALE':
                t_url = f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE%5E{code}&index={ind}&maxBedrooms={self.maxrooms}&minBedrooms={self.bedrooms}&maxPrice={self.maxprice}&minPrice={self.minprice}&displayPropertyType={self.type}&radius={self.radius}&propertyTypes=&mustHave=&dontShow=&furnishTypes=&keywords='
            if len(self.pcode) <= 4 and self.channel == 'SALE':
                t_url = f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=OUTCODE%5E{code}&index={ind}&insId=1&radius={self.radius}&displayPropertyType={self.type}&minPrice={self.minprice}&maxPrice={self.maxprice}&areaSizeUnit=sqft&googleAnalyticsChannel=buying&minBedrooms={self.bedrooms}&maxBedrooms={self.maxrooms}'
            if len(self.pcode) <= 4 and self.channel == 'LETTINGS':
                # t_url = f'https://www.rightmove.co.uk/property-to-rent/find.html?searchType=RENT&locationIdentifier=REGION%5E{code}&insId=1&radius={self.radius}&minPrice={self.minprice}&maxPrice={self.maxprice}&minBedrooms={self.bedrooms}&maxBedrooms={self.maxrooms}&displayPropertyType={self.type}&maxDaysSinceAdded=&sortByPriceDescending=&_includeLetAgreed=on&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&letType=&letFurnishType=&houseFlatShare='
                t_url = f'https://www.rightmove.co.uk/property-to-rent/find.html?searchType=RENT&locationIdentifier=POSTCODE%5E{code}&insId=1&radius={self.radius}&minPrice={self.minprice}&maxPrice={self.maxprice}&minBedrooms={self.bedrooms}&maxBedrooms={self.maxrooms}&displayPropertyType={self.type}&maxDaysSinceAdded=&sortByPriceDescending=&_includeLetAgreed=on&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&letType=&letFurnishType=&houseFlatShare='
            if len(self.pcode) > 4 and self.channel == 'LETTINGS':
                t_url = f'https://www.rightmove.co.uk/property-to-rent/find.html?searchType=RENT&locationIdentifier=POSTCODE%5E{code}&insId=1&radius={self.radius}&minPrice={self.minprice}&maxPrice={self.maxprice}&minBedrooms={self.bedrooms}&maxBedrooms={self.maxrooms}&displayPropertyType={self.type}&maxDaysSinceAdded=&sortByPriceDescending=&_includeLetAgreed=on&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&letType=&letFurnishType=&houseFlatShare='

            urls.append(t_url)

        for i in range(len(urls)):
            req_url = requests.get(urls[i])
            print("USing: ", urls[i])
            soup = BeautifulSoup(req_url.text, 'html.parser')
            results = soup.findAll('script')

            json_r = ''

            for r in results:
                l_r = list(utils.find_json_objects(r.text))
                print(l_r)
                for res in l_r:
                    if len(res) > 0:
                        json_r = res['properties']

            try:

                url = 'https://www.rightmove.co.uk/properties/'
                for props in json_r:
                    li = []
                    li.append(props['displayAddress'])
                    li.append(props['customer']['branchDisplayName'])
                    li.append(props['bedrooms'])
                    price_l = props['price']['displayPrices'][0]['displayPrice']
                    price_l.replace(',', '')
                    li.append(price_l)
                    li.append(url + str(props['id']))
                    li.append(props['propertyImages']['images'][0]['srcUrl'])
                    li.append("rmove")

                    json_data.append(li)
            except IndexError:
                pass
        return json_data

    def requestSold(self):

        utils = Utility()
        pcode = self.pcode
        res = []

        for i in range(1, 20, 1):
            pconv = str(i)
            apiurl = f"https://www.rightmove.co.uk/house-prices/{pcode}.html?page={pconv}"
            print("soldurl: ", apiurl)
            req_url = requests.get(apiurl)

            soup = BeautifulSoup(req_url.text, 'html.parser')
            results = soup.findAll('script')

            li = []
            for r in results:
                res_text = r.text
                found = list(utils.find_json_objects(res_text))
                li.append(found)
            itm = li[3][0]['results']['properties']

            if len(itm) != 0:
                for prop in itm:
                    p_li = []
                    p_li.append(prop['address'])
                    pric_li = []
                    for transaction in prop['transactions']:
                        pric_li.append([transaction['displayPrice'], transaction['dateSold']])
                    p_li.append(pric_li)
                    p_li.append(prop['images']['imageUrl'])
                    p_li.append(prop['detailUrl'])
                    res.append(p_li)
                    print("\n")
        return res

class OnTheMarket:

    def __init__(self, query, channel, radius, bedrooms, minprice, maxprice, resnum, maxrooms, type):
        self.pcode = query
        self.channel = channel
        self.radius = radius
        self.bedrooms = bedrooms
        self.minprice = minprice
        self.maxprice = maxprice
        self.resnum = resnum
        self.maxrooms = maxrooms
        self.type = type

    def request(self):

        utils = Utility()
        proxclass = Proxies()

        proxy = proxclass.getProxy()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        proxy_options = {
            'proxy': {
                'https': f'https://jhexogaj:3lf4cs4uk5v1@{proxy}',
            }
        }

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=options, seleniumwire_options=proxy_options)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )


        if self.type == 'flats':
            self.type = 'flats-apartments'
        if self.type == 'houses':
            self.type = 'detached'

        self.pcode = self.pcode.replace(' ', '-').lower()

        print("type: ", self.type)
        if self.radius != 0:
            url2 = f'https://www.onthemarket.com/{self.channel}/{self.bedrooms}-bed-property/{self.pcode}/?max-bedrooms={self.maxrooms}&max-price={self.maxprice}&min-price={self.minprice}&radius={self.radius}&view=grid'
        elif self.radius == 0:
            url2 = f'https://www.onthemarket.com/{self.channel}/{self.bedrooms}-bed-property/{self.pcode}/?max-bedrooms={self.maxrooms}&max-price={self.maxprice}&min-price={self.minprice}&view=grid'

        print(url2)
        driver.get(url2)

        pagesource = driver.page_source
        otm_li = []

        li = list(utils.find_json_objects(pagesource))
        for l in li:
            try:
                if l['header-data']:
                    data = l
                    dump = json.dumps(data, indent=4)
                    load = json.loads(dump)
                    baseurl = 'https://www.onthemarket.com'
                    otm_li = []
                    try:
                        for prop in load['properties']:

                            li = []
                            li.append(prop['display_address'])
                            li.append(prop['agent']['name'])
                            li.append(prop['bedrooms-text'])
                            price = prop['price'].split(" ")
                            pricemonth = price[0]
                            li.append(pricemonth)
                            li.append(baseurl + prop['property-link'])
                            try:
                                li.append(prop['images'][0]['default'])
                            except IndexError:
                                li.append(' ')
                            li.append("otm")

                            otm_li.append(li)
                            print(otm_li)
                    except KeyError:
                        for prop in data['properties']:
                            li = []
                            li.append(prop['display_address'])
                            li.append(prop['agent']['name'])
                            li.append(prop['bedrooms-text'])
                            li.append(prop['price'])
                            print("price: ", prop['price'])
                            # li.append(baseurl + prop['property-link'])
                            li.append(prop['images'][0]['default'])
                            li.append("otm")

                            otm_li.append(li)


            except KeyError:
                pass

        return otm_li


class CrystalRoof:

    def __init__(self, pcode):
        self.pcode = pcode

    def stats(self):

        split = self.pcode.split(" ")
        p1 = split[0]
        p2 = split[1]
        pc = p1+p2

        search_url = f"https://crystalroof.co.uk/report/postcode/{pc}/overview"
        response = urllib.request.urlopen(search_url)
        data = response.read()  # a `bytes` object
        soup = BeautifulSoup(data, 'html.parser')
        results = soup.findAll('script', {"id": "__NEXT_DATA__"})

        r = results[0].text

        parsed = json.loads(r)
        data = parsed['props']['initialReduxState']['report']['sectionResponses']['overview']['data']

        li = []
        li.append(data['loac']['supergroupname'])
        li.append(data['loac']['supergroupdescription'])
        li.append(data['loac']['groupname'])
        li.append(data['loac']['groupdescription'])
        li.append(data['income_lsoa']['mean'])
        li.append(data['income_lsoa']['median'])
        li.append(data['indices_of_deprivation_lsoa']['imdb_score'])
        li.append(data['crime_lsoa']['rate'])
        li.append(data['crime_lsoa']['rank'])
        li.append(data['transport']['metro']['name'])
        li.append(data['transport']['metro']['lines'])
        li.append(data['transport']['rail']['name'])
        li.append(data['transport']['rail']['lines'])
        li.append(data['amenities']['supermarkets']['businessname'])
        li.append(data['amenities']['groceries']['businessname'])
        li.append(data['schools']['name'])
        li.append(data['noise']['road']['noiseclass'])
        li.append(data['noise']['rail']['noiseclass'])
        li.append(data['noise']['aircraft']['noiseclass'])
        li.append(data['ethnicgroup']['white_british'])
        li.append(data['ethnicgroup']['white_irish'])
        li.append(data['ethnicgroup']['gypsy'])
        li.append(data['ethnicgroup']['other_white'])
        li.append(data['ethnicgroup']['mixed'])
        li.append(data['ethnicgroup']['indian'])
        li.append(data['ethnicgroup']['pakistani'])
        li.append(data['ethnicgroup']['bangladeshi'])
        li.append(data['ethnicgroup']['chinese'])
        li.append(data['ethnicgroup']['other_asian'])
        li.append(data['ethnicgroup']['black'])
        li.append(data['ethnicgroup']['arab'])
        li.append(data['ethnicgroup']['other'])
        li.append(data['religion']['christian'])
        li.append(data['religion']['buddhist'])
        li.append(data['religion']['hindu'])
        li.append(data['religion']['jewish'])
        li.append(data['religion']['muslim'])
        li.append(data['religion']['sikh'])
        li.append(data['religion']['other'])
        li.append(data['religion']['no_religion'])
        li.append(data['household']['one_person'])
        li.append(data['household']['couple_with_children'])
        li.append(data['household']['couple_without_children'])
        li.append(data['household']['same_sex_couple'])
        li.append(data['household']['lone_parent_with_children'])
        li.append(data['household']['lone_parent_without_children'])
        li.append(data['household']['multi_person_student'])
        li.append(data['household']['multi_person_other'])
        li.append(data['householdlifestage']['ageunder35'])
        li.append(data['householdlifestage']['age35to54'])
        li.append(data['householdlifestage']['age55to64'])
        li.append(data['householdlifestage']['age65above'])

        return li

class LandRegistry:

    def __init__(self, pcode):
        self.pcode = pcode
    def req(self):

        print("makeing a request to land registry")

        pcode = self.pcode.split(" ")
        pcode1 = pcode[0]
        pcode2 = '%20' + pcode[1]
        p_fin = pcode1 + pcode2
        num = 10
        li = []
        for i in range(num):
            base_url = f'https://landregistry.data.gov.uk/data/ppi/transaction-record.json?propertyAddress.postcode={p_fin}&_page={i}'
            print("BASE URL", base_url)
            x = requests.get(base_url).text
            loaded = json.loads(x)
            items = loaded['result']['items']
            if len(items) > 0:
                li.append(items)

        regs = []
        for itm in li:
            for list in itm:
                trans = []
                try:
                    trans.append((list['propertyAddress']['paon'], " " + list['propertyAddress']['street'],
                                  " " + list['propertyAddress']['town'], " " + list['propertyAddress']['county'],
                                  " " + list['propertyAddress']['district'], " " + list['propertyAddress']['locality'], " "+list['propertyAddress']['postcode']))
                    trans.append("£" + str(list['pricePaid']))
                    trans.append(list['transactionDate'])
                    regs.append(trans)
                except TypeError:
                    pass
                except KeyError:
                    pass

        return regs

class Planning:

    def __init__(self, pcode):
        self.pcode = pcode

    def request(self):
        API_KEY = 'KVB3BXNFRZ'
        P_CODE = self.pcode

        print("Planning pcode: ", self.pcode)

        requestobj = f'https://api.propertydata.co.uk/planning?key={API_KEY}&postcode={P_CODE}&decision_rating=positive&category=EXTENSION,LOFT%20CONVERSION&max_age_update=120&results=20'
        obj = requests.get(requestobj)

        load = json.loads(obj.text)
        data = load['data']['planning_applications']

        applications = []

        for app in data:
            li = []
            li.append(('url: ', app['url']))
            li.append(('address: ', app['address']))
            li.append(('type: ', app['type']))
            li.append(('status: ', app['status']))
            li.append(('proposal: ', app['proposal']))
            li.append(('type: ', app['type']))
            li.append(('status: ', app['status']))
            li.append(('decision: ', app['decision']['text']))
            li.append(('date_received: ', app['dates']['received_at']))
            li.append(('date_validated: ', app['dates']['validated_at']))
            li.append(('date_decided: ', app['dates']['decided_at']))
            li.append(('date_published: ', app['dates']['published_at']))
            li.append(('latitude: ', app['lat']))
            li.append(('longitude: ', app['lng']))
            li.append(('distance: ', app['distance']))
            applications.append(li)

        return applications

class Gumtree:

    def __init__(self, channel, pcode, radius, beds, minprice, maxprice, type):
        self.pcode = pcode
        self.channel = channel
        self.beds = beds
        self.minprice = minprice
        self.maxprice = maxprice
        self.radius = radius
        self.type = type

    def request(self):

        print("GUMTREE self.type: ", self.type)
        try:
            self.pcode = self.pcode.replace(" ", "")
        except:
            pass

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        proxy_options = {
            'proxy': {
                'https': 'https://woaokexr:6tq2q8b4e15q@185.199.229.156:7492',
            }
        }

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=options, seleniumwire_options=proxy_options)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        if self.radius < 1:
            self.radius = math.ceil(self.radius)

        if self.channel == 'for-sale':
            # url = f"https://www.gumtree.com/search?search_category=property-for-sale&search_location={self.pcode}&property_number_beds={self.beds}-bedroom&max_price={self.minprice}&min_price={self.maxprice}"
            url = f'https://www.gumtree.com/search?search_category=property-for-sale&search_location={self.pcode}&q=&distance={self.radius}&min_price={self.minprice}&max_price={self.maxprice}&min_property_number_beds={self.beds}&max_property_number_beds={self.beds}'
        elif self.channel == "to-rent":
            url = f"https://www.gumtree.com/search?search_category=property-to-rent&search_location={self.pcode}q=&distance={self.radius}&property_number_beds={self.beds}-bedroom&max_price={self.minprice}&min_price={self.maxprice}"
        print("gumtree URL: ", url)
        driver.get(url)
        time.sleep(2)

        pagesource = driver.page_source
        soup = BeautifulSoup(pagesource, 'html.parser')
        articles = soup.findAll('article', {"class", "listing-maxi"})
        props = []

        for article in articles:
                li = []
                # print(article)

                addr = article.find('span', {'class': 'truncate-line'})
                string = addr.text
                try:
                    sp = string.split('|')[1]
                    li.append(sp)
                except IndexError:
                    li.append(string)

                # Branch value
                li.append("Agency")

                # Beds
                li.append(self.beds)

                # Price
                price_soup = article.find('strong', {'class', 'h3-responsive'})
                price = price_soup.text
                orig_price = price
                price = price.replace('£', '')

                try:
                    price = price.replace(',', '')
                except:
                    pass

                try:
                    k_price = price.replace('pw', '')
                except:
                    pass

                try:
                    price = price.replace('pm', '')
                except:
                    pass



                print("Gumtree price: ", price)
                li.append(price)

                # Link
                s_link = article.find('a', {'class': 'listing-link'})
                r_link = s_link.get('href')
                li.append('https://www.gumtree.com'+r_link)

                # Image
                img = article.findNext('img')
                li.append(img.get('data-src'))
                li.append("gumtree")
                li.append(orig_price)

                props.append(li)

        return props
