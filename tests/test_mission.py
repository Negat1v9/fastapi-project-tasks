from httpx import AsyncClient
from .conftest import (create_task_in_db,
                       create_test_user_in_db,
                       get_test_user_by_id,
                       create_headers_for_user)

async def test_create_task(client: AsyncClient):
    user = {"id": 6,
            "email": "jfhgkksf@mail.com",
            "password": "qwerty123",}
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    owner_id = user_fr_db.fetchone()[0]
    task = {"id": 1,
            "task": "Test task",}
    res = await client.post("/task/", json=task, 
        headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    assert res.json()["id"] == task["id"]
    assert res.json()["owner_id"] == owner_id   
    
async def test_get_all_task(client: AsyncClient):
    user = {"id": 7,
            "email": "assgkad@mail.com",
            "password": "qwerty123",} 
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    owner_id = user_fr_db.fetchone()[0]
    for i in range(2, 4):
        task = {"id": i,
                "task": "Test test",
                "owner_id": owner_id,}
        await create_task_in_db(**task)
    res = await client.get("/task/", 
                headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    data_res = res.json()
    assert data_res[0]["id"] == 2
    assert data_res[1]["id"] == 3
    assert data_res[0]["owner_id"] == owner_id
    assert data_res[1]["owner_id"] == owner_id
    
async def test_patch_task(client: AsyncClient):
     user = {"id": 8,
            "email": "aaaayyyBd@mail.com",
            "password": "qwerty123",}
     await create_test_user_in_db(**user)
     user_fr_db = await get_test_user_by_id(user["id"])
     assert user_fr_db is not None
     owner_id = user_fr_db.fetchone()[0]
     task = task = {"id": 4,
                "task": "Test test",
                "owner_id": owner_id,}
     task_fr_db = await create_task_in_db(**task)
     assert task_fr_db is not None
     assert task["owner_id"] == task_fr_db.fetchone()[1]
     res = await client.patch("/task/", json={"id": task["id"], 
                                              "task": "hello",},
                    headers=create_headers_for_user(user["id"]))
     assert res.status_code == 200
     assert res.json()["task"] == "hello"
     assert res.json()["owner_id"] == user["id"]
     
async def test_delete_task(client: AsyncClient):
    user = {"id": 9,
            "email": "aaaayjsBd@mail.com",
            "password": "qwerty123",}
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    owner_id = user_fr_db.fetchone()[0]
    task = {"id": 5,
            "task": "Hashahha",
            "owner_id": owner_id,}
    task_fr_db = await create_task_in_db(**task) # 0-task, 1-owner_id, 2-task_id
    assert task_fr_db is not None
    task_id = task_fr_db.fetchone()[2]
    res = await client.delete(f"/task/?task_id={task_id}", 
        headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    