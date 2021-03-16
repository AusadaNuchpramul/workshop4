import uvicorn
from fastapi import FastAPI, Path, Query, HTTPException
from starlette.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from database.mongodb import MongoDB
from config.development import config
from model.Tree import createShoptreeModel, updateShoptreeModel

mongo_config = config["mongo_config"]
mongo_db = MongoDB(
    mongo_config["host"],
    mongo_config["port"],
    mongo_config["user"],
    mongo_config["password"],
    mongo_config["auth_db"],
    mongo_config["db"],
    mongo_config["collection"],
)
mongo_db._connect()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("trees/")
def index():
    return JSONResponse(content={"message": "Trees Info"}, status_code=200)


@app.get("/trees/")
def get_trees(
    sort_by: Optional[str] = None,
    order: Optional[str] = Query(None, min_length=3, max_length=3),
):

    try:
        result = mongo_db.find(sort_by, order)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.get("/trees/{tree_id}")
def get_trees_by_id(tree_id: str = Path(None, min_length=3, max_length=3)):
    try:
        result = mongo_db.find_one(tree_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if result is None:
        raise HTTPException(status_code=404, detail="tree Id not found !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.post("/trees")
def create_trees(tree: createShoptreeModel):
    try:
        tree_id = mongo_db.create(tree)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "tree_id": tree_id,
            },
        },
        status_code=201,
    )


@app.patch("/trees/{tree_id}")
def update_trees(
    tree: updateShoptreeModel,
    tree_id: str = Path(None, min_length=3, max_length=3),
):
    print("tree", tree)
    try:
        updated_tree_id, modified_count = mongo_db.update(tree_id, tree)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Tree Id: {updated_tree_id} is not update want fields",
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "tree_id": updated_tree_id,
                "modified_count": modified_count,
            },
        },
        status_code=200,
    )


@app.delete("/trees/{tree_id}")
def delete_trees_by_id(tree_id: str = Path(None, min_length=3, max_length=3)):
    try:
        deleted_tree_id, deleted_count = mongo_db.delete(tree_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if deleted_count == 0:
        raise HTTPException(
            status_code=404, detail=f"Tree Id: {deleted_tree_id} is not Delete"
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "tree_id": deleted_tree_id,
                "deleted_count": deleted_count,
            },
        },
        status_code=200,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3001, reload=True)
