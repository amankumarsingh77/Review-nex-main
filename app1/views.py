from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import bcrypt
import requests
from pymongo import MongoClient
from . import mongosb_conn
import random
import razorpay
import json
# Create your views here
#@login_required(login_url='login')

users_collection = mongosb_conn.conn()

razorpay_client = razorpay.Client(
auth=("rzp_test_hXpTQaYTljGvc0", "AWuGt1vpsfN5vBWPEMXn7u35"))

def HomePage(request):
    return render (request,'home_main.html')


def signupPage(request):
    username = request.session.get("username", "Guest")
    if username == "Guest":
        if request.method=='POST':
            uname=request.POST.get('username')
            email=request.POST.get('email')
            pass1=request.POST.get('password1')
            pass2=request.POST.get('password2')

            if pass1!=pass2:
                return HttpResponse("Your password and confrom password are not Same!!")
            # else:
            #     my_user=User.objects.create_user(uname,email,pass1)
            #     my_user.save()
                # return redirect('login')


            if users_collection.find_one({"username": uname}):
                return HttpResponse("Username already exists")

        # Hash the password (You should use a secure password hashing library like bcrypt)
            hashed_password = mongosb_conn.hash_password(pass1)

            user_id = int(random.random()*1000000)


        # Create a user document
            user_data = {
                "user_id":user_id,
                "username": uname,
                "password": hashed_password,
                "email":email,
                "products":[],
                "credits":100
            }

        # Insert the user document into the MongoDB collection
            result = users_collection.insert_one(user_data)

            return redirect("/login")
    else:
        return redirect("/dashboard")



    return render (request,'signup.html')

def LoginPage(request):
    username = request.session.get("username", "Guest")
    if username == "Guest":
        if request.method=='POST':
            username=request.POST.get('username')
            pass1=request.POST.get('pass')
            user = users_collection.find_one({"username": username})

        # Verify the password (You should use a password hashing library to compare passwords)
            if user and mongosb_conn.verify_password(pass1, user["password"]):
                request.session['username'] = username
                # return HttpResponse("Login Successful "+request.session.get("username",None))
                return redirect("/dashboard")
            else:
                return HttpResponse("Login failed")
    else:
        return redirect("/dashboard")
        
        
    return render (request,'login.html')
    


def dashboard(request):
    username = request.session.get("username","Guest")
    cost = 10
    # if username != "Guest":
    user = {"username":username}
    
    document = users_collection.find_one(user)

    
    

    if request.method == "POST":
            products = document.get("products", [])
            av_credits = document.get("credits")
            if av_credits > cost:
                print(type(av_credits))
                query = request.POST.get("query")
                for product in products:
                    if product['query']== query:
                        return redirect("/dashboard")
                print("Query",query)
                json_data = {
                    "query":query
                }
                
                url = "http://localhost:8001/get"
                response = requests.post(url,json=json_data)
            
            
            

            # new_search_history = document.get("product", []) + response.json()
                av_credits = av_credits - cost
                users_collection.update_one(
                {"username": username},
                {"$push": {"products": response.json()}},
                )
                users_collection.update_one(
                {"username": username},
                {"$set": {"credits": av_credits}},
                )
            
            return redirect("/dashboard")
    

    
    if document != None:
        products = document.get("products", [])
        
        # json_data_str = {"query":query,"data":json.dumps(products)}
        #     # return render(request,"dashboard.html",{"json_data":products})
        #     return redirect("home")
        # final_json_data=products.update({"username": username})
        
        context={
            "username":username,
            "json_data":products
        }
        
        return render(request,'home.html',context)
    
    return redirect("/login")

def product(request, product_id):
    username = request.session.get("username","Guest")
    print(product_id)
    if username != "Guest":
        user = {"username":username}
        document = users_collection.find_one(user)
        products = document.get("products", [])
        for product in products:
            # print(product['query']== product_id)
            # print(product['query'])
            if product['query']== product_id:
                # print("product"+product['query'],product_id)
                
                # return render(request,"dashboard.html",{"json_data":product})
                return render(request,"product.html",{"json_data":product})
            
        return HttpResponse("Product Not Found")
            

def Profile(request):
    username = request.session.get("username","Guest")
    if username != "Guest":
        user = {"username":username}
        document = users_collection.find_one(user)
        email=document.get("email")
        products = document.get("products", [])
        av_credits= document.get("credits")

        context = {
            "username":username,
            "email":email,
            "no_products":len(products),
            "credits":av_credits
        }
        return render(request,"profile.html",context=context)
    return redirect("login")

@csrf_exempt
def subscribe(request):
    username = request.session.get("username", "Guest")
    if username != "Guest":
        if request.method == 'POST':
            subscription_plan = request.POST.get('subscription_plan')

            if subscription_plan:
                # Map subscription plans to their corresponding details
                subscription_plans = {
                    '100_credits': {'plan_id': 'your_100_credits_plan_id', 'price': 49},
                    '500_credits': {'plan_id': 'your_500_credits_plan_id', 'price': 199},
                    '1000_credits': {'plan_id': 'your_1000_credits_plan_id', 'price': 499},
                }

                plan_details = subscription_plans.get(subscription_plan)

                if plan_details:
                    tot_cost = plan_details['price'] * 100
                    currency = 'INR'
                    request.session['tot_cost'] = tot_cost

                    # Create a Razorpay Order
                    razorpay_order = razorpay_client.order.create(dict(amount=tot_cost,
                                                                       currency=currency,
                                                                       payment_capture='0'))

                    razorpay_order_id = razorpay_order['id']
                    callback_url = '/paymenthandler/'
                    print(tot_cost)
                    context = {
                        'razorpay_order_id': razorpay_order_id,
                        'razorpay_merchant_key': "rzp_test_hXpTQaYTljGvc0",
                        'razorpay_amount': tot_cost,
                        'currency': currency,
                        'callback_url': callback_url,
                    }

                    return render(request, 'index.html', context=context)
    else:
        return redirect("/login")

    return render(request, 'subscribe.html')


@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            tot_cost = int(request.session.get("tot_cost", 0))
            username = request.session.get("username")

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            result = razorpay_client.utility.verify_payment_signature(params_dict)

            if result is not None:
                amount = tot_cost
                print(amount)
                if tot_cost is None:
                    raise SuspiciousOperation("tot_cost not found in session")

                user = users_collection.find_one({'username': username})
                print(username)
                final_credits = 0

                try:
                    if amount == 4900:
                        final_credits = user['credits'] + 100
                    elif amount == 19900:
                        final_credits = user['credits'] + 500
                    elif amount == 49900:
                        final_credits = user['credits'] + 1000


                    users_collection.update_one({'username': username}, {"$set": {"credits": final_credits}})

                    return redirect("profile")
                except Exception as e:
                    return JsonResponse({'message': f'Payment Unsuccessful - {str(e)}'}, status=400)
            else:
                return JsonResponse({'message': 'Payment Unsuccessful - Signature verification failed'}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Error - {str(e)}'}, status=400)
    else:
        return HttpResponseBadRequest()




def LogoutPage(request):
    # logout(request)
    request.session.clear()
    return redirect('login')

def about(request):
    return render(request,"about.html")
