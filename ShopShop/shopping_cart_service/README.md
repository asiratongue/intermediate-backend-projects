## Endpoints 

### **Carts**

**POST** `api/carts/add/<str:name>/`   
Add an Item to cart with given Product name. (use '%20' for spaces)

**DELETE** `api/carts/remove/<str:name>/`   
Remove an item from cart, using given Product name.

**GET** `api/carts/view/`   
View whats inside your cart.

**GET** `api/carts/health/`   
Consul health check, checks every 10s.
