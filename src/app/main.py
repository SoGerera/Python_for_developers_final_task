import uvicorn
from fastapi import FastAPI

from app.configs.app import settings
from app.api.v1.misc import router as misc_router
from app.api.v1.category_api import router as category_router
from app.api.v1.post_api import router as post_router
from app.api.v1.auth import router as auth_router
from app.api.v1.comment_api import router as comment_router
from app.api.v1.subscription_api import router as subscription_router

app = FastAPI(
    title=settings.app.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.include_router(misc_router, prefix="/api/v1/misc", tags=["misc"])
app.include_router(category_router, prefix="/api/v1/category", tags=["category"])
app.include_router(post_router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(comment_router, prefix="/api/v1/comments", tags=["comments"])
app.include_router(subscription_router, prefix="/api/v1/subscribe", tags=["subscriptions"])

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.app.app_host,
        port=settings.app.app_port,
        reload=True,
    )