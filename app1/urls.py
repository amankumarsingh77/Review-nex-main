from django.urls import path
from . import views
urlpatterns = [
    path('',views.HomePage,name='home'),
    path('login/',views.LoginPage,name='login'),
     path('signup/',views.signupPage,name='signup'),
      path('about/',views.about,name='about'),
      path('dashboard/',views.dashboard, name="home"),
      path('product/<str:product_id>/',views.product, name="product"),
      path('logout/',views.LogoutPage, name="logout"),
      path('purchase/',views.subscribe, name="subscribe"),
      path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
      path('profile/',views.Profile, name="profile")
      
]
