import json
import multiprocessing

import requests
import re
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request
import os
from Naked.toolshed.shell import execute_js, muterun_js
import random
import threading
from time import sleep

class Search:

    def __init__(self, query, channel, beds, minprice, maxprice):
        self.searchquery = query
        self.channel = channel
        self.beds = beds
        self.price_min = minprice
        self.price_max = maxprice

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

        with open('proxies.txt', 'w') as p:
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
        print("get proxy method")

        li = [ '185.199.229.156:7492',
                '185.199.228.220:7300',
               '185.199.231.45:8382',
                '188.74.210.207:6286',
                '188.74.183.10:8279',
                '188.74.210.21:6100',
                '45.155.68.129:8133',
                '154.95.36.199:6893',
                '45.94.47.66:8110',
                '144.168.217.88:8780'
        ]

        ind_rand = random.randint(0, 9)
        prox = li[ind_rand]
        return prox

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

        print("Zoopla requests: ", searchurl)
        baseurl = 'https://www.zoopla.co.uk/'

        print('search url: ', searchurl)

        # file = open('/home/alasdairkite/flasksearch/static/urls.txt', 'w')
        file = open('/static/urls.txt', 'w')
        prox = proxy.getProxy()
        print("Writing proxy to file: ", prox)
        file.write(searchurl)
        file.write("\n")
        file.write(prox)
        file.close()

        response = muterun_js('zoopla.js')
        if response.exitcode == 0:
            print(response.stdout)
        else:
            execute_js('zoopla.js')

        zoop_l = []

        with open('zoopla.json', 'r') as r:
            data = json.loads(r.read())
            print(json.dumps(data, indent=4))
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

    def __init__(self, query, channel, radius, bedrooms, minprice, maxprice, page):
        self.pcode = query
        self.channel = channel
        self.radius = radius
        self.bedrooms = bedrooms
        self.minprice = minprice
        self.maxprice = maxprice
        self.page = page

    def requestScrape(self):

        utils = Utility()


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
        print("CODE: ", code)


        properties = []
        print(type(self.page))
        num = int(self.page)
        for ind in range(2):
            print("Right move ")

            if len(self.pcode) > 4 and self.channel == 'SALE':
                t_url = f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE%5E{code}&index={ind}&maxBedrooms={self.bedrooms}&minBedrooms={self.bedrooms}&maxPrice={self.maxprice}&minPrice={self.minprice}&radius={self.radius}&propertyTypes=&mustHave=&dontShow=&furnishTypes=&keywords='
            if len(self.pcode) <= 4 and self.channel == 'SALE':
                t_url = f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=OUTCODE%5E{code}&index={ind}&insId=1&radius={self.radius}&minPrice={self.minprice}&maxPrice={self.maxprice}&areaSizeUnit=sqft&googleAnalyticsChannel=buying&minBedrooms={self.bedrooms}&maxBedrooms={self.bedrooms}'
            if len(self.pcode) <= 4 and self.channel == 'RENT':
                t_url = f'https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=OUTCODE%5E{code}&index={ind}&insId=1&radius={self.radius}&minPrice={self.minprice}&maxPrice={self.maxprice}&minBedrooms={self.bedrooms}&maxBedrooms={self.bedrooms}'
            if len(self.pcode) > 4 and self.channel == 'RENT':
                t_url = f'https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=OUTCODE%5E{code}&index={ind}&insId=1&radius={self.radius}&minPrice={self.minprice}&maxPrice={self.maxprice}&areaSizeUnit=sqft&googleAnalyticsChannel=renting&minBedrooms={self.bedrooms}&maxBedrooms={self.bedrooms}'

            req_url = requests.get(t_url)
            print("t_url: ", t_url)
            print(req_url)
            soup = BeautifulSoup(req_url.text, 'html.parser')
            results = soup.findAll('script')

            json_r = ''

            for r in results:
                l_r = list(utils.find_json_objects(r.text))
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
                    li.append(props['price']['displayPrices'][0]['displayPrice'])
                    li.append(url + str(props['id']))
                    li.append(props['propertyImages']['images'][0]['srcUrl'])
                    li.append("rmove")
                    properties.append(li)

            except IndexError:
                pass
        return properties

    def requestSold(self):

        utils = Utility()
        pcode = self.pcode
        res = []

        for i in range(1, 20, 1):
            pconv = str(i)
            apiurl = f"https://www.rightmove.co.uk/house-prices/{pcode}.html?page={pconv}"
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

    def __init__(self, query, channel, radius, bedrooms, minprice, maxprice, resnum):
        self.pcode = query
        self.channel = channel
        self.radius = radius
        self.bedrooms = bedrooms
        self.minprice = minprice
        self.maxprice = maxprice
        self.resnum = resnum

    def request(self):


        utils = Utility()
        proxy = Proxies()


        baseurl = 'https://www.onthemarket.com/'
        pcode = self.pcode.split(" ")
        p1 = pcode[0].lower()
        if len(pcode) > 1:
            p2 = pcode[1].lower()
            p_tot = p1+"-"+p2
        else:
            p_tot = p1

        otm_li = []
        self.pcode = p_tot

        print("Max price: ", self.maxprice)


        # https://www.onthemarket.com/for-sale/1-bed-property/cr0/?max-bedrooms=3&max-price=275000&min-price=80000&view=grid
        if self.channel == 'for-sale':
            url = f'https://www.onthemarket.com/{self.channel}/{self.bedrooms}-bed-property/{self.pcode}/?max-bedrooms={self.bedrooms}&max-price={self.maxprice}&min-price={self.minprice}&radius={self.radius}&view=grid'
        elif self.channel == 'lettings':
            url = f'https://www.onthemarket.com/to-rent/{self.bedrooms}-bed-property/{self.pcode}/?max-bedrooms={self.bedrooms}&max-price={self.maxprice}&min-price={self.minprice}&radius={self.radius}&view=grid'

        print("on the market channel: ", self.channel)
        print("on the market URL: ", url)

        for i in range(1):
            print('i in num: ', i)

            # file = open('/home/alasdairkite/flasksearch/static/urls.txt', 'w')
            file = open('./static/urls.txt', 'w')

            prox = proxy.getProxy()
            file.write(url+',')
            file.write("\n")
            file.write(prox)
            file.close()

        response = muterun_js('otm.js')
        if response.exitcode == 0:
            print(response.stdout)
        else:
            js_response = execute_js('otm.js')
        with open('static/file.json') as r:
            data = json.loads(r.read())
            try:
                for prop in data['top-properties']:
                    li = []
                    li.append(prop['display_address'])
                    li.append(prop['agent']['name'])
                    li.append(prop['bedrooms-text'])
                    li.append(prop['price'])
                    li.append(baseurl + prop['property-link'])
                    li.append(prop['images'][0]['default'])
                    li.append("otm")

                    otm_li.append(li)
            except KeyError:
                for prop in data['properties']:
                    li = []
                    li.append(prop['display_address'])
                    li.append(prop['agent']['name'])
                    li.append(prop['bedrooms-text'])
                    li.append(prop['price'])
                    li.append(baseurl + prop['property-link'])
                    li.append(prop['images'][0]['default'])
                    li.append("otm")

                    otm_li.append(li)

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
            if app['distance'] == 0:
                applications.append(li)

        return applications

class Gumtree:

    def __init__(self, channel, pcode, beds, minprice, maxprice, radius, type):
        self.pcode = pcode
        self.channel = channel
        self.beds = beds
        self.minprice = minprice
        self.maxprice = maxprice
        self.radius = radius
        self.type = type

    def request(self):

        print("GUMTREE self.type: ", self.type)
        print("Min price: ", self.minprice)
        print("maxprice: ", self.maxprice)
        print("radius: ", self.radius)
        if self.channel == 'for-sale':
            # url = f"https://www.gumtree.com/search?search_category=property-for-sale&search_location={self.pcode}&property_number_beds={self.beds}-bedroom&max_price={self.minprice}&min_price={self.maxprice}"
            url = f'https://www.gumtree.com/search?search_category=property-for-sale&search_location={self.pcode}&q=&distance={self.radius}&min_price={self.minprice}&max_price={self.maxprice}&min_property_number_beds={self.beds}&max_property_number_beds={self.beds}'
        elif self.channel == "to-rent":
            url = f"https://www.gumtree.com/search?search_category=property-to-rent&search_location={self.pcode}&property_number_beds={self.beds}-bedroom&max_price={self.minprice}&min_price={self.maxprice}"


        proxy = Proxies()
        file = open('static/urls.txt', 'w')
        # file = open('/home/alasdairkite/flasksearch/static/urls.txt', 'w')

        prox = proxy.getProxy()
        print("Writing proxy to file: ", prox)
        file.write(url + ",")
        file.write("\n")
        file.write(prox)
        file.close()

        response = muterun_js('gumtree.js')
        if response.exitcode == 0:
            print(response.stdout)
        else:
            execute_js('gumtree.js')

        with open('temp.txt', 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            articles = soup.find_all('article', {"class", "listing-maxi"})
            props = []

            for article in articles:
                li = []
                # print(article)

                addr = article.find('span', {'class': 'truncate-line'})
                string = addr.text
                sp = string.split('|')[1]
                li.append((string.split('|'))[1])

                # Branch value
                li.append("Agency")

                # Beds
                li.append(self.beds)

                # Price
                price_soup = article.find('strong', {'class', 'h3-responsive'})
                price = price_soup.text
                li.append(price)

                # Link
                s_link = article.find('a', {'class': 'listing-link'})
                r_link = s_link.get('href')
                li.append('https://www.gumtree.com'+r_link)

                # Image
                img = article.findNext('img')
                li.append(img.get('data-src'))
                li.append("gumtree")
                props.append(li)

        return props
