import xmltojson
import json
import requests
import utils
import re
import html_to_json
from bs4 import BeautifulSoup
import urllib.request
import cloudscraper

import certifi

from string import Template
from SPARQLWrapper import SPARQLWrapper, JSON

import ssl

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

    def __init__(self, query, channel, radius, bedrooms, minprice, maxprice):
        self.pcode = query
        self.channel = channel
        self.radius = radius
        self.bedrooms = bedrooms
        self.minprice = minprice
        self.maxprice = maxprice

    def requestScrape(self):

        utils = Utility()

        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}
        # Function to postcode
        print('https://www.rightmove.co.uk/property-for-sale/search.html?searchLocation=' + self.pcode)
        x = requests.get('https://www.rightmove.co.uk/property-for-sale/search.html?searchLocation=' + self.pcode, headers=headers)
        soup = BeautifulSoup(x.text, 'html.parser')
        results = soup.find('input', {'id': 'locationIdentifier'}).get('value')
        txt = results
        x = re.findall("[^^]*$", txt)
        code = x[0]
        print("CODE: ", code)


        properties = []

        for i in range(10):

            ind = i * 24

            if len(self.pcode) > 4 and self.channel == 'SALE':
                t_url = f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE%5E{code}&maxBedrooms={self.bedrooms}&minBedrooms={self.bedrooms}&maxPrice={self.maxprice}&minPrice={self.minprice}&radius={self.radius}&propertyTypes=&mustHave=&dontShow=&furnishTypes=&keywords='
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
                    li.append(props['summary'])
                    li.append(props['customer']['branchDisplayName'])
                    li.append(props['bedrooms'])
                    li.append(props['price']['displayPrices'][0]['displayPrice'])
                    li.append(url + str(props['id']))
                    li.append(props['propertyImages']['images'][0]['srcUrl'])
                    properties.append(li)

            except IndexError:
                break

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

    def __init__(self, query, channel, radius, bedrooms, minprice, maxprice):
        self.pcode = query
        self.channel = channel
        self.radius = radius
        self.bedrooms = bedrooms
        self.minprice = minprice
        self.maxprice = maxprice

    def request(self):

        print("On The Market Request")
        utils = Utility()

        print("pcode: ", self.pcode)
        print("channel: ", self.channel)
        print("radius: ", self.radius)
        print("bedrooms: ", self.bedrooms)
        print("min price: ", self.minprice)
        print("maxprice: ", self.maxprice)

        url = 'https://www.onthemarket.com/'
        pcode = self.pcode.split(" ")
        p1 = pcode[0].lower()
        if len(pcode) > 1:
            p2 = pcode[1].lower()
            p_tot = p1+"-"+p2
        else:
            p_tot = p1
        url_end = f'/?min-bedrooms={self.bedrooms}&max-bedrooms={self.bedrooms}&max-price={self.maxprice}&min-price={self.minprice}&radius={self.radius}&view=grid'
        search_url = url + self.channel + "/property/" + p_tot+url_end

        print(search_url)
        # search_url = base_url + p_tot + url_end

        scraper = cloudscraper.create_scraper()
        req = scraper.get(search_url)

        soup = BeautifulSoup(req.text, 'html.parser')
        results = soup.findAll('script', {'type': 'text/javascript'})
        for r in results:
            res_text = r.text
            try:
                found = list(utils.find_json_objects(res_text))
                try:
                    for f in found:
                        if len(f) > 20:
                            value = f
                except IndexError:
                    pass
            except TypeError:
                pass

        otm_li = []
        str = ""
        url="https://www.onthemarket.com"
        for prop in value['properties']:
            li = []
            li.append(prop['display_address'])
            for s in prop['features']:
                str+=s+" "
            li.append(prop['property-title']+str)
            li.append(prop['agent']['name'])
            li.append(prop['bedrooms-text'])
            li.append(prop['price'])
            li.append(url+prop['property-link'])
            li.append(prop['images'][0]['default'])
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

        print(json.dumps(data, indent=4))

        li = []
        li.append(data['loac'])
        li.append(data['income_lsoa'])
        li.append(data['indices_of_deprivation_lsoa'])
        li.append(data['crime_lsoa'])
        li.append(data['transport']['metro'])
        li.append(data['amenities']['supermarkets'])
        li.append(data['amenities']['groceries'])
        li.append(data['schools']['name'])
        li.append(data['noise'])
        li.append(data['ethnicgroup'])
        li.append(data['religion'])
        li.append(data['household'])
        li.append(data['houesholdlifestage'])

        return li

    # print(data['income_lsoa']['mean'])
    # print(data['income_lsoa']['median'])
    # print("crime rate: ", data['crime_lsoa']['rate'])
    # print("crime rank: ", data['crime_lsoa']['rank'])
    # print("\n")
    #
    # # Transport
    # print("transport metro: ", data['transport']['metro']['name'])
    # print("transport rail name: ", data['transport']['rail']['name'])
    # print("transport rail lines: ", data['transport']['rail']['lines'][0])
    #
    # # Amenities
    # print("Supermarkets names: ", data['amenities']['supermarkets']['businessname'])
    #
    # # Schools
    # print("School name: ", data['schools']['name'])
    # print("School ofsted ratings: ", data['schools']['ofstedrating'])
    #
    # # noise
    # print("Road noise class: ", data['noise']['road']['noiseclass'])
    #
    # # ethnicity
    # print("Ethnicity total: ", data['ethnicgroup']['total'])
    # print("Religion total: ", data['religion']['total'])
    # print("Household total: ", data['household']['total'])

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

    #Both methods below are for use with SPARQL
    # def getData(self):
    #
    #
    #     print("GET DATA")
    #
    #
    #
    #     # query built from https://landregistry.data.gov.uk/app/qonsole#
    #
    #     sparql = SPARQLWrapper("http://landregistry.data.gov.uk/landregistry/query", custom_cert_filename=certifi.where())
    #     sparql.setReturnFormat(JSON)
    #
    #     print("AFTER URL")
    #
    #     string = Template("""
    #         prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #         prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    #         prefix owl: <http://www.w3.org/2002/07/owl#>
    #         prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    #         prefix sr: <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>
    #         prefix ukhpi: <http://landregistry.data.gov.uk/def/ukhpi/>
    #         prefix lrppi: <http://landregistry.data.gov.uk/def/ppi/>
    #         prefix skos: <http://www.w3.org/2004/02/skos/core#>
    #         prefix lrcommon: <http://landregistry.data.gov.uk/def/common/>
    #
    #         SELECT ?paon ?saon ?street ?town ?county ?postcode ?amount ?date ?category
    #         WHERE
    #         {
    #           VALUES ?postcode {"$p1 $p2"^^xsd:string}
    #
    #           ?addr lrcommon:postcode ?postcode.
    #
    #           ?transx lrppi:propertyAddress ?addr ;
    #                   lrppi:pricePaid ?amount ;
    #                   lrppi:transactionDate ?date ;
    #                   lrppi:transactionCategory/skos:prefLabel ?category.
    #
    #           OPTIONAL {?addr lrcommon:county ?county}
    #           OPTIONAL {?addr lrcommon:paon ?paon}
    #           OPTIONAL {?addr lrcommon:saon ?saon}
    #           OPTIONAL {?addr lrcommon:street ?street}
    #           OPTIONAL {?addr lrcommon:town ?town}
    #         }
    #         ORDER BY ?amount
    #             """)
    #
    #     sparql.setQuery(string.substitute(p1='CT6', p2='5HZ'))
    #     li = []
    #     try:
    #         ret = sparql.queryAndConvert()
    #
    #         for r in ret["results"]["bindings"]:
    #             li.append(r)
    #             print(r)
    #         return li
    #     except Exception as e:
    #         print("ERROR")
    #         print(e)

    # def data2(self):
    #
    #
    #     # query built from https://landregistry.data.gov.uk/app/qonsole#
    #
    #     sparql = SPARQLWrapper("https://landregistry.data.gov.uk/landregistry/query")
    #     sparql.setReturnFormat(JSON)
    #
    #     string = Template("""
    #         prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #         prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    #         prefix owl: <http://www.w3.org/2002/07/owl#>
    #         prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    #         prefix sr: <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>
    #         prefix ukhpi: <http://landregistry.data.gov.uk/def/ukhpi/>
    #         prefix lrppi: <http://landregistry.data.gov.uk/def/ppi/>
    #         prefix skos: <http://www.w3.org/2004/02/skos/core#>
    #         prefix lrcommon: <http://landregistry.data.gov.uk/def/common/>
    #
    #         SELECT ?paon ?saon ?street ?town ?county ?postcode ?amount ?date ?category
    #         WHERE
    #         {
    #           VALUES ?postcode {"$p1 $p2"^^xsd:string}
    #
    #           ?addr lrcommon:postcode ?postcode.
    #
    #           ?transx lrppi:propertyAddress ?addr ;
    #                   lrppi:pricePaid ?amount ;
    #                   lrppi:transactionDate ?date ;
    #                   lrppi:transactionCategory/skos:prefLabel ?category.
    #
    #           OPTIONAL {?addr lrcommon:county ?county}
    #           OPTIONAL {?addr lrcommon:paon ?paon}
    #           OPTIONAL {?addr lrcommon:saon ?saon}
    #           OPTIONAL {?addr lrcommon:street ?street}
    #           OPTIONAL {?addr lrcommon:town ?town}
    #         }
    #         ORDER BY ?amount
    #             """)
    #
    #     sparql.setQuery(string.substitute(p1='CT6', p2='5HZ'))
    #
    #     try:
    #         ret = sparql.queryAndConvert()
    #
    #         for r in ret["results"]["bindings"]:
    #             print(r)
    #     except Exception as e:
    #         print(e)

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