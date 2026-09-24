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
            data={
                "title": title,
                "body": body,
            },
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    channel_id='high_importance_channel',
                    priority='max',
                    default_sound=True,
                    default_vibrate_timings=True,
                ),
            ),
            apns=messaging.APNSConfig(
                headers={
                    'apns-priority': '10',
                },
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=title,
                            body=body,
                        ),
                        sound='default',
                        badge=1,
                    ),
                ),
            ),
            tokens=tokens,
        )


        response = messaging.send_each_for_multicast(message)
        print(f'{response.success_count} messages were sent successfully')
        return {"success": True, "success_count": response.success_count, "failure_count": response.failure_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))