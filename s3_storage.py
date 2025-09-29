import os
import mimetypes
from pathlib import Path

try:
    import boto3  # type: ignore
except Exception:
    boto3 = None


def is_configured() -> bool:
    return bool(os.getenv("S3_BUCKET") and (boto3 is not None))


def public_base_url(bucket: str) -> str:
    base = os.getenv("S3_PUBLIC_BASE_URL")
    if base:
        return base.rstrip('/')
    return f"https://{bucket}.s3.amazonaws.com"


def upload_file(local_path: str, key: str) -> str:
    if not is_configured():
        raise RuntimeError("S3 not configured")
    bucket = os.getenv("S3_BUCKET")
    client = boto3.client("s3")
    content_type, _ = mimetypes.guess_type(local_path)
    extra = {"ACL": "public-read"}
    if content_type:
        extra["ContentType"] = content_type
    client.upload_file(local_path, bucket, key, ExtraArgs=extra)
    base = public_base_url(bucket)
    return f"{base}/{key}"
