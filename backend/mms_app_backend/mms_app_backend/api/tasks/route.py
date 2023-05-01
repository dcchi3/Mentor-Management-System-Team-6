from fastapi import Response, APIRouter, status, Depends
from sqlalchemy.orm import Session

from .constants import CREATED_TASK_SUCCESSFUL_MESSAGE, GET_TASKS_SUCCESSFUL_MESSAGE, UPDATE_TASK_SUCCESSFUL_MESSAGE, \
    TASK_NOT_FOUND_MESSAGE, TASK_DELETED_SUCCESSFUL_MESSAGE, TASK_NOT_COMPLETED_MESSAGE
from .crud import create_task_crud, get_tasks_crud, update_task_crud, delete_task_crud, close_task_crud
from .models import Task
from .responses import CreateTaskResponse, GetTasksResponse
from .schemas import CreateTask, UpdateTask
from ..authentication.constants import INVALID_AUTHENTICATION_MESSAGE
from ..authentication.helpers import verify_access_token
from ..utils import get_token, get_db

router = APIRouter()
get = router.get
post = router.post
patch = router.patch
delete = router.delete
put = router.put


@post('/admin/tasks', response_model=CreateTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: CreateTask, response: Response, jwt_token: str = Depends(get_token()),
                      db: Session = Depends(get_db)):
    task_response = CreateTaskResponse()
    user = verify_access_token(db, jwt_token)

    if user is None:
        task_response.message = INVALID_AUTHENTICATION_MESSAGE
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return task_response
    created_task = create_task_crud(db, task)
    if created_task:
        task_response.success = True
        task_response.data.task = created_task
        task_response.message = CREATED_TASK_SUCCESSFUL_MESSAGE
        return task_response


@get('/admin/tasks', status_code=status.HTTP_200_OK, response_model=GetTasksResponse)
async def get_tasks(response: Response, jwt_token: str = Depends(get_token()), db: Session = Depends(get_db)):
    tasks_response = GetTasksResponse()
    user = verify_access_token(db, jwt_token)
    if user is None:
        tasks_response.message = INVALID_AUTHENTICATION_MESSAGE
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return tasks_response
    tasks = get_tasks_crud(db)
    tasks_response.success = True
    tasks_response.data.tasks = tasks
    tasks_response.message = GET_TASKS_SUCCESSFUL_MESSAGE
    return tasks_response


# endpoint to update the tasks based on the inputs
@patch('/admin/tasks/{task_id}', response_model=CreateTaskResponse, status_code=status.HTTP_200_OK)
async def update_task(task_id: int, task: UpdateTask, response: Response, jwt_token: str = Depends(get_token()),
                      db: Session = Depends(get_db)):
    task_response = CreateTaskResponse()
    user = verify_access_token(db, jwt_token)
    task_instance = db.query(Task).filter(Task.id == task_id).first()

    if user is None:
        task_response.message = INVALID_AUTHENTICATION_MESSAGE
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return task_response

    if task_instance is None:
        task_response.message = TASK_NOT_FOUND_MESSAGE
        response.status_code = status.HTTP_404_NOT_FOUND
        return task_response

    updated_task = update_task_crud(db, task, task_id)
    if updated_task:
        task_response.message = UPDATE_TASK_SUCCESSFUL_MESSAGE
        task_response.data.task = updated_task
        task_response.success = True
        return task_response


# Endpoint to hard delete tasks
@delete('/admin/tasks/{task_id}', response_model=CreateTaskResponse, status_code=status.HTTP_200_OK)
async def delete_task(task_id: int, response: Response, hard: bool = False, jwt_token: str = Depends(get_token()),
                      db: Session = Depends(get_db)):
    """
    Endpoint to permanently delete tasks from the database.
    """
    user = verify_access_token(db, jwt_token)
    task_response = CreateTaskResponse()
    if user is None:
        task_response.message = INVALID_AUTHENTICATION_MESSAGE
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    task_instance = db.query(Task).filter(Task.id == task_id).first()
    if task_instance is None:
        task_response.message = TASK_NOT_FOUND_MESSAGE
        response.status_code = status.HTTP_404_NOT_FOUND
        return task_response
    if hard:
        deleted_task = delete_task_crud(db, task_instance)
    else:
        deleted_task = close_task_crud(db, task_instance)
    if deleted_task:
        task_response.message = TASK_DELETED_SUCCESSFUL_MESSAGE
        task_response.success = True
        return task_response



@put("/tasks/{task_id}/reopen", response_model=CreateTaskResponse, status_code=status.HTTP_200_OK)
    """
    This function reopens a completed task.

    :param task_id: The ID of the task that needs to be reopened
    :type task_id: int
    :param token: The token parameter is a string that represents the access token of the user who is
    trying to reopen a task. It is obtained through the get_token() function, which verifies the user's
    authentication and returns the access token
    :type token: str
    :param db: db is a dependency injection parameter that represents the database session. It is used
    to interact with the database and perform CRUD (Create, Read, Update, Delete) operations on the Task
    model
    :type db: Session
    :return: a response with a JSON object of type CreateTaskResponse, which contains a message and a
    success flag. The status code of the response is either 200, 401, 404, or 400 depending on the
    outcome of the function.
    """
async def reopen_task(task_id: int, token: str = Depends(get_token()), db: Session = Depends(get_db)):
    user = verify_access_token(db, token)
    task_response = CreateTaskResponse()
    if user is None:
        task_response.message = INVALID_AUTHENTICATION_MESSAGE
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return task_response

    task = db.query(Task).filter(Task.id == task_id).first()
    if task_instance is None:
        task_response.message = TASK_NOT_FOUND_MESSAGE
        response.status_code = status.HTTP_404_NOT_FOUND
        return task_response

    if not task.completed:
        task_response.message = TASK_NOT_COMPLETED_MESSAGE
        response.status_code = status.HTTP_400_BAD_REQUEST
        return task_response
    task.completed = False
    task.open = True
    update_task_crud(db, task, task_id)
    task_response.message = TASK_REOPEN_SUCCESSFUL_MESSAGE
    task_response.success = True
    return task_response
