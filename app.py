from flask import Flask, render_template, request, session, redirect, send_from_directory
from scripts.utils import listNeeds, generatePropositionExample, evaluateProposition, get_random_bank
from scripts.db_util import insert_user, fetch_user, UserNotFoundError, savePropositionResults, PropositionDatabase
import datetime
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'HrRdpsuJjIiOiPVdpqUk'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=60)
app.config['LIBRARY_PATH'] = os.path.abspath(
    os.path.join(os.getcwd(), 'library'))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/leaderboard")
def leaderboard():
    db = PropositionDatabase()
    propositions = db.fetch_propositions()
    return render_template("leaderboard.html", propositions=propositions)

@app.route("/budget")
def budget():
    return render_template("budget.html")

@app.route("/regulation")
def regulation():
    return render_template("regulation.html")

    

@app.route("/banks/<bankName>")
def banks(bankName):
    bankPath = os.path.abspath(os.path.join(os.getcwd(), 'library', 'banks'))
    bankFullName = request.view_args['bankName']+"_Bank.pdf"
    return send_from_directory(bankPath, bankFullName)


@app.route("/video")
def video():
    return render_template("video.html")

@app.route("/report")
def report():
    propsitionId = request.args.get('propsitionId')
    reportDirPath = os.path.abspath(os.path.join(os.getcwd(), 'reports'))    
    return send_from_directory(reportDirPath, 'Proposition_{}.csv'.format(propsitionId))


@app.route("/topologies")
def topologies():
    return send_from_directory(app.config['LIBRARY_PATH'], 'topologies.csv')


@app.route("/demographics")
def demographics():
    return send_from_directory(app.config['LIBRARY_PATH'], 'demographics.csv')


@app.route("/logout")
def logout():
    session.pop('userId', None)
    session.pop('userName', None)
    session.pop('teamName', None)
    session.pop('emailAddress', None)
    session.pop('bank', None)
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
        session.pop('userId', None)
        session.pop('userName', None)
        session.pop('teamName', None)
        session.pop('emailAddress', None)
        session.pop('bank', None)
        return render_template('login.html')
    else:
        userName = request.form['username']
        password = request.form['password']
        try:
            user = fetch_user(userName, password)
            session['userId'] = user['user_id']
            session['userName'] = user['user_name']
            session['teamName'] = user['team_name']
            session['emailAddress'] = user['email_address']
            session['bank'] = user['bank']
            return redirect('/')

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
        randomBank = get_random_bank()
        insert_user(userName, teamName, emailAddress, password, randomBank)
        return render_template(
            "login.html",
            msg="Thank you for Registering. Please login with your details")


@app.route("/game")
def startGame():
    if 'userName' not in session:
        return redirect('/login')
    
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
    if 'userId' not in session:
        return {}
    
    city = request.form['city']

    productType = request.form['productType']
    subcount1 = request.form['subcount1']
    subcount2 = request.form['subcount2']
    subcount3 = request.form['subcount3']
    productName = request.form['productName']
    revenue = request.form['revenue']

    moneyNeeds = request.form.getlist('moneyNeeds')
    customerExpNeeds = request.form.getlist('customerExpNeeds')
    sustainabilityNeeds = request.form.getlist('sustainabilityNeeds')
    proposition = request.form['proposition']

    matchingTopologies, predictedSubscriberTakeOut = evaluateProposition(
        city, productType, proposition, moneyNeeds, customerExpNeeds,
        sustainabilityNeeds)

    #print(session['userId'], session['bank'], city, productType, subcount1, subcount2, subcount3, productName, revenue, ",".join(moneyNeeds), ",".join(customerExpNeeds), ",".join(sustainabilityNeeds), matchingTopologies, predictedSubscriberTakeOut)
    propositionId = savePropositionResults(session['userId'], session['bank'], city, productType, subcount1, subcount2, subcount3, productName, revenue, ",".join(moneyNeeds), ",".join(customerExpNeeds), ",".join(sustainabilityNeeds), ",".join(matchingTopologies), predictedSubscriberTakeOut)


    return {
        'matchingTopologies': matchingTopologies,
        'predictedSubscriberTakeOut': predictedSubscriberTakeOut,
        'subscriberDiff': predictedSubscriberTakeOut - int(subcount3),
        'revenue': int(revenue) * int(predictedSubscriberTakeOut),
        'propositionId': propositionId
    }


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
