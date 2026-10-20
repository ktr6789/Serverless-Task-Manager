import json

# Format --> 'title: {description: ..., status: ...}'
# status is 'complete' or 'incomplete'
tasks = {}
next_task_id = 0

def create_task(title, description):
    global next_task_id
    task_id = next_task_id
    tasks[task_id] = {'title': title, 'description': description, 
                      'status': 'incomplete'}
    next_task_id += 1
    return task_id

def list_tasks():
    return tasks

def delete_task(task_id):
    check = tasks.pop(task_id, None)
    return check


def mark_task_complete(task_id):
    if task_id in tasks:
        tasks[task_id]['status'] = 'complete'
        return True
    else:
        return False


if __name__ == '__main__':
    # Interactive menu
    while (1):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Welcome to Task Manager!\n")
        
        print("What would you like to do?:")
        print("'1' to create a task")
        print("'2' to delete a task")
        print("'3' to mark a task as complete")
        print("'4' to list all tasks")
        choice = input("Enter choice: ")

        if choice not in {1,2,3,4}:

        # match choice:
        #     case 1:

        #     case 2:

        #     case 3:

        #     case 4:

