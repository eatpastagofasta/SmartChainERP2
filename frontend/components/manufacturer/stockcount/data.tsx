import { useState, useEffect } from "react";

export interface StockItem {
  productName: string;
  category: number; // Category ID, since API provides ID
  available: number;
  sold: number;
  demanded: number;
}

export interface CategoryItem {
  category_id: number;
  name: string;
  product_count: number;
  fill: string;
}

const BASE_URL = "http://127.0.0.1:8000/api";

export const useStockData = () => {
  const [stockData, setStockData] = useState<StockItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchStockData = async () => {
      if (!token) {
        setError("No token found. Please log in.");
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`${BASE_URL}/stock/`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) throw new Error("Failed to fetch stock data");

        const data = await response.json();
        console.log("Fetched stock data:", data);

        const formattedData = Array.isArray(data)
          ? data.map((item) => ({
              productName: item.name || "Unknown", // Fix: API returns 'name'
              category: item.category || 0, // Fix: API gives category as ID
              available: item.available_quantity || 0, // Fix: Correct API field
              sold: item.total_shipped || 0, // Fix: Correct API field
              demanded: item.total_required_quantity || 0, // Fix: Correct API field
            }))
          : [];

        setStockData(formattedData);
      } catch (error) {
        console.error("Error fetching stock data:", error);
        setError("Failed to load stock data");
      } finally {
        setLoading(false);
      }
    };

    fetchStockData();
  }, [token]);

  return { stockData, loading, error };
};

export const useCategoryData = () => {
  const [categoryData, setCategoryData] = useState<CategoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategoryData = async () => {
      try {
        const response = await fetch(`${BASE_URL}/category-stock/`); // Fix: Corrected endpoint

        if (!response.ok) throw new Error("Failed to fetch category data");

        const result = await response.json();
        console.log("Fetched category data:", result);

        const data = result.data || []; // Fix: API wraps response in 'data'

        const formattedData: CategoryItem[] = data.map(
          (category: { category_id: number; name: string; product_count: number }, index: number) => ({
            category_id: category.category_id, // Fix: API provides category_id
            name: category.name,
            product_count: category.product_count,
            fill: ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#A28AFF"][index % 5], // Assign colors dynamically
          })
        );

        setCategoryData(formattedData);
      } catch (error) {
        console.error("Error fetching category data:", error);
        setError("Failed to load category data");
      } finally {
        setLoading(false);
      }
    };

    fetchCategoryData();
  }, []);

  return { categoryData, loading, error };
};
