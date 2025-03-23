from flask import Flask, render_template, request, session, redirect, send_from_directory
from scripts.utils import listNeeds, generatePropositionExample, evaluateProposition, get_random_bank
from scripts.db_util import *
import datetime
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'HrRdpsuJjIiOiPVdpqUk'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=60)
app.config['LIBRARY_PATH'] = os.path.abspath(
    os.path.join(os.getcwd(), 'library'))

regulation_dict = {'reg1': 'How does the firm monitor and ensure that its products and services genuinely meet the needs of its target consumers?',
                   'reg2': 'What governance structures, like Board-level oversight, are in place to review and approve Consumer Duty-related assessments annually?',
                   'reg3': 'Are product and service communications clear, fair, and not misleading?',
                   'reg4': 'Does the firm actively monitor, respond to, and learn from complaints?'}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/review_budget" , methods=['POST', 'GET'])
def review_budget():
    budgets = view_active_budgets()

    return render_template("review_budget.html", budgets=budgets)

@app.route("/review_regulations")
def review_regulation():
    regulations = view_active_regulations()
    return render_template("review_regulations.html", regulations=regulations, mapping=regulation_dict)

@app.route("/manage_revenue", methods=['POST', 'GET'])
def manage_revenue():
    if request.method == 'GET':
        return render_template("manage_revenue.html")
    else:
        product = request.form['product']
        revenue = request.form['revenue']
        invalidate_revenue(product)
        save_revenue(product, revenue)
        return render_template("manage_revenue.html",
                               msg="Your Revenue details have been saved")


@app.route("/manage_penalties", methods=['POST', 'GET'])
def manage_penalties():
    if request.method == 'GET':
        return render_template("manage_penalties.html")
    else:
        culture = request.form['Culture']
        tornado = request.form['Tornado']
        fortune = request.form['Fortune']

        invalidate_penalties()
        save_penalty('Culture', culture)
        save_penalty('Tornado', tornado)
        save_penalty('Fortune', fortune)
        return render_template("manage_penalties.html",
                               msg="Your Penalties details have been saved")


@app.route("/leaderboard")
def leaderboard():
    db = PropositionDatabase()
    propositions = db.fetch_propositions()
    return render_template("leaderboard.html", propositions=propositions)


@app.route("/budget", methods=['POST', 'GET'])
def budget():
    if request.method == 'GET':
        return render_template("budget.html")
    else:
        csBudget = request.form['csBudget']
        itBudget = request.form['itBudget']
        marketingBudget = request.form['marketingBudget']
        salesBudget = request.form['salesBudget']
        opsBudget = request.form['opsBudget']
        bank = session['bank']
        invalidate_budget(bank)
        save_budget(bank, csBudget, itBudget, marketingBudget, salesBudget,
                    opsBudget)
        return render_template("budget.html",
                               msg="Your budget details have been saved")


@app.route("/regulation", methods=['POST', 'GET'])
def regulation():
    if request.method == 'GET':
        return render_template("regulation.html")
    else:
        reg1 = request.form['reg1']
        reg2 = request.form['reg2']
        reg3 = request.form['reg3']
        reg4 = request.form['reg4']
        bank = session['bank']
        invalidate_regulation(bank)
        save_regulations(bank, reg1, reg2, reg3, reg4)
        return render_template("regulation.html",
                               msg="Your regulation details have been saved")
    




@app.route("/banks/<bankName>")
def banks(bankName):
    bankPath = os.path.abspath(os.path.join(os.getcwd(), 'library', 'banks'))
    bankFullName = request.view_args['bankName'] + "_Bank.pdf"
    return send_from_directory(bankPath, bankFullName)


@app.route("/video")
def video():
    return render_template("video.html")


@app.route("/report")
def report():
    propsitionId = request.args.get('propsitionId')
    reportDirPath = os.path.abspath(os.path.join(os.getcwd(), 'reports'))
    return send_from_directory(reportDirPath,
                               'Proposition_{}.csv'.format(propsitionId))


@app.route("/topologies")
def topologies():
    return send_from_directory(app.config['LIBRARY_PATH'], 'topologies.csv')


@app.route("/demographics")
def demographics():
    return send_from_directory(app.config['LIBRARY_PATH'], 'demographics.csv')

@app.route("/consumer_duty")
def consumer_duty():
    return send_from_directory(app.config['LIBRARY_PATH'], 'regulation/Consumer_Duty_brochure.pdf')


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
            session['emailAddress'] = user['email_address']
            session['bank'] = user['bank']
            return redirect('/')

        except UserNotFoundError:
            return render_template(
                "login.html",
                msg="Username or password is incorrect. Please try again")

@app.route("/login_admin", methods=['POST', 'GET'])
def login_admin():
    if request.method == 'GET':
        session.pop('userId', None)
        session.pop('userName', None)
        session.pop('teamName', None)
        session.pop('emailAddress', None)
        session.pop('bank', None)
        return render_template('login_admin.html')
    else:
        userName = request.form['username']
        password = request.form['password']
        try:
            user = fetch_user(userName, password)
            session['userId'] = user['user_id']
            session['userName'] = user['user_name']
            session['emailAddress'] = user['email_address']
            return redirect('/admin')

        except UserNotFoundError:
            return render_template(
                "login_admin.html",
                msg="Username or password is incorrect. Please try again")




@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        userName = request.form['username']
        emailAddress = request.form['email']
        password = request.form['password']
        randomBank = get_random_bank()
        insert_user(userName, emailAddress, password, randomBank)
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
    print("Proposition submitted2")
    if 'userId' not in session:
        return {}

    city = request.form['city']

    productType = request.form['productType']
    subcount1 = request.form['subcount1']
    subcount2 = request.form['subcount2']
    subcount3 = request.form['subcount3']
    productName = request.form['productName']
    revenue = 1000

    print("hello2")
    moneyNeeds = request.form.getlist('moneyNeeds')
    customerExpNeeds = request.form.getlist('customerExpNeeds')
    sustainabilityNeeds = request.form.getlist('sustainabilityNeeds')
    proposition = request.form['proposition']
    print("hello")

    matchingTopologies, predictedSubscriberTakeOut = evaluateProposition(
        city, productType, proposition, moneyNeeds, customerExpNeeds,
        sustainabilityNeeds)

    #print(session['userId'], session['bank'], city, productType, subcount1, subcount2, subcount3, productName, revenue, ",".join(moneyNeeds), ",".join(customerExpNeeds), ",".join(sustainabilityNeeds), matchingTopologies, predictedSubscriberTakeOut)
    propositionId = savePropositionResults(
        session['userId'], session['bank'], city, productType, subcount1,
        subcount2, subcount3, productName, revenue, ",".join(moneyNeeds),
        ",".join(customerExpNeeds), ",".join(sustainabilityNeeds),
        ",".join(matchingTopologies), predictedSubscriberTakeOut)
    
    return {
        'matchingTopologies': matchingTopologies,
        'predictedSubscriberTakeOut': predictedSubscriberTakeOut,
        'subscriberDiff': predictedSubscriberTakeOut - int(subcount3),
        'propositionId': propositionId
    }


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
