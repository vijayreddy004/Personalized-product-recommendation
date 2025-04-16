import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Search, LogOut, Star } from 'lucide-react';
import axios from 'axios';

interface Product {
  name: string;
  brand: string;
  Rating: number;
  ReviewCount: number;
  image_url: string;
}

function Dashboard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const { logout } = useAuth();
  const userId = localStorage.getItem('userId');
  const navigate = useNavigate();

  const handleAddToCart = async (product: Product) => {
    try {
      await axios.post(
        `http://localhost:8000/add_to_database`,
        {
          Rating: product.Rating,
          ReviewCount: product.ReviewCount,
          productid: 0,
          category: '',
          brand: product.brand,
          name: product.name,
          description: '',
          image_url: product.image_url,
          tags: ''
        },
        {
          params: {
            user_id: userId
          }
        }
      );
      alert(`Added "${product.name}" to cart!`);
    } catch (error) {
      console.error('Error adding product to cart:', error);
    }
  };

  useEffect(() => {
    console.log('User ID:', userId);
    if (!userId) {
      navigate('/signin');
      return;
    }
    fetchAllProducts();
  }, [userId, navigate]);

  const fetchAllProducts = async () => {
    try {
      const response = await axios.get('http://localhost:8000/get-all-products');
      setProducts(response.data.products);
      console.log('tsx', products);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm) return;
    try {
      const response = await axios.get(`http://localhost:8000/getrecommendation`, {
        params: {
          item_name: searchTerm,
          user_id: userId
        }
      });
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const handleLogout = () => {
    logout();
    localStorage.removeItem('userId');
    navigate('/signin');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Product Recommendations</h1>
            </div>
            <div className="flex items-center">
              <Link
                to="/cart"
                className="flex items-center px-4 py-2 text-gray-700 hover:text-gray-900"
              >
                Cart
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center px-4 py-2 text-gray-700 hover:text-gray-900"
              >
                <LogOut className="h-5 w-5 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-4 mb-8">
          <input
            type="text"
            placeholder="Search for products..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button
            onClick={handleSearch}
            className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 flex items-center"
          >
            <Search className="h-5 w-5 mr-2" />
            Search
          </button>
        </div>

        {recommendations.length > 0 && (
          <div className="mb-12">
            <h2 className="text-2xl font-bold mb-4">Recommendations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map((product, index) => (
                <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden">
                  <img
                    src={product['image_url'].split('|')[0].trim()}
                    alt={product.name}
                    className="w-full h-48 object-cover"
                  />
                  <div className="p-4">
                    <h3 className="text-lg font-semibold mb-2">{product.name}</h3>
                    <p className="text-gray-600 mb-2">{product.brand}</p>
                    <div className="flex items-center">
                      <Star className="h-5 w-5 text-yellow-400 fill-current" />
                      <span className="ml-1">{product.Rating.toFixed(1)}</span>
                      <span className="ml-2 text-gray-500">({product.ReviewCount} reviews)</span>
                    </div>
                    <button
                      onClick={() => handleAddToCart(product)}
                      className="mt-2 w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 transition"
                    >
                      Add to Cart
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <h2 className="text-2xl font-bold mb-4">All Products</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden">
              <img
                src={product['image_url'].split('|')[0].trim()}
                alt={product.name}
                className="w-full h-48 object-cover"
              />
              <div className="p-4">
                <h3 className="text-lg font-semibold mb-2">{product.name}</h3>
                <p className="text-gray-600 mb-2">{product.brand}</p>
                <div className="flex items-center">
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <span className="ml-1">{product.Rating.toFixed(1)}</span>
                  <span className="ml-2 text-gray-500">({product.ReviewCount} reviews)</span>
                </div>
                <button
                      onClick={() => handleAddToCart(product)}
                      className="mt-2 w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 transition"
                    >
                      Add to Cart
                    </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
