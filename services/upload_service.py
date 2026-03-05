import os
import mimetypes
import uuid
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContentSettings

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

def upload_to_azure(file_path, blob_name=None, public=True):
    """
    Uploads a file to Azure Blob Storage and returns its URL.
    If public=True, assumes the container allows public blob access.
    """
    if not blob_name:
        base = os.path.basename(file_path)
        name, ext = os.path.splitext(base)
        blob_name = f"{name}-{uuid.uuid4().hex}{ext}".replace(" ", "_")

    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"

    print(f"⬆️ Uploading {file_path} → Azure Blob: {blob_name}")

    blob_client = container_client.get_blob_client(blob_name)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )

    if public:
        url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{blob_name}"
    else:
        from datetime import datetime, timedelta
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions

        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=AZURE_CONTAINER_NAME,
            blob_name=blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=12),
        )
        url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{blob_name}?{sas_token}"

    print(f"✅ Uploaded to Azure: {url}")
    return url
