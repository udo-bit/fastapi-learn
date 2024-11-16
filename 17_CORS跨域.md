## 使用 CORSMiddleware

1. 导入 CORSMiddleware。
2. 创建一个允许的源列表（由字符串组成）。
3. 将其作为「中间件」添加到你的 FastAPI 应用中。
4. 也可以指定后端是否允许凭证，方法和头部。
   4.1 allow_credentials: 指示跨域请求支持 cookies。默认是 False。另外，允许凭证时 allow_origins 不能设定为 ['*']，必须指定源。
   4.2 allow_methods: 指示允许的 HTTP 方法。默认是 ['GET']。
   4.3 allow_headers: 指示允许的 HTTP 头部。默认是 []。
   4.4 max_age - 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def main():
    return {"message": "Hello World"}
```
