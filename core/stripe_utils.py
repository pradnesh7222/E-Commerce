import stripe
from django.conf import settings

# Configure the Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(amount, currency='usd', payment_method_types=['card']):
    """
    Create a payment intent with Stripe.

    :param amount: The amount to be charged (in cents)
    :param currency: The currency for the payment
    :param payment_method_types: The payment method types allowed
    :return: Stripe PaymentIntent object
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method_types=payment_method_types,
        )
        return {'success': True, 'client_secret': intent.client_secret}
    except stripe.error.StripeError as e:
        return {'success': False, 'message': str(e)}

def confirm_payment(client_secret, payment_method_id):
    """
    Confirm the payment with the provided client secret and payment method ID.

    :param client_secret: The client secret from Stripe
    :param payment_method_id: The payment method ID to confirm
    :return: Stripe PaymentIntent object
    """
    try:
        result = stripe.PaymentIntent.confirm(
            client_secret=client_secret,
            payment_method=payment_method_id,
        )
        return {'success': True, 'payment_intent': result}
    except stripe.error.StripeError as e:
        return {'success': False, 'message': str(e)}