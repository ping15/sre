from django.db import models


class ExamSystemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using('exam-system')


class BaseModel(models.Model):
    objects = ExamSystemManager()

    class Meta:
        abstract = True


class AppExam(BaseModel):
    app_code = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'home_application_appexam'
        app_label = 'exam-system'


# class AppExamExam(BaseModel):
#     appexam = models.ForeignKey(Appexam, models.DO_NOTHING)
#     examarrange = models.ForeignKey('Examarrange', models.DO_NOTHING)
#
#     class Meta:
#         managed = False
#         db_table = 'home_application_appexam_exam'
#         unique_together = (('appexam', 'examarrange'),)


class AppManager(BaseModel):
    rtx_name = models.CharField(max_length=255)
    creator = models.CharField(max_length=255)
    create_time = models.DateTimeField()
    is_delete = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'home_application_appmanager'
        app_label = 'exam-system'


# class AppManagerSubjects(BaseModel):
#     appmanager = models.ForeignKey(AppManager, models.DO_NOTHING)
#     subject = models.ForeignKey('Subject', models.DO_NOTHING)
#
#     class Meta:
#         managed = False
#         db_table = 'home_application_appmanager_subjects'
#         unique_together = (('appmanager', 'subject'),)


# class AppSubject(BaseModel):
#     app_code = models.CharField(max_length=64)
#     last_operator = models.ForeignKey(AccountUser, models.DO_NOTHING, blank=True, null=True)
#     last_update_datetime = models.DateTimeField(blank=True, null=True)
#     subject = models.ForeignKey('Subject', models.DO_NOTHING, blank=True, null=True)
#     using_exam = models.ForeignKey('Examarrange', models.DO_NOTHING, blank=True, null=True)
#     app_name = models.CharField(max_length=128)
#
#     class Meta:
#         managed = False
#         db_table = 'home_application_appsubject'


class ExamArrange(BaseModel):
    title = models.TextField()
    description = models.CharField(max_length=255)
    paper_id = models.IntegerField()
    info = models.TextField()
    ip = models.TextField()
    student = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    address = models.TextField()
    notice = models.IntegerField()
    creator = models.CharField(max_length=255)
    newer = models.CharField(max_length=255)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    status = models.IntegerField()
    exam_type = models.CharField(max_length=255, blank=True, null=True)
    pass_grade = models.FloatField()
    training_class_id = models.IntegerField()
    subject = models.ForeignKey('Subject', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'home_application_examarrange'
        app_label = 'exam-system'


class ExamGrade(BaseModel):
    answer = models.TextField(blank=True, null=True)
    grade = models.FloatField()
    is_check = models.IntegerField()
    evaluation = models.TextField()
    exam_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'home_application_examgrade'
        app_label = 'exam-system'


class ExamStudent(BaseModel):
    exam_id = models.IntegerField()
    student_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    answer_ids = models.TextField()
    is_commit = models.IntegerField()
    change_grade_people = models.TextField(blank=True, null=True)
    completion_time = models.DateTimeField(blank=True, null=True)
    grade_people = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    is_super_pass = models.IntegerField()

    @property
    def exam_info(self):
        try:
            exam: ExamArrange = ExamArrange.objects.get(id=self.exam_id)
            return {
                "title": exam.title,
                # "description": exam.description,
                # "paper_id": exam.paper_id,
                # "info": exam.info,
                # "ip": exam.ip,
                # "student": exam.student,
                # "start_time": exam.start_time,
                # "end_time": exam.end_time,
                # "address": exam.address,
                # "notice": exam.notice,
                # "creator": exam.creator,
                # "newer": exam.newer,
                # "create_time": exam.create_time,
                # "update_time": exam.update_time,
                # "status": exam.status,
                # "exam_type": exam.exam_type,
                # "pass_grade": exam.pass_grade,
                "subject_name": exam.subject.display_name,
                "training_class_id": exam.training_class_id,
            }
        except ExamArrange.DoesNotExist:
            return {}

    class Meta:
        managed = False
        db_table = 'home_application_examstudent'
        app_label = 'exam-system'


class ExamType(BaseModel):
    exam_type = models.CharField(max_length=255)
    exam_desc = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'home_application_examtype'
        app_label = 'exam-system'


class ExamWhitelist(BaseModel):
    rtx = models.CharField(max_length=64)
    creator = models.CharField(max_length=64)
    create_time = models.DateTimeField()
    exam = models.ForeignKey(ExamArrange, models.DO_NOTHING)
    record = models.ForeignKey(ExamStudent, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'home_application_examwhitelist'
        unique_together = (('exam', 'rtx'),)
        app_label = 'exam-system'


class ExerciseArrange(BaseModel):
    title = models.TextField()
    desc_options = models.TextField(blank=True, null=True)
    tag = models.CharField(max_length=255)
    classify = models.CharField(max_length=1)
    answer = models.TextField()
    creator = models.CharField(max_length=255)
    newer = models.CharField(max_length=255)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    status = models.IntegerField()
    subject = models.ForeignKey('Subject', models.DO_NOTHING)
    hint = models.TextField()

    class Meta:
        managed = False
        db_table = 'home_application_exercisearrange'
        app_label = 'exam-system'


class ExerciseInstance(BaseModel):
    title = models.TextField()
    desc_options = models.TextField(blank=True, null=True)
    tag = models.CharField(max_length=255)
    classify = models.CharField(max_length=1)
    answer = models.TextField()
    score = models.FloatField()
    sign_time = models.DateTimeField()
    subject = models.ForeignKey('Subject', models.DO_NOTHING)
    hint = models.TextField()

    class Meta:
        managed = False
        db_table = 'home_application_exerciseinstance'
        app_label = 'exam-system'


class MailConfig(BaseModel):
    reciver = models.CharField(max_length=255)
    tag = models.CharField(max_length=1)
    operator = models.CharField(max_length=255)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'home_application_mailconfig'
        app_label = 'exam-system'


class MailContent(BaseModel):
    mail_content = models.TextField(blank=True, null=True)
    newer = models.CharField(max_length=255)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'home_application_mailcontent'
        app_label = 'exam-system'


class PaperArrange(BaseModel):
    title = models.TextField()
    description = models.TextField()
    instance_exercise = models.TextField()
    original_exercise = models.TextField()
    creator = models.CharField(max_length=255)
    newer = models.CharField(max_length=255)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    status = models.IntegerField()
    original_instance_dict = models.TextField()
    instance_original_dict = models.TextField()
    is_auto = models.IntegerField()
    subject = models.ForeignKey('Subject', models.DO_NOTHING)
    is_auto_check = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'home_application_paperarrange'
        app_label = 'exam-system'


class Subject(BaseModel):
    code_name = models.CharField(max_length=64)
    display_name = models.CharField(max_length=256)
    description = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'home_application_subject'
        app_label = 'exam-system'


# class SubjectAdminList(BaseModel):
#     subject = models.ForeignKey(Subject, models.DO_NOTHING)
#     user = models.ForeignKey(AccountUser, models.DO_NOTHING)
#
#     class Meta:
#         managed = False
#         db_table = 'home_application_subject_admin_list'
#         unique_together = (('subject', 'user'),)


class SubjectWhitelist(BaseModel):
    rtx = models.CharField(max_length=64)
    creator = models.CharField(max_length=64)
    create_time = models.DateTimeField()
    subject = models.ForeignKey(Subject, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'home_application_subjectwhitelist'
        unique_together = (('subject', 'rtx'),)
        app_label = 'exam-system'
