from django.urls import path
from . import views

urlpatterns = [
    path('dashindex/', views.dashindex, name='dashindex'),
    path('allmembers/', views.allmembers_page, name='allmembers'),
    path('api/manage-members/', views.manage_members_api, name='manage_members_api'),
    path('dashboard/toggle-status/<int:member_id>/', views.toggle_member_status, name='toggle_member_status'),
    path('allmembers/', views.all_members_page, name='all_members_page'),
    path('privatemessages/', views.privatemessages, name='privatemessages'),
    path('groupchats/', views.groupchats, name='groupchats'),
    path('darkmessages/', views.darkmessages, name='darkmessages'),
    path('reportemessages/', views.reportemessages, name='reportemessages'),
    path('privacydash/', views.privacydash, name='privacydash'),
    path('manageposts/', views.manageposts, name='manageposts'),
    path('useractivity/', views.useractivity, name='useractivity'),
    #path('prvtchat/', views.users_with_chat_data, name='prvtchat'),
    path('chatprivate/', views.private_messages_admin, name='chatprvate'),
    path("api/conversation/", views.conversation_view, name="conversation_view"),
    path("api/conversation/export/", views.export_conversation_csv, name="export_conversation_csv"),
    #path("api/toggle_ban_user/", views.toggle_ban_user, name="toggle_ban_user"),
    path("toggle-block-conversation/", views.toggle_block_conversation, name="toggle_block_conversation"),
    #path("contact-admin/", views.banned_account_page_contact_admin, name='contact_admin'), #banned_account_page_contact_admin

]
