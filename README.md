
# 🛍️ Personalized Product Recommendation System

This is a **Personalized Product Recommendation API** that offers content-based, collaborative, and hybrid product recommendations using FastAPI. It supports product listing, user authentication, and user-product interactions like adding to cart, deleting products, and fetching recommendations.

---

## 🚀 Features

- 🔐 **User Authentication** (`/signin`)
- 📦 **Product Management**:
  - Add products to user profile (`/add_to_database`)
  - Fetch all products (`/get-all-products`)
  - View user-specific products (`/get-user-products`)
  - Remove products from cart (`/delete_from_cart`)
- 🧠 **Recommendation System**:
  - Content-Based Filtering
  - Collaborative Filtering (Cosine & Nearest Neighbors)
  - Hybrid Recommendations (`/getrecommendation`)

---

## 🗂️ Project Structure

```
.
├── Data/
│   ├── Products.csv          # Master product catalog
│   ├── User_data.csv         # User-product interaction data
│   └── database.csv          # User authentication data
├── main.py                   # Main FastAPI application
├── README.md                 # Documentation
```

---

## 🧰 Tech Stack

- **FastAPI** - Web Framework
- **Pandas & NumPy** - Data Processing
- **scikit-learn** - Similarity & Recommendation Algorithms
- **CORS Middleware** - API Accessibility
- **Uvicorn** - ASGI Server

---

## 📊 Recommendation Techniques

### 1. 📌 Content-Based Filtering
- Uses TF-IDF vectorization on product `tags`.
- Recommends products similar to the input item name.

### 2. 👥 Collaborative Filtering (Cosine Similarity)
- Compares user-item ratings matrix to recommend products based on similar users.

### 3. 🤝 Collaborative Filtering (Nearest Neighbors)
- Uses `NearestNeighbors` model on sparse user-item matrix to find closest users and their rated items.

### 4. 🔀 Hybrid Recommendation
- Combines content-based and both collaborative methods (if user is registered and has ratings).

---

## 📡 API Endpoints

### ✅ Health Check
```bash
GET /
```

---

### 🔑 User Sign In
```bash
POST /signin
```
```json
{
  "username": "john",
  "password": "doe123"
}
```

---

### ➕ Add Product Interaction
```bash
POST /add_to_database?user_id=1
```
```json
{
  "Rating": 4.5,
  "ReviewCount": 123,
  "productid": 101,
  "category": "Electronics",
  "brand": "Sony",
  "name": "Sony Headphones",
  "description": "Noise cancelling headphones",
  "image_url": "http://example.com/img.jpg",
  "tags": "headphones music electronics"
}
```

---

### 📌 Get Recommendations
```bash
GET /getrecommendation?item_name=Sony%20Headphones&user_id=1
```

---

### 📃 Get All Products
```bash
GET /get-all-products
```

---

### 👤 Get User's Products
```bash
GET /get-user-products?user_id=1
```

---

### ❌ Delete Product from Cart
```bash
DELETE /delete_from_cart?user_id=1&productid=101
```

---

## ⚙️ Setup & Run

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/product-recommendation-api.git
cd product-recommendation-api
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note**: Add your `requirements.txt` with packages like `fastapi`, `pandas`, `scikit-learn`, `uvicorn`, etc.

### 3. Run the Server
```bash
uvicorn main:app --reload
```

---

## 📁 Example CSV Files

- `Products.csv`: All product details with columns like `productid`, `name`, `brand`, `tags`, etc.
- `User_data.csv`: Tracks each user's product interactions and ratings.
- `database.csv`: User credentials (`user_id`, `username`, `password`).

---

## ✍️ Author

**Guthikonda Vijay Venkat Reddy**  
www.linkedin.com/in/vijay-venkat-reddy | https://github.com/vijayreddy004 | vijay38.reddy@gmail.com
