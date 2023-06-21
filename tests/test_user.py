from httpx import AsyncClient
from tests.conftest import (test_async_session,
                            create_headers_for_user,
                            create_test_user_in_db,
                            get_test_user_by_id,)



# test creat user
async def test_creste_user(client: AsyncClient):
    user = {"id": 1,
            "email": "test@mail.com",
            "password": "qwerty123"}
    # create user with api
    res = await client.post("/user/", json=user)
    assert res.status_code == 201
    user_res = res.json()
    # test user is in db
    data = await get_test_user_by_id(user["id"])
    assert data is not None
    user_fr_db = data.fetchone()
    assert user_res["id"] == user_fr_db[0]
    assert user_res["email"] == user_fr_db[1]
    assert user_res["is_active"] == user_fr_db[2]
    
# test get user by id with token
async def test_get_user(client: AsyncClient):
    user ={"id": 2,
            "email": "test2@mail.com",
            "password": "qwerty123"}
    
    await create_test_user_in_db(**user)
    res: tuple = await get_test_user_by_id(user["id"])   
    assert res is not None
    user_fr_db = res.fetchone() # this is tuple 0-id, 1-email, 2-is_active
    token = create_headers_for_user(2)
    response = await client.get(f"/user/?user_id=2", headers=token)
    assert response.json()["id"] == user_fr_db[0]
    assert response.json()["email"] == user_fr_db[1]
    assert response.json()["is_active"] == user_fr_db[2]
        
# test delete user from db
async def test_delete_user(client: AsyncClient):
    user = {"id": 3,
            "email": "test3@mail.com",
            "password": "qwerty123",
            }
    await create_test_user_in_db(**user)
    res = await client.delete(f"/user/?user_id={user['id']}",
                        headers=create_headers_for_user(user["id"]))
    
    assert res.status_code == 200
    data: tuple = await get_test_user_by_id(user["id"])
    assert data is not None
    user_fr_db = data.fetchone()
    assert user["id"] == user_fr_db[0] #testing user in db
    assert res.json()["id"] == user_fr_db[0]
    assert res.json()["email"] == user_fr_db[1]
    assert res.json()["is_active"] == user_fr_db[2] == False