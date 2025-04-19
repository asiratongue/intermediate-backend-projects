# A Scalable E-Commerce Platform, AKA "ShopShop" 🛒🛍️😊
"ShopShop" is an E-Commerce Backend Platform using a microservices architecture, allowing users to sign up, view,
cart, and pay for products. Users are notified of purchase and order information via SMS and Email.


ShopShop was built using Django and DRF for back end, Posgresql as the db, Celery, Django Signals, and Redis for message queues + internal service communication, 
and Docker-Compose for containerization.
The ELK Stack is used for centralised logging and data visualisation, while Prometheus with Grafana is used for CPU/Memory Metrics.
The API gateway is handled with nginx, proxying requests to appropriate services.

## Features

### Core Services
- **User Service:** Registration, Login, Authentication, Profile Management
- **Product Service:** Product catalog management, Product search and detail view, Inventory
- **Shopping Cart Service:** Cart management, Cart view
- **Order Service:** Order creation, Order processing, Status tracking
- **Payment Service:** Secure payment processing via Stripe, Paypal, or Coinbase Commerce, Refunds, Webhooks.
- **Notification Service:** Email/SMS notifications via Sendgrid/Twilio

## Tech Stack

### Backend
- Django + Django DRF
- Postgresql with AWS RDS
- AWS S3 Bucket for product image storage
- Celery + Django Signals with Redis for Internal Service Communication


### Infrastructure
- Docker & Docker Compose
- Nginx for API Gateway & Load Balancing
- Stripe, Coinbase, & Paypal Payment Gateways.


### Monitoring & Logging
- Prometheus & Grafana (Resource Metrics)
- ELK Stack (Elasticsearch, Logstash, Kibana)
# Future Updates

- Finish/Create Admin Service, containing a centralised admin panel
- Implement Coinbase Commerce and Paypal Refunds into the payment service
- Deploy with Kubernetes, implement load balancing and auto-scaling
- CI/CD Integration with GitLab CI.
- add a proper link in to the order, for email notification.
