# Date    : 2024/7/1 12:28
# File    : test_service.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

def test_stream_output():
    import requests
    import json

    url = "http://localhost:5001/cmict/table-agent"

    payload = json.dumps({
        "request_id": "100220011022121",
        "session_id": "2",
        "query": "2005年和2006年的工业增加值分别是多少？",
        "streaming": True
    })
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url,
                                headers=headers,
                                data=payload,
                                stream=True)

    for line in response.iter_lines():
        str_data = line.decode("UTF-8")
        if "data: " in str_data:
            # 将单引号替换为双引号，并将True和False替换为小写（JSON标准）
            valid_json_str = str_data.replace("'", "\"").\
                replace("True", "true").replace("False", "false")

            # 移除开头的"data: "部分
            valid_json_str = valid_json_str[6:]

            # 解析JSON字符串
            try:
                data = json.loads(valid_json_str)
                # 提取result的内容
                result = data['data']['result']
                print(result, end='')
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")


def test_multiturn():
    import requests
    import json

    url = "http://localhost:5001/cmict/table-agent"

    while True:
        query = input("【用户】：")
        if query == "exit":
            break

        payload = json.dumps({
            "request_id": "100220011022121",
            "session_id": "2",
            "query": query,
            "streaming": True
        })
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url,
                                    headers=headers,
                                    data=payload,
                                    stream=True)

        print(f"【TableAgent】: ", end='')
        for line in response.iter_lines():
            str_data = line.decode("UTF-8")
            if "data: " in str_data:
                # 将单引号替换为双引号，并将True和False替换为小写（JSON标准）
                valid_json_str = str_data.replace("'", "\"").\
                    replace("True", "true").replace("False", "false")

                # 移除开头的"data: "部分
                valid_json_str = valid_json_str[6:]

                # 解析JSON字符串
                try:
                    data = json.loads(valid_json_str)
                    # 提取result的内容
                    result = data['data']['result']
                    print(result, end='')
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")

        print("")


if __name__ == "__main__":
    test_multiturn()
