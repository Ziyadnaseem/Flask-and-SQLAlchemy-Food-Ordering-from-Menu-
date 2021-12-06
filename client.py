# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 15:05:57 2021

@author: ziyad
"""

import random
import json
import requests


def win():
    """
    Prints the following pattern on winning:
        
    **** ****
    |  | |  |
    |  | |  |
    |  | |  |
    **** ****
        {}
      ______  
      
    """
    print("\n")
    print(" ****          ****")
    print("|    |        |    |")
    print("|    |        |    |")
    print("|    |        |    |")
    print(" ****          ****\n")
    print("         {}     ")
    print("   ______________   ")
    
    
def lose():
    """
    Prints the following pattern on not winning:
        
     ****
    *    *
    *    *
    *    *
    *    *
     ****
     
    """
    print("\n")
    print(" **** ")
    print("*    *")
    print("*    *")
    print("*    *")
    print("*    *")
    print(" **** ")


username = ""
ses = requests.Session()
info = []

def zero_menu():
    '''Checks if database has zero entries'''
    response = ses.get('http://localhost:8000/MenuRead')
    response = json.loads(response.text)
    temp = []
    for line in response:
        item = (line)
        full = response[line]['Full']
        half = response[line]['Half']
        temp_list = [item, half, full]
        temp.append(temp_list)
    return temp

def menu():
    '''Prints the food menu from database'''
    print("\nItem ID" + "\t\t" + "Half" + "\t\t" + "Full")
    response = ses.get('http://localhost:8000/MenuRead')
    response = json.loads(response.text)
    temp = []
    for line in response:
        item = (line)
        full = response[line]['Full']
        half = response[line]['Half']
        temp_list = [item, half, full]
        print((item), "\t\t", (half), "\t\t", (full))
        temp.append(temp_list)
    return temp


def do_signup():
    '''Signup'''
    uname = input("Username: ")
    password = input("Password: ")
    cred = {"name": uname, "password": password}
    response = ses.post('http://localhost:8000/register', json=cred).content
    print(response.decode("utf-8"))


def do_login():
    '''Login'''
    uname = input("Username: ")
    password = input("Password: ")
    cred = {"name": uname, "password": password}
    response = ses.post('http://localhost:8000/login', json=cred).content
    print(response.decode("utf-8"))
    if ("Success" in response.decode("utf-8")):
        global username
        username = uname
        return True
    return False


loggedIn = False

while True:
    while(not loggedIn):
        print("\n1. Signup")
        print("2. Login")
        print("3. Exit")
        task = int(input("\nEnter your choice: "))
        if(task == 1):
            do_signup()
        elif(task == 2):
            loggedIn = do_login()
        elif(task == 3):
            exit(0)
        else:
            print("Invalid input.")
            continue

    print("\n1. Order food items")
    print("2. Previous bill statements")
    if(username == "chef"):
        print("3. Add items to the menu")
        print("4. Logout\n")
    else:
        print("3. Logout\n")

    print("Choose an option: ",end="")
    option = int(input())
    if option == 1:
        order = []
        info = zero_menu()
        if(len(info)<=0):
            print("\nThere are no items in the menu currently.\n")
            continue
        while True:
            info = menu()
            ans=input("Would you like to order an item? (Y/N)\n")
            if ans.lower() == "y":
                flag = False
                item_id=int(input("Enter Item ID: "))
                portion=int(input("Select your portion:\n1.Half  2.Full\n"))
                quantity=int(input("Enter the quantity: "))
               
                temp=[]
                temp.append(item_id)
                temp.append(portion)
                temp.append(quantity)

                total_cost=0
                for i in info:
                    if int(i[0]) == item_id:
                        if portion == 1:
                            item_cost = (i[1]) * quantity
                        else:
                            item_cost = (i[2]) * quantity
                        temp.append(item_cost)
                        break
                order.append(temp)
                
                for itr in order:
                    for k in info:
                        if int(itr[0])==int(k[0]):
                            if int(itr[1])==1:
                                total_cost=total_cost+int(itr[2])*int(k[1])
                            else:
                                total_cost=total_cost+int(itr[2])*int(k[2])
                            break
            else:
                break
            
        for i in range(len(order)-1):
            for j in range(i+1,len(order)):
                if order[i][0]==order[j][0]:
                    if order[i][1]==order[j][1]:
                        order[i][2]+=order[j][2]
                        order[i][3]+=order[j][3]
                        order.pop(j)
                        j=j-1
                        i=i-1
                        
        if(len(order)>0):
            tip=int(input("How much tip you wish to give?\n1.0.  2.10%.  3.20%.\n"))
            if tip==1:
                print("\nTotal Amount:",round(total_cost*1.0,2))
            elif tip==2:
                total_cost=total_cost*1.1
                print("\nTotal Amount:",round(total_cost,2))
            else:
                total_cost=total_cost*1.2
                print("\nTotal Amount:",round(total_cost,2))
            
            n=int(input("Into how many people would you split the bill?\n"))
            print("\nContribution per person =",round(total_cost/n,2))
    
            ans2=input("Would you like to try our lucky draw? (Y/N)\n")
            discount=0
            if ans2.lower()=="y":
                val=random.randint(1,100)
                
                if 1<= val <=5:
                    win()
                    print("\nCONGRATS! You won a 50% discount.\n")
                    discount=0-total_cost*0.5
                    final_cost=total_cost*0.5
                    print("Discount/Increase:",round(discount,2))
                    
                elif 6<= val <=15:
                    win()
                    print("\nCONGRATS! You won a 25% discount.\n")
                    discount=0-total_cost*0.25
                    final_cost=total_cost*0.75
                    print("Discount/Increase:",round(discount,2))
            
                elif 16<= val <=30:
                    win()
                    print("\nCONGRATS! You won a 10% discount.\n")
                    discount=0-total_cost*0.10
                    final_cost=total_cost*0.90
                    print("Discount/Increase:",round(discount,2))        
                    
                elif 31<= val <=50:
                    lose()
                    print("\nNo discount. Better luck next time.\n")
                    discount=0
                    final_cost=total_cost
                    print("Discount/Increase:",round(discount,2))
                    
                else:
                    lose()
                    print("\nYou lose. There will be a 20% increase on your bill.\n")
                    discount=total_cost*0.20
                    final_cost=total_cost*1.20
                    print("Discount/Increase:",round(discount,2))
                    
            else:
                final_cost=total_cost
                
            print("\n\nFinal Bill\n")
            total_cost=0
            for itr in order:
                for k in info:
                    if int(itr[0])==int(k[0]):
                        if int(itr[1])==1:
                            item_cost=int(itr[2])*int(k[1])
                            total_cost=total_cost+item_cost
                            print(f"Item {itr[0]}[Half][{itr[2]}]: {round(item_cost,2)}")
                        else:
                            item_cost=int(itr[2])*int(k[2])
                            total_cost=total_cost+item_cost
                            print(f"Item {itr[0]}[Full][{itr[2]}]: {round(item_cost,2)}")
                        break
                    
            print("Total:",round(total_cost,2))
            
            if tip==1:
                print("Tip Percentage: 0")
            elif tip==2:
                print("Tip Percentage: 10")
            else:
                print("Tip Percentage: 20")
            
            if discount>=0:
                print("Discount/Increase:",round(discount,2))
            else:
                print("Discount/Increase:",round(discount,2))
            
            print("Final Total:",round(final_cost,2))
            print("Contribution per person:",round(final_cost/n,2))    
           
            bill_data = {}
            count = 0
            for item in order:
                count = count + 1
                temp_data = {}
                #cost = cost + item[2]
                temp_data["id"] = item[0]
                temp_data["quant"] = item[2]
                temp_data["price"] = item[3]
                if(item[1]==1):
                    temp_data["type"]="Half"
                else:
                    temp_data["type"]="Full"
                bill_data[count] = temp_data
    
            # print(bill_data)
            t_value = 0
            if(tip == 2):
                t_value = 10
            elif(tip == 3):
                t_value = 20
            else:
                t_value = 0
            dict = {}
            dict["tip"] = t_value
            dict["disc_inc"] = discount
            dict["total"] = final_cost
            if(ans2.lower()=="y"):
                dict["luckdraw"] = "Yes"
            else:
                dict["luckdraw"] = "No"
            dict["people"] = n
    
            bill_data["impinfo"] = dict
    
            response_server=ses.post('http://localhost:8000/insertbill',json=bill_data).content

    elif option == 2:
        response = ses.get('http://localhost:8000/getTransactionsId').content
        print("\nTransaction History:\n")
        res = json.loads(response.decode('utf-8'))
        if "status" in res:
            print(res["status"])
            continue
        for t_id in res:
            print("T.No.: ", res[t_id])
        ip = input("\nEnter Transaction number: ")
        print()
        data = {"tid": ip}
        response = ses.post("http://localhost:8000/getTrans",json=data).content
        res = json.loads(response.decode('utf-8'))
        if "status" in res.keys():
            print(res["status"])
            continue
        print("ItemId", "\t\t", "PT", "\t", "Qty", "\t" + "Price")
        for bill in res:
            if bill.isnumeric():
                print(res[bill]["itemid"], "\t\t",res[bill]["platetype"], "\t",
                    res[bill]["qty"], "\t",res[bill]["prc"])
        print()
        print("Tip: ", res["tip"])
        print("Participated in Lucky Draw: ", res["lucky_draw"])
        print("Discount/Increase: ", "%.2f" % res["discount"])
        print("Total Amount: ", "%.2f" % res["amount"])
        print("Total persons who split the bill: ", res["persons"])

    elif username == "chef" and option == 3:
        info = menu()
        updated_menu = {}
        id = input("\nEnter Item Id: ")
        half_prc = input("Enter Price for Half Plate: ")
        full_prc = input("Enter Price for Full Plate: ")
        updated_menu['Id'] = id
        updated_menu['phalf'] = half_prc
        updated_menu['pfull'] = full_prc
        response = ses.post('http://localhost:8000/writeMenu',json=updated_menu).content
        print(response.decode('utf-8'))

    elif username != "chef" and option == 3 or username == "chef" and option == 4:
        response = ses.get('http://localhost:8000/logout').content
        print()
        print(response.decode("utf-8"))
        loggedIn = False
        username = ""
    else:
        print("\nInvalid Input")
