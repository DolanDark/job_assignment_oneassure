import datetime
from flask import Blueprint, render_template, request, flash, session, redirect, url_for, current_app
import pandas as pd
from utils_blueprint import ClusterData

data = Blueprint("data", __name__)
print("data_blueprint executed")

def calculate_age(date_str):
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.date.today()
    return today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))

print('PROCO', current_app.config["COLLECTION_NAME"])

@data.route("/", methods=["GET","POST"])
@data.route("/home", methods=["GET","POST"])
def home_page():
    return render_template("home.html")

@data.route("/info")
def info():
    return render_template("info.html")

@data.route("/result")
def result():

    amount_payable = session['amountPayable']
    user_data = session['userData']

    # print("amount_payable", amount_payable)
    # print("userData", user_data)

    return render_template("result.html", items = user_data, total = amount_payable)

@data.route("/calculate_premium", methods=["GET","POST"])
def calculate_premium():

    sum_insured = request.json.get("sumInsured")
    tenure = request.json.get("tenure")
    city_tier = request.json.get("cityTier")
    member_list = request.json.get("memberList")

    if [x for x in (sum_insured, tenure, city_tier, member_list) if x in [None, ""]]:
        print("Primary Data Missing")
        flash('All fields not entered', category='error')

        return redirect(url_for('data.home_page'))
    
    for member in member_list:
        if [x for x in (member["name"], member["type"], member["age"]) if x in [None, ""]]:
            print("Secondary Data Missing")
            flash('All fields not entered for Members', category='error')
            return render_template("home.html")
    
    customer_age_range = [calculate_age(X["age"]) for X in member_list]
    customer_names = [X["name"] for X in member_list]

    data_frame = ClusterData().get_health_sheet()


    premium_data = []
    for customer_age,customer_name in zip(customer_age_range, customer_names):
        filtered_df = data_frame.loc[(data_frame['SumInsured'] == int(sum_insured)) 
                                    & (data_frame['Tenure'] == int(tenure))
                                    & (data_frame['TierID'] == int(city_tier))
                                    & (data_frame['Age'] == customer_age)]
        
        if len(filtered_df.index) != 1:
            print("Got duplicate premium data")
            raise Exception ("Duplicate premium data")
        
        user_data = filtered_df.to_dict('records')[0]
        user_data.update({"Name": customer_name})
        premium_data.append({ k:(v.strip() if k in ["ProductCode", "PlanCode", "PlanName"] else v) for k,v in user_data.items() })

    # print(premium_data)
    # print(len(premium_data))

    temp_list = []
    for customer in premium_data:
        policy_dict = {}
        policy_dict["name"] = customer["Name"]

        if customer["Age"] < 18:
            policy_dict["type"] = "Child"
        else:
            policy_dict["type"] = "Individual"

        if len(premium_data) > 1 and customer["Age"] != max([ X["Age"] for X in premium_data ] ):
            policy_dict["floaterDiscount"] = "50%"
            policy_dict["discountedRate"] = float(customer["Rate"]) * 0.5
        else:
            policy_dict["floaterDiscount"] = "0%"
            policy_dict["discountedRate"] = customer["Rate"]

        policy_dict["baseRate"] = customer["Rate"]
        policy_dict["total"] = policy_dict["discountedRate"]
        temp_list.append(policy_dict)

    amount_payable = sum([X["total"] for X in temp_list])

    # print("TOTAL AMT PAYABLE - ", amount_payable)
    # print("TEMPLATE DATA", temp_list)

    session['amountPayable'] = amount_payable
    session['userData'] = temp_list

    return redirect(url_for('data.result'))

