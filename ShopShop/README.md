# A Scalable E-Commerce Platform, AKA "ShopShop" 🛒🛍️😊
"ShopShop" is an E-Commerce Backend Platform using a microservices architecture, allowing users to sign up, view,
cart, and pay for products. Users are notified of purchase and order information via SMS and Email.
Each service runs as its own independent Django project, and thus can be scaled effectively in production deployment.

## Features

### Core Services
- **User Service:** Registration, Login, Authentication, Profile Management
- **Product Service:** Product catalog management, Product search and detail view, Inventory tracking.
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
- Stripe, Coinbase, & Paypal Payment Gateways


### Monitoring & Logging
- Prometheus & Grafana (Resource Metrics)
- ELK Stack (Elasticsearch, Logstash, Kibana)

## Running ShopShop
### Prerequisites
- Docker Engine 24.0+/Docker Desktop 4.35+
- Postgresql 16+ (for local development)
- S3 Bucket + RDS Configured For Storage / Your Cloud service of choice.
### Environment Setup:
1) Clone the repository:


   ```git clone https://github.com/asiratongue/intermediate-backend-projects.git```


   ```cd ShopShop```

2) Create & Configure .env files for each service. EG for payment service:
   ```AWS_S3_CUSTOM_DOMAIN=DOMAIN```
   ```AWS_ACCESS_KEY_ID=SECRET_KEY```
   ```AWS_SECRET_ACCESS_KEY=SECRET_KEY```
   ```AWS_S3_REGION_NAME=REGION_NAME```
   

3) Run the application with docker:
```docker-compose build```
```docker-compose up -d```

### Service Mappings

| Service             | Internal Port | External Port | Endpoint                                    |
|----------------------|---------------|---------------|---------------------------------------------|
| API Gateway (Nginx)  | 80            | 80            | `http://localhost/`                         |
| User Service         | 8000          | N/A           | `http://localhost/api/users` (via Gateway)  |
| Product Service      | 8000          | N/A           | `http://localhost/api/products/` (via Gateway) |
| Cart Service         | 8000          | N/A           | `http://localhost/api/carts/` (via Gateway)  |
| Payment Service      | 8000          | N/A           | `http://localhost/api/payments/` (via Gateway) |
| Order Service        | 8000          | N/A           | `http://localhost/api/orders/` (via Gateway)  |
| Notification Service | N/A           | N/A           | Internal Communication                      |
| Grafana              | 3000          | 3000          | `http://localhost:3000`                     |
| Kibana               | 5601          | 5601          | `http://localhost:5601`                     |
| Prometheus           | 9090          | 9090          | `http://localhost:9090`                     |

# Future Updates

- Finish/Create Admin Service, containing a centralised admin panel
- Implement Coinbase Commerce and Paypal Refunds into the payment service.
- Deploy with Kubernetes, implement load balancing and auto-scaling.
- CI/CD Integration with GitLab CI.
- Add a proper link in to the order, for email notification. 😆
