import json
import requests
import re
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request
import cloudscraper
import os
from proxy_requests import ProxyRequests
from playwright.sync_api import sync_playwright

class Proxies:

    def createProxyList(self):


        url = 'https://free-proxy-list.net/'

        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find("table", {"class": "table table-striped table-bordered"})
        tbody = table.find("tbody")

        proxies = []

        for tr in tbody:
            cells = tr.findAll("td")
            proxies.append(cells[0].text)

        if os.path.exists('proxies.txt'):
            print('proxy path exists')
        else:
            with open('proxies.txt', 'w') as f:
                for proxy in proxies:
                    f.write(proxy)
                    f.write('\n')

    def getProxyList(self):

        p_list = []
        with open('proxies.txt', 'r') as p:
            for proxy in p:
                p_list.append(proxy)

        return p_list

    def increaseProxVar(self, ind):
        print("INCREASE PROX VAR")
        proxlength = len(self.getProxyList())
        if ind >= proxlength:
            ind = 0
        else:
            ind+=1
        return ind


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

    def __init__(self, query, channel):
        self.searchquery = query
        self.channel = channel

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

    def returnResults(self):
        print("return results")
        with open('static/zoopla/zooplafile.json', 'r') as f:
            props = []
            data = json.loads(f.read())
            # print(data['props']['pageProps']['regularListingsFormatted'])
            listings = data['props']['pageProps']['regularListingsFormatted']
            for listing in listings:
                li = []
                li.append(listing['address'])
                li.append(listing['branch']['name'])
                li.append(listing['features'][0]['content'])
                li.append(listing['price'])
                li.append('http://www.zoopla.co.uk'+listing['listingUris']['detail'])
                li.append(listing['image']['src'])
                props.append(li)
        return props
    def getResults(self):

        util = Utility()


        print("searching: ", f'https://www.zoopla.co.uk/{self.channel}/property/{self.searchquery}/?q={self.searchquery}&results_sort=newest_listings&search_source={self.channel}')
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(
                f'https://www.zoopla.co.uk/{self.channel}/property/{self.searchquery}/?q={self.searchquery}&results_sort=newest_listings&search_source={self.channel}')
            all_quotes = page.query_selector('body')
            found = list(util.find_json_objects(all_quotes.inner_html()))
            print(found)
            l_one = found[1]
            print("found: ", found)
            with open('static/zoopla/search.json', 'w') as search:
                search.write(json.dumps(found[0], indent=4))
                print("write search")
            with open('static/zoopla/zooplafile.json', 'w') as all_quotes:
                all_quotes.write(json.dumps(found[1], indent=4))
                print("write zoopla results")
            return


    def requests(self):

        util = Utility()
        print("Zoopla requests")

        #if search.json exists check to see what the last search was and whether it contains values of the new search
        if os.path.isfile('static/zoopla/search.json') and os.path.isfile('static/zoopla/zooplafile.json'):
            with open('static/zoopla/search.json') as f, open('static/zoopla/zooplafile.json') as res:
                data = json.loads(f.read())
                data2 = json.loads(res.read())
                print("file found: ")
                print(data2['props']['pageProps']['initialState']['dfpAdTargeting']['search_location'])
                if data['search_location'] == self.searchquery and data2['props']['pageProps']['initialState']['dfpAdTargeting']['search_location']:
                    print("Match: ", data['search_location'], " ", self.searchquery)
                    a = self.returnResults()
                    return a
                else:
                    self.getResults()
                    a = self.returnResults()
                    return a
        else:
            self.getResults()
            a = self.returnResults()
            return a


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


        baseurl = 'https://www.onthemarket.com'
        pcode = self.pcode.split(" ")
        p1 = pcode[0].lower()
        if len(pcode) > 1:
            p2 = pcode[1].lower()
            p_tot = p1+"-"+p2
        else:
            p_tot = p1

        otm_li = []

        if int(self.radius) < 1:
            self.radius = '0.5'
        for i in range(2):
            print('i in num: ', i)
            url_end = f'/?min-bedrooms={self.bedrooms}&max-bedrooms={self.bedrooms}&max-price={self.maxprice}&min-price={self.minprice}&page={i}&radius={self.radius}&view=grid'
            search_url = baseurl + self.channel + "/property/" + p_tot+url_end
            print(search_url)

            r = ProxyRequests(search_url)
            r = requests.get(search_url)


            # scraper = cloudscraper.create_scraper()
            # req = scraper.get(search_url, headers=header, proxies=proxlist)

            soup = BeautifulSoup(r.text, 'html.parser')
            results = soup.findAll('script', {'type': 'text/javascript'})
            for r in results:
                res_text = r.text
                try:
                    found = list(utils.find_json_objects(res_text))
                    try:
                        for value in found:
                            if len(value) > 20:

                                for prop in value['properties']:
                                    li = []
                                    li.append(prop['display_address'])
                                    li.append(prop['agent']['name'])
                                    li.append(prop['bedrooms-text'])
                                    li.append(prop['price'])
                                    li.append(baseurl + prop['property-link'])
                                    print(baseurl+prop['property-link'])
                                    li.append(prop['images'][0]['default'])
                                    otm_li.append(li)

                    except IndexError:
                        pass
                except TypeError:
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

    def __init__(self, pcode, radius, beds, minprice, maxprice, type):
        self.pcode = pcode
        self.beds = beds
        self.minprice = minprice
        self.maxprice = maxprice
        self.radius = radius
        self.type = type

    def request(self):



        # gumtree: 1, 3, 5, 10, 15, 30, 50, 75, 100, 1000
        print("GUMTREE self.type: ", self.type)

        if self.type == "sales":
            # url = f'https://www.gumtree.com/search?search_category=flats-houses&search_location={self.pcode}&property_number_beds={self.beds}&q=&distance={self.radius}&min_price={self.minprice}&max_price={self.maxprice}'
            url = f'https://www.gumtree.com/search?featured_filter=false&q=&search_category=property-for-sale&urgent_filter=false&sort=date&search_scope=false&photos_filter=false&search_location={self.pcode}&tl=&distance={self.radius}&property_number_beds={self.beds}&min_price={self.minprice}&max_price={self.maxprice}'
        if self.type == "lettings":
            url = f'https://www.gumtree.com/search?search_category=flats-houses&search_location={self.pcode}&property_number_beds={self.beds}&q=&distance={self.radius}&min_price={self.minprice}&max_price={self.maxprice}'

        print(url)
        response = requests.get(url)
        print(response.status_code)
        print(response.text)


        listingcont = SoupStrainer('article', {'class': 'listing-maxi'})
        count = BeautifulSoup(response.text, "html.parser", parse_only=listingcont)
        props = []

        for listing in count:
            li = []

            link_strain = SoupStrainer('a')
            a_soup = BeautifulSoup(str(listing), 'html.parser', parse_only=link_strain)
            li.append(a_soup.find('a', href=True)['href'])

            title = SoupStrainer('h2', {'class': 'listing-title'})
            title_s = BeautifulSoup(str(listing), 'html.parser', parse_only=title)
            li.append(title_s.text)

            price_st = SoupStrainer('strong', {'class': 'h3-responsive'})
            price_soup = BeautifulSoup(str(listing), 'html.parser', parse_only=price_st)
            li.append(price_soup.text)

            desc_st = SoupStrainer('p', {
                'class': 'listing-description txt-sub txt-tertiary truncate-paragraph hide-fully-to-m'})
            desc_soup = BeautifulSoup(str(listing), 'html.parser', parse_only=desc_st)
            li.append(desc_soup.text)

            images = SoupStrainer('img')
            img_soup = BeautifulSoup(str(listing), 'html.parser', parse_only=images)
            try:
                li.append(img_soup.find('img', src=True)['data-src'])
            except KeyError:
                li.append(img_soup.find('img', src=True)['src'])

            props.append(li)

        if (len(props)) == 0:
            return url
        return props
