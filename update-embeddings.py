
from flask import Flask, request, jsonify
import requests
import re
import subprocess

# 第一步：创建新工作区的请求 URL
url = 'http://192.168.1.54:3001/api/v1/workspace/new'

# 请求头部信息
headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
    'Content-Type': 'application/json',
}

# 请求体数据
data = {
    'name': 'My New Workspace'
}

# 发送 POST 请求以创建工作区
response = requests.post(url, headers=headers, json=data)

# 打印响应结果
print(response.status_code)
print(response.json())  # 如果返回的是 JSON 数据，可以直接通过 .json() 方法获取解析后的 Python 对象

###---------------------------------------------


app = Flask(__name__)

@app.route('/api/get_details', methods=['POST'])
def get_details():
    # 获取参数（使用request.form获取）
    product = request.form.get('product')
    item = request.form.get('item')

    # 构建要发送的数据
    data_to_send = {
        "textContent": f"产品: {product}, 项目: {item}",
        "metadata": {
            "product": product,
            "item": item,
            "title": "123",  # 添加 'title' 键值对
            "description": "Details of the product and item",
            "source": "Flask API"
        }
    }

    print("product:", product)
    print("item:", item)
    print(request.form.keys())

    # 发送POST请求到目标API
    api_url = 'http://192.168.1.54:3001/api/v1/document/raw-text'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7'
    }

    try:
        response = requests.post(api_url, json=data_to_send, headers=headers)
        print("response.text:", response.text)
        response_data = response.json()

        # 从响应中提取 'location' 字段的值
        documents = response_data.get('documents', [])
        if not documents:
            return jsonify({'error': 'Documents not found in the response'}), 500

        # 提取第一个文档的 'location' 字段
        location = documents[0].get('location', '')
        print("location:", location)  # 增加调试输出

        # 固定提取 custom-documen 至 .json 段的内容
        match = re.search(r'custom-documents[\\/].*?\.json', location)
        if match:
            formatted_location = match.group().replace('\\', '/')
            print("formatted_location:", formatted_location)  # 增加调试输出

            # 调用 curl 命令发送第二个请求
            curl_command = [
                'curl', '-X', 'POST', 
                'http://192.168.1.54:3001/api/v1/workspace/my-new-workspace/update-embeddings',
                '-H', 'accept: application/json',
                '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
                '-H', 'Content-Type: application/json',
                '-d', f'{{"adds": ["{formatted_location}"]}}'
            ]
            result = subprocess.run(curl_command, capture_output=True, text=True)
            print("Curl command result:", result.stdout)

            return jsonify({
                "first_response": response_data,
                "second_response": result.stdout
            }), 200
        else:
            print("Location format not found in the first response")  # 增加调试输出
            return jsonify({'error': 'Location format not found in the first response'}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'RequestException: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


