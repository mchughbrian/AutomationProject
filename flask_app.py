import os
from flask import Flask, request, redirect, render_template, json, jsonify, send_from_directory
import requests
from twilio.twiml.messaging_response import MessagingResponse
import MySQLdb
import datetime
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import json
import pandas as pd
import re
from PIL import Image
import cv2
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from pyzbar.pyzbar import decode
from twilio.rest import Client

##############################################have description pdf also ################################
app = Flask(__name__, template_folder=".")

#initialize google maps
GoogleMaps(app, key="AIzaSyAjLuxuJLj8-UISkpSPatWj7DYe51-X3iI")

#from class demo for barcode uploading imge
app.config['UPLOAD_FOLDER'] = 'mysite/uploads'

#connect to database
db=MySQLdb.connect(
    host='brianM1931Z.mysql.pythonanywhere-services.com',
    user='brianM1931Z',
    passwd='myfinalproj',
    db='brianM1931Z$ENGN1931Z_FinalProj')

#db.ping() found this was giving me an error for some reason

#create tables if they do not exist...
#FUTURE --> make this more robust.. make secondary keys to prevent duplicates of resturants but allow
#multiple comments and average ratings

c=db.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS foodproj
    (id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL,
    rate INT,
    price INT,
    comments VARCHAR(256),
    category VARCHAR(15),
    datee VARCHAR(12),
    latitude FLOAT,
    longitude FLOAT,
    PRIMARY KEY (id))''')

c.execute('''CREATE TABLE IF NOT EXISTS beer
    (id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL,
    rate INT,
    style VARCHAR(256),
    abv VARCHAR(15),
    brewery VARCHAR(256),
    datee VARCHAR(12),
    PRIMARY KEY (id))''')


#returns home page. The home page was taken from demo online THIS WAS TAKEN FROM W3SCHOOLS ONLINE TUTORIAL ON HTML NAVBAR  https://www.w3schools.com/css/tryit.asp?filename=trycss_navbar_vertical_borders
@app.route("/",methods=["GET","POST"])
def start():
    return render_template('pdtest.html')

#this portion of code is for uploads. This was taken from in class demo  https://github.com/engn1931z/pythonAnywhereSetup
@app.route("/barcode",methods=["GET","POST"])
def hello_world():
    return render_template('index.html')


#user input section of code.
@app.route("/form", methods=["GET","POST"])
def form_example():


    if request.method == 'POST': #only entered when the form is submitted then we can grab the info that we submitted

        #grab info from user input
        search_category = request.form.get('category')
        rating = request.form.get('rating')
        area = request.form.get('area')

        #ping database to ensure connection - crashes because of this sometimes though.. confused
        #db.ping()

        #create empty lists that will be appeneded in later code
        names =[]
        rate = []
        price = []
        comments =[]
        locationsUP= []

        #######################################GET INFO FROM MY SQL############################
        c.execute("SELECT id,name,rate,price,comments FROM foodproj WHERE category LIKE %s AND rate > "+rating ,(search_category+'%',));
        #fetchmany returns a list of tuples.
        resturants=(c.fetchmany(100))
        c.execute("SELECT name,latitude,longitude FROM foodproj WHERE category LIKE %s AND rate > "+rating ,(search_category+'%',));
        locations = (c.fetchmany(100))
        col = len(resturants)

        #########################################CONVERT AREA TO LAT & LONG##############
        params_loc = {"address":area,"key":'AIzaSyAqQAftbih60mZEyxUrOE9RHuxVT_7_42E'}
        loc =requests.get("https://maps.googleapis.com/maps/api/geocode/json?",params=params_loc)
        rr = loc.json()
        zz = rr.get('results')
        print(zz[0].keys())
        bounds = zz[0].get('geometry')
        print(bounds.keys())
        bounds = bounds.get('location')
        lat = bounds['lat']
        lng = bounds['lng']

        ######################################ADD TO TABLE and maps ################
        for ii in range(0,col):
            one_lat = str(locations[ii][1])
            one_long = str(locations[ii][2])
            two_lat = str(lat)
            two_long = str(lng)
            trial1 = one_lat + ',' + one_long
            trial2 = two_lat + ',' + two_long


            #check distance between the two coordinates
            params = {'units':'imperial','origins':trial1,'destinations':trial2,'key':'AIzaSyCcGauODtaF_kAwD1iKIq-ciKEicc40M0w'}
            z=requests.get("https://maps.googleapis.com/maps/api/distancematrix/json?",params=params)

            #parse results
            r = z.json()
            tt=r.get('rows')
            ayy = tt[0].get('elements')
            thisisit = ayy[0].get('distance')
            distance = thisisit.get("text")

            #regex to only get numbers in distance
            distance=re.sub("[^0-9.]", "", distance)
            distance = float(distance)

            #if distance is less than 25 miles the resturant info will be added to the lists
            if distance < 25:
                temp_loc =[]
                names.append(resturants[ii][1])
                rate.append(resturants[ii][2])
                price.append(resturants[ii][3])
                comments.append(resturants[ii][4])
                temp_loc = [locations[ii][0],locations[ii][1],locations[ii][2]]
                locationsUP.append(temp_loc)


        #use pandas to create a table
        d = pd.DataFrame({'name':names, 'rate':rate, 'price':price,'comments':comments})
        #define order
        d = d[['rate','name','price','comments']]
        #sort table by rating
        d = d.sort_values(['rate'], ascending = False)

        #return google maps appened with the locationsUP (all coordinates for resturants that meet criteria) then display pandas table and title
        return render_template('test.html',value=locationsUP,data=d.to_html(),name = 'RESTURANTS')

    #set up the form.. when submit is clicked will execute the above ^
    return '''<form method = "POST">
        <label for="category">Type of meal</label>
        <select id = "category" name = "category">
        <option category="lunch">lunch</option>
        <option category="breakfast">breakfast</option>
        <option category="dinner">dinner</option>
        <option category="brunch">brunch</option>
        <option category="bar">bar</option>
        </select><br>
        <label for="category">Find above what rating</label>
        <select id = "rating" name = "rating">
        <option rating="1">1</option>
        <option rating="2">2</option>
        <option rating="3">3</option>
        <option rating="4">4</option>
        <option rating="5">5</option>
        <option rating="6">6</option>
        <option rating="7">7</option>
        <option rating="8">8</option>
        <option rating="9">9</option>
        </select><br>
        insert area (city,StateAbbr): <input type ="string" name = "area"><br>
        <input type ="submit" value="Submit"><br>

        </form?'''


@app.route("/sms", methods=['GET','POST'])
def sms_reply():

    #PARSING TEXT MESSAGE

    #get the body of the text that was sent
    body = request.values.get('Body',None)

    #start response
    resp=MessagingResponse()

    #ping database to test connection.. giving error...
    #db.ping()

    #convert to lower case just going to be easier to work with
    body = body.lower()

    #look for first 4 characters to see if we will be adding a resturant or beer, or rating a beer from a barcode
    headBeer = body[0:4]

    #if the text starts with beer we are adding a beer to the database. Parse text below
    #NOTE: I have set up text template in phone so will be in consistant format
    if headBeer == 'beer':
        print('in the beer loop')

        #find beer name and rating
        indexB = body.find('beer:')
        indexR = body.find('rate:')
        beer = body[indexB+5:indexR]
        rateB = body[indexR+5:]
        rateB = rateB.replace(' ','')
        rateB = int(rateB)

        #THIS WOULD GO TO GOOGLE APPSCRIPT BUT THE SITE BLOCKED GOOGLE APPSCRIPT
        whatweneed = beer
        paramsB = {'q':whatweneed}
        untappedurl2 = ('https://untappd.com/search?')

        html = requests.get(untappedurl2,params=paramsB).content
        soup = BeautifulSoup(html, "lxml")

        #find alcohol content of first result
        for p in soup.find('p', class_="abv"):
            #print(h1.find("a")['href'])
            abv = (p)

        abv = str(abv)

        ########WOULD HAVE BEEN DONE IF APPSCRIPT############
        #urlB = untappedurl2 + urlencode(paramsB)
        #urlG1 = 'https://script.google.com/macros/s/AKfycbwz8FFCDl99LX-MyAcm3-SCY18NtueI8sc5kHSBpV4eWOtnOi3-/exec'
        #paramsG = {'url':urlB}
        #html = requests.get(urlG1, paramsG).content

        #soup = BeautifulSoup(html, "lxml")

        #####################################################

        #find first returned brewery
        for p2 in soup.find('p', class_="brewery"):
            #print(h1.find("a")['href'])
            brewery = p2

        #need additional parsing to remove html
        p2 = str(p2)
        ind_find3 = p2.find('">')
        ind_find4 = p2.find('</')
        brewery = p2[ind_find3+2:ind_find4]
        print(brewery)

        #get the name of the beer.. search may be slightly off so this is offical name
        for p3 in soup.find('p', class_='name'):
            name = p3

        #needed additional parsing
        p3 = (str(p3))
        ind_find1 = p3.find('">')
        ind_find2 = p3.find('</')
        name = p3[ind_find1+2:ind_find2]
        print(name)

        #find the style of beer of first result
        for p4 in soup.find('p', class_='style'):
            style = (p4)

        #get date .. might be of interest in the furture
        now = datetime.datetime.now()
        dtime = now.strftime("%Y-%m-%d %H:%M")
        dtime = dtime[0:10]
        style = str(p4)

        #add to databse and commit changes
        c.execute('''INSERT INTO beer (name,rate,style,abv,brewery,datee) VALUES (%s,%s,%s,%s,%s,%s) ''',
        (name,rateB,style,abv,brewery,dtime))
        db.commit()


        #send confirmation message
        resp.message("added"+name)

        return str(resp)


    elif headBeer=='name':
        #parse text message. I have a template on my phone for this on phone so will be consistant
        #find name rating category comments and location from text. Note location is just town or city like 'Providence'
        #NOTE location is general i.e Providence or Cranston.
        indexN = body.find('name')
        indexR = body.find('rate')
        indexCat = body.find('category')
        indexCom = body.find('comments')
        indexLoc = body.find('location')
        name = body[indexN+5:indexR]
        rate = body[indexR+5:indexCat]
        category = body[indexCat+9:indexCom]
        comments = body[indexCom+9:indexLoc]
        area = body[indexLoc+9:]
        #0-10
        rate = rate.replace(' ','')
        rate = int(rate)
        category = category.replace(' ','')

        ###########################################################################################

        #query yelp API
        #get coordinates to use with google maps and get price
        params={"term":name,"location":area,"limit":"1"}
        headers = {'Authorization': 'Bearer m5fXIAtm1-HrRU0h3exn3eS-wElwxFdRg9iB3RiT5RwIurD7XP_sNiXVB__KtF-qdUQA6TfXfn4kReCW1WANQ0ocMW7Q_P5vNXi8bMk7B5KTNBa8ZPZT3MRVji3lWnYx' }
        x = requests.get('https://api.yelp.com/v3/businesses/search',params = params, headers=headers)

        #parse response
        r = x.json()
        xx = r.get('businesses')
        zz = xx[0].get('price')
        coordinates = xx[0].get('coordinates')
        latitude = coordinates.get('latitude')
        longitude = coordinates.get('longitude')

        #get price from yelp.. conver $$$$ to integer
        if zz == "$":
            price = 1
        elif zz == "$$":
            price = 2
        elif zz == "$$$":
            price = 3
        elif zz == "$$$$":
            price = 4

        #want to add date
        now = datetime.datetime.now()
        dtime = now.strftime("%Y-%m-%d %H:%M")
        dtime = dtime[0:10]

        #add to database
        c.execute('''INSERT INTO foodproj (name,rate,price,category,comments,datee,longitude,latitude) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ''',
        (name,rate,price,category,comments,dtime,longitude,latitude))
        db.commit()



        #Send confirmation message

        resp.message("added"+name)

        return str(resp)

#if the two text templates were not recognized we are adding a beer based on a barcode upload
#just looking to add rating or change the UPC name if necessary
    else:

        rateB = int(headBeer[0:2])
        text_file = open('text_file.txt','r')
        tB = text_file.read()

        #Based on text recieved for UPC code may not want to search entire product name
        #i.e dont want to search with terms SINGLE or BOTTLE
        if 'change' in body:
            index_c = body.find('change')
            bName = body[index_c:]
            bName = bName.replace('change:','')
            bName = bName.replace('change','')
            paramsB = {'q':bName}
        else:
            paramsB = {'q':tB}



        #would have used google appscript but blocked...
        untappedurl2 = ('https://untappd.com/search?')
        html = requests.get(untappedurl2,params=paramsB).content
        soup = BeautifulSoup(html, "lxml")

        #find first abv content result
        for p in soup.find('p', class_="abv"):
            #print(h1.find("a")['href'])
            abv = (p)

        abv = str(abv)

        #find first brewery result
        for p2 in soup.find('p', class_="brewery"):
            #print(h1.find("a")['href'])
            brewery = p2

        #parse out additional info
        p2 = str(p2)
        ind_find3 = p2.find('">')
        ind_find4 = p2.find('</')
        brewery = p2[ind_find3+2:ind_find4]
        print(brewery)

        #find name first result
        for p3 in soup.find('p', class_='name'):
            name = p3

        #parse out additional info
        p3 = (str(p3))
        ind_find1 = p3.find('">')
        ind_find2 = p3.find('</')
        name = p3[ind_find1+2:ind_find2]
        print(name)

        #find first result style
        for p4 in soup.find('p', class_='style'):
            style = (p4)

        #date may be interesting somewhere down the line
        now = datetime.datetime.now()
        dtime = now.strftime("%Y-%m-%d %H:%M")
        dtime = dtime[0:10]
        style = str(p4)

        #add to databse
        c.execute('''INSERT INTO beer (name,rate,style,abv,brewery,datee) VALUES (%s,%s,%s,%s,%s,%s) ''',
        (name,rateB,style,abv,brewery,dtime))
        db.commit()

        #send confirmation email
        resp.message("added"+name)

        return str(resp)


#return beer database. Fetch and append to list and display in pandas
@app.route("/beer")
def beer():
    c.execute("SELECT name,rate,style,abv,brewery,datee FROM beer");
    beers=(c.fetchmany(100))

    beer_name = []
    beer_rate = []
    beer_style = []
    beer_abv = []
    beer_brewery = []
    for ii in range(0,len(beers)):
        beer_name.append(beers[ii][0])
        beer_rate.append(beers[ii][1])
        beer_style.append(beers[ii][2])
        beer_abv.append(beers[ii][3])
        beer_brewery.append(beers[ii][4])


    d_beers = pd.DataFrame({'name':beer_name, 'rate':beer_rate, 'style':beer_style,'abv':beer_abv,'brewery':beer_brewery})
    d_beers = d_beers[['rate','name','style','abv','brewery']]
    d_beers = d_beers.sort_values(['rate'], ascending = False)
    return d_beers.to_html()


###########################this is just for testing#####################
@app.route("/test")
def img_test():

    f = '/home/brianM1931Z/mysite/uploads/IMG_20180509_195245.jpg'
    img = cv2.imread(f)
    img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img_binary = cv2.threshold(img_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    cv2.imwrite(f.replace('.','_binary.'),img_binary)
    img=Image.open(f.replace('.','_binary.'))
    #text = pytesseract.image_to_string(img)
    decoded = decode(img)

    if len(decoded)>0:
        for x in decoded:
            barcode = x.data.decode()
        return barcode
        #return '\n\n'.join([x.data.decode() for x in decoded])
    else:
        return 'barcode not returned'

#################################################################


@app.route('/upload', methods=['POST'])
def upload_file():

    #set up to allow for sending of sms with out replying
    from twilio.rest import Client
    account_sid = "ACe88cd5fca13eaa569472952a7403f6ac"
    auth_token = "83ba644686f3cd5cfcb508d4a2978d6e"
    client = Client(account_sid, auth_token)

    #from class demo https://github.com/engn1931z/pythonAnywhereSetup
    file = request.files['image']
    f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

    file.save(f)
    # add your custom code to check that the uploaded file is a valid image and not a malicious file (out-of-scope for this post)

    #Professor ZIA helped with this. use open CV to conver to gray scale and binarize the image then decode
    img = cv2.imread(f)
    img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img_binary = cv2.threshold(img_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    cv2.imwrite(f.replace('.','_binary.'),img_binary)
    img=Image.open(f.replace('.','_binary.'))
    #text = pytesseract.image_to_string(img)
    decoded = decode(img)

    if len(decoded)>0:
        for x in decoded:
            barcode = x.data.decode()
        #return '\n\n'.join([x.data.decode() for x in decoded])
    else:
        ########if code not found text to retry better picture
        client.api.account.messages.create(
            to="+15164040292",
            from_="+15162178138",
            body="Barcode Not Readable!")
        return 'barcode not returned'

    #delete the images.. save storage
    bfile = f.replace('.','_binary.')
    os.remove(bfile)
    os.remove(f)

    #will need to make this a google script in future..
    urlUPC = 'https://www.upcdatabase.com/item/' + barcode
    htmlUPC = requests.get(urlUPC).content
    soup = BeautifulSoup(htmlUPC, 'html.parser')

    #get product description from code
    soup = BeautifulSoup(htmlUPC, 'html.parser')
    divs = soup.findAll("table",{"class":'data'})
    divs = str(divs)
    #remove html encoding.. From regex cheat sheet.
    add_string3 = re.sub('(\<(/?[^\>]+)\>)','',divs)
    lst = add_string3.split('\n')

    for l in lst:
        if "Description" in l:
            ans = l.replace('Description','')


    #attempt to remove things.. in
    ans = ans.replace('SINGL','')
    ans = ans.replace('BOTTL','')


        #send text to ask for rating also allows user to see the product returend
    client.api.account.messages.create(
        to="+15164040292",
        from_="+15162178138",
        body="Please send the rating for"+ans)

    #we will save to text file so we can store this name so when text comes in can just read text file and add.
    text_file = open('text_file.txt','w')
    text_file.write(ans)
    text_file.close()

    return ans
##########gooo to /sms and get the number.. this way we dont have to recode theee database entries and stuff. .. .
