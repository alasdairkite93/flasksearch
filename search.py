import json
import re
import sys
import werkzeug.exceptions
from flask import Flask, abort, session, request, render_template, jsonify, redirect, url_for
import sites
import threading
import os
import pytest
import requests
from geopy.geocoders import Nominatim

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_bad_request(e):
    return render_template('tpage.html')


@app.route('/planningdata', methods=["GET"])
def planning_data():
    planapps = sites.Planning(session['postcode'])
    plans = planapps.request()
    return jsonify(plans)


@app.route('/googleef90634c0cbd5779.html', methods=["GET"])
def returnpage():
    return render_template('googleef90634c0cbd5779.html')


@app.route('/landregistry')
def sold_prices():
    landregister = sites.LandRegistry(session['postcode'])
    registry = landregister.req()
    return jsonify(registry)


@app.route('/zooplasale', methods=["GET"])
def zoopla_sales():
    zoop = sites.Zoopla(session['postcode'], "for-sale", session['brooms'], session['minprice'], session['maxprice'])
    zooplaresults = zoop.requests()

    return zooplaresults


@app.route('/zooplalet', methods=["GET"])
def zoopla_lets():
    zoop = sites.Zoopla(session['postcode'], "to-rent")
    zooplaresults = zoop.requests()

    return jsonify(zooplaresults)


@app.route('/rightmovesale/', methods=["GET"])
def rmove_sales():
    rmove = sites.Rightmove(session['postcode'], "SALE", session['radius'], session['brooms'], session['minprice'],
                            session['maxprice'], session['resnum'], session['maxrooms'], session['propertytype'])
    rmove_results = rmove.requestScrape()

    return jsonify(rmove_results)


@app.route('/gumtreesales', methods=["GET"])
def gumtree_scrape():
    gum = sites.Gumtree('for-sale', session['postcode'], session['brooms'], session['minprice'], session['maxprice'],
                        session['radius'], session['type'])
    gumresults = gum.request()
    # session['proxindex'] = proxies.increaseProxVar(session['proxindex'])

    return jsonify(gumresults)


@app.route('/gumtreesales', methods=["GET"])
def gumtree_lets():
    print("gumtree lets")
    gum = sites.Gumtree('to-rent', session['postcode'], session['brooms'], session['minprice'], session['maxprice'],
                        session['radius'], session['type'])
    gumresults = gum.request()

    return jsonify(gumresults)


@app.route('/rmoverent', methods=["GET"])
def rmove_lets():
    rmove = sites.Rightmove(session['postcode'], "RENT", session['radius'], session['brooms'], session['minprice'],
                            session['maxprice'], session['resnum'], session['maxrooms'], session['propertytype'])
    rmove_results = rmove.requestScrape()
    # session['proxindex'] = proxies.increaseProxVar(session['proxindex'])

    return jsonify(rmove_results)


@app.route('/rmovesold', methods=["GET"])
def rmov_sold():
    rmove = sites.Rightmove(session['postcode'], None, None, None, None, None, None, None, None)
    rmov_res = rmove.requestSold()

    return jsonify(rmov_res)


@app.route('/otmsale', methods=["GET"])
def otm_sales():
    otmsale = sites.OnTheMarket(session['postcode'], "to-rent", session['radius'], session['brooms'],
                                session['minprice'], session['maxprice'], session['resnum'], session['maxrooms'],
                                session['propertytype'])
    otm_results = otmsale.request()

    return jsonify(otm_results)


@app.route('/otmrent', methods=["GET"])
def otm_rent():
    print("OTM Rent pages: ", " radius: ", session['radius'], " minprice ", session['minprice'])
    otmrent = sites.OnTheMarket(session['postcode'], "to-rent", session['radius'], session['brooms'],
                                session['minprice'], session['maxprice'], session['resnum'], session['maxrooms'],
                                session['propertytype'])
    otm_results = otmrent.request()

    return jsonify(otm_results)


@app.route('/crystalroof', methods=["GET"])
def crystal_stats():
    crysstats = sites.CrystalRoof(session['postcode'])
    resp = crysstats.stats()
    return jsonify(resp)


# Updates
@app.route('/typeupdate', methods=["GET", "POST"])
def update_type():
    if request.method == "POST":
        type = request.form.get("propertytype")
        session['propertytype'] = type
        return render_template('base.html')
    return render_template('base.html')


@app.route('/pcodeupdate', methods=["GET", "POST"])
def update_pcode():
    print("Update PCODE ")
    if request.method == "POST":
        update = request.form.get("pcodeupdate")

        print("UPDATE CONTENTS: ", update)

        POSTCODE = '([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})'
        print("full postcode regex")
        match = re.search(POSTCODE, update)

        if match != None:
            print("MATCH: ", match.group())
            session['postcode'] = match.group().replace(' ', '')
            session['display'] = update
            return render_template('base.html')

        else:
            POSTCODE = '([A-Za-z][A-Ha-hJ-Yj-y][0-9][0-9]?)'
            print("partial postcode regex")
            match = re.search(POSTCODE, update)
            print("MATCH: ", match.group())
            session['postcode'] = match.group()
            session['display'] = match.group()
            return render_template('base.html')

    return render_template('base.html')


@app.route('/example', methods=["GET", "POST"])
def example():
    print("example method")
    if request.method == "POST":
        example_txt = request.form.get("example")
        print("example_txt: ", example_txt)
        return render_template('base.html')


@app.route('/pandr_update', methods=["GET", "POST"])
def update_pcode_radius():
    print("UPDATE RADIUS")
    if request.method == "POST":
        update = request.form.get("pcodeupdate")
        session['postcode'] = update.upper()
        return render_template('base.html')

    return render_template('base.html')


@app.route('/numres', methods=["GET", "POST"])
def update_results():
    print("update_results")
    if request.method == "POST":
        update = request.form.get("resultnum")
        session['resnum'] = update
        return render_template('base.html')

    return render_template('base.html')


@app.route('/broomupdate', methods=["POST"])
def update_rooms():
    if request.method == "POST":
        brooms = request.form.get("minrooms")
        session['brooms'] = brooms

        return render_template('base.html')


@app.route('/maxroomupdate', methods=["POST"])
def update_maxrooms():
    if request.method == "POST":
        maxroom = request.form.get("maxroom")
        session['maxrooms'] = maxroom

        return render_template('base.html')


@app.route('/radiusupdate', methods=["POST"])
def update_radius():
    if request.method == "POST":
        radius = request.form.get("radius")
        session['radius'] = radius
        return render_template('base.html')


@app.route("/googleef90634c0cbd5779.html")
def google_site_verf():
    return render_template("googleef90634c0cbd5779.html")


@app.route("/sitemap.xml")
def sitemap():
    return render_template("sitemap.xml")


@app.route('/priceupdate', methods=["POST"])
def update_min_price():
    if request.method == "POST":
        minprice = request.form.get("minprice")
        session['minprice'] = minprice

        return render_template('base.html')


@app.route('/updatesession', methods=["GET", "POST"])
def update_session():
    print("UPDATE FORM TO LETTINGS")

    if request.method == "POST":
        print("REQUEST METHOD POST")
        value = request.form.get("page")
        print("REQUEST VALUE: ", value)

        if value == 'sales':
            print("if values sales")
            session['type'] = 'lettings'
            print("UPDATE FORM TO LETTINGS")
            return render_template('base.html')
        elif value == 'lettings':
            print("if values lettings")
            session['type'] = 'sales'
            print("UPDATE FORM TO Lettings")
            return render_template('base.html')


@app.route('/maxpriceupdate', methods=["POST"])
def update_max_price():
    if request.method == "POST":
        maxprice = request.form.get("maxprice")
        session['maxprice'] = maxprice

        return render_template('base.html')


@app.route('/lettings', methods=["POST"])
def letsform():
    if request.method == "POST":
        search_query = request.form.get("pcode")
        session['postcode'] = search_query.upper()
        return render_template('lettings.html')
    return render_template('form.html')


@app.route('/returnall', methods=["GET"])
def returnAll():
    if session['type'] == 'sales':

        print("Return all")

        query = sites.Query(session['postcode'], "for-sale", session['radius'], session['brooms'],
                                    session['minprice'], session['maxprice'], session['resnum'], session['maxrooms'],
                                    session['propertytype'])
        res = query.scrape()
        li = list(res.queue)
        print('returnall: ', len(li))
        return jsonify(li)

        # otmsale = sites.OnTheMarket(session['postcode'], "for-sale", session['radius'], session['brooms'],
        #                             session['minprice'], session['maxprice'], session['resnum'], session['maxrooms'],
        #                             session['propertytype'])
        # otm_results = otmsale.request()
        # print("returned results of a")
        #
        # rmove = sites.Rightmove(session['postcode'], "SALE", session['radius'], session['brooms'], session['minprice'],
        #                         session['maxprice'], session['resnum'], session['maxrooms'], session['propertytype'])
        # rmove_results = rmove.requestScrape()
        # print("returned results of b")
        #
        # gum = sites.Gumtree('for-sale', session['postcode'], session['brooms'], session['minprice'],
        #                     session['maxprice'], session['radius'], session['type'])
        # gumresults = gum.request()
        # print("returned results of c")
        #
        # # zoop = sites.Zoopla(session['postcode'], "for-sale")
        # # zooplaresults = zoop.requests()
        # # print("returned results of d")
        #
        # res = otm_results + rmove_results + gumresults
        #
        # # Removed otm from the list
        # return jsonify(res)

    elif session['type'] == 'lettings':

        otmsale = sites.OnTheMarket(session['postcode'], "to-rent", session['radius'], session['brooms'],
                                    session['minprice'], session['maxprice'], session['resnum'], session['maxrooms'],
                                    session['propertytype'])
        otm_results = otmsale.request()

        rmove = sites.Rightmove(session['postcode'], "LETTINGS", session['radius'], session['brooms'],
                                session['minprice'],
                                session['maxprice'], session['resnum'], session['maxrooms'], session['propertytype'])
        rmove_results = rmove.requestScrape()

        gum = sites.Gumtree('to-rent', session['postcode'], session['brooms'], session['minprice'],
                            session['maxprice'], session['radius'], session['type'])
        gumresults = gum.request()

        # zoop = sites.Zoopla(session['postcode'], "for-sale")
        # zooplaresults = zoop.requests()
        # print("returned results of d")

        res = otm_results + rmove_results + gumresults
        # Removed otm from the list
        return jsonify(res)


@app.route('/lettingsudate', methods=["GET", "POST"])
def lettings():
    if request.method == "POST":
        session['type'] = "lettings"
        return ('base.html')
    pass


@app.route('/back', methods=["GET"])
def goBack():
    session.clear()
    return render_template('form.html')


@app.route('/', methods=["GET", "POST"])
def search():
    # proxies = sites.Proxies()
    # prox_list = proxies.createProxyList()
    print("SEARCH ")
    if request.method == "POST":
        search_query = request.form.get("pcode")
        print("Search query: ", search_query)

        POSTCODE = '([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})|([A-Za-z][A-Ha-hJ-Yj-y][0-9][0-9]?)'
        match = re.search(POSTCODE, search_query)
        print("MATCH: ", match.group())

        session['postcode'] = match.group(0).replace(' ', '')

        session['length'] = len(search_query)
        session['display'] = search_query

        session['radius'] = 1
        session['brooms'] = 2
        session['resnum'] = 1
        session['proxindex'] = 0

        salestype = request.form.get("sales")
        if salestype:
            session['minprice'] = 50000
            session['maxprice'] = 250000
            session['type'] = salestype
        lettings = request.form.get("lettings")
        if lettings:
            session['type'] = lettings
            session['minprice'] = 450
            session['maxprice'] = 2000

        print("session{'type'}: ", session['type'])
        print("minprice: ", session['minprice'])
        print("maxprice: ", session['maxprice'])
        return render_template('b_2.html')

    return render_template('tpage.html')


@app.route('/pageload', methods=["GET", "POST"])
def get_results():
    print("session['searchtype']: ", session['searchtype'], " session['type']: ", session['type'])
    if request.method == "GET":
        if session['searchtype'] == 'rightmove' and session['type'] == 'sales':
            rmove = sites.Rightmove(session['postcode'], "SALE", session['radius'], session['brooms'],
                                    session['minprice'],
                                    session['maxprice'], session['resnum'], session['maxrooms'],
                                    session['propertytype'])
            rmove_results = rmove.requestScrape()
            return jsonify(rmove_results)

        if session['searchtype'] == 'gumtree' and session['type'] == 'sales':
            print("get results gumtree sales")
            gum = sites.Gumtree('for-sale', session['postcode'], session['brooms'], session['minprice'],
                                session['maxprice'], session['radius'], session['type'])
            gumresults = gum.request()
            return jsonify(gumresults)

        if session['searchtype'] == 'onthemarket' and session['type'] == 'sales':
            otmsale = sites.OnTheMarket(session['postcode'], "for-sale", session['radius'], session['brooms'],
                                        session['minprice'], session['maxprice'], session['resnum'],
                                        session['maxrooms'], session['propertytype'])
            otm_results = otmsale.request()
            print("OTM: ", otm_results)
            return jsonify(otm_results)

        if session['searchtype'] == 'rightmove' and session['type'] == 'lettings':
            rmove = sites.Rightmove(session['postcode'], "LETTINGS", session['radius'], session['brooms'],
                                    session['minprice'],
                                    session['maxprice'], session['resnum'], session['maxrooms'],
                                    session['propertytype'])
            rmove_results = rmove.requestScrape()
            return jsonify(rmove_results)

        if session['searchtype'] == 'gumtree' and session['type'] == 'lettings':
            print("get results gumtree sales")

            gum = sites.Gumtree('to-rent', session['postcode'], session['brooms'], session['minprice'],
                                session['maxprice'], session['radius'], session['type'])
            gumresults = gum.request()

            return jsonify(gumresults)

        if session['searchtype'] == 'onthemarket' and session['type'] == 'lettings':
            otmsale = sites.OnTheMarket(session['postcode'], "to-rent", session['radius'], session['brooms'],
                                        session['minprice'], session['maxprice'], session['resnum'],
                                        session['maxrooms'], session['propertytype'])
            otm_results = otmsale.request()

            return jsonify(otm_results)

        if session['searchtype'] == 'all':
            result = returnAll()
            return result


@app.route('/f2submit', methods=["GET", "POST"])
def search_p2():
    print("Search_p2: ")

    if request.method == "POST":
        searchtype = request.form.get("option")
        session['searchtype'] = searchtype
        minprice = request.form.get("minprice")
        n_min = minprice.replace('£', '')
        print("n_min: ", n_min)
        session['minprice'] = n_min
        maxprice = request.form.get("maxprice")
        n_max = maxprice.replace('£', '')
        print("n_max: ", n_max)
        session['maxprice'] = n_max
        radius = request.form.get("radius")
        print("radius: ", radius)
        session['radius'] = radius
        maxrooms = request.form.get("maxrooms")
        print("maxrooms: ", maxrooms)
        session['maxrooms'] = maxrooms
        minrooms = request.form.get("minrooms")
        print("minrooms: ", minrooms)
        session['minroom'] = minrooms
        type = request.form.get("propertytype")
        session['propertytype'] = type

        return render_template('base.html')


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/searchtest', methods=["GET", "POST"])
    def search():

        # proxies = sites.Proxies()
        # prox_list = proxies.createProxyList()

        if request.method == "POST":
            search_query = request.form.get("pcode")
            session['postcode'] = search_query.upper()
            session['radius'] = 1
            session['brooms'] = 2
            session['resnum'] = 1
            session['proxindex'] = 0

            salestype = request.form.get("sales")
            if salestype:
                session['minprice'] = 50000
                session['maxprice'] = 250000
                session['type'] = salestype
            lettings = request.form.get("lettings")
            if lettings:
                session['type'] = lettings
                session['minprice'] = 450
                session['maxprice'] = 2000

            print("session{'type'}: ", session['type'])
            print("minprice: ", session['minprice'])
            print("maxprice: ", session['maxprice'])
            return render_template('b_2.html')

        return render_template('tpage.html')

    @app.route('/f2submit', methods=["GET", "POST"])
    def search_p2():
        print("Search_p2: ")

        if request.method == "POST":
            searchtype = request.form.get("option")
            session['searchtype'] = searchtype
            minprice = request.form.get("minprice")
            n_min = minprice.replace('£', '')
            print("n_min: ", n_min)
            session['minprice'] = n_min
            maxprice = request.form.get("maxprice")
            n_max = maxprice.replace('£', '')
            print("n_max: ", n_max)
            session['maxprice'] = n_max
            radius = request.form.get("radius")
            print("radius: ", radius)
            session['radius'] = radius
            maxrooms = request.form.get("maxrooms")
            print("maxrooms: ", maxrooms)
            session['maxrooms'] = maxrooms
            minrooms = request.form.get("minrooms")
            print("minrooms: ", minrooms)
            session['minroom'] = minrooms
            type = request.form.get("propertytype")
            session['propertytype'] = type

            return render_template('base.html')

    @app.route('/planningdata', methods=["GET"])
    def planning_data():
        planapps = sites.Planning(session['postcode'])
        plans = planapps.request()
        return jsonify(plans)

    @app.route('/landregistry')
    def sold_prices():
        landregister = sites.LandRegistry(session['postcode'])
        registry = landregister.req()
        return jsonify(registry)

    @app.route('/zooplasale', methods=["GET"])
    def zoopla_sales():
        zoop = sites.Zoopla(session['postcode'], "for-sale", session['brooms'], session['minprice'],
                            session['maxprice'])
        zooplaresults = zoop.requests()

        return zooplaresults

    @app.route('/zooplalet', methods=["GET"])
    def zoopla_lets():
        zoop = sites.Zoopla(session['postcode'], "to-rent")
        zooplaresults = zoop.requests()

        return jsonify(zooplaresults)

    @app.route('/rightmovesale/', methods=["GET"])
    def rmove_sales():
        print("rmove sales")
        rmove = sites.Rightmove(session['postcode'], "SALE", session['radius'], session['brooms'], session['minprice'],
                                session['maxprice'], session['resnum'], session['maxrooms'], session['propertytype'])
        rmove_results = rmove.requestScrape()
        print("rmove response return")
        return jsonify(rmove_results)

    @app.route('/gumtreesales', methods=["GET"])
    def gumtree_scrape():

        gum = sites.Gumtree('for-sale', session['postcode'], session['brooms'], session['minprice'],
                            session['maxprice'], session['radius'], session['type'])
        gumresults = gum.request()
        # session['proxindex'] = proxies.increaseProxVar(session['proxindex'])

        return jsonify(gumresults)

    @app.route('/gumtreesales', methods=["GET"])
    def gumtree_lets():

        print("gumtree lets")
        gum = sites.Gumtree('to-rent', session['postcode'], session['brooms'], session['minprice'], session['maxprice'],
                            session['radius'], session['type'])
        gumresults = gum.request()

        return jsonify(gumresults)

    @app.route('/rmoverent', methods=["GET"])
    def rmove_lets():
        print("Rmove lets postcode ", session['postcode'])
        rmove = sites.Rightmove(session['postcode'], "RENT", session['radius'], session['brooms'], session['minprice'],
                                session['maxprice'], session['resnum'], session['maxrooms'], session['propertytype'])
        rmove_results = rmove.requestScrape()
        # session['proxindex'] = proxies.increaseProxVar(session['proxindex'])

        return jsonify(rmove_results)

    @app.route('/rmovesold', methods=["GET"])
    def rmov_sold():
        rmove = sites.Rightmove(session['postcode'], None, None, None, None, None, None, None, None)
        rmov_res = rmove.requestSold()

        return jsonify(rmov_res)

    @app.route('/otmsale', methods=["GET"])
    def otm_sales():
        otmsale = sites.OnTheMarket(session['postcode'], "to-rent", session['radius'], session['brooms'],
                                    session['minprice'], session['maxprice'], session['resnum'], session['maxrooms'],
                                    session['propertytype'])
        otm_results = otmsale.request()

        return jsonify(otm_results)

    @app.route('/otmrent', methods=["GET"])
    def otm_rent():
        print("OTM Rent pages: ", " radius: ", session['radius'], " minprice ", session['minprice'])
        otmrent = sites.OnTheMarket(session['postcode'], "to-rent", session['radius'], session['brooms'],
                                    session['minprice'], session['maxprice'], session['resnum'], session['maxrooms'],
                                    session['propertytype'])
        otm_results = otmrent.request()

        return jsonify(otm_results)

    @app.route('/crystalroof', methods=["GET"])
    def crystal_stats():
        crysstats = sites.CrystalRoof(session['postcode'])
        resp = crysstats.stats()
        return jsonify(resp)

    # Updates
    @app.route('/typeupdate', methods=["GET", "POST"])
    def update_type():
        if request.method == "POST":
            type = request.form.get("propertytype")
            session['propertytype'] = type
            return render_template('base.html')
        return render_template('base.html')

    @app.route('/pandr_update', methods=["GET", "POST"])
    def update_pcode_radius():
        print("UPDATE RADIUS")
        if request.method == "POST":
            update = request.form.get("pcodeupdate")
            session['postcode'] = update.upper()
            session['display'] = update.upper()
            return render_template('base.html')

        return render_template('base.html')

    @app.route('/numres', methods=["GET", "POST"])
    def update_results():
        print("update_results")
        if request.method == "POST":
            update = request.form.get("resultnum")
            session['resnum'] = update
            return render_template('base.html')

        return render_template('base.html')

    @app.route('/broomupdate', methods=["POST"])
    def update_rooms():
        if request.method == "POST":
            brooms = request.form.get("minrooms")
            session['brooms'] = brooms

            return render_template('base.html')

    @app.route('/maxroomupdate', methods=["POST"])
    def update_maxrooms():
        if request.method == "POST":
            maxroom = request.form.get("maxroom")
            session['maxrooms'] = maxroom

            return render_template('base.html')

    @app.route('/radiusupdate', methods=["POST"])
    def update_radius():
        if request.method == "POST":
            radius = request.form.get("radius")
            session['radius'] = radius
            return render_template('base.html')

    @app.route('/priceupdate', methods=["POST"])
    def update_min_price():
        if request.method == "POST":
            minprice = request.form.get("minprice")
            session['minprice'] = minprice

            return render_template('base.html')

    @app.route('/updatesession', methods=["GET", "POST"])
    def update_session():
        print("UPDATE FORM TO LETTINGS")

        if request.method == "POST":
            print("REQUEST METHOD POST")
            value = request.form.get("page")
            print("REQUEST VALUE: ", value)

            if value == 'sales':
                print("if values sales")
                session['type'] = 'lettings'
                print("UPDATE FORM TO LETTINGS")
                return render_template('base.html')
            elif value == 'lettings':
                print("if values lettings")
                session['type'] = 'sales'
                print("UPDATE FORM TO Lettings")
                return render_template('base.html')

    @app.route('/maxpriceupdate', methods=["POST"])
    def update_max_price():
        if request.method == "POST":
            maxprice = request.form.get("maxprice")
            session['maxprice'] = maxprice

            return render_template('base.html')

    @app.route('/returnall', methods=["GET"])
    def returnAll():
        if session['type'] == 'sales':

            print("Return all")

            otmsale = sites.OnTheMarket(session['postcode'], "for-sale", session['radius'], session['brooms'],
                                        session['minprice'], session['maxprice'], session['resnum'],
                                        session['maxrooms'], session['propertytype'])
            otm_results = otmsale.request()
            print("returned results of a")

            rmove = sites.Rightmove(session['postcode'], "SALE", session['radius'], session['brooms'],
                                    session['minprice'],
                                    session['maxprice'], session['resnum'], session['maxrooms'],
                                    session['propertytype'])
            rmove_results = rmove.requestScrape()
            print("returned results of b")

            gum = sites.Gumtree('for-sale', session['postcode'], session['brooms'], session['minprice'],
                                session['maxprice'], session['radius'], session['type'])
            gumresults = gum.request()
            print("returned results of c")

            # zoop = sites.Zoopla(session['postcode'], "for-sale")
            # zooplaresults = zoop.requests()
            # print("returned results of d")

            res = otm_results + rmove_results + gumresults

            # Removed otm from the list
            return jsonify(res)

        elif session['type'] == 'lettings':

            otmsale = sites.OnTheMarket(session['postcode'], "to-rent", session['radius'], session['brooms'],
                                        session['minprice'], session['maxprice'], session['resnum'],
                                        session['maxrooms'], session['propertytype'])
            otm_results = otmsale.request()

            rmove = sites.Rightmove(session['postcode'], "LETTINGS", session['radius'], session['brooms'],
                                    session['minprice'],
                                    session['maxprice'], session['resnum'], session['maxrooms'],
                                    session['propertytype'])
            rmove_results = rmove.requestScrape()

            gum = sites.Gumtree('to-rent', session['postcode'], session['brooms'], session['minprice'],
                                session['maxprice'], session['radius'], session['type'])
            gumresults = gum.request()

            # zoop = sites.Zoopla(session['postcode'], "for-sale")
            # zooplaresults = zoop.requests()
            # print("returned results of d")

            res = otm_results + rmove_results + gumresults
            print(res)
            # Removed otm from the list
            return jsonify(res)

    @app.route('/pageload', methods=["GET", "POST"])
    def get_results():

        print("session['searchtype']: ", session['searchtype'], " session['type']: ", session['type'])
        if request.method == "GET":
            if session['searchtype'] == 'rightmove' and session['type'] == 'sales':
                rmove = sites.Rightmove(session['postcode'], "SALE", session['radius'], session['brooms'],
                                        session['minprice'],
                                        session['maxprice'], session['resnum'], session['maxrooms'],
                                        session['propertytype'])
                rmove_results = rmove.requestScrape()
                print("rmove results ", rmove_results)
                return jsonify(rmove_results)

            if session['searchtype'] == 'gumtree' and session['type'] == 'sales':
                print("get results gumtree sales")
                gum = sites.Gumtree('for-sale', session['postcode'], session['brooms'], session['minprice'],
                                    session['maxprice'], session['radius'], session['type'])
                gumresults = gum.request()
                return jsonify(gumresults)

            if session['searchtype'] == 'onthemarket' and session['type'] == 'sales':
                otmsale = sites.OnTheMarket(session['postcode'], "for-sale", session['radius'], session['brooms'],
                                            session['minprice'], session['maxprice'], session['resnum'],
                                            session['maxrooms'], session['propertytype'])
                otm_results = otmsale.request()
                print("OTM: ", otm_results)
                return jsonify(otm_results)

            if session['searchtype'] == 'rightmove' and session['type'] == 'lettings':
                rmove = sites.Rightmove(session['postcode'], "LETTINGS", session['radius'], session['brooms'],
                                        session['minprice'],
                                        session['maxprice'], session['resnum'], session['maxrooms'],
                                        session['propertytype'])
                rmove_results = rmove.requestScrape()
                return jsonify(rmove_results)

            if session['searchtype'] == 'gumtree' and session['type'] == 'lettings':
                print("get results gumtree sales")

                gum = sites.Gumtree('to-rent', session['postcode'], session['brooms'], session['minprice'],
                                    session['maxprice'], session['radius'], session['type'])
                gumresults = gum.request()

                return jsonify(gumresults)

            if session['searchtype'] == 'onthemarket' and session['type'] == 'lettings':
                otmsale = sites.OnTheMarket(session['postcode'], "to-rent", session['radius'], session['brooms'],
                                            session['minprice'], session['maxprice'], session['resnum'],
                                            session['maxrooms'], session['propertytype'])
                otm_results = otmsale.request()

                return jsonify(otm_results)

            if session['searchtype'] == 'all':
                result = returnAll()
                return result

    return app


if __name__ == '__main__':
    sys.path.append('/home/alasdairkite/flasksearch/flasksearch/node_modules')

    context = ('local.crt', 'local.key')
    app.secret_key = "super secret key"
    app.config['SECRET_KEY'] = 'the random string'
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    app.run()
