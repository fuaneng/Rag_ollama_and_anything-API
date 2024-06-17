from flask import Flask, request, jsonify
import requests
import re
import subprocess
import json

app = Flask(__name__)

# 创建全局的 Session 对象
session = requests.Session()

# 请求头部信息
headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
    'Content-Type': 'application/json',
}

def create_workspace():
    # 第一步：创建新工作区的请求 URL
    url = 'http://192.168.1.54:3001/api/v1/workspace/new'
    data = {'name': '123'}
    
    response = session.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception("Failed to create workspace")
    
    return response.json()

def upload_document(data_to_send):
    api_url = 'http://192.168.1.54:3001/api/v1/document/raw-text'
    response = session.post(api_url, json=data_to_send, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to upload document")
    
    return response.json()

def update_embeddings(location):
    formatted_location = re.search(r'custom-documents[\\/].*?\.json', location).group().replace('\\', '/')
    curl_command = [
        'curl', '-X', 'POST', 
        'http://192.168.1.54:3001/api/v1/workspace/123/update-embeddings',
        '-H', 'accept: application/json',
        '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
        '-H', 'Content-Type: application/json',
        '-d', f'{{"adds": ["{formatted_location}"]}}'
    ]
    result = subprocess.run(curl_command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Failed to update embeddings")
    
    return formatted_location

def chat():
    curl_command = [
        'curl', '-X', 'POST',
        'http://192.168.1.54:3001/api/v1/workspace/123/chat',
        '-H', 'accept: application/json',
        '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
        '-H', 'Content-Type: application/json',
        '-d', '{"message": "Please provide detailed information about 74ACT16244: must include product model, brand, category, description, packaging, parameters and other detailed information", "mode": "chat"}'
    ]
    result = subprocess.run(curl_command, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        raise Exception("Failed to chat")
    
    return json.loads(result.stdout).get("textResponse", "textResponse not found in response")

def delete_workspace():
    curl_command = [
        'curl', '-X', 'DELETE',
        'http://192.168.1.54:3001/api/v1/workspace/123',
        '-H', 'accept: */*',
        '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7'
    ]
    result = subprocess.run(curl_command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Failed to delete workspace")

def remove_documents(location):
    curl_command = [
        'curl', '-X', 'DELETE',
        'http://192.168.1.54:3001/api/v1/system/remove-documents',
        '-H', 'accept: application/json',
        '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
        '-H', 'Content-Type: application/json',
        '-d', f'{{"names": ["{location}"]}}'
    ]
    result = subprocess.run(curl_command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Failed to remove documents")

@app.route('/api/get_details', methods=['POST'])
def get_details():
    try:
        product = request.form.get('product')
        item = request.form.get('item')

        data_to_send = {
            "textContent": f"产品: {product}, 项目: {item}",
            "metadata": {
                "product": product,
                "item": item,
                "title": "123",
                "description": "Details of the product and item",
                "source": "Flask API"
            }
        }

        workspace = create_workspace()
        response_data = upload_document(data_to_send)
        documents = response_data.get('documents', [])
        if not documents:
            return jsonify({"success": False, "data": None, "msg": 'Documents not found in the response'}), 500

        location = documents[0].get('location', '')
        formatted_location = update_embeddings(location)
        text_response = chat()
        delete_workspace()
        remove_documents(formatted_location)

        response_data = {
            "success": True,
            "data": text_response,
            "msg": "Data returned successfully!"
        }

    except Exception as e:
        response_data = {
            "success": False,
            "data": None,
            "msg": f"数据处理失败：{str(e)}"
        }

    response_json = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
    return response_json, 200, {'Content-Type': 'application/json; charset=utf-8'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
