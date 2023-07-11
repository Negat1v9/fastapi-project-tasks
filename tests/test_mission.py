import time
from httpx import AsyncClient
from .conftest import (create_task_in_db,
                       create_test_user_in_db,
                       get_test_user_by_id,
                       create_headers_for_user,
                       create_user_not_id,
                       test_async_session)

from app.group.group_action import (_create_group_users,
                                         _add_user_in_group, _create_group_task)

async def test_create_task(client: AsyncClient):
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    owner_id = user_fr_db.id
    task = {"id": 1,
            "task": "Test task",}
    res = await client.post("/task/", json=task, 
        headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    assert res.json()["id"] == task["id"]
    assert res.json()["owner_id"] == owner_id   
    
async def test_get_all_task(client: AsyncClient):
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    owner_id = user_fr_db.id
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
     user: dict = create_user_not_id()
     await create_test_user_in_db(**user)
     user_fr_db = await get_test_user_by_id(user["id"])
     assert user_fr_db is not None
     owner_id = user_fr_db.id
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
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    owner_id = user_fr_db.id
    task = {"id": 5,
            "task": "Hashahha",
            "owner_id": owner_id,}
    task_fr_db = await create_task_in_db(**task) # 0-task, 1-owner_id, 2-task_id
    assert task_fr_db is not None
    task_id = task_fr_db.fetchone()[2]
    res = await client.delete(f"/task/?task_id={task_id}", 
        headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    assert res.json() == task["id"]
    
async def test_create_group(client: AsyncClient):
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    res = await client.post("/group/create", json={"name": "Test"},
            headers=create_headers_for_user(user["id"]))
    assert res.status_code == 201
    assert res.json()["name"] == "Test"
    assert res.json()["manager_id"] == user["id"]
    
async def test_add_user_in_group(client: AsyncClient):
    # owner of group
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    new_user_in_group: dict = create_user_not_id()
    await create_test_user_in_db(**new_user_in_group)
    group = await _create_group_users(test_async_session(), user["id"])
    assert group is not None
    assert group.manager_id == user["id"]
    new_group = {"user_id": new_user_in_group["id"],
                "group_id": group.id}
    res = await client.post("/group/add/user", json=new_group,
            headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    assert res.json()["user_id"] == new_user_in_group["id"]
    assert res.json()["group_id"] == group.id
    
async def test_get_all_users_group(client: AsyncClient):
    # owner group
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    new_user_in_group: dict = create_user_not_id()
    await create_test_user_in_db(**new_user_in_group)
    group = await _create_group_users(test_async_session(), user["id"], "GroupName")
    assert group is not None
    assert group.name == "GroupName"
    # add user in group
    user_in_group = await _add_user_in_group(test_async_session(), 
                        new_user_in_group["id"], group.id)
    assert user_in_group is not None
    res = await client.get("group/user",
                headers=create_headers_for_user(new_user_in_group["id"]))
    assert res.status_code == 200
    data: list = res.json()
    assert data[0]["user_id"] == new_user_in_group["id"]
    assert data[0]["group"]["name"] == "GroupName"
    
async def test_delete_user_fr_group(client: AsyncClient):
    # owner group
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    new_user_in_group: dict = create_user_not_id()
    await create_test_user_in_db(**new_user_in_group)
    group = await _create_group_users(test_async_session(), user["id"])
    assert group is not None
    user_in_group = await _add_user_in_group(test_async_session(), 
                        new_user_in_group["id"], group.id)
    assert user_in_group is not None
    res = await client.delete(
    f"/group/drop/user?del_user_id={new_user_in_group['id']}&"\
        f"group_id={group.id}",
                headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    
async def test_create_group_task(client: AsyncClient):
    # owner group
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    group = await _create_group_users(test_async_session(), user["id"])
    user_in_group = await _add_user_in_group(test_async_session(), user["id"],
                                             group.id)
    assert user_in_group.user_id == user["id"]
    assert group is not None
    new_task: dict = {"task": "Simple task",
                      "group_id": group.id,}
    res = await client.post("/group/add/task", json=new_task,
                headers=create_headers_for_user(user["id"]))
    assert res.status_code == 201
    data = res.json()
    assert data["task"] == "Simple task"
    assert data["owner_id"] == user["id"]
    
async def test_get_all_group_task(client: AsyncClient):
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    group = await _create_group_users(test_async_session(), user["id"], "TestName")
    user_in_group = await _add_user_in_group(test_async_session(), user["id"], group.id)
    assert user_in_group is not None
    task: dict = {"task": "Text",
                  "group_id": group.id}
    task_in_db = await _create_group_task(test_async_session(), user["id"], **task)
    assert task_in_db is not None
    res = await client.get(f"/group/all/task?group_id={group.id}", 
            headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    tasks = res.json()
    assert tasks[0]["task"] == task["task"]
    assert tasks[0]["owner"]["id"] == user["id"]
    
async def tets_edit_group_task(client: AsyncClient):
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    group = await _create_group_users(test_async_session(), user["id"])
    user_in_group = await _add_user_in_group(test_async_session(), user["id"],
                                             group.id)
    assert user_in_group.user_id == user["id"]
    assert group is not None
    task: dict = {"task": "One Task",
                  "group_id": group.id}
    task_in_db = await _create_group_task(test_async_session(), user["id"], **task)
    assert task_in_db is not None
    edit_task: dict = {"task_id": task_in_db.id,
                       "task": "Two task"}
    res = await client.patch("/group/edit/task", json=edit_task,
                headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    assert res.json()["task"] == edit_task["task"]
    assert res.json()["id"] == edit_task["task_id"]
    
async def test_delete_group_task(client: AsyncClient):
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    group = await _create_group_users(test_async_session(), user["id"])
    user_in_group = await _add_user_in_group(test_async_session(), user["id"],
                                             group.id)
    assert user_in_group.user_id == user["id"]
    assert group is not None
    task: dict = {"task": "To Delete",
                  "group_id": group.id}
    task_in_db = await _create_group_task(test_async_session(), user["id"], **task)
    
    res = await client.delete(f"/group/delete/task?task_id={task_in_db.id}",
                headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    assert res.json() == task_in_db.id
    
async def test_edit_group(client: AsyncClient):
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    group = await _create_group_users(test_async_session(), user["id"], "NameGroup")
    user_in_group = await _add_user_in_group(test_async_session(), user["id"],
                                             group.id)
    assert user_in_group.user_id == user["id"]
    assert group is not None
    new_group_params = {"name": "SecondName",
                        "is_open": "True"}
    res = await client.patch(f"/group/edit/{group.id}", json=new_group_params,
                    headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["id"] == group.id
    assert res_data["name"] == new_group_params["name"]
    assert res_data["is_open"] == True
    
async def test_delete_group(client: AsyncClient):
    user: dict = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    group = await _create_group_users(test_async_session(), user["id"], "NameGroup")
    user_in_group = await _add_user_in_group(test_async_session(), user["id"],
                                             group.id)
    assert user_in_group.user_id == user["id"]
    assert group is not None
    res = await client.delete(f"/group/drop/group/{group.id}",
            headers=create_headers_for_user(user["id"]))
    assert res.status_code == 200
    assert res.json()["status"] == "success"