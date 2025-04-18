from django.urls import path
from . import views
from marketplace.views import start_chat  # Import chat from Marketplace

urlpatterns = [
    path('', views.home, name='lostnfound_home'),
    
    # Lost Item URLs
    path('lost/report/', views.report_lost_item, name='report_lost_item'),
    path('lost/<int:item_id>/', views.lost_item_detail, name='lost_item_detail'),
    path('lost/my-items/<int:item_id>/edit/', views.edit_lost_item, name='edit_lost_item'),
    path('lost/my-items/<int:item_id>/delete/', views.close_lost_item, name='close_lost_item'),
    path('lost/<int:item_id>/close/', views.close_lost_item, name='close_lost_item'),
    path('lost/items/', views.lost_items_list, name='lost_items_list'),
    path('lost/my-items/', views.my_lost_items, name='my_lost_items'),
    
    # Found Item URLs
    path('found/report/', views.report_found_item, name='report_found_item'),
    path('found/<int:item_id>/', views.found_item_detail, name='found_item_detail'),
    path('found/my-items/<int:item_id>/edit/', views.edit_found_item, name='edit_found_item'),
    path('found/my-items/<int:item_id>/delete/', views.close_found_item, name='close_found_item'),
    path('found/<int:item_id>/close/', views.close_found_item, name='close_found_item'),
    path('found/items/', views.found_items_list, name='found_items_list'),
    path('found/my-items/', views.my_found_items, name='my_found_items'),
    
    # Claiming & Matching URLs
    path('found/<int:item_id>/claim/', views.claim_found_item, name='claim_found_item'),
    path('claim/<int:claim_id>/review/', views.review_claim, name='review_claim'),
    path('match/<int:match_id>/confirm/', views.confirm_match, name='confirm_match'),
    path('claims/my-claims/', views.my_claims, name='my_claims'),

    # Chat URL
    path('chat/<int:item_id>/', views.start_chat_lostfound, name='start_chat_lostfound'),
    
    # Notification URLs
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/unread-notifications-count/', views.unread_notifications_count, name='unread_notifications_count'),
    path('claims/to-review/', views.my_claims_to_review, name='my_claims_to_review'),

    

]
