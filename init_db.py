from pymongo import MongoClient
from config import Config

def init_database():
    try:
        # Connect to MongoDB
        client = MongoClient(Config.MONGO_URI)
        db = client.Readoria
        products = db.products

        # Check if products exist
        if products.count_documents({}) == 0:
            print("Initializing sample products...")
            sample_products = [
                {
                    "name": "Into The Fall",
                    "price": 15.99,
                    "category": "Novel",
                    "description": "A captivating novel about transformation and resilience",
                    "image_url": "/static/images/into the fall-fic.jpg",
                    "stock": 50
                },
                {
                    "name": "On Writing",
                    "price": 15.99,
                    "category": "Memoir",
                    "description": "A memoir of the craft of writing",
                    "image_url": "/static/images/on writing - memoir.jpg",
                    "stock": 50
                },
                {
                    "name": "Metamorphosis",
                    "price": 15.99,
                    "category": "Novel",
                    "description": "Franz Kafka's masterpiece about transformation",
                    "image_url": "/static/images/metamorphsis-fiction.jpg",
                    "stock": 50
                },
                {
                    "name": "World War Z",
                    "price": 15.99,
                    "category": "History",
                    "description": "An oral history of the zombie war",
                    "image_url": "/static/images/world war z -history.jpg",
                    "stock": 50
                },
                {
                    "name": "Atomic Habits",
                    "price": 15.99,
                    "category": "self-motivation",
                    "description": "An easy and proven way to build good habits and break bad ones",
                    "image_url": "/static/images/atomic habits.jpg",
                    "stock": 50
                },
                {
                    "name": "Lets Pretend This Never Happend",
                    "price": 15.99,
                    "category": "Memoir",
                    "description": "A mostly true memoir",
                    "image_url": "/static/images/nothing happend -memoir.jpg",
                    "stock": 50
                },
                {
                    "name": "A People's History of the United States",
                    "price": 15.99,
                    "category": "History",
                    "description": "History from the perspective of the common people",
                    "image_url": "/static/images/people-history.jpg",
                    "stock": 50
                },
                {
                    "name": "Between Two Kingdom",
                    "price": 15.99,
                    "category": "Memoir",
                    "description": "A memoir of a life interrupted",
                    "image_url": "/static/images/between two kingdom-memoir.jpg",
                    "stock": 50
                },
                {
                    "name": "How To Influence and win Friends",
                    "price": 15.99,
                    "category": "self-motivation",
                    "description": "The classic guide to building relationships",
                    "image_url": "/static/images/how to influence and win frds.jpg",
                    "stock": 50
                },
                {
                    "name": "Sapiens: A Brief History of Humankind",
                    "price": 15.99,
                    "category": "History",
                    "description": "A brief history of human evolution and civilization",
                    "image_url": "/static/images/sapiens-history.jpg",
                    "stock": 50
                },
                {
                    "name": "The NoteBook:Nicholas Sparks",
                    "price": 15.99,
                    "category": "Novel",
                    "description": "A story of love lost and found",
                    "image_url": "/static/images/the notebook -fiction.jpg",
                    "stock": 50
                },
                {
                    "name": "Ikigai",
                    "price": 15.99,
                    "category": "self-motivation",
                    "description": "The Japanese secret to a long and happy life",
                    "image_url": "/static/images/ikigai.jpg",
                    "stock": 50
                },
                {
                    "name": "Something in the Wall",
                    "price": 15.99,
                    "category": "Novel",
                    "description": "A thrilling mystery novel",
                    "image_url": "/static/images/something in the wall-fiction.jpg",
                    "stock": 50
                },
                {
                    "name": "Psychology of Money",
                    "price": 15.99,
                    "category": "self-motivation",
                    "description": "Timeless lessons on wealth, greed, and happiness",
                    "image_url": "/static/images/psycology of money.jpg",
                    "stock": 50
                },
                {
                    "name": "The Art Of Being Alone",
                    "price": 15.99,
                    "category": "self-motivation",
                    "description": "Finding peace and purpose in solitude",
                    "image_url": "/static/images/the art of being alone.jpg",
                    "stock": 50
                },
                {
                    "name": "The 48 Laws of Power",
                    "price": 15.99,
                    "category": "self-motivation",
                    "description": "A guide to understanding and wielding power",
                    "image_url": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1694722764i/1303.jpg",
                    "stock": 50
                },
                {
                    "name": "The Five Am Club",
                    "price": 15.99,
                    "category": "self-motivation",
                    "description": "Own your morning, elevate your life",
                    "image_url": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1545910967i/37502596.jpg",
                    "stock": 50
                }
            ]

            # Add description and stock to each product
            for product in sample_products:
                product['price'] = float(product['price'])  # Ensure price is float
                product['stock'] = int(product['stock'])    # Ensure stock is integer
                # Rename 'image' to 'image_url' if it exists
                if 'image' in product:
                    product['image_url'] = product.pop('image')

            result = products.insert_many(sample_products)
            print(f"Successfully inserted {len(sample_products)} products!")
            print(f"Product IDs: {result.inserted_ids}")
        else:
            print(f"Found {products.count_documents({})} existing products in database")

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

if __name__ == "__main__":
    init_database()
