from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Load test data
def load_test_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'seed.json'), 'r') as f:
        return json.load(f)

# In-memory storage for contexts
contexts = load_test_data()

@app.route('/api/account/authenticate', methods=['POST'])
def authenticate():
    """Mock authentication endpoint"""
    data = request.json
    if (data.get('tenancyName') == 'test_tenant' and 
        data.get('usernameOrEmailAddress') == 'test_user' and 
        data.get('password') == 'test_password'):
        return jsonify({
            'result': {
                'accessToken': 'mock_token',
                'expireInSeconds': 3600
            }
        })
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/services/app/Context/GetContexts', methods=['GET'])
def get_contexts():
    """Mock endpoint to get all contexts"""
    max_results = request.args.get('maxResultCount', default=100, type=int)
    return jsonify({
        'result': {
            'items': contexts[:max_results],
            'totalCount': len(contexts)
        }
    })

@app.route('/api/services/app/Context/GetContext', methods=['GET'])
def get_context():
    """Mock endpoint to get a specific context"""
    context_id = request.args.get('id')
    context = next((c for c in contexts if c['id'] == context_id), None)
    if context:
        return jsonify({'result': context})
    return jsonify({'error': 'Context not found'}), 404

@app.route('/api/services/app/Context/CreateContext', methods=['POST'])
def create_context():
    """Mock endpoint to create a new context"""
    data = request.json
    new_context = {
        'id': str(len(contexts) + 1),
        'name': data.get('name'),
        'description': data.get('description', ''),
        'type': data.get('type'),
        'value': data.get('value'),
        'createdAt': datetime.utcnow().isoformat() + 'Z',
        'updatedAt': datetime.utcnow().isoformat() + 'Z',
        'createdBy': 'test_user',
        'updatedBy': 'test_user',
        'organizationUnitId': 'Default',
        'isDeleted': False
    }
    contexts.append(new_context)
    return jsonify({'result': new_context})

@app.route('/api/services/app/Context/UpdateContext', methods=['PUT'])
def update_context():
    """Mock endpoint to update a context"""
    data = request.json
    context_id = data.get('id')
    context = next((c for c in contexts if c['id'] == context_id), None)
    if context:
        context.update({
            'name': data.get('name', context['name']),
            'description': data.get('description', context['description']),
            'type': data.get('type', context['type']),
            'value': data.get('value', context['value']),
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
            'updatedBy': 'test_user'
        })
        return jsonify({'result': context})
    return jsonify({'error': 'Context not found'}), 404

@app.route('/api/services/app/Context/DeleteContext', methods=['DELETE'])
def delete_context():
    """Mock endpoint to delete a context"""
    context_id = request.args.get('id')
    global contexts
    contexts = [c for c in contexts if c['id'] != context_id]
    return jsonify({'result': True})

def start_server():
    """Start the mock server"""
    app.run(host='localhost', port=5000)

if __name__ == '__main__':
    start_server() 