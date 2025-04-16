import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Product {
    productid: number; // Add id field for product identification
    name: string;
    brand: string;
    Rating: number;
    ReviewCount: number;
    image_url: string;
}

function Cart() {
    const [cartItems, setCartItems] = useState<Product[]>([]);
    const userId = localStorage.getItem('userId');

    useEffect(() => {
        const fetchCartItems = async () => {
            try {
                const response = await axios.get('http://localhost:8000/get-user-products', {
                    params: { user_id: userId },
                });
                setCartItems(response.data.products);
            } catch (error) {
                console.error('Error fetching cart items:', error);
            }
        };

        fetchCartItems();
    }, [userId]);

    const handleDelete = async (productId: number) => {
        try {
            await axios.delete(`http://localhost:8000/delete_from_cart?user_id=${userId}&productid=${productId}`);
            setCartItems((prev) => prev.filter((item) => item.productid !== productId));
        } catch (error) {
            console.error('Error deleting item from cart:', error);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <h1 className="text-2xl font-bold mb-4">Your Cart</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cartItems.map((item) => (
                    <div key={item.productid} className="bg-white rounded-lg shadow-md overflow-hidden">
                        <img
                            src={item.image_url.split('|')[0].trim()}
                            alt={item.name}
                            className="w-full h-48 object-cover"
                        />
                        <div className="p-4">
                            <h3 className="text-lg font-semibold mb-2">{item.name}</h3>
                            <p className="text-gray-600 mb-2">{item.brand}</p>
                            <div className="flex items-center">
                                <span className="ml-1">Rating: {item.Rating.toFixed(1)}</span>
                                <span className="ml-2 text-gray-500">({item.ReviewCount} reviews)</span>
                            </div>
                            <button
                                onClick={() => handleDelete(item.productid)}
                                className="mt-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                            >
                                Remove from Cart
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Cart;