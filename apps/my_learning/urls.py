from django.urls import path

from apps.my_learning.views.historical_grades import HistoricalGradesApiView
from apps.my_learning.views.pending_exams import PendingExamsApiView

urlpatterns = [
    # 待考试
    path('pending_exams/', PendingExamsApiView.as_view(), name='pending_exams'),

    # 历史成绩查询
    path('historical_grades/', HistoricalGradesApiView.as_view(), name='historical_grades'),
]
