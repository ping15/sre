from typing import List

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin, Group, Permission
from django.db import models
from django.db.models import QuerySet
from django.utils.functional import classproperty
from django.utils.translation import ugettext_lazy as _


class Attachment(models.Model):
    file = models.FileField(_("附件"), upload_to="attachment/")


class CourseTemplate(models.Model):
    """课程模板"""

    STATUS_ORDERING_RULE = [
        ("停课", 3),
        ("准备期", 2),
        ("暂停", 1),
        ("授课", 0),
    ]

    name = models.CharField(_("课程名称"), max_length=32, unique=True)
    level = models.CharField(
        _("级别"),
        choices=[
            ("primary", _("初级")),
            ("intermediate", _("中级")),
            ("senior", _("高级")),
        ],
        max_length=32,
    )
    abbreviation = models.CharField(_("英文缩写"), max_length=32)
    num_lessons = models.IntegerField(_("课时数量"))
    version = models.CharField(_("版本"), max_length=16)
    release_date = models.DateField(_("上线日期"))
    status = models.CharField(
        _("状态"),
        choices=[
            ("preparation", _("准备期")),
            ("in_progress", _("授课")),
            ("suspended", _("暂停")),
            ("terminated", _("停课")),
        ],
        max_length=32,
    )
    assessment_method = models.CharField(
        _("考核方式"),
        choices=[
            ("closed_book_exam", _("闭卷考试")),
            ("computer_exam", _("闭卷机考")),
            ("practical", _("实操")),
            ("defense", _("答辩")),
        ],
        max_length=16,
    )
    attachments = models.JSONField(_("附件区域"), default=list)
    certification = models.CharField(_("认证证书"), max_length=32)
    trainees_count = models.IntegerField(_("培训人次"))
    client_company_count = models.IntegerField(_("客户数"))
    class_count = models.IntegerField(_("开班次数"))
    num_instructors = models.IntegerField(_("讲师数量"))
    material_content = models.TextField(
        _("教材内容"),
    )
    course_overview = models.TextField(_("课程概述"))
    target_students = models.TextField(_("目标学员"))
    learning_objectives = models.TextField(_("学习目标"))
    learning_benefits = models.TextField(_("学习收益"))
    course_content = models.TextField(_("课程内容"))
    remarks = models.TextField(_("备注"))
    exam_type = models.JSONField(
        _("考试题型"),
        choices=[
            ("multiple_choice", _("多选题")),
            ("single_choice", _("单选题")),
        ],
        default=list,
    )
    num_questions = models.IntegerField(_("考题数量"))
    exam_duration = models.IntegerField(
        _("考试时长"),
        choices=[
            (45, _("45分钟")),
            (60, _("60分钟")),
            (120, _("120分钟")),
        ],
    )
    exam_language = models.CharField(
        _("考试语言"),
        choices=[
            ("chinese", _("中文")),
            ("english", _("英文")),
        ],
        max_length=8,
    )
    passing_score = models.IntegerField(_("过线分数"))
    require_authorized_training = models.BooleanField(_("是否要求授权培训"))
    certification_body = models.JSONField(
        _("认证机构"),
        choices=[
            # Ministry of Industry and Information Technology
            ("miit_talent_center", _("工信部人才中心")),
            ("exam_center", _("教考中心")),
        ],
        default=list,
    )

    def __str__(self):
        return self.name

    @property
    def course_module_count(self):
        """课程模块数量"""
        return len(self.course_content)

    @classproperty
    def names(self):
        return list(self.objects.values_list("name", flat=True))


class ManageCompany(models.Model):
    """管理公司"""

    name = models.CharField(_("名称"), max_length=32, unique=True)
    email = models.EmailField(_("邮箱"), max_length=32)
    type = models.CharField(
        _("类型"),
        choices=[
            ("default", "默认公司"),
            ("partner", "合作伙伴"),
        ],
        max_length=32,
    )

    @property
    def client_companies(self) -> QuerySet["ClientCompany"]:
        return ClientCompany.objects.filter(affiliated_manage_company_name=self.name)

    @classproperty
    def names(self) -> List[str]:
        return list(self.objects.values_list("name", flat=True))

    def delete(self, using=None, keep_parents=False):
        self.client_companies.delete()
        super().delete(using, keep_parents)

    def __str__(self):
        return self.name


class Administrator(AbstractUser):
    username = models.CharField(_("名称"), max_length=64, db_index=True)
    # email = models.EmailField(_("邮箱"), max_length=64, blank=True)
    phone = models.CharField(_("手机号码"), max_length=16, db_index=True)
    # password = models.CharField(_("登录密码"), max_length=32)
    affiliated_manage_company_name = models.CharField(_("管理公司"), max_length=32)
    # manage_company = models.ForeignKey(
    #     ManageCompany,
    #     verbose_name=_("管理公司"),
    #     on_delete=models.CASCADE,
    #     related_name='managers',
    # )
    role = models.CharField(
        _("权限角色"),
        choices=[
            ("super_manager", _("平台管理员")),
            ("company_manager", _("鸿雪公司管理员")),
            ("partner_manager", _("合作伙伴管理员")),
        ],
        max_length=16,
        db_index=True,
    )
    groups = models.ManyToManyField(
        Group, verbose_name=_("groups"), blank=True, related_name="manager_set"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        related_name="manager_set",
    )

    def __str__(self):
        return self.username

    @property
    def identity(self) -> str:
        return (
            "super_administrator"
            if self.role == "平台管理员"
            else "manage_company_administrator"
        )

    @property
    def affiliated_manage_company(self) -> ManageCompany:
        return ManageCompany.objects.get(name=self.affiliated_manage_company_name)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    class Meta:
        app_label = "platform_management"


class Instructor(models.Model):
    """讲师"""

    username = models.CharField(_("姓名"), max_length=64, db_index=True)
    phone = models.CharField(_("电话"), max_length=16)
    email = models.EmailField(_("邮箱"), max_length=64)
    city = models.CharField(_("所在城市"), max_length=32)
    company = models.CharField(_("所在公司"), max_length=64)
    department = models.CharField(_("部门"), max_length=32)
    position = models.CharField(_("岗位"), max_length=32)
    introduction = models.TextField(_("简介"))
    teachable_courses = models.JSONField(_("可授课程"), default=list)
    satisfaction_score = models.FloatField(_("满意度评分"), default=0.0)
    hours_taught = models.IntegerField(_("已授课时"), default=0)
    is_partnered = models.BooleanField(_("是否合作"), default=True)
    id_photo = models.JSONField(_("证件照"), default=dict)

    last_login = models.DateTimeField(_("最后登录时间"), blank=True, null=True)
    # training_class = models.OneToOneField(
    #     TrainingClass,
    #     related_name='instructor',
    #     verbose_name=_("课堂"),
    #     on_delete=models.CASCADE
    # )

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def identity(self) -> str:
        return "instructor"

    def __str__(self):
        return self.username


class ClientCompany(models.Model):
    """客户公司"""

    # 基本信息
    name = models.CharField(_("客户公司名称"), max_length=32, unique=True)
    contact_person = models.CharField(_("联系人"), max_length=32)
    contact_phone = models.CharField(_("电话"), max_length=16)
    contact_email = models.EmailField(_("邮箱"), max_length=64)
    payment_method = models.CharField(
        _("参会费支付方式"),
        choices=[
            ("public_card", _("刷公务卡")),
            ("telegraphic_transfer", _("电汇")),
            ("wechat", _("对公微信")),
            ("alipay", _("对公支付宝")),
        ],
        max_length=32,
    )
    affiliated_manage_company_name = models.CharField(_("管理公司"), max_length=64)

    # 通讯信息
    certificate_address = models.CharField(_("证书收件地址"), max_length=128)
    recipient_name = models.CharField(_("收件人"), max_length=32)
    recipient_phone = models.CharField(_("收件人电话"), max_length=16)

    # 开票信息
    invoice_company_name = models.CharField(_("公司名称"), max_length=64)
    tax_identification_number = models.CharField(_("纳税人识别号"), max_length=32)
    invoice_company_address = models.CharField(_("单位地址"), max_length=128)
    invoice_company_phone = models.CharField(_("单位电话"), max_length=16)
    bank_name = models.CharField(_("开户行"), max_length=64)
    bank_account = models.CharField(_("账号"), max_length=32)

    @property
    def students(self) -> QuerySet["ClientStudent"]:
        return ClientStudent.objects.filter(affiliated_client_company_name=self.name)

    @property
    def affiliated_manage_company(self) -> ManageCompany:
        return ManageCompany.objects.get(name=self.affiliated_manage_company_name)

    @property
    def student_count(self) -> int:
        return self.students.count()

    @classproperty
    def names(self) -> List[str]:
        return list(self.objects.values_list("name", flat=True))

    def delete(self, using=None, keep_parents=False):
        self.students.delete()
        super().delete(using, keep_parents)

    def __str__(self):
        return self.name


class ClientStudent(models.Model):
    """客户学员"""

    username = models.CharField(_("名称"), max_length=64)
    gender = models.CharField(_("性别"), max_length=32)
    id_number = models.CharField(_("身份证号"), max_length=32)
    education = models.CharField(
        _("学历"),
        choices=[
            ("associate", _("专科")),
            ("bachelor", _("本科")),
            ("master", _("硕士研究生")),
            ("doctorate", _("博士生")),
        ],
        max_length=32,
    )
    phone = models.CharField(_("电话"), max_length=16)
    email = models.EmailField(_("邮箱"), max_length=64)
    # affiliated_client_company = models.ForeignKey(
    #     ClientCompany,
    #     verbose_name=_("客户公司"),
    #     on_delete=models.CASCADE,
    #     related_name='students',
    # )
    affiliated_client_company_name = models.CharField(_("客户公司"), max_length=64)
    department = models.CharField(_("部门"), max_length=32)
    position = models.CharField(_("职位"), max_length=32)
    id_photo = models.JSONField(_("证件照"), default=dict)

    last_login = models.DateTimeField(_("最后登录时间"), blank=True, null=True)

    @property
    def affiliated_client_company(self) -> ClientCompany:
        return ClientCompany.objects.get(name=self.affiliated_client_company_name)

    @property
    def affiliated_manage_company(self) -> ManageCompany:
        return ManageCompany.objects.get(
            name=self.affiliated_client_company.affiliated_manage_company_name
        )

    @property
    def affiliated_manage_company_name(self) -> str:
        return self.affiliated_manage_company.name

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def identity(self):
        return "client_student"

    def __str__(self):
        return self.username


class ClientApprovalSlip(models.Model):
    """客户审批单据"""

    class Status(models.TextChoices):
        PENDING = "pending", "待处理"
        APPROVED = "approval", "同意"
        REJECTED = "rejected", "驳回"

    name = models.CharField(_("标题"), max_length=64)
    affiliated_manage_company_name = models.CharField(_("管理公司"), max_length=32)
    affiliated_client_company_name = models.CharField(_("客户公司"), max_length=32)
    submitter = models.CharField(_("提单人"), max_length=32)
    status = models.CharField(
        _("状态"),
        choices=Status.choices,
        max_length=32,
        default=Status.PENDING.value,
    )
    submission_datetime = models.DateTimeField(_("提单时间"))
    submission_info = models.JSONField(_("提交信息"), default=dict)

    @property
    def affiliated_manage_company(self) -> ManageCompany:
        return ManageCompany.objects.get(name=self.affiliated_manage_company_name)

    @property
    def affiliated_client_company(self) -> ClientCompany:
        return ClientCompany.objects.get(name=self.affiliated_client_company_name)

    @classproperty
    def affiliated_client_company_names(self) -> List:
        return list(
            self.objects.values_list("affiliated_client_company_name", flat=True)
        )

    def __str__(self):
        return self.name
