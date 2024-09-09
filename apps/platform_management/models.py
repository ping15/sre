from typing import List

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models import QuerySet
from django.utils.functional import classproperty
from django.utils.translation import ugettext_lazy as _

from common.utils import global_constants


class Attachment(models.Model):
    file = models.FileField(_("附件"), upload_to="attachment/")


class CourseTemplate(models.Model):
    """课程模板"""

    class Level(models.TextChoices):
        PRIMARY = "primary", "初级"
        INTERMEDIATE = "intermediate", "中级"
        SENIOR = "senior", "高级"

    class Status(models.TextChoices):
        PREPARATION = "preparation", "准备期"
        IN_PROGRESS = "in_progress", "授课"
        SUSPENDED = "suspended", "暂停"
        TERMINATED = "terminated", "停课"

    class AssessmentMethod(models.TextChoices):
        CLOSED_BOOK_EXAM = "closed_book_exam", "闭卷考试"
        COMPUTER_EXAM = "computer_exam", "闭卷机考"
        PRACTICAL = "practical", "实操"
        DEFENSE = "defense", "答辩"

    class ExamType(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", "多选题"
        SINGLE_CHOICE = "single_choice", "单选题"
        SUBJECTIVE = "subjective", "主观题"

    class ExamDuration(models.TextChoices):
        FORTY_FIVE = 45, "45分钟"
        SIXTY = 90, "90分钟"
        ONE_HUNDRED_TWENTY = 120, "120分钟"

    class ExamLanguage(models.TextChoices):
        CHINESE = "chinese", "中文"
        ENGLISH = "english", "英文"

    class CertificationBody(models.TextChoices):
        # # Ministry of Industry and Information Technology
        MIIT_TALENT_CENTER = "miit_talent_center", "工信部人才中心"
        EXAM_CENTER = "exam_center", "教考中心"

    STATUS_ORDERING_RULE = [
        ("停课", 3),
        ("准备期", 2),
        ("暂停", 1),
        ("授课", 0),
    ]

    name = models.CharField(_("课程名称"), max_length=32, unique=True)
    level = models.CharField(
        _("级别"),
        choices=Level.choices,
        max_length=32,
    )
    abbreviation = models.CharField(_("英文缩写"), max_length=32)
    num_lessons = models.IntegerField(_("课时数量"))
    version = models.CharField(_("版本"), max_length=16)
    release_date = models.DateField(_("上线日期"))
    status = models.CharField(
        _("状态"),
        choices=Status.choices,
        max_length=32,
    )
    assessment_method = models.CharField(
        _("考核方式"),
        choices=AssessmentMethod.choices,
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
    target_students = models.TextField(_("目标学员"), default="")
    learning_objectives = models.TextField(_("学习目标"), default="")
    learning_benefits = models.TextField(_("学习收益"), default="")
    course_content = models.TextField(_("课程内容"))
    remarks = models.TextField(_("备注"))
    exam_type = models.JSONField(
        _("考试题型"),
        choices=ExamType.choices,
        default=list,
    )
    num_questions = models.IntegerField(_("考题数量"))
    exam_duration = models.IntegerField(
        _("考试时长"),
        choices=ExamDuration.choices,
    )
    exam_language = models.CharField(
        _("考试语言"),
        choices=ExamLanguage.choices,
        max_length=8,
    )
    passing_score = models.IntegerField(_("过线分数"))
    require_authorized_training = models.BooleanField(_("是否要求授权培训"))
    certification_body = models.JSONField(
        _("认证机构"),
        choices=CertificationBody.choices,
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

    class Meta:
        ordering = ["-id"]


class ManageCompany(models.Model):
    """管理公司"""

    class Type(models.TextChoices):
        DEFAULT = "default", "默认公司"
        PARTNER = "partner", "合作伙伴"

    name = models.CharField(_("名称"), max_length=32, unique=True)
    email = models.EmailField(_("邮箱"), max_length=32)
    type = models.CharField(
        _("类型"),
        choices=Type.choices,
        max_length=32,
    )

    @property
    def client_companies(self) -> QuerySet["ClientCompany"]:
        return ClientCompany.objects.filter(affiliated_manage_company_name=self.name)

    @property
    def client_company_names(self) -> List[str]:
        return list(self.client_companies.values_list("name", flat=True))

    @property
    def students(self) -> QuerySet["ClientStudent"]:
        return ClientStudent.objects.filter(
            affiliated_client_company_name__in=self.client_companies.values_list(
                "name", flat=True
            )
        )

    @classproperty
    def names(self) -> List[str]:
        return list(self.objects.values_list("name", flat=True))

    @classmethod
    def sync_name(cls, old_name: str, new_name: str):
        ClientCompany.objects.filter(affiliated_manage_company_name=old_name).update(
            affiliated_manage_company_name=new_name
        )

    def delete(self, using=None, keep_parents=False):
        self.client_companies.delete()
        self.administrators.all().delete()
        super().delete(using, keep_parents)

    def __str__(self):
        return self.name


class Administrator(AbstractUser):
    """管理员"""

    class Role(models.TextChoices):
        SUPER_MANAGER = "super_manager", "平台管理员"
        COMPANY_MANAGER = "company_manager", "鸿雪公司管理员"
        PARTNER_MANAGER = "partner_manager", "合作伙伴管理员"

    username = models.CharField(_("名称"), max_length=64, db_index=True)
    phone = models.CharField(_("手机号码"), max_length=16, db_index=True, unique=True)
    affiliated_manage_company = models.ForeignKey(
        ManageCompany,
        on_delete=models.CASCADE,
        verbose_name=_("管理公司"),
        related_name="administrators",
    )
    role = models.CharField(
        _("权限角色"),
        choices=Role.choices,
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
    def affiliated_manage_company_name(self) -> str:
        return self.affiliated_manage_company.name

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    class Meta:
        app_label = "platform_management"


class Instructor(models.Model):
    """讲师"""

    username = models.CharField(_("姓名"), max_length=64, db_index=True)
    phone = models.CharField(_("电话"), max_length=16, unique=True)
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
    def role(self) -> str:
        return global_constants.Role.INSTRUCTOR.value

    @property
    def is_active(self) -> bool:
        return True

    def __str__(self):
        return self.username


class ClientCompany(models.Model):
    """客户公司"""

    class PaymentMethod(models.TextChoices):
        PUBLIC_CARD = "public_card", "刷公务卡"
        TELEGRAPHIC_TRANSFER = "telegraphic_transfer", "电汇"
        WECHAT = "wechat", "对公微信"
        ALIPAY = "alipay", "对公支付宝"

    # 基本信息
    name = models.CharField(_("客户公司名称"), max_length=32, unique=True)
    contact_person = models.CharField(_("联系人"), max_length=32)
    contact_phone = models.CharField(_("电话"), max_length=16)
    contact_email = models.EmailField(_("邮箱"), max_length=64)
    payment_method = models.CharField(
        _("参会费支付方式"),
        choices=PaymentMethod.choices,
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

    created_date = models.DateField(_("创建时间"), auto_now_add=True)

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

    @classmethod
    def sync_name(cls, old_name: str, new_name: str):
        ClientStudent.objects.filter(affiliated_client_company_name=old_name).update(
            affiliated_client_company_name=new_name
        )

    def delete(self, using=None, keep_parents=False):
        from apps.teaching_space.models import TrainingClass

        TrainingClass.objects.filter(target_client_company_name=self.name).delete()
        self.students.delete()
        super().delete(using, keep_parents)

    def __str__(self):
        return self.name


class ClientStudent(models.Model):
    """客户学员"""

    class Education(models.TextChoices):
        HIGHSCHOOL = "highschool", "高中"
        ASSOCIATE = "associate", "专科"
        BACHELOR = "bachelor", "本科"
        MASTER = "master", "硕士研究生"
        DOCTORATE = "doctorate", "博士生"

    username = models.CharField(_("名称"), max_length=64)
    gender = models.CharField(_("性别"), max_length=32)
    id_number = models.CharField(_("身份证号"), max_length=32)
    education = models.CharField(
        _("学历"),
        choices=Education.choices,
        max_length=32,
    )
    phone = models.CharField(_("电话"), max_length=16, unique=True)
    email = models.EmailField(_("邮箱"), max_length=64)
    affiliated_client_company_name = models.CharField(_("客户公司"), max_length=64)
    department = models.CharField(_("部门"), max_length=32)
    position = models.CharField(_("职位"), max_length=32)
    id_photo = models.JSONField(_("证件照"), default=dict)

    last_login = models.DateTimeField(_("最后登录时间"), blank=True, null=True)
    created_date = models.DateField(_("创建时间"), auto_now_add=True)

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
    def role(self) -> str:
        return global_constants.Role.CLIENT_STUDENT.value

    @property
    def is_active(self) -> bool:
        return True

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


class Event(models.Model):
    """日程事件"""

    from apps.teaching_space.models import TrainingClass

    class EventType(models.TextChoices):
        CLASS_SCHEDULE = "class_schedule", "培训班排课"
        ONE_TIME_UNAVAILABILITY = "one_time_unavailability", "登记一次性不可用时间规则"
        RECURRING_UNAVAILABILITY = "recurring_unavailability", "登记周期性不可用时间规则"
        CANCEL_UNAVAILABILITY = "cancel_unavailability", "取消单日不可用时间"

        @classmethod
        def rule_types(cls) -> List[str]:
            return [cls.ONE_TIME_UNAVAILABILITY, cls.RECURRING_UNAVAILABILITY]

    class FreqType(models.TextChoices):
        WEEKLY = "weekly", "每周"
        MONTHLY = "monthly", "每月"

    event_type = models.CharField(_("事件类型"), max_length=50, choices=EventType.choices)
    freq_type = models.CharField(
        choices=FreqType.choices, max_length=16, null=True, blank=True
    )
    freq_interval = models.JSONField(default=list)
    start_date = models.DateField(_("开始时间"))
    end_date = models.DateField(_("结束时间"), null=True, blank=True)
    instructor = models.ForeignKey(
        Instructor,
        related_name="events",
        verbose_name=_("讲师"),
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    training_class = models.OneToOneField(
        TrainingClass,
        related_name="events",
        on_delete=models.CASCADE,
        verbose_name=_("培训班"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("日程事件")
        verbose_name_plural = verbose_name
