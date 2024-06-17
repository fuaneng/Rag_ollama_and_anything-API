from flask import Flask, request, jsonify
import requests
import re
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
    url = 'http://192.168.1.54:3001/api/v1/workspace/new'
    data = {'name': '123'}
    try:
        response = session.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"创建工作区失败: {e}")

def upload_document(data_to_send):
    api_url = 'http://192.168.1.54:3001/api/v1/document/raw-text'
    try:
        response = session.post(api_url, headers=headers, json=data_to_send)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"上传文档失败: {e}")

def update_embeddings(location):
    try:
        match = re.search(r'custom-documents[\\/].*?\.json', location)
        if not match:
            raise ValueError("位置格式不正确")
        formatted_location = match.group().replace('\\', '/')
        url = 'http://192.168.1.54:3001/api/v1/workspace/123/update-embeddings'
        data = {'adds': [formatted_location]}
        response = session.post(url, headers=headers, json=data)
        response.raise_for_status()
        return formatted_location
    except (requests.RequestException, ValueError) as e:
        raise RuntimeError(f"更新嵌入失败: {e}")

def chat():
    url = 'http://192.168.1.54:3001/api/v1/workspace/123/chat'
    data = {
        "message": "Please provide detailed information about 74ACT16244: must include product model, brand, category, description, packaging, parameters and other detailed information",
        "mode": "chat"
    }
    try:
        response = session.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("textResponse", "textResponse not found in response")
    except requests.RequestException as e:
        raise RuntimeError(f"聊天请求失败: {e}")

def delete_workspace():
    url = 'http://192.168.1.54:3001/api/v1/workspace/123'
    try:
        response = session.delete(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"删除工作区失败: {e}")

def remove_documents(location):
    url = 'http://192.168.1.54:3001/api/v1/system/remove-documents'
    data = {'names': [location]}
    try:
        response = session.delete(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"删除文档失败: {e}")

@app.route('/api/get_details', methods=['POST'])
def get_details():
    try:
        if request.is_json:
            data = request.get_json()
            product = data.get('product')
            item = data.get('item')
        else:
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

        create_workspace()
        response_data = upload_document(data_to_send)
        documents = response_data.get('documents', [])
        if not documents:
            return jsonify({"success": False, "data": None, "msg": 'Documents not found in the response'}), 500

        location = documents[0].get('location', '')
        formatted_location = update_embeddings(location)
        text_response = chat()
        remove_documents(formatted_location)
        delete_workspace()

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
