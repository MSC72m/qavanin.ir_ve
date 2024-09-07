from fastapi import FastAPI
from .router.endpoints import router as api_router


app = FastAPI(
    title="Law Document API",
    description="API for querying and managing law documents",
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Welcome to the Law Document API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
