from django.shortcuts import render, redirect
from .models import Profile, Order
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import OrderForm
import pymongo

connection = pymongo.MongoClient("mongodb://localhost:27017")
db = connection["btcEx"]

def signin(request):
    orders = Order.objects.all()
    if request.method == 'POST':
        username = request.POST['username']
        psw = request.POST['psw']

        user = authenticate(username= username, password= psw)

        if user is not None:
            login(request, user)
            return redirect('mainPage')
        else:
            pass
    return render(request, 'app/signin.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        psw1 = request.POST['psw1']
        psw2 = request.POST['psw2']
        if psw1 == psw2:
            new_user = User.objects.create_user(username, email, psw1)
            new_user.save()
            new_profile = Profile.objects.create(user=new_user, btc=10.0, profit=0.0)
            new_profile.save()
    return render(request, 'app/signup.html')

def signout(request):
    logout(request)
    return redirect('signin')

def mainPage(request):
    sellOrders = db.app_order.find({"active": True, "typology": "sell"}).sort([("price", pymongo.ASCENDING)])
    buyOrders = db.app_order.find({"active": True, "typology": "buy"}).sort([("price", pymongo.DESCENDING)])
    username = request.user.username
    profile = Profile.objects.get(user=request.user)
    if request.method =='POST':
        form = OrderForm(request.POST)
        if form.is_valid():            
            order = form.save(commit=False)
            order.profile = profile
            order.save()
            if order.typology == 'sell':
                orders = Order.objects.order_by('-price')
                if order.quantity > profile.btc:
                    order.active = False
                    order.save()
                else:
                    profile.btc -= order.quantity
                    profile.save()
                    for buyOrder in orders:
                        if buyOrder.active and buyOrder.typology=='buy' and buyOrder.price >= order.price and buyOrder.profile != profile:
                            bProfile = Profile.objects.get(_id=buyOrder.profile._id) 
                            if buyOrder.quantity >= order.quantity:
                                bProfile.btc += order.quantity
                                bProfile.profit -= (buyOrder.price * order.quantity)
                                profile.profit += (buyOrder.price * order.quantity)
                                buyOrder.quantity -= order.quantity
                                order.active = False
                                if buyOrder.quantity == 0:
                                    buyOrder.active = False 
                            else:
                                bProfile.btc += buyOrder.quantity 
                                bProfile.profit -= (buyOrder.price * buyOrder.quantity)
                                profile.profit += (buyOrder.price * buyOrder.quantity)
                                order.quantity -= buyOrder.quantity
                                buyOrder.active = False 
                            bProfile.save()
                            profile.save()
                            buyOrder.save()
                            order.save()
                            if order.active == False:
                                break
            if order.typology == 'buy':
                orders = Order.objects.order_by('price')
                for sellOrder in orders:
                    if sellOrder.active and sellOrder.typology=='sell' and sellOrder.price <= order.price and sellOrder.profile != profile:
                        sProfile = Profile.objects.get(_id=sellOrder.profile._id)
                        if sellOrder.quantity <= order.quantity:
                            profile.btc += sellOrder.quantity
                            profile.profit -= (sellOrder.price * sellOrder.quantity)
                            sProfile.profit += (sellOrder.price * sellOrder.quantity)
                            order.quantity -= sellOrder.quantity
                            sellOrder.active = False
                            if order.quantity == 0:
                                order.active = False
                        else:
                            profile.btc += order.quantity
                            profile.profit -= (sellOrder.price * order.quantity)
                            sProfile.profit += (sellOrder.price * order.quantity)
                            sellOrder.quantity -= order.quantity
                            order.active = False
                        sProfile.save()
                        profile.save()
                        sellOrder.save()
                        order.save()
                        if order.active == False:
                            break            
    else:
        form = OrderForm()
    return render(request, 'app/mainPage.html', {'form': form, 'sellOrders': sellOrders, 'buyOrders': buyOrders, 'profile': profile, 'username': username,})
            