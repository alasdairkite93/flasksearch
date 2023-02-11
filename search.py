from flask import Flask, session, request, render_template, jsonify, redirect, url_for
import sites


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
proxies = sites.Proxies()
prox_list = proxies.getProxyList()

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
    zoop = sites.Zoopla(session['postcode'], "for-sale")
    zooplaresults = zoop.requests()
    return jsonify(zooplaresults)

@app.route('/zooplalet', methods=["GET"])
def zoopla_lets():
    zoop = sites.Zoopla(session['postcode'], "to-rent")
    zooplaresults = zoop.requests()
    return jsonify(zooplaresults)

@app.route('/rightmovesale/', methods=["GET"])
def rmove_sales():
    rmove = sites.Rightmove(session['postcode'], "SALE", session['radius'], session['brooms'], session['minprice'], session['maxprice'], session['resnum'])
    rmove_results = rmove.requestScrape()
    session['proxindex'] = proxies.increaseProxVar(session['proxindex'])
    return jsonify(rmove_results)


@app.route('/gumtreesales', methods=["GET"])
def gumtree_scrape():
    gum = sites.Gumtree(session['postcode'], session['brooms'], session['minprice'], session['maxprice'], session['radius'], session['type'])
    gumresults = gum.request()
    session['proxindex'] = proxies.increaseProxVar(session['proxindex'])
    print("Gumtree scrape results: ", gumresults)
    return jsonify(gumresults)

@app.route('/rmoverent', methods=["GET"])
def rmove_lets():
    rmove = sites.Rightmove(session['postcode'], "RENT", session['radius'], session['brooms'], session['minprice'], session['maxprice'], session['resnum'])
    rmove_results = rmove.requestScrape()
    session['proxindex'] = proxies.increaseProxVar(session['proxindex'])
    return jsonify(rmove_results)

@app.route('/rmovesold', methods=["GET"])
def rmov_sold():
    rmove = sites.Rightmove(session['postcode'], None, None, None, None, None, None)
    rmov_res = rmove.requestSold()
    return jsonify(rmov_res)

@app.route('/otmsale', methods=["GET"])
def otm_sales():
    otmsale = sites.OnTheMarket(session['postcode'], "for-sale", session['radius'], session['brooms'], session['minprice'], session['maxprice'], session['resnum'])
    otm_results = otmsale.request()
    session['proxindex'] = proxies.increaseProxVar(session['proxindex'])
    return jsonify(otm_results)

@app.route('/otmrent', methods=["GET"])
def otm_rent():
    print("OTM Rent pages: ", " radius: ", session['radius'], " minprice ", session['minprice'])
    otmrent = sites.OnTheMarket(session['postcode'], "to-rent", session['radius'], session['brooms'], session['minprice'], session['maxprice'], session['resnum'])
    otm_results = otmrent.request()
    session['proxindex'] = proxies.increaseProxVar(session['proxindex'])
    return jsonify(otm_results)

@app.route('/crystalroof', methods=["GET"])
def crystal_stats():
    crysstats = sites.CrystalRoof(session['postcode'])
    resp = crysstats.stats()
    return jsonify(resp)

@app.route('/pcodeupdate', methods=["GET", "POST"])
def update_pcode():

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


@app.route('/returnsales', methods=["GET", "POST"])
def salesform():
    if request.method == "POST":
        search_query = request.form.get("pcode")
        session['postcode'] = search_query
        return render_template('sales.html')
    return render_template('form.html')


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


        # a = otm_sales()

        b = rmove_sales()

        c = gumtree_scrape()

        d = zoopla_sales()

        #Removed otm from the list
        return [a, b, c, d]



@app.route('/back', methods=["GET"])
def goBack():
    session.clear()
    return render_template('form.html')


@app.route('/', methods =["GET", "POST"])
def search():
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
        return render_template('base.html')

    return render_template('form.html')

if __name__ == '__main__':

    proxy = sites.Proxies()
    proxy.createProxyList()


    context = ('local.crt', 'local.key')
    app.secret_key = "super secret key"
    app.config['SECRET_KEY'] = 'the random string'
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    app.run()
