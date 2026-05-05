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
    created_task, customer_first_token, response_for_task, client
):
    """Проверка выбора исполнителя для задачи заказчком"""
    response = await client.post(
        f"/task/{created_task['id']}/user/{4}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    assert response.json()["selected_executor_id"] == 4


@pytest.mark.anyio
async def test_select_executor_for_task_where_has_another_executor(
    created_task, customer_first_token, response_for_task, client
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
    created_task, customer_first_token, client
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
    customer_first_token,
    client,
):
    """Проверка завершения задачи заказчиком"""
    response = await client.post(
        f"/task/done_task_customer/{created_task['id']}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    assert response.json()["done_customer"]


@pytest.mark.anyio
async def test_delete_finished_task(
    created_task,
    done_executor_task,
    customer_first_token,
    client,
):
    """Проверка удаления завершенной задачи заказчиком"""
    response = await client.post(
        f"/task/done_task_customer/{created_task['id']}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    response = await client.delete(
        f"/task/delete/{created_task['id']}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_done_customer_his_task_when_executor_havent_done(
    created_task,
    customer_first_token,
    client,
):
    """Проверка завершения задачи заказчиком, когда задача не выполнена"""
    response = await client.post(
        f"/task/done_task_customer/{created_task['id']}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_done_customer_his_task_when_customer_havent_enough_money(
    created_task_too_expensive,
    executor_first_token,
    customer_first_token,
    client,
):
    """Проверка завершения задачи заказчиком, когда у заказчика не хватает денег"""
    await client.post(  # Отклил на задачу
        f"/bid/{created_task_too_expensive['id']}/response/",
        headers={"Authorization": f"Bearer {executor_first_token}"},
    )

    await client.post(  # выбор исполнителя для задачи
        f"/task/{created_task_too_expensive['id']}/user/{4}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )

    response = await client.post(  # завершение задачи исполнителем
        f"/task/done_task_executor/{created_task_too_expensive['id']}/",
        headers={"Authorization": f"Bearer {executor_first_token}"},
    )

    response = await client.post(
        f"/task/done_task_customer/{created_task_too_expensive['id']}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_get_free_tasks_by_executor(
    executor_first_token,
    executor_second_token,
    customer_first_token,
    created_some_task,
    client,
):
    """Проверка получение задач, на которые никто не назначен"""
    for k in range(3):
        task = created_some_task[k]
        await client.post(  # Отклил на задачу
            f"/bid/{task['id']}/response/",
            headers={"Authorization": f"Bearer {executor_first_token}"},
        )
        await client.post(  # выбор исполнителя для задачи
            f"/task/{task['id']}/user/{4}/",
            headers={"Authorization": f"Bearer {customer_first_token}"},
        )
    response = await client.get(  # выбор исполнителя для задачи
        "/task/open/",
        headers={"Authorization": f"Bearer {executor_second_token}"},
    )
    assert response.json()["total"] == 2


@pytest.mark.anyio
async def test_get_my_responsed_tasks_by_executor(
    executor_first_token,
    created_some_task,
    client,
):
    """Проверка получения задач, на которые откликнулся исполнитель"""
    for k in range(3):
        task = created_some_task[k]
        await client.post(  # Отклил на задачу
            f"/bid/{task['id']}/response/",
            headers={"Authorization": f"Bearer {executor_first_token}"},
        )
    response = await client.get(  # выбор исполнителя для задачи
        "/task/my_responsed_tasks/",
        headers={"Authorization": f"Bearer {executor_first_token}"},
    )
    assert response.json()["total"] == 3
