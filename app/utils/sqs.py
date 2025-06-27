import os
from app.schemas.responses.url import URLSuccessItem
import boto3
import json
from app.core.configs import settings

sqs = boto3.client(
    "sqs",
    region_name="ap-south-1",
    aws_access_key_id=str(settings.ACCESS_KEY_ID),
    aws_secret_access_key=str(settings.SECRET_ACCESS_KEY)
)

QUEUE_MAP = {
    "INSTAGRAM": "https://sqs.ap-south-1.amazonaws.com/303258618035/instagram-inc-url-processing-queue",
    "FACEBOOK": "https://sqs.ap-south-1.amazonaws.com/303258618035/facebook-inc-url-processing-queue",
    "YOUTUBE": "https://sqs.ap-south-1.amazonaws.com/303258618035/youtube-inc-url-processing-queue",
    "WEBSITE": "https://sqs.ap-south-1.amazonaws.com/303258618035/website-inc-url-processing-queue"
}

def push_to_sqs(success_urls: list[URLSuccessItem]):
    platform_groups = {}

    for item in success_urls:
        platform = item.platform.upper()
        if platform not in QUEUE_MAP:
            continue
        platform_groups.setdefault(platform, []).append(item)

    for platform, items in platform_groups.items():
        entries = [
            {
                "Id": str(i),
                "MessageBody": json.dumps(item.dict())
            }
            for i, item in enumerate(items)
        ]
        queue_url = QUEUE_MAP[platform]
        for batch in (entries[i:i + 10] for i in range(0, len(entries), 10)):
            sqs.send_message_batch(QueueUrl=queue_url, Entries=batch)
