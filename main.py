from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.users import user_router
from app.auth import auth_router
from app.missions import mission_router
from app.group import group_router

app = FastAPI(title="Todo List App")

origins = ["http://localhost:8000",
           "http://127.0.0.1:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

app.include_router(auth_router.auth_router)
app.include_router(user_router.router)
app.include_router(mission_router.router)
app.include_router(group_router.router)

@app.get("/")
async def root():
    return{"message": "This is Todo list app"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
