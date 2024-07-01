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
        "query": "黑龙江第一产业占比均值是多少",
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
        print(line.decode("UTF-8"))


if __name__ == "__main__":
    test_stream_output()
