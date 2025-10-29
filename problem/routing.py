from django.urls import re_path
from . import consumer

ws_urlpatterns = [
    re_path(r'ws/problem/(?P<problem_id>\d+)/(?P<chatspace_uuid>[^/]+)/$', consumer.ProblemConsumer.as_asgi()),
]