import re

from rest_framework import serializers

from apps.platform_management.models import (
    Administrator,
    ClientCompany,
    ClientStudent,
    CourseTemplate,
    Instructor,
    ManageCompany,
)


class BasicSerializerValidator:
    @classmethod
    def validate_phone(cls, value):
        """
        Validate phone number.
        Simple validation for phone number (example: 11 digits only).
        You can customize this as per your requirements.
        """
        pattern = re.compile(r"^1[35678]\d{9}$")
        if not pattern.match(value):
            raise serializers.ValidationError("手机号必须为11位，第一位为1，第二位可选数字[3,5,6,7,8]")

        return value

    @classmethod
    def validate_affiliated_manage_company_name(cls, value):
        exist_manage_companies = ManageCompany.names
        if value not in exist_manage_companies:
            raise serializers.ValidationError(
                f"该管理公司不存在, 可选管理公司: {exist_manage_companies}"
            )
        return value

    @classmethod
    def validate_affiliated_client_company_name(cls, value):
        exist_client_companies = ClientCompany.names
        if value not in exist_client_companies:
            raise serializers.ValidationError(
                f"该客户公司不存在, 可选客户公司: {exist_client_companies}"
            )
        return value

    @classmethod
    def validate_teachable_courses(cls, value):
        valid_courses = CourseTemplate.names
        invalid_courses = [course for course in value if course not in valid_courses]
        if invalid_courses:
            raise serializers.ValidationError(f"存在部分课程不存在, 可选课程: {valid_courses}")
        return value

    @classmethod
    def validate_target_client_company_name(cls, value):
        return cls.validate_affiliated_client_company_name(value)

    @classmethod
    def validate_course_name(cls, value):
        exist_courses = CourseTemplate.names
        if value not in exist_courses:
            raise serializers.ValidationError(f"该课程不存在, 可选课程: {exist_courses}")
        return value


class PhoneCreateSerializerValidator:
    @classmethod
    def validate_phone(cls, value):
        """
        Validate phone number.
        Simple validation for phone number (example: 11 digits only).
        You can customize this as per your requirements.
        """
        pattern = re.compile(r"^1[35678]\d{9}$")
        if not pattern.match(value):
            raise serializers.ValidationError("手机号必须为11位，第一位为1，第二位可选数字[3,5,6,7,8]")

        if Instructor.objects.filter(phone=value).exists():
            raise serializers.ValidationError("具有 手机号码 的 instructor 已存在。")
        if Administrator.objects.filter(phone=value).exists():
            raise serializers.ValidationError("具有 电话 的 instructor 已存在。")
        if ClientStudent.objects.filter(phone=value).exists():
            raise serializers.ValidationError("具有 电话 的 client student 已存在。")

        return value
