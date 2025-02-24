"""Service for managing product data and specifications."""

from typing import Dict, List, Optional
from pydantic import BaseModel

from ..models.specs import ProductData, TechnicalSpecs
from ..database import get_db_pool

class ProductService:
    """Service for fetching and managing product data."""
    
    def __init__(self, db_pool=None):
        """Initialize the service with optional db pool."""
        self.db_pool = db_pool or get_db_pool()
    
    async def get_products(
        self,
        model_numbers: List[str]
    ) -> Dict[str, ProductData]:
        """
        Get product data for specified model numbers.
        
        Args:
            model_numbers: List of product model numbers
            
        Returns:
            Dictionary mapping model numbers to their data
        """
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT model_number, data
                    FROM products
                    WHERE model_number = ANY($1)
                """
                rows = await conn.fetch(query, model_numbers)
                
                # Process results
                result = {}
                for row in rows:
                    model = row['model_number']
                    data = ProductData.model_validate(row['data'])
                    result[model] = data
                
                return result
                
        except Exception as e:
            raise
    
    async def get_technical_specs(
        self,
        model_number: str
    ) -> TechnicalSpecs:
        """
        Get detailed technical specifications for a product.
        
        Args:
            model_number: Product model number
            
        Returns:
            Technical specifications for the product
        """
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT technical_specs
                    FROM product_specifications
                    WHERE model_number = $1
                """
                row = await conn.fetchrow(query, model_number)
                
                if not row:
                    raise ValueError(f"No specifications found for model {model_number}")
                
                specs = TechnicalSpecs.model_validate(row['technical_specs'])
                return specs
                
        except Exception as e:
            raise
    
    async def search_products(
        self,
        query: str,
        limit: int = 10
    ) -> List[ProductData]:
        """
        Search for products matching query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching products
        """
        try:
            async with self.db_pool.acquire() as conn:
                search_query = """
                    SELECT model_number, data
                    FROM products
                    WHERE 
                        to_tsvector('english', data->>'name' || ' ' || data->>'description')
                        @@ plainto_tsquery('english', $1)
                    LIMIT $2
                """
                rows = await conn.fetch(search_query, query, limit)
                
                results = [
                    ProductData.model_validate(row['data'])
                    for row in rows
                ]
                
                return results
                
        except Exception as e:
            raise 