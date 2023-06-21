from httpx import AsyncClient
from .conftest import create_test_user_in_db, get_test_user_by_id
from app.oauth2 import verify_access_token
async def test_auth_user(client: AsyncClient):
    user = {"id": 5,
            "email": "aaassds@mail.com",
            "password": "qwerty123",}
    await create_test_user_in_db(**user)
    res = await client.post("/login/", data={"username": {user['email']},
                                        "password": {user['password']}})
    assert res.status_code == 307
    