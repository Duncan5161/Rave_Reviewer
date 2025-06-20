# Rave Reviewer
This is a Flask web application, which enables users to create a profile, log-in into the website and leave reviews not for nightclubs generically, but for particular nights that they have attended at nightclubs. This reflects what has been my experience, whereby different nights at a certain club can vary substantially. It provides the option to rate criteria specific to nightclubs such as security and sound quality, and a chance for those who identify as women or non-binary to rate how safe they feel. These could vary according to the night you attend and also, so far as I can tell, are not criteria available for review on other websites.

# Technologies used 
1. Python: Underlying code including routes for each web page, connecting to SQLite3 database to save and access data, data validation for new clubs and reviews on the backend, and user creation and login using FLask Login. 
2. Flask: Programme written using the Flask web framework.
3. HTML: Used to render the web pages.
4. CSS: Used via a stylesheet to produce the basic visual rendering seen on the web app.
5. Bootstrap: Used to create the drop-down menu that enables the user to browse the different web pages. 
6. Jinja: Loops used to render information via dictionaries, including for clubs and reviews, show the correct option from login, register and logout depending on current status and to only render the female safety option for users not registered as male via 'show restricted'. 
7. SQLlite3: Used to create three tables: users, clubs and reviews, to which data can be saved and from which data is rendered on the corresponding web pages. 

# Installation 
1.  Clone the repository: `git clone <https://github.com/Duncan5161/Rave_Reviewer>`   
2.  Create a virtual environment: `python3 -m venv venv`
3.  Activate the environment: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt

# Usage
1. Navigate to the the project directory: 'cd Rave_Reviewer' 
2. Run the application: "Flask Run'
3. Access the app in your browser: http://127.0.0.1:5000

# Design Choices
## 1. Linking SQLite3 with Flask
I had to decide how to link the SQL database with Flask which was interesting as numerous methods were listed – I eventually used the method from the Flask documentation as this allowed easy querying and submitting of data without the use of a cursor in each instance. I chose SQLite3 as it is the simplest implementation of SQL and had sufficient features for this project.

## 2. Implementing Flask Login
Another significant piece of work during implementation was making the log-in. I elected to use Flask Login to create a session so that a user, who will already have registered through the ‘create profile’ page, can log-in and remain logged in. 

I used the static method for the user class to call the user’s ID on each page of the web application and ensure this is aligned with the database ID (that is created at the time of the profile being created). Once complete I used the ‘login-required’ decorator on the  relevant pages (view profile, add a club and add a review) to block users accessing the pages without being logged in.

## 3. Implementing the review filter for clubs and for nights 
I used a conditional statement to skip database entries that don’t match the filter the user has requested. This method only loads and sends the required data. I implemented this and the club filter using GET, rather than POST, as no new information was being submitted to the SQL database and information being sent was not private.

## 4. Hiding the women's safety category if the user identifies as male
This was something that I considered approaching in a range of ways - (1) render all options and use JavaScript to prevent the women’s safety category from appearing (2) render all options and allow submission but block from the server-side if the user identifies as male or (3) only render this option is the user does not identify as male.

I ultimately chose option three primarily as this reduces the chances of client-side interference. Using a Jinga ‘if restricted’ loop, with ‘show_restricted’ defined as false should the user identify as male, I ensured that if the currently logged in profile had the gender assigned as male this successfully hid the female safety part of a new review.

# Video Demo: https://youtu.be/CmmrxOD7SKo

# Deployment
The final website was pushed to Github, then hosted via Python Anywhere. The live demo via Python Anywhere is here: https://rave-reviewer-duncan51.eu.pythonanywhere.com/
# Author 
Duncan Shallard-Brown - duncan51@hotmail.co.uk
