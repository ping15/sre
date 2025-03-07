from django.urls import include, path
from rest_framework import routers

from apps.teaching_space.views.training_class import TrainingClassModelViewSet

router = routers.SimpleRouter(trailing_slash=True)

# 公司信息

# 客户学员

# 培训班
router.register(r"training_class", TrainingClassModelViewSet, basename="training_class")

# 日程

urlpatterns = [
    path("", include(router.urls)),
]
