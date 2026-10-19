import json

# Format --> 'title: {description: ..., status: ...}'
# status is 'complete' or 'incomplete'
tasks = {}

def create_task(title, description, status):
    tasks[title] = {}
    tasks[title]['description'] = description
    tasks[title]['status'] = status

def list_tasks():
    if len(tasks) == 0:
        print("No tasks created")
        return
    
    print("Active tasks are: \n")

    for title, task_details in tasks.items():
        print(f"Title: {title},\ndescription: {task_details['description']},\nstatus: {task_details['status']}\n")

def delete_task(title):
    check = tasks.pop(title, None)
    if check == None:
        print(f'Task "{title}" doesn\'t exist')
    else:
        print(f'Successfully deleted task "{title}"')    


def mark_task_complete(title):
    check = tasks.get(title, None)
    if check == None:
        print(f'Task "{title}" doesn\'t exist')
    else:
        print(f'Marked task "{title}" as complete. ')
        while (1):
            decision = input("Would you like to remove task from list?: ")
            print()
            if decision.lower() == 'yes':
                delete_task(title)
                return
            elif decision.lower() == 'no':
                tasks[title]['status'] = 'complete'
                return
            else:
                print("Error - please respond with 'yes' or 'no'.")

if __name__ == '__main__':
    create_task('Comp3411', 'Study for comp3411 assignment showcase', 'Incomplete')
    create_task('Comp6080', 'Catchup on lectures', 'Incomplete')
    list_tasks()
    mark_task_complete('Comp3411')
    list_tasks()