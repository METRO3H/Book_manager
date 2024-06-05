from typing import Union
from fastapi import FastAPI
from server.request.manga.get_all import Get_All

app = FastAPI()

# Manga
@app.get("/manga/all")
async def run():
   return await Get_All()
