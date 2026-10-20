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

def menu_choices():
    print("'1' to create a task")
    print("'2' to delete a task")
    print("'3' to mark a task as complete")
    print("'4' to list all tasks")
    print("'5' to quit")
    print()

if __name__ == '__main__':
    # Interactive menu

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("Welcome to Task Manager!\n")
    print("What would you like to do? Choose from the following list:")
    menu_choices()

    while (1):
        try:
            choice = int((input("Enter choice: ")))
        except ValueError:
            print("Please enter an integer from the following list: ")
            menu_choices()
            continue

        if choice not in {1,2,3,4,5}:
            print("Unrecognised action. Choose from the following:")
            menu_choices()
            continue
                
        match choice:
            case 1:
                title = input('Enter task title: ').strip()

                if not title:
                    print("Task must have title")
                    continue

                description = input("Enter task description: ")
                task_id = create_task(title, description)
                print(f"Task id for referring back to this task: {task_id}")
                print("Task created successfully.")
            case 2:
                try:
                    del_task_id = int(input('Enter task id: '))
                except ValueError: 
                    print("Enter valid integer")
                    continue
                
                del_check = delete_task(del_task_id)
                if del_check is None:
                    print("Invalid task id")
                    continue
                print("Task deleted successfully.")
            case 3:
                try:
                    mark_complete_task_id = int(input("Enter task id: "))
                except ValueError:  
                    print("Enter valid integer")
                    continue

                complete_check = mark_task_complete(mark_complete_task_id)
                if not complete_check:
                    print("Invalid task id")
                    continue
                print("Task marked as complete.")
            case 4:
                task_to_print = list_tasks()
                if not task_to_print:
                    print("No tasks exist.")
                for task_id, task in task_to_print.items():
                    print(f"Task id: {task_id}, Title: {task['title']}, Description: {task['description']}, Status: {task['status']}")
            case 5:
                print("Quitting...")
                break