## 1. 基本使用

使用 Cookie 函数显示声明 Cookie 参数

```python
from typing import Annotated

from fastapi import Cookie, FastAPI

app = FastAPI()


@app.get("/items/")
async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    return {"ads_id": ads_id}
```

## 2. 使用 Pydantic 封装 Cookie

```python
class Cookies(BaseModel):
    # 禁止额外的cookie字段
    model_config = {"extra": "forbid"}
    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@app.get("/items/")
async def read_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies
```
