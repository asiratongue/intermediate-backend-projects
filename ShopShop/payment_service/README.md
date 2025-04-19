## Endpoints 

### **Payments**

**POST** `api/payments/checkout/<str:id>/`   
Pay for an order, choose which payment gateway you'd like to pay with.
Must pass the jwt token within json data itself using "Content-Type: application/json", not with Authorization: Bearer.
- <str:id> -> UUID of order number.
- {"method" : "stripe" or "crypto" or "paypal"}

`api/payments/success/`   
Payment success template view.

'api/payments/cancel/`   
Payment cancelled template view.

**GET** `api/payments/refund/<str:id>/`   
Get a refund from the payment provider.
Must pass the jwt token within json data itself using "Content-Type: application/json", not with Authorization: Bearer.
- <str:id> -> UUID of order number.
- {"method" : "stripe" or "crypto" or "paypal"}

**POST** `api/payments/webhook/stripe/`   
Stripe webhook endpoint, triggers on 'checkout.session.completed' events.

**POST** `api/payments/webhook/paypal/`   
Paypal webhook endpoint, triggers on 'CHECKOUT.ORDER.APPROVED', 'PAYMENT.CAPTURE.DENIED', and 'PAYMENT.CAPTURE.REFUNDED' events.

**POST** `api/payments/webhook/coinbase/`   
Coinbase webhook endpoint, triggers on 'charge:confirmed', 'charge:failed', 'charge:pending' events.

**GET** `api/payments/health/`   
Consul health check, checks every 10s.

