from flask import Flask, request, jsonify
import requests
import re
import subprocess
import json

app = Flask(__name__)

# 创建全局的 Session 对象
session = requests.Session()

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
    'name': '123'
}

# 发送 POST 请求以创建工作区
response = session.post(url, headers=headers, json=data)

# 打印响应结果
print(response.status_code)
print(response.json())  # 如果返回的是 JSON 数据，可以直接通过 .json() 方法获取解析后的 Python 对象

# 第二步 链接路由获取数据语内容并进行语料上传、嵌入、更具语料信息chat获取输出、返回数据、删除工作区和语料信息
@app.route('/api/get_details', methods=['POST'])
def get_details():
    try:
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

        # 发送 POST 请求到目标 API
        api_url = 'http://192.168.1.54:3001/api/v1/document/raw-text'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7'
        }

        response = session.post(api_url, json=data_to_send, headers=headers)
        print("response.text:", response.text)
        response_data = response.json()

        # 从响应中提取 'location' 字段的值
        documents = response_data.get('documents', [])
        if not documents:
            return jsonify({"success": False, "data": None, "msg": 'Documents not found in the response'}), 500

        # 提取第一个文档的 'location' 字段
        location = documents[0].get('location', '')
        print("location:", location)  # 增加调试输出

        # 固定提取 custom-documen 至 .json 段的内容
        match = re.search(r'custom-documents[\\/].*?\.json', location)
        if match:
            formatted_location = match.group().replace('\\', '/')
            print("formatted_location:", formatted_location)  # 增加调试输出

            # 调用 curl 命令发送第一个请求
            curl_command1 = [
                'curl', '-X', 'POST', 
                'http://192.168.1.54:3001/api/v1/workspace/123/update-embeddings',
                '-H', 'accept: application/json',
                '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
                '-H', 'Content-Type: application/json',
                '-d', f'{{"adds": ["{formatted_location}"]}}'
            ]
            result1 = subprocess.run(curl_command1, capture_output=True, text=True)
            print("Curl command result 1:", result1.stdout)

        # 调用 curl 命令发送第二个请求
        curl_command2 = [
            'curl', '-X', 'POST',
            'http://192.168.1.54:3001/api/v1/workspace/123/chat',
            '-H', 'accept: application/json',
            '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
            '-H', 'Content-Type: application/json',
            '-d', '{"message": "Please provide detailed information about 74ACT16244: must include product model, brand, category, description, packaging, parameters and other detailed information", "mode": "chat"}'
        ]

        result2 = subprocess.run(curl_command2, capture_output=True, text=True, encoding='utf-8')
        print("Curl command result 2:", result2.stdout)

        json_response = json.loads(result2.stdout)
        text_response = json_response.get("textResponse", "textResponse not found in response")
        print("Text Response:", text_response)

        # 调用 curl 命令发送第三个请求，删除工作区
        curl_command3 = [
            'curl', '-X', 'DELETE',
            'http://192.168.1.54:3001/api/v1/workspace/123',
            '-H', 'accept: */*',
            '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7'
        ]
        result3 = subprocess.run(curl_command3, capture_output=True, text=True)
        print("Curl command result 3:", result3.stdout)

        # 调用 curl 命令发送第四个请求，从系统永久删除嵌入文档嵌入
        curl_command4 = [
            'curl', '-X', 'DELETE',
            'http://192.168.1.54:3001/api/v1/system/remove-documents',
            '-H', 'accept: application/json',
            '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
            '-H', 'Content-Type: application/json',
            '-d', f'{{"names": ["{formatted_location}"]}}'
        ]
        result4 = subprocess.run(curl_command4, capture_output=True, text=True)
        print("Curl command result 4:", result4.stdout)

        # 返回成功提示信息
        success_message = "Data returned successfully!"
        response_data = {
            "success": True,
            "data": text_response,
            "msg": success_message
        }

    except Exception as e:
        # 返回失败提示信息
        error_message = f"数据处理失败：{str(e)}"
        response_data = {
            "success": False,
            "data": None,
            "msg": error_message
        }

    # 设置正确的字符编码为utf-8
    response_json = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
    return response_json, 200, {'Content-Type': 'application/json; charset=utf-8'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
