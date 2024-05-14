from django.urls import path, include
from rest_framework import routers
from .views import BookView, MemberView, TransactionView

app_name = "lms_app"

router = routers.DefaultRouter()
router.register(r"books", BookView,)
router.register(r'members', MemberView)
router.register(r'transactions', TransactionView)


urlpatterns = [
    path("", include(router.urls)),
]