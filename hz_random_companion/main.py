from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from config import settings

app = FastAPI(title="杭州跨时代随机伴侣 - 后端服务", version="1.0.0")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)