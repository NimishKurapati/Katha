from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('novel/<int:novel_id>/', views.read_novel, name='read_novel'),
    path('novel/<int:novel_id>/chapter/<int:chapter_num>/',
         views.read_novel, name='read_chapter'),
    path('novel/<int:novel_id>/rate/', views.rate_novel, name='rate_novel'),
    path('novel/<int:novel_id>/wishlist/',
         views.toggle_wishlist, name='toggle_wishlist'),

    # Reader Sections
    path('my-novels/', views.my_novels, name='my_novels'),
    path('wishlist/', views.wishlist_view, name='wishlist'),

    # Writer Sections
    path('writer/', views.writer_dashboard, name='writer_dashboard'),
    path('writer/novel/<int:novel_id>/add-chapter/',
         views.add_chapter, name='add_chapter'),

    # Admin Approval Sections
    path('admin-panel/requests/', views.manage_writer_requests,
         name='manage_writer_requests'),
    path('admin-panel/requests/<int:req_id>/<str:action>/',
         views.process_writer_request, name='process_writer_request'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
]
