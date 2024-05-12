import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import Flask, jsonify, request

app = Flask(__name__)

cred = credentials.Certificate('E:/AOU/grad.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    print("Endpoint: /")
    return 'This is the Wassla App Recommendation System!'

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    try:
        print("Endpoint: /recommendations")
        request_data = request.get_json()
        print("Request Data:", request_data)
        user_id = request_data.get('user_id')
        print("User ID:", user_id)
        if not user_id:
            return jsonify({'error': 'User ID is required in the request body'}), 400
        user_wishlist_ref = db.collection('wishlist').document(user_id).collection('items')
        user_wishlist_docs = user_wishlist_ref.stream()
        user_wishlist = [doc.to_dict() for doc in user_wishlist_docs]

        if not user_wishlist:
            return jsonify({'error': 'User has no items in wishlist'}), 404
        recommendations, categories, most_frequent_category = generate_recommendations(user_wishlist)
        print("Recommendations:", recommendations)

        if not recommendations:
            return jsonify({'message': 'No recommendations found'}), 200

        return jsonify(recommendations)
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

def generate_recommendations(wishlist):
    try:
        categories = set()
        category_counts = {}
        for item in wishlist:
            category = item.get('category')
            categories.add(category)
            category_counts[category] = category_counts.get(category, 0) + 1

        if not categories:
            return [], None, None
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        most_frequent_category = sorted_categories[0][0]
        recommended_products_ref = db.collection('products').document(most_frequent_category).collection('products').limit(3)
        recommended_products_docs = recommended_products_ref.stream()
        recommended_products = [doc.to_dict() for doc in recommended_products_docs]
        return recommended_products, categories, most_frequent_category
    except Exception as e:
        print("Error:", e)
        return [], None, None

if __name__ == '__main__':
    app.run(debug=True)
