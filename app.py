from flask import Flask, render_template, request, session, redirect, send_from_directory
from scripts.utils import listNeeds, generatePropositionExample, evaluateProposition
from scripts.db_util import insert_user, fetch_user, UserNotFoundError
import datetime
import os

app = Flask(__name__)
app.secret_key = 'HrRdpsuJjIiOiPVdpqUk'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=60)
app.config['LIBRARY_PATH'] = os.path.abspath(
    os.path.join(os.getcwd(), 'library'))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video")
def video():
    return render_template("video.html")


@app.route("/topologies")
def topologies():
    return send_from_directory(app.config['LIBRARY_PATH'], 'topologies.csv')


@app.route("/demographics")
def demographics():
    return send_from_directory(app.config['LIBRARY_PATH'], 'demographics.csv')


@app.route("/logout")
def logout():
    session.pop('userName', None)
    session.pop('teamName', None)
    session.pop('emailAddress', None)
    return redirect('/login')


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        session.pop('userName', None)
        session.pop('teamName', None)
        session.pop('emailAddress', None)
        return render_template('login.html')
    else:
        userName = request.form['username']
        password = request.form['password']
        try:
            user = fetch_user(userName, password)
            session['userName'] = user['user_name']
            session['teamName'] = user['team_name']
            session['emailAddress'] = user['email_address']
            return render_template("index.html")

        except UserNotFoundError:
            return render_template(
                "login.html",
                msg="Username or password is incorrect. Please try again")


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        userName = request.form['username']
        teamName = request.form['teamName']
        emailAddress = request.form['email']
        password = request.form['password']
        insert_user(userName, teamName, emailAddress, password)
        return render_template(
            "login.html",
            msg="Thank you for Registering. Please login with your details")


@app.route("/game")
def startGame():
    moneyNeeds, _ = listNeeds('money_needs')
    customerExpNeeds, _ = listNeeds('customer_exp')
    sustainabilityNeeds, _ = listNeeds('sustainability')
    return render_template("newGame.html",
                           moneyNeeds=moneyNeeds,
                           customerExpNeeds=customerExpNeeds,
                           sustainabilityNeeds=sustainabilityNeeds)


@app.route("/generate-proposition", methods=['POST'])
def generateProposition():

    print("Proposition generated")
    productType = request.form['productType']
    productName = request.form['productName']

    moneyNeeds = request.form.getlist('moneyNeeds')
    customerExpNeeds = request.form.getlist('customerExpNeeds')
    sustainabilityNeeds = request.form.getlist('sustainabilityNeeds')

    generatedProposition = generatePropositionExample(productName, productType,
                                                      moneyNeeds,
                                                      customerExpNeeds,
                                                      sustainabilityNeeds)
    print(generatedProposition)
    return generatedProposition


@app.route("/submit-proposition", methods=['POST'])
def submitProposition():
    print("Proposition submitted")
    city = request.form['city']

    productType = request.form['productType']
    subcount1 = request.form['subcount1']
    subcount2 = request.form['subcount2']
    subcount3 = request.form['subcount3']
    productName = request.form['productName']

    moneyNeeds = request.form.getlist('moneyNeeds')
    customerExpNeeds = request.form.getlist('customerExpNeeds')
    sustainabilityNeeds = request.form.getlist('sustainabilityNeeds')
    proposition = request.form['proposition']

    matchingTopologies, predictedSubscriberTakeOut = evaluateProposition(
        city, productType, proposition, moneyNeeds, customerExpNeeds,
        sustainabilityNeeds)

    return {
        'matchingTopologies': matchingTopologies,
        'predictedSubscriberTakeOut': predictedSubscriberTakeOut,
        'subscriberDiff': predictedSubscriberTakeOut - int(subcount3)
    }


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
