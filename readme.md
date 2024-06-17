# 使用Flask实现的API接口说明文档

本项目的使用先决条件基于ollama和anything-llm

一个基于Flask框架实现的API接口，该接口通过与外部API交互，完成创建工作区、上传语料、嵌入处理、获取数据以及删除操作的功能。以下是详细的功能说明和使用方法。

## 环境准备

在使用本API之前，请确保您已经安装了以下依赖：

```bash
pip install Flask requests
```

## 代码结构

该API主要由两部分组成：
1. 在启动时发送POST请求创建工作区。
2. 通过`/api/get_details`路由处理POST请求，进行数据上传、嵌入处理、聊天获取信息并最终删除工作区及嵌入文档。

### 第一步：创建新工作区

代码启动时，将自动发送POST请求以创建一个新的工作区。

**请求URL**: `http://192.168.1.54:3001/api/v1/workspace/new`

**请求头部**:
- `accept`: `application/json`
- `Authorization`: `Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7`
- `Content-Type`: `application/json`

**请求体**:
```json
{
    "name": "123"
}
```

**响应处理**:
- 打印响应状态码。
- 打印响应内容（JSON格式）。

### 第二步：处理/api/get_details路由

**路由URL**: `/api/get_details`

**请求方法**: `POST`

**功能说明**:
1. 获取POST请求中的参数`product`和`item`。
2. 构建要发送的数据并发送到目标API以获取文档信息。
3. 提取返回的文档信息中的`location`字段并进行格式化处理。
4. 使用curl命令发送多个POST请求进行数据上传、嵌入处理和信息获取。
5. 删除工作区和嵌入文档。
6. 返回处理结果。

**详细代码逻辑**:

```python
@app.route('/api/get_details', methods=['POST'])
def get_details():
    try:
        # 获取参数
        product = request.form.get('product')
        item = request.form.get('item')

        # 构建发送的数据
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

        # 发送数据到目标API
        api_url = 'http://192.168.1.54:3001/api/v1/document/raw-text'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7'
        }
        response = session.post(api_url, json=data_to_send, headers=headers)
        response_data = response.json()

        # 提取文档的location字段
        documents = response_data.get('documents', [])
        if not documents:
            return jsonify({"success": False, "data": None, "msg": 'Documents not found in the response'}), 500

        location = documents[0].get('location', '')

        # 格式化location字段
        match = re.search(r'custom-documents[\\/].*?\.json', location)
        if match:
            formatted_location = match.group().replace('\\', '/')

            # 发送嵌入更新请求
            curl_command1 = [
                'curl', '-X', 'POST', 
                'http://192.168.1.54:3001/api/v1/workspace/123/update-embeddings',
                '-H', 'accept: application/json',
                '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
                '-H', 'Content-Type: application/json',
                '-d', f'{{"adds": ["{formatted_location}"]}}'
            ]
            result1 = subprocess.run(curl_command1, capture_output=True, text=True)

        # 发送聊天请求获取信息
        curl_command2 = [
            'curl', '-X', 'POST',
            'http://192.168.1.54:3001/api/v1/workspace/123/chat',
            '-H', 'accept: application/json',
            '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
            '-H', 'Content-Type: application/json',
            '-d', '{"message": "Please provide detailed information about 74ACT16244: must include product model, brand, category, description, packaging, parameters and other detailed information", "mode": "chat"}'
        ]
        result2 = subprocess.run(curl_command2, capture_output=True, text=True, encoding='utf-8')

        # 解析聊天请求的响应
        json_response = json.loads(result2.stdout)
        text_response = json_response.get("textResponse", "textResponse not found in response")

        # 删除工作区
        curl_command3 = [
            'curl', '-X', 'DELETE',
            'http://192.168.1.54:3001/api/v1/workspace/123',
            '-H', 'accept: */*',
            '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7'
        ]
        result3 = subprocess.run(curl_command3, capture_output=True, text=True)

        # 删除嵌入文档
        curl_command4 = [
            'curl', '-X', 'DELETE',
            'http://192.168.1.54:3001/api/v1/system/remove-documents',
            '-H', 'accept: application/json',
            '-H', 'Authorization: Bearer F8MRZSD-5HTMHTH-M0NJK2B-N9DQWJ7',
            '-H', 'Content-Type: application/json',
            '-d', f'{{"names": ["{formatted_location}"]}}'
        ]
        result4 = subprocess.run(curl_command4, capture_output=True, text=True)

        # 返回成功信息
        success_message = "Data returned successfully!"
        response_data = {
            "success": True,
            "data": text_response,
            "msg": success_message
        }

    except Exception as e:
        # 返回错误信息
        error_message = f"数据处理失败：{str(e)}"
        response_data = {
            "success": False,
            "data": None,
            "msg": error_message
        }

    # 设置响应编码为utf-8
    response_json = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
    return response_json, 200, {'Content-Type': 'application/json; charset=utf-8'}
```

### 启动服务

使用以下命令启动Flask服务：

```bash
python your_script_name.py
```

服务将会在`http://0.0.0.0:5000`运行，您可以通过POST请求访问`/api/get_details`路由来获取相关数据。

## 使用示例

### 请求示例

使用`curl`命令发送请求：

```bash
curl -X POST http://0.0.0.0:5000/api/get_details -d "product=example_product&item=example_item"
```

### 响应示例

```json
{
    "success": true,
    "data": "Detailed information about the product and item",
    "msg": "Data returned successfully!"
}
```

## 注意事项

1. 确保API服务器地址和端口号正确配置。
2. 确保`Authorization`头部的`Bearer`令牌有效。
3. 在正式环境中，建议对敏感信息进行加密处理。
4. 本示例代码中的硬编码值仅供测试使用，在实际应用中应根据具体需求进行动态配置。#   R a g _ o l l a m a _ a n d _ a n y t h i n g - A P I  
 