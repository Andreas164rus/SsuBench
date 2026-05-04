import pytest


@pytest.mark.anyio
async def test_create_task(customer_first_token, client):
    """Проверка создания заказчиком задачи"""
    response = await client.post(
        "/task/create/",
        json={"title": "Test Task", "description": "Desc", "price": 50},
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    assert response.json() == {
        "title": "Test Task",
        "description": "Desc",
        "price": 50.0,
        "id": 1,
        "selected_executor_id": None,
        "done_executor": False,
        "done_customer": False,
    }


# @pytest.mark.anyio
# async def test_get_all_tasks(created_task, executor_first_token, client):
#     response = await client.get(
#         "/task/all/?page=1&size=50",
#         headers={"Authorization": f"Bearer {executor_first_token}"},
#     )
# assert {
#     "items": [
#         {
#             "title": "Test Task",
#             "description": "Desc",
#             "price": 100.0,
#             "selected_executor_id": None,
#         }
#     ],
#     "total": 1,
#     "page": 1,
#     "size": 50,
#     "pages": 1,
# } == response.json()


@pytest.mark.anyio
async def test_repeat_response_task(created_task, executor_first_token, client):
    """Проверка невозможности несколько раз откликнуться на одну и ту же задачу"""
    response = await client.post(
        f"/bid/{created_task['id']}/response/",
        headers={"Authorization": f"Bearer {executor_first_token}"},
    )
    response = await client.post(
        f"/bid/{created_task['id']}/response/",
        headers={"Authorization": f"Bearer {executor_first_token}"},
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_select_executor_for_task(
    created_task, customer_first_token, response_for_task, executor_first_token, client
):
    """Проверка выбора исполнителя для задачи заказчком"""
    response = await client.post(
        f"/task/{created_task['id']}/user/{4}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    assert response.json()["selected_executor_id"] == 4


@pytest.mark.anyio
async def test_select_executor_for_task_where_has_another_executor(
    created_task, customer_first_token, response_for_task, executor_first_token, client
):
    """Проверка выбора другого исполнителя для задачи, на которой уже закреплен другой исполнитель заказчком"""
    response = await client.post(
        f"/task/{created_task['id']}/user/{4}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    response = await client.post(
        f"/task/{created_task['id']}/user/{5}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_select_executor_who_didnt_response_for_task(
    created_task, customer_first_token, executor_first_token, client
):
    """Проверка выбора исполнителя, который не записывался на задачу, для задачи заказчком"""
    response = await client.post(
        f"/task/{created_task['id']}/user/{4}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_done_executor_his_task(
    created_task,
    selected_executor_for_a_task,
    executor_first_token,
    client,
):
    """Проверка завершения задачи исполнителем"""
    response = await client.post(
        f"/task/done_task_executor/{created_task['id']}/",
        headers={"Authorization": f"Bearer {executor_first_token}"},
    )
    assert response.json()["done_executor"]


@pytest.mark.anyio
async def test_done_customer_his_task(
    created_task,
    done_executor_task,
    executor_first_token,
    customer_first_token,
    client,
):
    """Проверка завершения задачи заказчиком"""
    response = await client.post(
        f"/task/done_task_customer/{created_task['id']}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    assert response.json()["done_customer"]


# @pytest.mark.anyio
# async def test_done_task_by_cutomer(
#     created_task,
#     response_for_task,
#     customer_first_token,
#     executor_first_token,
#     done_executor_task,
#     client,
# ):

#     print(done_executor_task)
# response = await client.post(
#     f"/task/done_task_customer/{created_task['id']}/",
#     headers={"Authorization": f"Bearer {executor_first_token}"},
# )
# assert response.json()["done_executor"]


# @pytest.mark.anyio
# async def test_done_task_by_foreign_executor(
#     created_task,
#     response_for_task,
#     response_for_task_by_second_executor,
#     customer_first_token,
#     executor_second_token,
#     client,
# ):
#     print(response_for_task_by_second_executor)
# response = await client.post(
#     f"/task/done_task_executor/{created_task['id']}/",
#     headers={"Authorization": f"Bearer {executor_second_token}"},
# )
#     print(response.json())
#     # assert response.json()["done_executor"]
