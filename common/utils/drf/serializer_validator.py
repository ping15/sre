import re
from typing import List

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
    def validate_phone(cls, value: str):
        """手机号11位校验"""
        pattern = re.compile(r"^1[356789]\d{9}$")
        if not pattern.match(value):
            raise serializers.ValidationError("手机号必须为11位，第一位为1，第二位可选数字[3,5,6,7,8,9]")

        return value

    @classmethod
    def validate_affiliated_manage_company_name(cls, value: str):
        """管理公司存活校验"""
        exist_manage_companies = ManageCompany.names
        if value not in exist_manage_companies:
            raise serializers.ValidationError(f"该管理公司不存在, 可选管理公司: {exist_manage_companies}")
        return value

    @classmethod
    def validate_affiliated_client_company_name(cls, value: str):
        """客户公司存活校验"""
        exist_client_companies = ClientCompany.names
        if value not in exist_client_companies:
            raise serializers.ValidationError(f"该客户公司不存在, 可选客户公司: {exist_client_companies}")
        return value

    @classmethod
    def validate_teachable_courses(cls, courses: List[str]):
        """课程模板存活校验"""
        valid_courses = CourseTemplate.names
        invalid_courses = [course for course in courses if course not in valid_courses]
        if invalid_courses:
            raise serializers.ValidationError(f"存在部分课程不存在, 可选课程: {valid_courses}")
        return courses

    @classmethod
    def validate_target_client_company_name(cls, value: str):
        """客户公司存活校验"""
        return cls.validate_affiliated_client_company_name(value)

    @classmethod
    def validate_course_name(cls, value: str):
        """课程模板存活校验"""
        exist_courses = CourseTemplate.names
        if value not in exist_courses:
            raise serializers.ValidationError(f"该课程不存在, 可选课程: {exist_courses}")
        return value


class PhoneCreateSerializerValidator:
    @classmethod
    def validate_phone(cls, value: str):
        """手机号唯一性校验"""
        pattern = re.compile(r"^1[356789]\d{9}$")
        if not pattern.match(value):
            raise serializers.ValidationError("手机号必须为11位，第一位为1，第二位可选数字[3,5,6,7,8,9]")

        if Instructor.objects.filter(phone=value).exists():
            raise serializers.ValidationError("有讲师存在该手机号。")
        if Administrator.objects.filter(phone=value).exists():
            raise serializers.ValidationError("有管理员存在该手机号。")
        if ClientStudent.objects.filter(phone=value).exists():
            raise serializers.ValidationError("有客户学员存在该手机号。")

        return value
