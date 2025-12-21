from django.urls import path
from . import views

urlpatterns = [
    path('', views.sotuv_list, name='sotuv_list'),
    path('<int:id>/', views.sotuv_detail, name='sotuv_detail'),
]
