#Import flask and relevant libraries
from flask import Flask, render_template, request, g, flash, session 
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from email_validator import validate_email, EmailNotValidError
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

#Create login manager class
login_manager = LoginManager()

#Configure application
app = Flask(__name__)

#Set secret key
app.secret_key = '82b4f2f57b767da6f241fb9e0e4c24f0411221ebaa6fe1984215b5a4ca494231' #Generated using 'import secrets'

#Initialise login manager
login_manager = LoginManager()
login_manager.init_app(app) #Linking login manager to Flask app (after app created) before routes processed; allows Flask to manager user sessions/handle login and out
login_manager.login_view = 'login'

#Prep SQL database
DATABASE = 'project/database.db'
def get_db():

    db = getattr(g, '_database', None) #Check if db is already stored in g, if it does not exist create one
    if db is None:
        db = g._database = sqlite3.connect('database.db')
        db.row_factory = sqlite3.Row
    return db #Return db object

@app.teardown_appcontext #close connection after each request
def close_connection(exception):
    db = getattr(g, '_database', None)

    if db is not None:
        db.close()

def query_db(query, args=(), one=False): #make querying easier by returning requests in dictionaries (not tuples)
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return(rv[0] if rv else None) if one else rv

#User class - represents a user and their attributes - implements method required by flask login from User Mixin (defaults for is_authenticated, is_active, is_anonymous and get_id)
class User (UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        user_id_1 = query_db("SELECT * FROM users WHERE id = ?", [user_id], one=True)
        if user_id_1:
            print('USER FOUND')
            return User(id=user_id_1['id'], username=user_id_1['username'], password=user_id_1['password_hash'])
        print('USER NOT FOUND')
        return None

#User loader - loads user ID from database - no need to define User_ID
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id) #UserMixin has 'get_id' method

#Home page
@app.route("/")
def index():
  test = current_user.get_id()
  print(f"Username: {test}")

  return render_template("index.html")

#View Reviews by night
@app.route("/reviews", methods=["GET", "POST"])
def reviews():

 if request.method == "GET":

   #Make list of club review info, appending a dictionary for each club's info every time
    list = []
    club_list = []
    club_dict = {
        "Club": 'All',
    }
    club_list.append(club_dict)

    night_list = []
    night_dict = {
        "Night":'All',
    }
    night_list.append(night_dict)

    #Pull filter data from HTML file
    club_select = request.args.get("club_select")
    print(club_select)
    night_select = request.args.get("night_select")
    print(night_select)

    #Create list of clubs
    for club_list1 in query_db("SELECT name FROM clubs"):
        club = (club_list1['name'])
        print(f"TEST CLUB NAME: {club}")
        club_dict = {
                    "Club": club,
                     }
        club_list.append(club_dict)
    print(club_list)

    #Create list of nights (distinct)
    for night_list1 in query_db("SELECT DISTINCT night FROM reviews"):
        night = (night_list1['night'])
        print(f"TEST CLUB NAME: {night}")
        #Add logic to skip (continue) if the night entry is blank
        if night == "":
            continue
        else:
            night_dict = {
                        "Night": night,
                        }
        night_list.append(night_dict)
    print(night_list)

    #Put each column in variable using SQL query
    for reviews in query_db("SELECT * FROM reviews"):
        description = (reviews['description'])
        club = (reviews['club'])
        date_visited = (reviews['date_visited'])
        night = (reviews['night'])
        DJs = (reviews['DJs'])
        if DJs == None:
            DJs = ''
        rating_overall = (reviews['rating_overall'])
        rating_crowd = (reviews['rating_crowd'])
        rating_security = (reviews['rating_security'])
        rating_sound = (reviews['rating_sound'])
        rating_womensafety = (reviews['rating_womensafety'])
        comments = (reviews['comments'])

        #Pull city from 'club' table
        for city in query_db("SELECT city FROM clubs WHERE name = ?", [club]):
            city_name = (city['city'])
            print(city_name)

        #Check if filter selected and if so filter data
        if club_select == None:
            club_select = 'All'

        if night_select == None:
            night_select ='All'

        if club_select == 'All' and night_select == 'All': #If both set to all, continue as normal to render all reviews
            pass
        elif club_select != 'All' and club_select != club: #If a club is selected and it does not match current DB row, skip this iteration
            continue
        elif night_select != 'All' and night_select != night: #If a night is seleted and it does not match current DB row, skip this iteration
           continue

        #Put into dict where key names match jinja column 'name'
        dict = {
                "description": description,
                "club": club,
                "date_visited": date_visited,
                "night": night,
                "DJ": DJs,
                "city": city_name,
                "rating_overall": rating_overall,
                "rating_crowd": rating_crowd,
                "rating_security": rating_security,
                "rating_sound": rating_sound,
                "rating_womensafety": rating_womensafety,
                "comments": comments,
            }
        list.append(dict)
        #print(list)
        list.reverse()

    return render_template("reviews.html", dict=list, club_list=club_list, night_list=night_list)

 else:
    return render_template("reviews.html")

#Clubs
@app.route("/clubs", methods = ["GET", "POST"])
def clubs():

 if request.method == "GET":

    list = []
    city_list = []
    city_dict = {
        "City": 'All',
    }
    city_list.append(city_dict)

    #Create dict with one instance of each city
    for city_search in query_db ("SELECT DISTINCT city from clubs"): #Used distinct to only include each city once

        city_1 = (city_search['city'])
        print(f"City_1: {city_1}")
        if city_1 in city_list:
            print('Found')
            pass
        else:
            print('Not Found')
            city_dict = {
            "City": city_1,
        }
        city_list.append(city_dict)
    print(city_list)

    #Filter by city
    city_select = request.args.get("city_select")
    print (f"TEST CITY SELECT: {city_select}")
    if city_select == None:
        city_select = 'All'
    print(f"TEST CITY SELECT: {city_select}")

    for clubs_1 in query_db("SELECT * FROM clubs"): 
        name = (clubs_1['name'])
        city = (clubs_1['city'])
        main_genre = (clubs_1['main_genre'])
        friday_close = (clubs_1['closing_time_friday'])
        if friday_close == '':
            friday_close = "Not Known"
        saturday_close = (clubs_1['closing_time_saturday'])
        if saturday_close == '':
            saturday_close = "Not Known"

        review_count = query_db("SELECT * FROM reviews WHERE club = ?", [name]) 
        length = len(review_count)
        #print(f"length: {length}")

        if city_select == 'All': #If 'All' is selected go to next stage so all clubs added
            pass
        elif city_select != city: #If selected city does not match current club line in Db, skip it
            continue
        print(name)

        #Find average overall rating for club
        average_rating = query_db("SELECT avg(rating_overall) FROM reviews WHERE club = ?", [name])
        average_overall = (average_rating[0][0])
        print(f"Average: {average_overall}")
        if average_overall == None:
            average_overall = 'No reviews sumbmitted yet'

        else:
            average_overall = str(round(average_overall, 2)) #Round figure to two decimal places, if there are enough ratings
            print(f"FINAL AVERAGE CHECK: {average_overall}")

        #Find average women's safety rating for club
        women_safety = query_db("SELECT avg(rating_womensafety) FROM reviews WHERE club = ?", [name])
        women_safety_rating = (women_safety[0][0])
        #print(f"Women: {women_safety}")
        if women_safety_rating == None:
            women_safety_rating = 'No ratings sumbmitted yet'

        else:
           women_safety_rating = str(round(women_safety_rating, 2))
        print(f"Women: {women_safety_rating}")

        #Find the night with the best rating at that club - search for all nights from the current club by average overall rating, group by night then list in descending order
        best_night = query_db("SELECT avg(rating_overall), night FROM reviews WHERE club = ? GROUP BY night ORDER BY rating_overall DESC", [name])
        print(f"Test: {best_night}")

        #If returned object is empty, this must be because there are no reviews to search so return corresponding message
        if best_night == []:
            print('empty')
            best_night_final = 'No reviews yet'

        else: #Otherwise use the first entry in the table, which will be the night with the highest average score for that club
            best_night_final = (best_night[0][1])
            print(best_night_final)

        dict ={
            "club_name": name,
            "city": city,
            "main_genre": main_genre,
            "friday_close": friday_close,
            "saturday_close": saturday_close,
            "reviews_submitted": length,
            "average_overall": average_overall,
            "women_safety": women_safety_rating,
            "best_night_final": best_night_final
        }

        list.append(dict)
        print(list)

    return render_template("clubs.html", dict=list, city_list=city_list)

#Add Review
@app.route("/add_review", methods = ["GET", "POST"])
@login_required
def add_review():

   if request.method == "GET":

        #Make list of dictionaries with each club name attached
        list = []
        for clubs in query_db("SELECT name FROM clubs ORDER BY name ASC"):
            club = (clubs['name'])
           
            dict = {
                    "club_name": club,
                    }
            list.append(dict)
            print(list)

        user_id_number = current_user.get_id()
        user = query_db("SELECT * FROM users WHERE id = ?", [user_id_number], one=True)
        user_added_by = (user['username'])
        #print(user_added_by)

        gender_1 = query_db("SELECT gender FROM users WHERE username = ?", [user_added_by], one=True)
        gender=(gender_1[0])

        #Check if user is male and remove women's safety form if they are
        if gender == "male":
            show_restricted = False
        else:
            show_restricted = True

        print(show_restricted)

        return render_template("add_review.html", dict=list, show_restricted=show_restricted)

   else: #Method is POST

        list = []
        for clubs in query_db("SELECT name FROM clubs ORDER BY name ASC"):
            club = (clubs['name'])
            print(club)

            dict = {
                    "club_name": club,
                    }
            list.append(dict)
            print(list)

        #Set variables
        description = request.form.get("description")
        print(f"Description: {description}")
        club_name = request.form.get("club")
        print(f"Club name: {club_name}")
        date = request.form.get("date")
        print(f"Date: {date}")
        length = len(date)
        print(length)
        night = request.form.get("night")
        print(night)
        DJs = request.form.get("DJ_1")
        print(DJs)
        overall_rating = request.form.get("overall")
        print(overall_rating)
        crowd_rating = request.form.get("crowd")
        print(crowd_rating)
        security_rating = request.form.get("security")
        print(security_rating)
        sound_rating = request.form.get("security")
        print(sound_rating)
        women_safety_rating = request.form.get("women")
        print(women_safety_rating)
        comments = request.form.get("comments")
        print(comments)

        user_id_number = current_user.get_id()
        user = query_db("SELECT * FROM users WHERE id = ?", [user_id_number], one=True)
        user_added_by = (user['username'])

        #Check description server-side
        if len(description) < 3:
                flash ("Please add description")
                return render_template("add_review.html", dict=list)

        elif len(description) > 40:
            flash ("Description max length exceeded - must be between 3-40 characters or less")
            return render_template("add_review.html", dict=list)

        #Check date server side
        if date == "":
            flash ("Please add date")
            return render_template("add_review.html", dict=list)

    #Check max text length server side
        #i.Night or brand
        length_night = len(night)
        print(f"LengthNight: {length_night}")
        if length_night > 30:
            flash ("Night/brand/event description max length exceeded")
            return render_template("add_review.html", dict=list)

        #ii. Headline DJ
        length_dj = len(DJs)
        print(f"LengthNight: {length_dj}")
        if length_dj > 30:
            flash ("Headline DJ max length exceeded")
            return render_template("add_review.html", dict=list)

        #iii. Comments
        length_comments = len(comments)
        print(f"LengthNight: {length_comments}")
        if length_comments > 100:
            flash ("Comments max length exceeded")
            return render_template("add_review.html", dict=list)

        #Add to database
        g.db = sqlite3.connect('database.db')

        g.db.execute(
            "INSERT INTO reviews(description, club, date_visited, night, DJs, rating_overall, rating_crowd, rating_security, rating_sound, rating_womensafety, user_added_by, comments) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (description, club_name, date, night, DJs, overall_rating, crowd_rating, security_rating, sound_rating, women_safety_rating, user_added_by, comments) #brackets at the end make it one argument
        )

        g.db.commit()

        return render_template("thank_you_review.html"), {"Refresh": "1; 'reviews'"}

#Add Club
@app.route("/add_club", methods = ["GET", "POST"])
@login_required
def add_club():

    if request.method == "POST":

        #Set variables
        club_name = request.form.get("club")
        print(f"Club Name: {club_name}")
        city = request.form.get("city")
        print(f"City: {city}")
        postcode = request.form.get("postcode")
        closing_monday = request.form.get("Monday")
        closing_tuesday = request.form.get("Tuesday")
        closing_wednesday = request.form.get("Wednesday")
        closing_thursday = request.form.get("Thursday")
        closing_friday= request.form.get("Friday")
        closing_saturday = request.form.get("Saturday")
        closing_sunday = request.form.get("Sunday")
        main_genre= request.form.get("genre")

        user_id_number = current_user.get_id()
        user = query_db("SELECT * FROM users WHERE id = ?", [user_id_number], one=True)
        user_added_by = (user['username'])

        #Check club is not in database already
        club = query_db("SELECT name FROM clubs WHERE name = ?", [club_name], one="True")

        if club is None:
            print("Club not in database")
            pass

        else:
            print("Club already in database")
            flash("Club already added - please navigate to 'add review'")
            return render_template("add_club.html")

        #Check postcode is valid
        postcode = request.form.get("postcode")
        length = len(postcode)
        if postcode == 0: #If not entered ok
            pass
        elif length < 3 and length > 0: #If entered but too short, raise error
            flash("Postcode too short - field not mandatory but must be valid if entered")
            return render_template("add_club.html")

        #Check if club name is entered
        name = request.form.get("club")
        length = len(name)
        if length <1:
            flash("Please enter club name")
            return render_template("add_club.html")

        #Check if city is entered
        city = request.form.get("city")
        length = len(city)
        if length <1:
            flash("Please enter city name")
            return render_template("add_club.html")

        #Add to database
        g.db = sqlite3.connect('database.db')

        g.db.execute(
            "INSERT INTO clubs(name, city, postcode, closing_time_monday, closing_time_tuesday, closing_time_wednesday, closing_time_thursday, closing_time_friday, closing_time_saturday, closing_time_sunday, main_genre, user_added_by) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (club_name, city, postcode, closing_monday, closing_tuesday, closing_wednesday, closing_thursday, closing_friday, closing_saturday, closing_sunday, main_genre, user_added_by) #brackets at the end make it one argument
        )

        g.db.commit()

        #Redirect to add review
        return render_template("thank_you_club.html"), {"Refresh": "1; 'add_review'"}

    else:
        return render_template("add_club.html")

#Create profile
@app.route("/create_profile", methods = ["GET", "POST"])
def create_profile():
    """ Create profile """

    if request.method == "POST":

        username = request.form.get("username")
        city = request.form.get("city")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = request.form.get("email")
        gender = request.form.get('select_gender')
        hashed_password = generate_password_hash(password, method="scrypt", salt_length=16) 
        print(f"Test: {hashed_password}")

        if current_user.is_authenticated:
            return render_template("user_exists.html")

        #Check if username is already in use
        user = query_db("SELECT * FROM users WHERE username = ?", [username], one=True)

        if user is None:
            print('Is new user')
        else:
            print('is not new user')
            flash("Username already in use ")
            return render_template("create_profile.html")

        #Check username is at least 8 characters
        username_length = len(username)
        print(f"Username length: {username_length}")
        if username_length < 8:
               flash("Username must be eight characters or more")
               return render_template("create_profile.html")

        #Check password length at least 8 characters
        password_length = len(password)
        print(f"Password length: {password_length}")
        if password_length < 8:
               flash("Password must be eight characters or more")
               return render_template("create_profile.html")

        #Check passwords match
        print(f"Password: {password}")
        print(f"Confirm: {confirm}")
        if password != confirm:
               flash("Passwords do not match")
               return render_template("create_profile.html")

        #Check if email in DB (and thus no new profile required)
        email_check = query_db("SELECT * FROM users WHERE email = ?", [email], one=True)

        if email_check is None:
            print('Is new email')
            print(f"Email: {email}")
        else:
            print('is not new email')
            flash("Email already in use ")
            return render_template("create_profile.html")

        #Validate email address as an email address
        try:
             emailinfo = validate_email(email)
             print(f"Email info: {emailinfo}")
        except EmailNotValidError:
            flash("Email not valid")
            print(f"Email not valid")
            return render_template("create_profile.html")

        #Assuming above tests passed, save user in DB
        g.db = sqlite3.connect('database.db')

        g.db.execute(
            "INSERT INTO users(username, city, password_hash, email, gender) VALUES (?,?,?,?,?)", (username, city, hashed_password, email, gender) #brackets at the end make it one argument
        )

        g.db.commit()

        return render_template("thank_you.html"), {"Refresh": "3; '/'"}

    else:

        if current_user.is_authenticated:
            flash('Profile already created')

        return render_template("create_profile.html")

#View Profile
@app.route("/profile")
@login_required
def profile():

   #Get info about user from users table
   user_id_number = current_user.get_id()
   user = query_db("SELECT * FROM users WHERE id = ?", [user_id_number], one=True)
   username = (user['username'])
   print(f"Test profile username: {username}")
   city = (user['city'])

   #Put into list for rendering
   list_0 = []
   list = []
   dict = {
            "City": city,
            "Username": username,
           }
   list_0.append(dict)
   #print(list)

   #Loop over previous reviews (searching by username) and put in dictionary
   for reviews in query_db("SELECT * FROM reviews WHERE user_added_by = ?", [username]):
        #print(reviews['club'])
        description = (reviews['description'])
        club = (reviews['club'])
        date_visited = (reviews['date_visited'])
        night = (reviews['night'])
        DJs = (reviews['DJs'])
        rating_overall = (reviews['rating_overall'])
        rating_crowd = (reviews['rating_crowd'])
        rating_security = (reviews['rating_security'])
        rating_sound = (reviews['rating_sound'])
        rating_womensafety = (reviews['rating_womensafety'])
        comments = (reviews['comments'])

   #Put into dict
        dict = {
                "description": description,
                "club": club,
                "date_visited": date_visited,
                "night": night,
                "DJ": DJs,
                #"city": city_name,
                "rating_overall": rating_overall,
                "rating_crowd": rating_crowd,
                "rating_security": rating_security,
                "rating_sound": rating_sound,
                "rating_womensafety": rating_womensafety,
                "comments": comments,
            }
        list.append(dict)
        print(list)

   #Render on page
   return render_template("profile.html", dict=list, list_0=list_0)

#Log-in
@app.route("/login", methods = ["GET", "POST"])
def login():
    """ Log in"""

    if request.method == "POST":

        username_1 = request.form.get('username')
        #password = request.form.get('pasword')

        #Check if username is in database
        user = query_db("SELECT username FROM users WHERE username = ?", [username_1], one=True)

        if user is None:
                flash("Username not found - please check spelling or register for new account")
                return render_template('login.html')
        else:
            print("User in Database")
            pass

        #Check password is correct
        password_check = query_db("SELECT password_hash FROM users WHERE username = ?", [username_1], one=True)
        print(password_check['password_hash'])
        if not check_password_hash(password_check['password_hash'],request.form.get("password")): 
            print("Passwords do not match")
            flash("Incorrect Password")
            return render_template("login.html")

        else:
            print("password do match")

        #If valid, create session
        username = request.form.get('username')
        user_id = query_db("SELECT * FROM users WHERE username = ?", [username_1], one=True)
        user = User(id=user_id['id'], username=user_id['username'], password=user_id['password_hash'])
        print(f"Username: {username}")
        if request.method == "POST": 
            login_user(user)
            print("Sesssion Created")
            test = current_user.get_id()
            print(f"TEST USERNAME CHECK_LOGIN: {test}")

            return render_template("index.html")
        else:
            return render_template("login.html")

    else:
        return render_template("login.html")

#Log out
@app.route("/logout") #No need for HTML page - it loads the 'logout' route when this address entered then redirects
def logout():
    """Log user out"""
    logout_user()

    return render_template("login.html")

#Thank-you
@app.route("/thank_you")
def thank_you():
    return render_template("thank-you.html")

#Apology
@app.route("/thank_you")
def apology():
    return render_template("apology.html")
