from django.urls import include, path
from rest_framework import routers

from apps.my_learning.views.historical_grades import HistoricalGradesApiView
from apps.my_learning.views.pending_exams import PendingExamsApiView

router = routers.SimpleRouter(trailing_slash=True)

# 历史成绩查询
router.register(r"historical_grades", HistoricalGradesApiView, basename="historical_grades")

urlpatterns = [
    # 待考试
    path('pending_exams/', PendingExamsApiView.as_view(), name='pending_exams'),

    path("", include(router.urls)),
    # # 历史成绩查询
    # path('historical_grades/', HistoricalGradesApiView.as_view({"get": "list"}), name='historical_grades'),
]
