from pymongo import MongoClient


dns = "mongodb+srv://sachasereropro_db_user:Europe2511@cluster0.ksm29hm.mongodb.net/?appName=Cluster0"

def connect_to_mongodb():
    try: 
        client = MongoClient(dns, ssl=True)
        
        client.server_info()
        print("Connexion réussie à MongoDB Atlas!")
        
        db = client.search
        print("Base de données 'search' prête à l'utilisation")
        
        return db
    except Exception as e:
        print(f"Erreur de connexion à MongoDB Atlas: {e}")
        return None


connect_to_mongodb()