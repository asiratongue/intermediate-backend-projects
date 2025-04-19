## Endpoints 

### **Carts**

**GET** `api/products/view/`   
Returns the catalogue of all products.

**GET** `api/products/search/`   
Search the catalogue with set parameters:
- 'title' -> search product by title
- 'sort_by' -> sort by highest or lowest price, alphabetical order or reverse alphabetical order.  

**GET** `api/products/retrieve/<str:name>`   
Retrieve information for a specific product.

**GET** `api/products/health/`   
Consul health check, checks every 10s.
