
## Endpoints 

### **Users**

**POST** `api/users/register/`   
Register a new user, recieve a JWT code.

**POST** `api/users/login/`   
User Login, recieve a JWT code.

**POST** `api/users/validate/`   
Validate a JWT Token, for external use.

**PUT** `api/users/update/`   
Update user details. (email, username, or password)

**DELETE** `api/users/delete/`   
Delete user account, requires JWT and password.

**POST** `api/users/health/`   
Consul health check, checks every 10s.
