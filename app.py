import os
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from difflib import get_close_matches
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
users_data = pd.read_csv("Data/User_data.csv", on_bad_lines='skip', engine='python')
products_data = pd.read_csv("Data/Products.csv")
def Content_based_recommendations(data, item_name, top_n=5):
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix_content = tfidf_vectorizer.fit_transform(data['tags'])
    cosine_similarities_content = cosine_similarity(tfidf_matrix_content, tfidf_matrix_content)
    matches = get_close_matches(item_name, data['name'])
    secondary_matches = data[data['name'].str.contains(item_name, case=False, na=False)]['name'].tolist()
    if not matches and not secondary_matches:
        raise ValueError(f"Item with name similar to '{item_name}' not found.")
    if not matches:
        matches = secondary_matches
    close_match = matches[0]
    item_index = data[data['name'] == close_match].index[0]
    similar_items = list(enumerate(cosine_similarities_content[item_index]))
    similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)
    top_similar_items = similar_items[0:top_n]
    recommended_item_indices = [x[0] for x in top_similar_items]
    recommended_items_details = data.iloc[recommended_item_indices][['name', 'ReviewCount', 'brand', 'image_url', 'Rating']]
    return recommended_items_details
model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=10)
def Collaborative_neighbours_based_recommendations(data,target_user_id, top_n=10):
    user_item_matrix = data.pivot_table(index='Id', columns='productid', values='Rating', aggfunc='mean').fillna(0)
    if target_user_id not in user_item_matrix.index:
        raise ValueError(f"User with Id {target_user_id} not found.")
    user_item_sparse = csr_matrix(user_item_matrix.values)
    model.fit(user_item_sparse)
    target_user_idx = user_item_matrix.index.get_loc(target_user_id)
    distances, indices = model.kneighbors([user_item_matrix.iloc[target_user_idx]], n_neighbors=top_n+1)
    similar_user_indices = indices.flatten()[1:]
    recommended_product_ids = set()
    target_user_rated = set(user_item_matrix.columns[user_item_matrix.iloc[target_user_idx] > 0])
    for idx in similar_user_indices:
        similar_user_ratings = user_item_matrix.iloc[idx]
        unrated_by_target = (similar_user_ratings > 0) & (~user_item_matrix.columns.isin(target_user_rated))
        recommended_product_ids.update(user_item_matrix.columns[unrated_by_target])
        if len(recommended_product_ids) >= top_n:
            break
    recommended_items_details = data[data['productid'].isin(list(recommended_product_ids))][['name', 'ReviewCount', 'brand', 'image_url', 'Rating']]
    return recommended_items_details.head(top_n)
def Collaborative_based_recommendations(data, target_user_id, top_n=10):
    user_item_matrix = data.pivot_table(index='Id', columns='productid', values='Rating', aggfunc='mean').fillna(0)
    user_similarity = cosine_similarity(user_item_matrix)
    try:
        target_user_index = user_item_matrix.index.get_loc(target_user_id)
    except KeyError:
        raise ValueError(f"User with Id {target_user_id} not found.")
    user_similarities = user_similarity[target_user_index]
    similar_users_indices = user_similarities.argsort()[::-1][1:]
    recommended_items = []
    for user_index in similar_users_indices:
        rated_by_similar_user = user_item_matrix.iloc[user_index]
        not_rated_by_target_user = (rated_by_similar_user == 0) & (user_item_matrix.iloc[target_user_index] == 0)
        recommended_items.extend(user_item_matrix.columns[not_rated_by_target_user][:top_n])
    recommended_items_details = data[data['productid'].isin(recommended_items)][['name', 'ReviewCount', 'brand', 'image_url', 'Rating']]
    return recommended_items_details.head(10)
def hybrid_recommendations(products_data,users_data, target_user_id, item_name, top_n=10):
    content_based_rec = Content_based_recommendations(products_data, item_name, top_n)
    hybrid_recommendation = content_based_rec
    AUTH_DB_PATH = "Data/database.csv"
    auth_db = pd.read_csv(AUTH_DB_PATH)
    existing_user = auth_db[auth_db['user_id'] == target_user_id]
    if len(existing_user) > 0:
        user_data_db = pd.read_csv("Data/User_data.csv")
        new_user = user_data_db[user_data_db['Id'] == target_user_id]
        if new_user.empty==False:
            collaborative_filtering_rec = Collaborative_based_recommendations(users_data, target_user_id, top_n)
            collaborative_model_filtering_rec = Collaborative_neighbours_based_recommendations(users_data,target_user_id,top_n)
            hybrid_recommendation = pd.concat([content_based_rec,collaborative_model_filtering_rec, collaborative_filtering_rec]).drop_duplicates()
    return hybrid_recommendation.head(10)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Product(BaseModel):
    Rating: float
    ReviewCount: int
    productid: int
    category: str
    brand: str
    name: str
    description: str
    image_url: str
    tags: str
class UserAuth(BaseModel):
    username: str
    password: str
@app.get("/")
def ping():
    return {"status": "ok"}
@app.post("/signin")
def signin(user: UserAuth):
    """
    Authenticate user signin. Creates new user if not exists.
    Expected JSON body:
    {
        "username": "<str>",
        "password": "<str>"
    }
    """
    AUTH_DB_PATH = "Data/database.csv"
    if not os.path.exists(AUTH_DB_PATH):
        pd.DataFrame(columns=['user_id', 'username', 'password']).to_csv(AUTH_DB_PATH, index=False)
    auth_db = pd.read_csv(AUTH_DB_PATH)
    existing_user = auth_db[auth_db['username'] == user.username]
    if len(existing_user) > 0:
        if existing_user.iloc[0]['password'] == user.password:
            return {"message": "Login successful", "user_id": int(existing_user.iloc[0]['user_id'])}
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        new_user_id = 1 if len(auth_db) == 0 else auth_db['user_id'].max() + 1
        new_user = pd.DataFrame([{
            'user_id': new_user_id,
            'username': user.username, 
            'password': user.password
        }])
        new_user.to_csv(AUTH_DB_PATH, mode='a', header=False, index=False)
        return {"message": "New user created successfully", "user_id": int(new_user_id)}
@app.post("/add_to_database")
def add_to_database(user_id: int, product: Product):
    product_dict = {
        "Id": user_id,
        'productid': product.productid,
        'Rating': product.Rating,
        'ReviewCount': product.ReviewCount,
        'category': product.category,
        'brand': product.brand,
        'name': product.name,
        'image_url': product.image_url,
        'description': product.description,
        'tags': product.tags
    }
    new_product_df = pd.DataFrame([product_dict])
    file_path = "Data/User_data.csv"
    write_header = not os.path.isfile(file_path) or os.stat(file_path).st_size == 0

    # Ensure newline at end of file before appending
    if not write_header:
        with open(file_path, "rb+") as f:
            f.seek(-1, os.SEEK_END)
            last_char = f.read(1)
            if last_char != b'\n':
                f.write(b'\n')

    new_product_df.to_csv(file_path, mode='a', header=write_header, index=False)
    return {"message": "Product added successfully."}
@app.get("/getrecommendation")
def get_recommendation(item_name: str, user_id: int):
    """
    Get hybrid recommendations using the provided target user id and item name.
    Query parameters:
    - target_user_id: id of the target user (float)
    - item_name: name of the item to base recommendations on
    Returns a JSON list of recommended products.
    """
    try:
        recommendations = hybrid_recommendations(products_data,users_data,user_id, item_name, top_n=10)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    recommendations = recommendations.replace([np.inf, -np.inf], np.nan)
    recommendations = recommendations.where(pd.notnull(recommendations), None)
    rec_list = recommendations.to_dict(orient="records")
    return {"recommendations": rec_list}
@app.get("/get-all-products")
def get_all_products():
    """
    Get all products from the products.csv file.
    Returns a JSON list of all products.
    """
    try:
        products_data = pd.read_csv("Data/Products.csv")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Products file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    products_data = products_data.replace([np.inf, -np.inf], np.nan).fillna("")
    products_list = products_data.to_dict(orient="records")
    return {"products": products_list}
@app.get("/get-user-products")
def get_user_products(user_id: int):
    """
    Get all products added by a specific user from User_data.csv.
    Query parameter:
    - user_id: ID of the user (int)
    Returns a JSON list of products added by the user.
    """
    try:
        user_data = pd.read_csv("Data/User_data.csv", on_bad_lines='skip', engine='python')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User data file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    user_products = user_data[user_data['Id'] == user_id]
    user_products = user_products.replace([np.inf, -np.inf], np.nan).fillna("")
    products_list = user_products.to_dict(orient="records")
    return {"products": products_list}
@app.delete("/delete_from_cart")
def delete_from_cart(user_id: int, productid: int):
    """
    Delete a product from a user's cart in User_data.csv.
    Query parameters:
    - user_id: ID of the user (int)
    - productid: ID of the product to remove (int)
    """
    file_path = "Data/User_data.csv"
    try:
        user_data = pd.read_csv(file_path, on_bad_lines='skip', engine='python')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User data file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    initial_len = len(user_data)
    user_data = user_data[~((user_data['Id'] == user_id) & (user_data['productid'] == productid))]
    if len(user_data) == initial_len:
        raise HTTPException(status_code=404, detail="Product not found in user's cart.")
    user_data.to_csv(file_path, index=False)
    return {"message": "Product deleted from cart successfully."}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)