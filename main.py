from fastapi import FastAPI
from routers import account_router, restaurant_router, menu_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# default origin of the url
@app.get("/")
def home():
    return {"message":"Smile and Wave Boys!"}

# include all the routes from routers folder
app.include_router(account_router.router)
app.include_router(restaurant_router.router)
app.include_router(menu_router.router)
