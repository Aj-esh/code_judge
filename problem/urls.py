from django.urls import path
from . import views

urlpatterns = [
    # This path renders the HTML page for the user to see.
    path('<int:pid>/', views.p_detail, name='problem_detail'),
    
    # This path is ONLY for the background JavaScript calls.
    path('api/<int:pid>/', views.ProblemView.as_view(), name='problem_api'),
]