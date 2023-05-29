from django.shortcuts import render, redirect
from .models import Profile, Order
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import OrderForm

sellOrders= []
buyOrders = []

def signin(request):
    orders = Order.objects.all()
    if request.method == 'POST':
        username = request.POST['username']
        psw = request.POST['psw']

        user = authenticate(username= username, password= psw)

        if user is not None:
            login(request, user)
            for order in orders:
                if order.typology == 'sell' and order not in sellOrders and order.active == True:
                    sellOrders.append(order)
                if order.typology == 'buy' and order not in buyOrders and order.active == True:
                    buyOrders.append(order)
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
    username = request.user.username
    profile = Profile.objects.get(user=request.user)
    if request.method =='POST':
        form = OrderForm(request.POST)
        if form.is_valid():            
            order = form.save(commit=False)
            order.profile = profile
            order.save()
            if order.typology == 'sell':
                if order.quantity > profile.btc:
                    order.active = False
                    order.save()
                else:
                    profile.btc -= order.quantity
                    profile.save()
                    sellOrders.append(order)
                    for buyOrder in buyOrders:
                        if buyOrder.quantity == order.quantity and buyOrder.price >= order.price and buyOrder.profile != profile:
                            bProfile = Profile.objects.get(_id=buyOrder.profile._id) 
                            bProfile.btc += order.quantity
                            bProfile.profit -= buyOrder.price
                            profile.profit += buyOrder.price
                            buyOrder.active = False
                            order.active = False
                            bProfile.save()
                            profile.save()
                            buyOrder.save()
                            order.save()
                            buyOrders.remove(buyOrder)
                            sellOrders.remove(order)
                            break
            if order.typology == 'buy':
                buyOrders.append(order)
                for sellOrder in sellOrders:
                    if sellOrder.quantity == order.quantity and sellOrder.price <= order.price and sellOrder.profile != profile:
                        sProfile = Profile.objects.get(_id=sellOrder.profile._id)
                        sProfile.profit += sellOrder.price
                        profile.btc += sellOrder.quantity
                        profile.profit -= sellOrder.price
                        sellOrder.active = False
                        order.active = False
                        sProfile.save()
                        profile.save()
                        sellOrder.save()
                        order.save()
                        sellOrders.remove(sellOrder)
                        buyOrders.remove(order)
                        break            
    else:
        form = OrderForm()
    return render(request, 'app/mainPage.html', {'form': form, 'sellOrders': sellOrders, 'buyOrders': buyOrders, 'profile': profile, 'username': username,})
            