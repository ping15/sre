from functools import wraps

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError


def check_bucket(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_valid:
            return {"error": "无可用cos_client"}

        try:
            return func(self, *args, **kwargs)

        except CosClientError:
            return {"error": "无可用cos_client"}
    return wrapper


class CosClient:
    def __init__(
        self,
        secret_id: str,
        secret_key: str,
        region: str,
        bucket: str,
        token: str = None,
        scheme: str = "https"
    ):
        try:
            self.config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
            self.client = CosS3Client(self.config)
            self.bucket = bucket
            self.is_valid = True
        except CosClientError:
            self.is_valid = False

    @check_bucket
    def upload_file_by_local_path(self, local_file_path: str, key: str) -> dict:
        try:
            return self.client.upload_file(
                Bucket=self.bucket,
                LocalFilePath=local_file_path,
                Key=key,
                PartSize=1,
                MAXThread=10,
                EnableMD5=False
            )
            # logging.info(f"File uploaded successfully: {response['ETag']}")
            # return response
        except CosServiceError as e:
            return {"error": f"本地上传文件失败, 状态码: {e.get_error_code()}, 错误信息: {e.get_error_msg()}"}

    @check_bucket
    def upload_file_by_fp(self, fp: InMemoryUploadedFile, key: str) -> dict:
        try:
            return self.client.put_object(Bucket=self.bucket, Body=fp, Key=key, StorageClass="STANDARD")
            # logging.info(f"File uploaded successfully: {response['ETag']}")
            # return response
        except CosServiceError as e:
            return {"error": f"上传文件失败, 状态码: {e.get_error_code()}, 错误信息: {e.get_error_msg()}"}

    @check_bucket
    def download_file(self, key: str) -> dict:
        try:
            return self.client.get_object(Bucket=self.bucket, Key=key)
        except CosServiceError as e:
            return {"error": f"下载文件失败, 状态码: {e.get_error_code()}, 错误信息: {e.get_error_msg()}"}

    @check_bucket
    def delete_file(self, key: str) -> dict:
        try:
            return self.client.delete_object(Bucket=self.bucket, Key=key)
        except CosServiceError as e:
            return {"error": f"删除文件失败, 状态码: {e.get_error_code()}, 错误信息: {e.get_error_msg()}"}


cos_client = CosClient(
    secret_id=settings.COS_SECRET_ID,
    secret_key=settings.COS_SECRET_KEY,
    region=settings.COS_REGION,
    bucket=settings.COS_BUCKET,
)
