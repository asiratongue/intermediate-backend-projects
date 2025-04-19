## Endpoints 

### **Orders**

**POST** `api/orders/ops/create/`   
Create an order, fetching the authenticated users cart.
- must provide some extra info about the order, eg: '{"billing" : "123 Fake Street, IA2 B34", "shipping" : "123 Fake Gardens, IA2 B34", "contact" : "+447654321012"}'  

**GET** `api/orders/<str:id>/`
Retrieve complete order details.
- <str:id> -> UUID of Order.


**PUT** `api/orders/<str:id>/`
Update order details.
- <str:id> -> UUID of Order.


**POST** `api/orders/status/<str:id>/`   
Update an orders status, requires Admin status to access, sends an SMS + Email notification.
- <str:id> -> UUID of Order.


**DELETE** `api/orders/ops/delete/`   
Delete a single or a list of orders, requires Admin status to access.


**GET** `api/history/<str:id>/`   
Retrieve order history for a given order.
- <str:id> -> UUID of Order.

**GET** `api/consul/health/`   
Consul health check, checks every 10s.


**GET** `api/contact/<str:id>/`   
Retrieves a specifc orders contact number, internal use only.
- <str:id> -> UUID of Order's contact number to retrieve.

