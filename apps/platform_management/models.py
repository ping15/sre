from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin, Group, Permission
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Attachment(models.Model):
    file = models.FileField(upload_to='attachment/')


class CourseTemplate(models.Model):
    """课程模板"""
    STATUS_ORDERING_RULE = [
        ("停课", 3),
        ("准备期", 2),
        ("暂停", 1),
        ("授课", 0),
    ]

    name = models.CharField(_("课程名称"), max_length=32, db_index=True)
    level = models.CharField(
        _("级别"),
        # choices=[
        #     ('primary', _("初级")),
        #     ('intermediate', _("中级")),
        #     ('senior', _("高级")),
        # ],
        max_length=32,
    )
    abbreviation = models.CharField(_("英文缩写"), max_length=32)
    num_lessons = models.IntegerField(_("课时数量"))
    version = models.CharField(_("版本"), max_length=16)
    release_date = models.DateField(_("上线日期"))
    status = models.CharField(
        _("状态"),
        # choices=[
        #     ('preparation', _("准备期")),
        #     ('in_progress', _("授课")),
        #     ('suspended', _("暂停")),
        #     ('terminated', _("停课")),
        # ],
        max_length=32,
    )
    assessment_method = models.CharField(
        _("考核方式"),
        # choices=[
        #     ('closed_book_exam', _("闭卷考试")),
        #     ('computer_exam', _("闭卷机考")),
        #     ('practical', _("实操")),
        #     ('defense', _("答辩")),
        # ],
        max_length=16,
    )
    attachments = models.JSONField(_("附件区域"), default=list)
    certification = models.CharField(_("认证证书"), max_length=32)
    trainees_count = models.IntegerField(_("培训人次"))
    client_company_count = models.IntegerField(_("客户数"))
    class_count = models.IntegerField(_("开班次数"))
    num_instructors = models.IntegerField(_("讲师数量"))
    material_content = models.TextField(_("教材内容"),)
    course_overview = models.TextField(_("课程概述"))
    target_students = models.TextField(_("目标学员"))
    learning_objectives = models.TextField(_("学习目标"))
    learning_benefits = models.TextField(_("学习收益"))
    course_content = models.JSONField(_("课程内容"), default=list)
    remarks = models.TextField(_("备注"))
    exam_type = models.JSONField(
        _("考试题型"),
        # choices=[
        #     ('multiple_choice', _("多选题")),
        #     ('single_choice', _("单选题")),
        # ],
        default=list,
    )
    num_questions = models.IntegerField(_("考题数量"))
    exam_duration = models.IntegerField(
        _("考试时长"),
        # choices=[
        #     (45, _("45分钟")),
        #     (60, _("60分钟")),
        #     (120, _("120分钟")),
        # ],
    )
    exam_language = models.CharField(
        _("考试语言"),
        # choices=[
        #     ('chinese', _("中文")),
        #     ('english', _("英文")),
        # ],
        max_length=8
    )
    passing_score = models.IntegerField(_("过线分数"))
    require_authorized_training = models.BooleanField(_("是否要求授权培训"))
    certification_body = models.JSONField(
        _("认证机构"),
        # choices=[
        #     ('none', _("无证")),
        #     ('any_one', _("任何一个证")),
        #     ('two_certificates', _("两证")),
        # ],
        default=list,
    )

    def __str__(self):
        return self.name

    @property
    def course_module_count(self):
        """课程模块数量"""
        return len(self.course_content)


class Administrator(AbstractUser):
    # username = models.CharField(_("名称"), max_length=32, db_index=True)
    # email = models.EmailField(_("邮箱"), max_length=64, blank=True)
    phone = models.CharField(_("手机号码"), max_length=16, db_index=True)
    # password = models.CharField(_("登录密码"), max_length=32)
    manage_company = models.CharField(_("管理公司"), max_length=32)
    # manage_company = models.ForeignKey(
    #     ManageCompany,
    #     verbose_name=_("管理公司"),
    #     on_delete=models.CASCADE,
    #     related_name='managers',
    # )
    role = models.CharField(
        _("权限角色"),
        choices=[
            ('super_manager', _('超级管理员')),
            ('company_manager', _('管理公司管理员')),
            ('partner_manager', _('合作伙伴管理员')),
        ],
        max_length=16,
        db_index=True,
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='manager_set'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='manager_set'
    )

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    class Meta:
        app_label = 'platform_management'


# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
#
#
# class UserManager(BaseUserManager):
#     def _create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_user(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', False)
#         extra_fields.setdefault('is_superuser', False)
#         return self._create_user(email, password, **extra_fields)
#
#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self._create_user(email, password, **extra_fields)
#
#
# class Manager(AbstractBaseUser, PermissionsMixin):
#     # username = models.CharField(_("名称"), max_length=32, db_index=True)
#     email = models.EmailField(_("邮箱"), max_length=64, blank=True)
#     phone = models.CharField(_("手机号码"), max_length=16, db_index=True)
#     # password = models.CharField(_("登录密码"), max_length=32)
#     manage_company = models.CharField(_("管理公司"), max_length=32)
#     # manage_company = models.ForeignKey(
#     #     ManageCompany,
#     #     verbose_name=_("管理公司"),
#     #     on_delete=models.CASCADE,
#     #     related_name='managers',
#     # )
#     role = models.CharField(
#         _("权限角色"),
#         choices=[
#             ('super_manager', _('超级管理员')),
#             ('company_manager', _('管理公司管理员')),
#             ('partner_manager', _('合作伙伴管理员')),
#         ],
#         max_length=16,
#         db_index=True,
#     )
#
#     objects = UserManager()
#
#     USERNAME_FIELD = 'email'
#     EMAIL_FIELD = 'email'
#     REQUIRED_FIELDS = []
#
#     # def __str__(self):
#     #     return self.e
#
#     def has_perm(self, perm, obj=None):
#         return self.is_superuser
#
#     def has_module_perms(self, app_label):
#         return self.is_superuser
#
#     @property
#     def is_admin(self):
#         return self.is_superuser
#
#     @property
#     def is_staff(self):
#         return self.is_admin
