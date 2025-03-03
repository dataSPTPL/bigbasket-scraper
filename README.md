# BigBasket Scraper

This script scrapes product data from BigBasket and stores it in a PostgreSQL database.

## Features
- Scrapes product details like brand, price, ratings, and availability.
- Stores data in a PostgreSQL database.

## Requirements
- Python 3.x
- Libraries: `requests`, `beautifulsoup4`, `pandas`, `psycopg2`

## Usage
1. Clone the repository.
2. Install the required libraries: `pip install -r requirements.txt`.
3. Run the script: `python bigbasket_scraper.py`.

## Database Setup
- Create a PostgreSQL database named `bigbasket`.
- Create a table named `products` with the following schema:
  ```sql
  CREATE TABLE products (
      id SERIAL PRIMARY KEY,
      brand VARCHAR(255),
      sponsered VARCHAR(255),
      product VARCHAR(255),
      product_description TEXT,
      ratings VARCHAR(50),
      rating_count VARCHAR(50),
      discounted_price NUMERIC,
      stock_availability VARCHAR(255),
      pack VARCHAR(255),
      product_review TEXT,
      variant_available BOOLEAN,
      offers TEXT
  );
