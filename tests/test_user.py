from httpx import AsyncClient
from tests.conftest import (create_headers_for_user,
                            create_test_user_in_db,
                            get_test_user_by_id,
                            create_user_not_id)



# test creat user
async def test_creste_user(client: AsyncClient):
    user = create_user_not_id()
    id = user.pop("id")
    # create user with api
    res = await client.post("/user/", json=user)
    assert res.status_code == 201
    user_res = res.json()
    id = user_res["id"]
    # test user is in db
    user_fr_db = await get_test_user_by_id(id)
    # assert data is not None
    assert user_res["id"] == user_fr_db.id
    print(user_fr_db)
    assert user_res["first_name"] == user_fr_db.first_name
    assert user_res["last_name"] == user_fr_db.last_name
    assert user_res["email"] == user_fr_db.email
    
# test get user by id with token
async def test_get_user(client: AsyncClient):
    user = create_user_not_id()
    await create_test_user_in_db(**user)
    user_fr_db = await get_test_user_by_id(user["id"])   
    assert user_fr_db is not None
    token = create_headers_for_user(user["id"])
    response = await client.get(f"/user/?user_id={user['id']}", headers=token)
    user_res = response.json()
    assert user_res["id"] == user_fr_db.id
    assert user_res["first_name"] == user_fr_db.first_name
    assert user_res["last_name"] == user_fr_db.last_name
    assert user_res["email"] == user_fr_db.email
        
# test delete user from db
async def test_delete_user(client: AsyncClient):
    user = create_user_not_id()
    await create_test_user_in_db(**user)
    res = await client.delete(f"/user/?user_id={user['id']}",
                        headers=create_headers_for_user(user["id"]))
    
    assert res.status_code == 200
    user_fr_db = await get_test_user_by_id(user["id"])
    assert user_fr_db is not None
    user_res = res.json()
    assert user_res["id"] == user_fr_db.id
    assert user_res["first_name"] == user_fr_db.first_name
    assert user_res["last_name"] == user_fr_db.last_name
    assert user_res["email"] == user_fr_db.email