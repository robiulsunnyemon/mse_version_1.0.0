import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(
    prefix="/stripe",
    tags=["stripe"]
)

class CreatePayment(BaseModel):
    amount: int
    currency: str = "usd"


@router.post("/create-payment-intent")
async def create_payment_intent(payment_data: CreatePayment):

    try:

        intent = stripe.PaymentIntent.create(
            amount=payment_data.amount,
            currency=payment_data.currency,
            metadata={'integration_with': 'fastapi_flutter'}
        )

        return {
            "clientSecret": intent.client_secret,
            "paymentIntentId": intent.id

        }


    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")