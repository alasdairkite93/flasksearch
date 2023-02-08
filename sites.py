import json
import requests
import re
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request
import cloudscraper


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

    def requests(self):

        print("Zoopla Request")

        b_url = 'https://www.zoopla.co.uk/'

        radius = '?q=ct65hz&radius=0.5&search_source=refine&view_type=list'

        url = b_url+self.channel+"/property/"+self.searchquery+radius

        head = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}

        req_resp = requests.get(url, headers=head)
        print(req_resp.text)
        soup = BeautifulSoup(req_resp.text, 'html.parser')
        results = soup.findAll('script', {'type':'application/json'})

        res_json = ''

        for r in results:
            res_text = r.text
            found = list(self.find_json_objects(res_text))
            list_js = found[0]
            print(found[0])
            res_json=json.dumps(list_js)
            print(res_json)

        test = json.loads(res_json)

        # function to get list of results
        listings = test['props']['pageProps']['initialProps']['searchResults']['listings']['extended']
        set = []
        for i in listings:
            li = []
            li.append(i['address'])
            li.append(i['price'])
            li.append(i['image']['src'])
            li.append(i['branch']['name'])
            li.append(i['listingId'])
            set.append(li)

        return set

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

        global t_url
        utils = Utility()


        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}
        # Function to postcode

        rent = 'property-to-rent'
        sales = 'property-for-sale'

        if self.channel == "SALE":
            search_url = f'https://www.rightmove.co.uk/{sales}/search.html?searchLocation='

        else:
            search_url = f'https://www.rightmove.co.uk/{rent}/search.html?searchLocation='

        x = requests.get(search_url + self.pcode, headers=headers)
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
        print(properties)
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

    def request(self, otm_li=None):

        global value
        utils = Utility()

        num = '0'

        baseurl = 'https://www.onthemarket.com/'
        pcode = self.pcode.split(" ")
        p1 = pcode[0].lower()
        if len(pcode) > 1:
            p2 = pcode[1].lower()
            p_tot = p1+"-"+p2
        else:
            p_tot = p1

        otm_li = []

        if self.radius < 1
            self.radius = self.radius +0.5
        num = int(self.resnum)
        for i in range(2):
            print('i in num: ', i)
            url_end = f'/?min-bedrooms={self.bedrooms}&max-bedrooms={self.bedrooms}&max-price={self.maxprice}&min-price={self.minprice}&page={i}&radius={r_d}&view=grid'
            search_url = baseurl + self.channel + "/property/" + p_tot+url_end
            print(search_url)
            scraper = cloudscraper.create_scraper()
            req = scraper.get(search_url)

            soup = BeautifulSoup(req.text, 'html.parser')
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

    def __init__(self, pcode, beds, minprice, maxprice, radius, type):
        self.pcode = pcode
        self.beds = beds
        self.minprice = minprice
        self.maxprice = maxprice
        self.radius = radius
        self.type = type

    def request(self):

        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

        # gumtree: 1, 3, 5, 10, 15, 30, 50, 75, 100, 1000
        if self.type == "sales":
            url = f'https://www.gumtree.com/search?search_category=property-for-sale&search_location={self.pcode}&property_number_beds={self.beds}&q=&distance={self.radius}&min_price={self.minprice}&max_price={self.maxprice}'
        if self.type == "lettings":
            url = f'https://www.gumtree.com/search?search_category=property-to-rent&search_location={self.pcode}&property_number_beds={self.beds}&q=&distance={self.radius}&min_price={self.minprice}&max_price={self.maxprice}'

        proxlist = {
            'http':'http://user-spox3wdwyy-sessionduration-1:jabawooky@gate.smartproxy.com:10000',
        }

        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }



        response = requests.get(url, headers=header, proxies=proxlist)

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

        return props
