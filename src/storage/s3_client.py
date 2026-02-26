"""S3 client wrapper with error handling and retry logic."""

import logging
from io import BytesIO
from typing import BinaryIO

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from src.storage.exceptions import S3OperationException

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_MODE = "adaptive"
CONNECT_TIMEOUT = 10  # seconds
READ_TIMEOUT = 60  # seconds

# Presigned URL expiration
DEFAULT_PRESIGNED_URL_EXPIRY = 3600  # 1 hour in seconds


class S3Client:
    """AWS S3 client wrapper with error handling and retry logic.

    Attributes:
        bucket_name: S3 bucket name for file storage
        region: AWS region for S3 bucket
        client: Boto3 S3 client instance
    """

    def __init__(
        self,
        bucket_name: str,
        region: str,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
    ) -> None:
        """Initialize S3 client with retry configuration.

        Args:
            bucket_name: Name of the S3 bucket
            region: AWS region where bucket is located
            aws_access_key_id: AWS access key ID (optional, uses env/IAM if not provided)  # noqa: E501
            aws_secret_access_key: AWS secret access key (optional)
        """
        self.bucket_name = bucket_name
        self.region = region

        # Configure retry logic and timeouts
        retry_config = Config(
            region_name=region,
            retries={
                "max_attempts": MAX_RETRIES,
                "mode": RETRY_MODE,
            },
            connect_timeout=CONNECT_TIMEOUT,
            read_timeout=READ_TIMEOUT,
        )

        # Initialize S3 client
        if aws_access_key_id and aws_secret_access_key:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                config=retry_config,
            )
        else:
            # Use default credential chain (env vars, IAM role, etc.)
            self.client = boto3.client("s3", config=retry_config)

        logger.info(
            "S3 client initialized",
            extra={
                "bucket_name": self.bucket_name,
                "region": self.region,
            },
        )

    def upload_file(
        self,
        file: BinaryIO,
        s3_key: str,
        content_type: str,
        metadata: dict = None,
    ) -> str:
        """Upload file to S3 bucket.

        Args:
            file: File-like object to upload
            s3_key: S3 object key (path) for the file
            content_type: MIME type of the file
            metadata: Optional metadata dict to attach to S3 object

        Returns:
            str: S3 key of uploaded file

        Raises:
            S3OperationException: If upload operation fails

        Example:
            client = S3Client("my-bucket", "us-east-1")
            with open("document.pdf", "rb") as f:
                s3_key = client.upload_file(
                    f,
                    "users/123/document.pdf",
                    "application/pdf"
                )
        """
        try:
            logger.info(
                "Uploading file to S3",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                    "content_type": content_type,
                },
            )

            file.seek(0)

            extra_args = {
                "ContentType": content_type,
            }

            if metadata:
                extra_args["Metadata"] = metadata

            self.client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args,
            )

            logger.info(
                "File uploaded successfully to S3",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                },
            )

            return s3_key

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            logger.error(
                "S3 upload failed",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                    "error_code": error_code,
                    "error_message": error_message,
                },
            )

            raise S3OperationException(
                "upload",
                f"Failed to upload to {s3_key}: {error_message}",
                original_error=e,
            )

        except BotoCoreError as e:
            logger.error(
                "S3 upload failed due to BotoCore error",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                    "error": str(e),
                },
            )

            raise S3OperationException(
                "upload",
                f"Failed to upload to {s3_key}: {str(e)}",
                original_error=e,
            )

    def download_file(self, s3_key: str) -> BytesIO:
        """Download file from S3 bucket.

        Args:
            s3_key: S3 object key (path) to download

        Returns:
            BytesIO: File content as BytesIO object

        Raises:
            S3OperationException: If download operation fails

        Example:
            client = S3Client("my-bucket", "us-east-1")
            file_content = client.download_file("users/123/document.pdf")
        """
        try:
            logger.info(
                "Downloading file from S3",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                },
            )

            file_obj = BytesIO()
            self.client.download_fileobj(
                self.bucket_name,
                s3_key,
                file_obj,
            )

            file_obj.seek(0)

            logger.info(
                "File downloaded successfully from S3",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                },
            )

            return file_obj

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            logger.error(
                "S3 download failed",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                    "error_code": error_code,
                    "error_message": error_message,
                },
            )

            raise S3OperationException(
                "download",
                f"Failed to download {s3_key}: {error_message}",
                original_error=e,
            )

        except BotoCoreError as e:
            logger.error(
                "S3 download failed due to BotoCore error",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                    "error": str(e),
                },
            )

            raise S3OperationException(
                "download",
                f"Failed to download {s3_key}: {str(e)}",
                original_error=e,
            )

    def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3 bucket.

        Args:
            s3_key: S3 object key (path) to delete

        Returns:
            bool: True if deletion successful

        Raises:
            S3OperationException: If delete operation fails

        Example:
            client = S3Client("my-bucket", "us-east-1")
            success = client.delete_file("users/123/document.pdf")
        """
        try:
            logger.info(
                "Deleting file from S3",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                },
            )

            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key,
            )

            logger.info(
                "File deleted successfully from S3",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                },
            )

            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            logger.error(
                "S3 delete failed",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                    "error_code": error_code,
                    "error_message": error_message,
                },
            )

            raise S3OperationException(
                "delete",
                f"Failed to delete {s3_key}: {error_message}",
                original_error=e,
            )

        except BotoCoreError as e:
            logger.error(
                "S3 delete failed due to BotoCore error",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                    "error": str(e),
                },
            )

            raise S3OperationException(
                "delete",
                f"Failed to delete {s3_key}: {str(e)}",
                original_error=e,
            )

    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = DEFAULT_PRESIGNED_URL_EXPIRY,
    ) -> str:
        """Generate presigned URL for temporary file access.

        Args:
            s3_key: S3 object key (path) for the file
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Presigned URL for file access

        Raises:
            S3OperationException: If presigned URL generation fails

        Example:
            client = S3Client("my-bucket", "us-east-1")
            url = client.generate_presigned_url(
                "users/123/document.pdf",
                expiration=3600
            )
        """
        try:
            logger.info(
                "Generating presigned URL",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                    "expiration": expiration,
                },
            )

            url = self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": s3_key,
                },
                ExpiresIn=expiration,
            )

            logger.info(
                "Presigned URL generated successfully",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                },
            )

            return url

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            logger.error(
                "Presigned URL generation failed",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                    "error_code": error_code,
                    "error_message": error_message,
                },
            )

            raise S3OperationException(
                "generate_presigned_url",
                f"Failed to generate presigned URL for {s3_key}: {error_message}",
                original_error=e,
            )

        except BotoCoreError as e:
            logger.error(
                "Presigned URL generation failed due to BotoCore error",
                extra={
                    "bucket": self.bucket_name,
                    "s3_key": s3_key,
                    "error": str(e),
                },
            )

            raise S3OperationException(
                "generate_presigned_url",
                f"Failed to generate presigned URL for {s3_key}: {str(e)}",
                original_error=e,
            )
