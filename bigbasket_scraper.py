import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import psycopg2
from psycopg2 import sql

base_url = "https://www.bigbasket.com/ps/?q=rusk&nc=as&page="
headers = {"User-Agent": "Mozilla/5.0"}

all_data = []
page = 1

while True:
    url = base_url + str(page)
    print(f"Fetching: {url}")  # Debugging URL requests
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    parent_container = soup.find('div', class_="grid grid-flow-col gap-x-6 relative mt-5 pb-5 border-t border-dashed border-silverSurfer-400")
    if not parent_container:
        print("No more products found, stopping.")
        break

    product_containers = parent_container.find_all('div', class_="SKUDeck___StyledDiv-sc-1e5d9gk-0 eA-dmzP")
    
    for container in product_containers:
        brand_elem = container.find('span', class_='Label-sc-15v1nk5-0 BrandName___StyledLabel2-sc-hssfrl-1 gJxZPQ keQNWn')
        brand = brand_elem.text.strip() if brand_elem else "N/A"
        
        brand_sponsered = container.find('span',class_ ='Label-sc-15v1nk5-0 Tags___StyledLabel2-sc-aeruf4-1 gJxZPQ ixttPj')
        sponsered =brand_sponsered.text.strip() if brand_sponsered else "N/A"
        
        product_elem = container.find('h3', class_='block m-0 line-clamp-2 font-regular text-base leading-sm text-darkOnyx-800 pt-0.5 h-full')
        product = product_elem.text.strip() if product_elem else "N/A"

        rating_elem = container.find('span', class_='Label-sc-15v1nk5-0 ReviewsAndRatings___StyledLabel-sc-2rprpc-1 gJxZPQ egHBA-d')
        rating = rating_elem.text.strip() if rating_elem else "N/A"
        
        rating_count_elem = container.find('span', class_='Label-sc-15v1nk5-0 gJxZPQ')
        rating_count = rating_count_elem.text.strip() if rating_count_elem else "N/A"
        
        price_elem = container.find('span', class_='Label-sc-15v1nk5-0 Pricing___StyledLabel-sc-pldi2d-1 gJxZPQ AypOi')
        discounted_price = price_elem.text.strip() if price_elem else "N/A"

        discounted_price = price_elem.text.strip() if price_elem else "N/A"
        discounted_price = re.sub(r"[^\d.]", "", discounted_price)  # Remove non-numeric characters except decimal point

        availability = container.find('span',class_='Label-sc-15v1nk5-0 Tags___StyledLabel2-sc-aeruf4-1 gJxZPQ gPgOvC')
        stock_availability=availability.text.strip() if availability else "N/A"
        
        pack_elem = container.find('div', class_='py-1.5 xl:py-1')
        pack = pack_elem.text.strip() if pack_elem else "N/A"
        variant = pack_elem.find('button') is not None if pack_elem else False
        
        product_url= container.find('a',class_='h-full',href=True)
        product_URL= "https://www.bigbasket.com" + product_url['href'] if product_url else "N/A"
        
        if product_url != "N/A":
            print(f"Fetching product details from: {product_URL}")
            product_response = requests.get(product_URL, headers=headers)
            product_soup = BeautifulSoup(product_response.text, "html.parser")

            # Example: Scrape product description
            description_elem = product_soup.find('p')
            description = description_elem.text.strip() if description_elem else "N/A"
            
            reviews = product_soup.find_all('div', class_='pt-2.5 pb-4 text-md leading-md text-darkOnyx-600')
            product_review = [review.text.strip() for review in reviews] if reviews else ["N/A"]
            all_reviews = " | ".join(product_review)

            offers = product_soup.find_all('span', class_='Label-sc-15v1nk5-0')

            formatted_offers = []

            for offer in offers:
                strong_tags = offer.find_all('strong')
                if len(strong_tags) >= 2:
                    main_offer = strong_tags[0].text.strip()
                    terms = strong_tags[1].text.strip()
                    formatted_offers.append(f"{main_offer} - T&C : {terms}")

                else:
                    description = "N/A"
        
        
        all_data.append({
            'Brand': brand,
            'Sponsered': sponsered,
            'Product': product,
            'Product Decription':description,
            'Ratings': rating,
            'Rating Count': rating_count,
            'Discounted Price': discounted_price,
            'Discount': discount,
            'Stock Availability': stock_availability,
            'Pack': pack,
            'Product review':all_reviews,
            'Variant Available': variant,
            'Offers': formatted_offers
        })
    
    print(f"Scraped {len(product_containers)} products from page {page}")
    page += 1
    time.sleep(2)  # Prevent rate limiting

# Convert to DataFrame
df = pd.DataFrame(all_data)

# Database connection details
conn = psycopg2.connect(
    dbname="bigbasket",  # Your database name
    user="your_username",  # Your PostgreSQL username
    password="your_password",  # Your PostgreSQL password
    host="localhost",  # Your database host (e.g., localhost or cloud host)
    port="5432"  # Default PostgreSQL port
)
cursor = conn.cursor()

# Insert data into PostgreSQL
for data in all_data:
    insert_query = sql.SQL("""
        INSERT INTO products (
            brand, sponsered, product, product_description, ratings, rating_count,
            discounted_price, stock_availability, pack, product_review, variant_available, offers
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """)
    cursor.execute(insert_query, (
        data['Brand'], data['Sponsered'], data['Product'], data['Product Decription'],
        data['Ratings'], data['Rating Count'], data['Discounted Price'],
        data['Stock Availability'], data['Pack'], data['Product review'],
        data['Variant Available'], data['Offers']
    ))
    conn.commit()

cursor.close()
conn.close()
print("Data inserted into PostgreSQL successfully!")
