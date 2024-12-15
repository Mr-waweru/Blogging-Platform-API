# Blogging-Platform-API

## **1. Overview**
The Blogging Platform API uses **Token-Based Authentication** provided by Django Rest Framework (DRF). This ensures that only authenticated users can access protected API endpoints.

---

## **2. Prerequisites**

Before testing the authentication, ensure that:
1. You have a Django superuser or regular user.
2. You have set up Django REST Framework with `TokenAuthentication`.

---

## **3. Generating a Token for a User**

### **Step 1: Create a User (if not already created)**
Run the following command to create a user:

```bash
python3 manage.py createsuperuser
```
- Enter the **username**, **email** (optional), and **password**.

### **Step 2: Generate a Token for the User**
Run the following command to create a token for the user:

```bash
python3 manage.py drf_create_token <username>
```

For example:
```bash
python3 manage.py drf_create_token user1
```

**Output**:
```text
Generated token <your-token>
```

---

## **4. Testing Authentication**

### **Step 1: Obtain Token**
To retrieve a token for an existing user:

- **Endpoint**: `/api/token/`  
- **Method**: `POST`  
- **Body (JSON)**:
   ```json
   {
       "username": "user1",
       "password": "your-password"
   }
   ```

**Response**:
```json
{
    "token": "your-generated-token"
}
```

---

### **Step 2: Access Protected Endpoints**

To access any secure endpoint, you must include the token in the **Authorization** header.

#### **Header Example**:
```http
Authorization: Token your-generated-token
```

---

### **Step 3: Example - Access `/api/posts/`**

- **Endpoint**: `/api/posts/`  
- **Method**: `GET`  
- **Header**:
   ```
   Authorization: Token your-generated-token
   ```

**Request Example**:
```http
GET /api/posts/ HTTP/1.1
Host: example.com
Authorization: Token your-generated-token
```

**Response Example**:
```json
[
    {
        "id": 1,
        "title": "First Post",
        "content": "This is the first post.",
        "author": "John Doe",
        "created_at": "2024-12-15T10:00:00Z"
    }
]
```

---

## **5. Troubleshooting**

1. **User Does Not Exist**:  
   - Ensure you have created a user with `createsuperuser`.

2. **Token Missing in Header**:  
   - Ensure the `Authorization` header is correctly set with `Token <your-token>`.

3. **Permission Denied (403)**:  
   - Ensure your endpoint allows authenticated users by adding:
     ```python
     @permission_classes([IsAuthenticated])
     ```

---

## **6. Notes**

- Authentication is required for all endpoints unless explicitly set otherwise.
- Tokens are persistent and must be stored securely. Treat them like passwords.

---

## **Conclusion**

This setup ensures that the Blogging Platform API is secure and only authenticated users can access protected resources. Use the provided steps to test the authentication functionality.