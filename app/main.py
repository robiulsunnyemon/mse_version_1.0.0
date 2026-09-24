from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from firebase_admin import messaging
from app.db.db import engine, Base, get_db
from app.models.fcm_token import FCMTokenModel
from app.routers.race import race_router
from app.routers.event import event_router
from app.routers.user import router as user_router
from app.routers.notification import notification_router
from app.routers.promotions import promotion_router
from app.routers.fcm_token import fcm_token_router
from app.utils.schedular_push_notification import send_scheduled_notifications
from app.routers.notification_box import notification_box_router
from app.utils.firebase_loader import initialize_firebase
from fastapi.middleware.cors import CORSMiddleware
from app.payment.stripe_payment import router as stripe_payment_router
from app.auth.routers.auth_user import router as auth_user_router
from app.request_and_report.request.routers.request import request_router
from app.request_and_report.report.routers.report import report_router
from app.routers.dropbox import router as dropbox_router


# Load environment variables
load_dotenv()
scheduler = BackgroundScheduler()
scheduler.add_job(send_scheduled_notifications, CronTrigger(minute='*/1'))

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    if not scheduler.running:
        scheduler.start()
    yield
    scheduler.shutdown()

# FastAPI app
app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




from sqlalchemy import text

#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Safe column migration for existing tables
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS is_subscribed BOOLEAN DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS subscription_expiry TIMESTAMP NULL;"))
        conn.execute(text("ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS subscription_product_id VARCHAR NULL;"))
        conn.execute(text("ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS subscription_purchase_token VARCHAR NULL;"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_subscribed BOOLEAN DEFAULT FALSE;"))
        conn.commit()
except Exception as e:
    print(f"⚠️ Column migration notice: {e}")


# Firebase initialization (with error handling)
try:
    initialize_firebase()
except Exception as e:
    print(f"⚠️ Firebase setup failed, but continuing: {e}")



# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Hello, MotorSportsEasy is working!"}


# 🛠️ Debug endpoint to test FCM push notification immediately
@app.get("/debug/test-fcm/{user_id}", tags=["Debug"])
def debug_test_fcm(user_id: int, db: Session = Depends(get_db)):
    user_tokens = db.query(FCMTokenModel).filter(FCMTokenModel.user_id == user_id).all()
    tokens = [t.token for t in user_tokens if t.token]
    if not tokens:
        return {"error": f"No FCM tokens found for user_id={user_id}"}
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title="🔥 Live Test Notification",
                body="If you see this, push notification is working 100%!"
            ),
            data={
                "title": "Live Test",
                "body": "Push notification test"
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
                headers={'apns-priority': '10'},
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title="🔥 Live Test Notification",
                            body="If you see this, push notification is working 100%!"
                        ),
                        sound='default',
                        badge=1,
                    )
                )
            ),
            tokens=tokens
        )
        response = messaging.send_each_for_multicast(message)
        results = []
        for idx, resp in enumerate(response.responses):
            results.append({
                "token": tokens[idx][:25] + "...",
                "success": resp.success,
                "error": str(resp.exception) if resp.exception else None
            })
        return {
            "success_count": response.success_count,
            "failure_count": response.failure_count,
            "results": results
        }
    except Exception as e:
        return {"exception": str(e)}


# Include routers
app.include_router(race_router)
app.include_router(event_router)
app.include_router(user_router)
app.include_router(notification_router)
app.include_router(promotion_router)
app.include_router(fcm_token_router)
app.include_router(notification_box_router)
app.include_router(stripe_payment_router)
app.include_router(auth_user_router)
app.include_router(request_router)
app.include_router(report_router)
app.include_router(dropbox_router)
