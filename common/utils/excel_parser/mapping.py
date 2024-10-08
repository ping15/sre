INSTRUCTOR_EXCEL_MAPPING = {
    "姓名": {"type": str, "value": "username"},
    "电话": {"type": str, "value": "phone"},
    "邮箱": {"type": str, "value": "email"},
    "所在城市": {"type": str, "value": "city"},
    "所在公司": {"type": str, "value": "company"},
    "部门": {"type": str, "value": "department"},
    "岗位": {"type": str, "value": "position"},
    "简介": {"type": str, "value": "introduction"},
    "可授课程": {"type": list, "value": "teachable_courses"},
}

ADMINISTRATOR_EXCEL_MAPPING = {
    "管理员名称": {"type": str, "value": "username"},
    "邮箱": {"type": str, "value": "email"},
    "手机": {"type": str, "value": "phone"},
    "所属公司": {"type": str, "value": "affiliated_manage_company_name"},
    "权限角色": {"type": str, "value": "role"},
}

CLIENT_STUDENT_EXCEL_MAPPING = {
    "学员名称": {"type": str, "value": "username"},
    "性别": {"type": str, "value": "gender"},
    "身份证号": {"type": str, "value": "id_number"},
    "学历": {"type": str, "value": "education"},
    "电话": {"type": str, "value": "phone"},
    "邮箱": {"type": str, "value": "email"},
    "所属客户公司": {"type": str, "value": "affiliated_client_company_name"},
    "部门": {"type": str, "value": "department"},
    "职位": {"type": str, "value": "position"},
}

TRAINING_CLASS_SCORE_EXCEL_MAPPING = {
    "序号": {"type": int, "value": "id"},
    "讲师分数": {"type": float, "value": "score"},
}
