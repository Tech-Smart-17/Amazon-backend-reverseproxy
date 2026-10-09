# Amazon Backend System API Documentation

Complete RESTful API specifications for `/api/v1/` endpoints.

## Base URL
`http://localhost:8000/api/v1`

---

## 1. Authentication (`/api/v1/auth`)

### Register User
`POST /auth/register`
- **Request Body**:
  ```json
  {
    "email": "customer@amazon.com",
    "password": "Password123!",
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "role": "customer"
  }
  ```
- **Response** `201 Created`:
  ```json
  {
    "success": true,
    "message": "User registered successfully",
    "user_id": "8a32a67e-..."
  }
  ```

### Login User
`POST /auth/login`
- **Request Body**:
  ```json
  {
    "email": "admin@amazon.com",
    "password": "Admin@123456"
  }
  ```
- **Response** `200 OK`:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer"
  }
  ```

---

## 2. Product Catalog (`/api/v1/products`)

### List Products
`GET /products?category_id={id}&brand={brand}&min_price=100&max_price=2000&sort_by=price_asc`
- **Response** `200 OK`:
  ```json
  [
    {
      "id": "prod-123",
      "sku": "AMZ-IPHONE-15-PRO",
      "title": "Apple iPhone 15 Pro Max 256GB Titanium",
      "price": 1199.0,
      "discount_percentage": 5.0,
      "final_price": 1139.05,
      "stock_quantity": 150
    }
  ]
  ```

---

## 3. Semantic Search (`/api/v1/search`)

### Vector Search
`GET /search?q=wireless+headphones+with+noise+cancelling&limit=5`
- Uses ChromaDB vector store similarity search.

---

## 4. Shopping Cart (`/api/v1/cart`)

### Add Item to Cart
`POST /cart/items`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "product_id": "prod-123",
    "quantity": 2
  }
  ```

---

## 5. Orders & Payments (`/api/v1/orders` & `/api/v1/payments`)

### Create Order (Checkout)
`POST /orders`
- **Request Body**:
  ```json
  {
    "address_id": "addr-456",
    "payment_method": "credit_card",
    "coupon_code": "WELCOME10"
  }
  ```

### Process Payment
`POST /payments/process`
- **Request Body**:
  ```json
  {
    "order_id": "order-789",
    "payment_method": "credit_card",
    "card_number": "4111222233334444"
  }
  ```
