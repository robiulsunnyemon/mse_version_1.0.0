from typing import List
from fastapi import HTTPException
from firebase_admin import messaging


async def send_bulk_notification(tokens: List[str], title: str, body: str):
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            tokens=tokens,
        )


        response = messaging.send_each_for_multicast(message)
        print(f'{response.success_count} messages were sent successfully')
        return {"success": True, "success_count": response.success_count, "failure_count": response.failure_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))