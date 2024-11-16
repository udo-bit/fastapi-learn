## 1. 基本使用

- 使用 Header 函数声明一个参数为 Header 参数
- 默认情况下，Header 把参数名中的字符由下划线（\_）改为连字符（-）来提取并存档请求头
- 如需禁用下划线自动转换为连字符，可以把 Header 的 convert_underscores 参数设置为 False
- Header 不用区分大小写
- 类型声明中可以使用 list 定义多个请求头

```python
@app.get("/items/")
async def read_items(
    user_agent: Annotated[str | None, Header()] = None,
    strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
    x_token: Annotated[list[str] | None, Header()] = None,
):
    return {"User-Agent": user_agent}
```

## 2. 使用 Pydantic 封装 Header 参数

```python

class CommonHeaders(BaseModel):
    model_config = {"extra": "forbid"}

    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []

@app.get("/items/")
async def read_items(headers: Annotated[CommonHeaders, Header()]):
    return headers
```
