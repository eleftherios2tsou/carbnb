import uuid
import boto3
from app.config import settings

def get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )

def make_car_photo_key(car_id: str, ext: str = "jpg") -> str:
    return f"cars/{car_id}/{uuid.uuid4()}.{ext}"

def presign_put_url(key: str, content_type: str = "image/jpeg", expires_seconds: int = 900) -> str:
    s3 = get_s3_client()
    return s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": settings.aws_s3_bucket, "Key": key, "ContentType": content_type},
        ExpiresIn=expires_seconds,
    )

def public_url(key: str) -> str:
    region = settings.aws_region
    bucket = settings.aws_s3_bucket
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

def delete_object(key: str) -> None:
    s3 = get_s3_client()
    s3.delete_object(Bucket=settings.aws_s3_bucket, Key=key)
