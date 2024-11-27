from typing import List

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models import QuerySet
from django.utils.functional import classproperty

from common.utils import global_constants


class Attachment(models.Model):
    file = models.FileField("附件", upload_to="attachment/")


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

    name = models.CharField("课程名称", max_length=128, unique=True)
    level = models.CharField("级别", choices=Level.choices, max_length=32)
    abbreviation = models.CharField("英文缩写", max_length=32)
    num_lessons = models.IntegerField("课时数量")
    version = models.CharField("版本", max_length=16, default="")
    release_date = models.DateField("上线日期", blank=True, null=True)
    status = models.CharField("状态", choices=Status.choices, max_length=32)
    assessment_method = models.CharField("考核方式", choices=AssessmentMethod.choices, max_length=16)
    attachments = models.JSONField("附件区域", default=list)
    certification = models.CharField("认证证书", max_length=32)
    trainees_count = models.IntegerField("培训人次")
    client_company_count = models.IntegerField("客户数")
    class_count = models.IntegerField("开班次数")
    num_instructors = models.IntegerField("讲师数量")
    material_content = models.TextField("教材内容")  # 富文本
    course_overview = models.TextField("课程概述")
    target_students = models.TextField("目标学员", default="")  # 富文本
    learning_objectives = models.TextField("学习目标", default="")  # 富文本
    learning_benefits = models.TextField("学习收益", default="")  # 富文本
    course_content = models.TextField("课程内容")  # 富文本
    remarks = models.TextField("备注")
    exam_type = models.JSONField("考试题型", choices=ExamType.choices, default=list)
    num_questions = models.IntegerField("考题数量", null=True, blank=True)
    exam_duration = models.IntegerField("考试时长", choices=ExamDuration.choices, null=True, blank=True)
    exam_language = models.CharField("考试语言", choices=ExamLanguage.choices, max_length=8, null=True, blank=True)
    passing_score = models.IntegerField("过线分数", null=True, blank=True)
    require_authorized_training = models.BooleanField("是否要求授权培训", null=True, blank=True)
    certification_body = models.JSONField("认证机构", choices=CertificationBody.choices, default=list)

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
        verbose_name = "课程模板"
        verbose_name_plural = verbose_name


class ManageCompany(models.Model):
    """管理公司"""

    class Type(models.TextChoices):
        DEFAULT = "default", "默认公司"
        PARTNER = "partner", "合作伙伴"

    name = models.CharField("名称", max_length=128, unique=True)
    email = models.EmailField("邮箱", max_length=256)
    type = models.CharField("类型", choices=Type.choices, max_length=32, default=Type.PARTNER.value,)

    @property
    def client_companies(self) -> QuerySet["ClientCompany"]:
        """该管理公司下所有客户公司"""
        return ClientCompany.objects.filter(affiliated_manage_company_name=self.name)

    @property
    def client_company_names(self) -> List[str]:
        """该管理公司下所有客户公司名称"""
        return list(self.client_companies.values_list("name", flat=True))

    @property
    def students(self) -> QuerySet["ClientStudent"]:
        """该管理公司下所有客户学员"""
        return ClientStudent.objects.filter(
            affiliated_client_company_name__in=self.client_companies.values_list("name", flat=True)
        )

    @classproperty
    def names(self) -> List[str]:
        """管理公司所有名称"""
        return list(self.objects.values_list("name", flat=True))

    @classmethod
    def sync_name(cls, old_name: str, new_name: str):
        """修改管理公司名称时同步下面客户公司的所属管理公司名称"""
        ClientCompany.objects.filter(affiliated_manage_company_name=old_name).update(
            affiliated_manage_company_name=new_name
        )

    def delete(self, using=None, keep_parents=False):
        """删除管理公司时删除下面所有客户公司"""
        self.client_companies.delete()
        super().delete(using, keep_parents)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "管理公司"
        verbose_name_plural = verbose_name


class Administrator(AbstractUser):
    """管理员"""

    class Role(models.TextChoices):
        SUPER_MANAGER = "super_manager", "平台管理员"
        COMPANY_MANAGER = "company_manager", "鸿雪公司管理员"
        PARTNER_MANAGER = "partner_manager", "合作伙伴管理员"

    username = models.CharField("名称", max_length=128, db_index=True)
    phone = models.CharField("手机号码", max_length=16, db_index=True, unique=True)
    affiliated_manage_company = models.ForeignKey(
        ManageCompany,
        on_delete=models.CASCADE,
        verbose_name="管理公司",
        related_name="administrators",
    )
    role = models.CharField("权限角色", choices=Role.choices, max_length=16, db_index=True)
    groups = models.ManyToManyField(Group, verbose_name="groups", blank=True, related_name="manager_set")
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        related_name="manager_set",
    )

    def __str__(self):
        return self.username

    @property
    def affiliated_manage_company_name(self) -> str:
        return self.affiliated_manage_company.name

    @property
    def is_super_administrator(self) -> bool:
        return self.role == Administrator.Role.SUPER_MANAGER

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    class Meta:
        app_label = "platform_management"
        verbose_name = "管理员"
        verbose_name_plural = verbose_name


class Instructor(models.Model):
    """讲师"""

    username = models.CharField("姓名", max_length=128, db_index=True)
    phone = models.CharField("电话", max_length=16, unique=True)
    email = models.EmailField("邮箱", max_length=256)
    city = models.CharField("所在城市", max_length=64)
    company = models.CharField("所在公司", max_length=256)
    department = models.CharField("部门", max_length=32)
    position = models.CharField("岗位", max_length=32)
    introduction = models.TextField("简介")
    teachable_courses = models.JSONField("可授课程", default=list)
    satisfaction_score = models.FloatField("满意度评分", default=0.0)
    hours_taught = models.IntegerField("已授课时", default=0)
    is_partnered = models.BooleanField("是否合作", default=True)
    id_photo = models.JSONField("证件照")

    last_login = models.DateTimeField("最后登录时间", blank=True, null=True)

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_super_administrator(self) -> bool:
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

    class Meta:
        verbose_name = "讲师"
        verbose_name_plural = verbose_name


class ClientCompany(models.Model):
    """客户公司"""

    class PaymentMethod(models.TextChoices):
        PUBLIC_CARD = "public_card", "刷公务卡"
        TELEGRAPHIC_TRANSFER = "telegraphic_transfer", "电汇"
        WECHAT = "wechat", "对公微信"
        ALIPAY = "alipay", "对公支付宝"

    # 基本信息
    name = models.CharField("客户公司名称", max_length=128, unique=True)
    contact_person = models.CharField("联系人", max_length=128)
    contact_phone = models.CharField("电话", max_length=16)
    contact_email = models.EmailField("邮箱", max_length=256)
    payment_method = models.CharField("参会费支付方式", choices=PaymentMethod.choices, max_length=32)
    affiliated_manage_company_name = models.CharField("管理公司", max_length=128)

    # 通讯信息
    certificate_address = models.CharField("证书收件地址", max_length=256)
    recipient_name = models.CharField("收件人", max_length=128)
    recipient_phone = models.CharField("收件人电话", max_length=16)

    # 开票信息
    invoice_company_name = models.CharField("公司名称", max_length=128)
    tax_identification_number = models.CharField("纳税人识别号", max_length=32)
    invoice_company_address = models.CharField("单位地址", max_length=128)
    invoice_company_phone = models.CharField("单位电话", max_length=16)
    bank_name = models.CharField("开户行", max_length=128)
    bank_account = models.CharField("账号", max_length=64)

    created_date = models.DateField("创建时间", auto_now_add=True)

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

        TrainingClass.objects.filter(target_client_company=self).delete()
        self.students.delete()
        super().delete(using, keep_parents)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "客户公司"
        verbose_name_plural = verbose_name


class ClientStudent(models.Model):
    """客户学员"""

    class Education(models.TextChoices):
        HIGHSCHOOL = "highschool", "高中"
        ASSOCIATE = "associate", "专科"
        BACHELOR = "bachelor", "本科"
        MASTER = "master", "硕士研究生"
        DOCTORATE = "doctorate", "博士生"

    username = models.CharField("名称", max_length=128)
    gender = models.CharField("性别", max_length=32)
    id_number = models.CharField("身份证号", max_length=32, blank=True)
    education = models.CharField("学历", choices=Education.choices, max_length=32)
    phone = models.CharField("电话", max_length=16, unique=True)
    email = models.EmailField("邮箱", max_length=256, blank=True)
    affiliated_client_company_name = models.CharField("客户公司", max_length=128)
    department = models.CharField("部门", max_length=128, blank=True)
    position = models.CharField("职位", max_length=128, blank=True)
    id_photo = models.JSONField("证件照")

    last_login = models.DateTimeField("最后登录时间", blank=True, null=True)
    created_date = models.DateField("创建时间", auto_now_add=True)

    @property
    def affiliated_client_company(self) -> ClientCompany:
        return ClientCompany.objects.get(name=self.affiliated_client_company_name)

    @property
    def affiliated_manage_company(self) -> ManageCompany:
        return ManageCompany.objects.get(name=self.affiliated_client_company.affiliated_manage_company_name)

    @property
    def affiliated_manage_company_name(self) -> str:
        return self.affiliated_manage_company.name

    @property
    def affiliated_manage_company_id(self) -> int:
        return self.affiliated_manage_company.id

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_super_administrator(self) -> bool:
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

    @property
    def exam_system_username(self):
        return f"sre-{self.phone}"

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "客户学员"
        verbose_name_plural = verbose_name


class ClientApprovalSlip(models.Model):
    """客户审批单据"""

    class Status(models.TextChoices):
        PENDING = "pending", "待处理"
        AGREED = "agreed", "同意"
        REJECTED = "rejected", "驳回"

    name = models.CharField("标题", max_length=128)
    affiliated_manage_company_name = models.CharField("管理公司", max_length=128)
    affiliated_client_company_name = models.CharField("客户公司", max_length=128)
    submitter = models.CharField("提单人", max_length=128)
    status = models.CharField("状态", choices=Status.choices, max_length=32, default=Status.PENDING.value)
    submission_datetime = models.DateTimeField("提单时间")
    submission_info = models.JSONField("提交信息", default=dict)

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

    class Meta:
        verbose_name = "客户资料审批"
        verbose_name_plural = verbose_name


class Event(models.Model):
    """日程事件"""

    from apps.teaching_space.models import TrainingClass

    class EventType(models.TextChoices):
        CLASS_SCHEDULE = "class_schedule", "培训班排课"
        ONE_TIME_UNAVAILABILITY = "one_time_unavailability", "登记一次性不可用时间规则"
        RECURRING_UNAVAILABILITY = "recurring_unavailability", "登记周期性不可用时间规则"
        CANCEL_UNAVAILABILITY = "cancel_unavailability", "取消单日不可用时间"

        @classproperty
        def create_choices(cls):
            empty = [(None, cls.__empty__)] if hasattr(cls, '__empty__') else []
            return empty + [
                (member.value, member.label) # noqa
                for member in cls if member != cls.CLASS_SCHEDULE
            ]

        @classproperty
        def rule_types(self) -> List:
            return [self.ONE_TIME_UNAVAILABILITY, self.RECURRING_UNAVAILABILITY]

    class FreqType(models.TextChoices):
        WEEKLY = "weekly", "每周"
        BIWEEKLY = "biweekly", "每两周"
        MONTHLY = "monthly", "每月"

    event_type = models.CharField("事件类型", max_length=64, choices=EventType.choices)
    freq_type = models.CharField(choices=FreqType.choices, max_length=16, null=True, blank=True)
    freq_interval = models.JSONField(default=list)
    start_date = models.DateField("开始时间")
    end_date = models.DateField("结束时间", null=True, blank=True)
    instructor = models.ForeignKey(
        Instructor,
        related_name="events",
        verbose_name="讲师",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    training_class = models.OneToOneField(
        TrainingClass,
        related_name="event",
        on_delete=models.CASCADE,
        verbose_name="培训班",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "日程事件"
        verbose_name_plural = verbose_name
