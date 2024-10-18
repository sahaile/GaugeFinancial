from django.urls import path
from . import views

urlpatterns = [
    path('',views.homepage,name=""),
    path('register/',views.register,name="register"),
    path('my-login/',views.my_login,name="my-login"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('user-logout/',views.user_logout,name="user-logout"),
    path('new-bankstatement/',views.new_bankstatement,name="new-bankstatement"),
    path('bankstatements/',views.bankstatements,name="bankstatements"),
    path('view-bankstatement/<int:pk>/',views.view_bankstatement,name="view-bankstatement"),
    path('delete-bankstatement/<int:pk>/',views.delete_bankstatement,name="delete-bankstatement"),
    path('analyze-bankstatement/<int:pk>/',views.analyze_bankstatement,name="analyze-bankstatement"),
    path('profile',views.profile,name="profile"),
    path('edit-profile',views.edit_profile,name="edit-profile"),
    path('edit-password',views.edit_password,name="edit-password"),
    path('delete-profile',views.delete_profile,name="delete-profile"),
]
