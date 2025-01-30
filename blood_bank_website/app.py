from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from pymongo import MongoClient
from bson import ObjectId, errors

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['blood_management']
collection = db['blood_types']

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Mission page
@app.route('/mission')
def mission():
    return render_template('mission.html')

# Guidelines page
@app.route('/guidelines')
def guidelines():
    return render_template('guidelines.html')

# Blood Availability page
@app.route('/bloodavail')
def bloodavail():
    blood_types = list(collection.find())
    for blood_type in blood_types:
        blood_type['_id'] = str(blood_type['_id'])  # Convert ObjectId to string for JSON serialization
    return render_template('bloodavail.html', blood_types=blood_types)

# Check Blood Availability API
VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

# Check Blood Availability API
@app.route('/blood_management/check_availability', methods=['POST'])
def check_availability():
    data = request.get_json()
    blood_group = data.get('blood_group')

    # Validate blood group
    if blood_group not in VALID_BLOOD_GROUPS:
        return jsonify({'message': 'Please mention a correct blood group'}), 400

    blood_type = collection.find_one({'type': blood_group})

    # Check if blood group exists in the database
    if blood_type:
        units = int(blood_type.get('unit', 0))  # Default to 0 if 'unit' is missing
        if units > 0:
            return jsonify({'message': 'Yes, the blood is available'})
        else:
            return jsonify({'message': 'Blood is not available'})
    else:
        return jsonify({'message': 'Blood is not available'})

# Other route definitions go here...
@app.route('/index')
def index():
    return render_template('index.html')

    
# History page
@app.route('/history')
def history():
    return render_template('history.html')

# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Admin Login page
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # Simple authentication for demo purposes
            return redirect(url_for('adminpage'))
        else:
            flash('Invalid credentials, please try again.')
            return redirect(url_for('adminlogin'))
    return render_template('adminlogin.html')

# Admin Dashboard page
VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

# Admin Dashboard page
@app.route('/adminpage')
def adminpage():
    blood_types = list(collection.find({'type': {'$in': VALID_BLOOD_GROUPS}}))  # Only find standard types
    for blood_type in blood_types:
        blood_type['_id'] = str(blood_type['_id'])  # Convert ObjectId to string for JSON serialization
    return render_template('adminpage.html', blood_types=blood_types)

# API to add a new blood type
@app.route('/blood_management/blood_types', methods=['POST'])
def add_blood_type():
    data = request.get_json()
    if data['type'] not in VALID_BLOOD_GROUPS:
        return jsonify({'error': 'Invalid blood type. Only standard blood types are allowed.'}), 400

    blood_type = {
        'type': data['type'],
        'unit': data['unit']
    }
    result = collection.insert_one(blood_type)
    blood_type['_id'] = str(result.inserted_id)
    return jsonify(blood_type), 201

# API to update an existing blood type
@app.route('/blood_management/blood_types/<id>', methods=['PUT'])
def update_blood_type(id):
    try:
        data = request.get_json()
        if data['type'] not in VALID_BLOOD_GROUPS:
            return jsonify({'error': 'Invalid blood type. Only standard blood types are allowed.'}), 400
        
        blood_type = {
            'type': data['type'],
            'unit': data['unit']
        }
        result = collection.update_one({'_id': ObjectId(id), 'type': {'$in': VALID_BLOOD_GROUPS}}, {'$set': blood_type})
        if result.matched_count:
            blood_type['_id'] = id
            return jsonify(blood_type), 200
        else:
            return jsonify({'error': 'Blood type not found or not a valid type for editing.'}), 404
    except errors.InvalidId:
        return jsonify({'error': 'Invalid ID format'}), 400

# API to delete a blood type
@app.route('/blood_management/blood_types/<id>', methods=['DELETE'])
def delete_blood_type(id):
    try:
        result = collection.delete_one({'_id': ObjectId(id), 'type': {'$in': VALID_BLOOD_GROUPS}})
        if result.deleted_count:
            return jsonify({'status': 'Deleted'}), 200
        else:
            return jsonify({'error': 'Blood type not found or not a valid type for deletion.'}), 404
    except errors.InvalidId:
        return jsonify({'error': 'Invalid ID format'}), 400

if __name__ == '__main__':
    app.run(debug=True)