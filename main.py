from database import engine
from fastapi import FastAPI
from routers import auth, todos, admin, users
import models
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()

# Add the CORS middleware
origins = [

    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   

#Create the database tables
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

