# urls.py
from django.urls import path
from users.views import new_post_view, home_page, index_page, login_page, logout_page, signup_view, posts_page
from . import views

urlpatterns = [
    
    path('', index_page, name="index"),
    path('login/', login_page, name="login"),
    path('logout/', logout_page, name="logout"),
    path('signup/', signup_view, name="signup"),
    path('posts/', posts_page, name="posts"),
    path('chatter/', home_page, name="home"),  # ✅ Updated this line
    path('posts/new/', new_post_view, name='new_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),
    path('elyse/', views.go_to_chat_with_user5, name='go-to-user5-chat'),
    
    # Add these to your urlpatterns
    path('souls/', views.souls_tunnel, name='souls-tunnel'),
    path('tunnel/', views.go_to_souls, name='go-to-souls'),
    path('add-memory/', views.add_memory, name='add-memory'),
    
    #banned accounts
    path('unbann_accounts/', views.unbann_accounts, name='unbann_accounts'),
    path('account_banned/', views.account_banned, name='account_banned'),
    path('ban/<int:user_id>/', views.ban_user, name='ban_user'),
    path('unban/<int:user_id>/', views.unban_user, name='unban_user'),
    path("ban-user/<int:member_id>/", views.ban_user, name="ban_user"),
    path("unban-user/<int:member_id>/", views.unban_user, name="unban_user"),
    path('banned/', views.banned_page, name='banned_page'),
    path('thank-you/', views.thank_you, name='thank_you'),
]