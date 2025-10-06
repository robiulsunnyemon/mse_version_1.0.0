from firebase_admin import messaging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.db.db import get_db
from app.models.notification_box import NotificationBoxModel
from app.models.race import RaceModel
from app.models.event import EventModel
from app.models.fcm_token import FCMTokenModel
from app.models.notification import NotificationModel


def send_scheduled_notifications():
    db: Session = next(get_db())
    try:
        # সব টাইম UTC
        current_time = datetime.now(timezone.utc)
        print(f"[DEBUG] Running scheduled notification job at {current_time}")

        # আগামী ২ দিনের সকল ইভেন্ট
        upcoming_events = db.query(EventModel).filter(
            EventModel.started_at >= current_time,
            EventModel.started_at <= current_time + timedelta(days=2)
        ).all()
        print(f"[DEBUG] Upcoming events count: {len(upcoming_events)}")

        for event in upcoming_events:
            event_start = event.started_at
            if event_start.tzinfo is None:
                event_start = event_start.replace(tzinfo=timezone.utc)
            print(f"[DEBUG] Processing event {event.id} at {event_start}")

            notifications = db.query(NotificationModel).filter(
                NotificationModel.race_id == event.race_id
            ).all()
            print(f"[DEBUG] Notifications to send for event {event.id}: {len(notifications)}")

            for notification in notifications:
                # Notification time in UTC
                notification_time = event_start - timedelta(hours=notification.notification_hour)
                if notification_time.tzinfo is None:
                    notification_time = notification_time.replace(tzinfo=timezone.utc)

                print(f"[DEBUG] Notification scheduled for user {notification.user_id} at {notification_time} (current_time={current_time})")

                # Window check: current_time >= notification_time এবং 1 মিনিটের window
                if notification_time <= current_time < notification_time + timedelta(minutes=1):
                    print(f"[DEBUG] Time to send notification for user {notification.user_id}")

                    # User FCM tokens
                    user_tokens_objs = db.query(FCMTokenModel).filter(
                        FCMTokenModel.user_id == notification.user_id
                    ).all()
                    tokens = [t.token for t in user_tokens_objs if t.token]
                    print(f"[DEBUG] Found {len(tokens)} FCM tokens for user {notification.user_id}")

                    if not tokens:
                        print(f"[DEBUG] No tokens found for user {notification.user_id}, skipping.")
                        continue

                    race = db.query(RaceModel).filter(RaceModel.id == event.race_id).first()
                    if not race:
                        print(f"[DEBUG] No race found for event {event.id}, skipping notification.")
                        continue

                    title = "Race Reminder!"
                    body = f"{race.name} at {event.location} is on {event.tv_broadcast_chanel} in {notification.notification_hour} hour."
                    print(f"[DEBUG] Sending notification: {title} - {body}")

                    try:
                        message = messaging.MulticastMessage(
                            notification=messaging.Notification(
                                title=title,
                                body=body,
                            ),
                            tokens=tokens,
                        )

                        response = messaging.send_each_for_multicast(message)
                        print(f"[DEBUG] {response.success_count} messages sent for event {event.id}.")
                        if response.failure_count > 0:
                            print(f"[DEBUG] {response.failure_count} messages failed. Responses: {response.responses}")

                        for user_token_obj in user_tokens_objs:
                            notification_box_entry = NotificationBoxModel(
                                user_id=user_token_obj.user_id,
                                notification_title=title,
                                notification_body=body
                            )
                            db.add(notification_box_entry)
                        db.commit()
                        print(f"[DEBUG] Notifications saved in NotificationBoxModel for user {notification.user_id}")



                    except Exception as e:
                        print(f"[ERROR] Failed to send notification for event {event.id}: {e}")
                else:
                    print(f"[DEBUG] Not time yet for user {notification.user_id} (scheduled at {notification_time})")

    finally:
        db.close()
        print("[DEBUG] Database session closed")
