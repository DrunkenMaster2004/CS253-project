from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import cart_view
urlpatterns = [
    path('', views.home, name='marketplace_home'),
    

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='marketplace/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='marketplace/logout.html',http_method_names=['post', 'get']), name='logout'),
    path('create-profile/', views.create_profile, name='create_profile'),
    

    path('profile/', views.profile, name='profile'),
    

    path('item/add/', views.add_item, name='add_item'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item/<int:item_id>/edit/', views.edit_item, name='edit_item'),
    path('item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('items/', views.items_list, name='items_list'),
    
    path('wishlist/toggle/<int:item_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.my_wishlist, name='my_wishlist'),
    
    path('chat/start/item/<int:item_id>/', views.start_chat, name='start_chat_item'),
    path('chat/start/profile/<int:profile_id>/', views.start_chat, name='start_chat_profile'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chats/', views.chat_list, name='chat_list'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    #path('cart/update/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
   
    path('cart/checkout/', views.checkout, name='checkout'),

    
    

]