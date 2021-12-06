from flask import Flask, request, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bill.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretkey'
db=SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


#Database for username and password
class RegisterInfo(UserMixin, db.Model):
    u_name = db.Column(db.String(80), primary_key=True, unique=True)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, u_name, password):
        self.u_name = u_name
        self.password = password


#Database for food menu
class Menu(db.Model):
    ItemId = db.Column(db.Integer, primary_key=True, nullable=False)
    half_price = db.Column(db.Float, nullable=False)
    full_price = db.Column(db.Float, nullable=False)

    def __init__(self, ItemId, half_price, full_price):
        self.ItemId = ItemId
        self.half_price = half_price
        self.full_price = full_price


#Database to store transaction's information
class User_TransId_info(db.Model):
    Tid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_name = db.Column(db.String(80), nullable=False)
    tip = db.Column(db.Integer)
    discount = db.Column(db.Float)
    lucky_draw = db.Column(db.String(10))
    amount = db.Column(db.Float)
    persons = db.Column(db.Integer)

    def __init__(self, u_name, tip, discount, lucky_draw, amount, persons):
        self.u_name = u_name
        self.tip = tip
        self.discount = discount
        self.lucky_draw = lucky_draw
        self.amount = amount
        self.persons = persons


#Database to store the final total bill
class Trans_Info(db.Model):
    Tid = db.Column(db.Integer, primary_key=True)
    ItemId = db.Column(db.Integer, nullable=False, primary_key=True)
    PT = db.Column(db.String(10), nullable=False, primary_key=True)
    Qt = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, Tid, ItemId, PT, Qt, price):
        self.Tid = Tid
        self.ItemId = ItemId
        self.PT = PT
        self.Qt = Qt
        self.price = price


@login_manager.user_loader
def load_user(user_id):
    return RegisterInfo.query.get(user_id)


@app.route('/register', methods=['POST'])
def register():
    if(request.method == 'POST'):
        post_data = request.get_json()
        name = post_data['name']
        passwrd = post_data['password']
        check = RegisterInfo.query.filter_by(u_name=name).first()
        if check is not None:
            return "ID already exists."
        else:
            new_user = RegisterInfo(u_name=name, password=passwrd)
            app.logger.warning(new_user)
            db.session.add(new_user)
            db.session.commit()
            return "User added successfully."



@app.route('/login', methods=['POST'])
def login():
    post_data = request.get_json()
    username = post_data['name']
    password = post_data['password']
    check_user = RegisterInfo.query.filter_by(u_name=username).first()
    if check_user is not None:
        if(check_user.password == password):
            RegisterInfo.id = username
            login_user(check_user)
            return "Successful Login"
        else:
            return "Incorrect password."
    else:
        return "User doesn't exist."



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return "Sign out successful"



@app.route('/MenuRead')
@login_required
def menuread():
    menu = Menu.query.all()
    items = {}
    for item in menu:
        temp = {}
        temp["Half"] = item.half_price
        temp["Full"] = item.full_price
        items[item.ItemId] = temp

    return jsonify(items)



@app.route('/writeMenu', methods=['POST'])
@login_required
def writeMenu():
    data = request.get_json()
    id = data['Id']
    phalf = data['phalf']
    pfull = data['pfull']
    check = Menu.query.filter_by(ItemId=id).first()
    if (current_user.u_name == "chef"):
        if(check is not None):
            check.half_price = phalf
            check.full_price = pfull
            db.session.commit()
            return "Menu is updated."
        else:
            menu = Menu(ItemId=id, half_price=phalf, full_price=pfull)
            db.session.add(menu)
            db.session.commit()
            return "New item is added."
    else:
        return "Only chef is allowed to change the menu."



@app.route('/insertbill', methods=['POST'])
@login_required
def insertbill():
    post_data = request.get_json()
    lst = post_data["impinfo"]
    tb_data = User_TransId_info(
        u_name=current_user.u_name,
        tip=lst["tip"],
        discount=lst["disc_inc"],
        lucky_draw=lst["luckdraw"],
        amount=lst["total"],
        persons=lst["people"])
    db.session.add(tb_data)
    db.session.commit()

    for id in post_data:
        if id != "impinfo":
            tb_data = Trans_Info(
                Tid=tb_data.Tid,
                ItemId=post_data[id]["id"],
                PT=post_data[id]["type"],
                Qt=post_data[id]["quant"],
                price=post_data[id]["price"])
            db.session.add(tb_data)
            db.session.commit()
        else:
            pass
    return "Bill inserted into the database."



@app.route('/getTransactionsId')
@login_required
def getTransactionsId():
    check = User_TransId_info.query.filter_by(u_name=current_user.u_name)
    if check is not None:
        count = 0
        data = {}
        for info in check:
            data[count] = info.Tid
            count = count + 1
        temp = len(data)
        if (temp<1):
            return {"status": "No available transactions to show."}
        return data
    else:
        return {"status": "No available transactions to show."}



@app.route('/getTrans', methods=['POST'])
@login_required
def getTrans():
    req = request.get_json()
    tid = req['tid']
    data = {}
    check = Trans_Info.query.filter_by(Tid=tid)
    if check is not None:
        count = 0
        for row in check:
            tmp = {}
            tmp["itemid"] = row.ItemId
            tmp["platetype"] = row.PT
            tmp["qty"] = row.Qt
            tmp["prc"] = row.price
            count = count + 1
            data[str(count)] = tmp

        additional_data = User_TransId_info.query.filter_by(u_name=current_user.u_name, Tid=tid).first()
        if additional_data is not None:
            data["tip"] = additional_data.tip
            data["discount"] = additional_data.discount
            data["lucky_draw"] = additional_data.lucky_draw
            data["amount"] = additional_data.amount
            data["persons"] = additional_data.persons
            return data
        else:
            return {"status": "Error: No such transaction ID"}
    else:
        return {"status": "Invalid transaction ID"}



if __name__ == '__main__':
    db.create_all()
    app.run(port=8000,debug=True)
