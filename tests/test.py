import unittest
import app
from unittest.mock import patch

class ConditionalCheckFailedException(Exception):
    pass

class FakeTable:
    def __init__(self):
        # {Task["task_id"]: Task, ...}
        self.items = {}

    def put_item(self, Item):
        self.items[Item["task_id"]] = Item

    def scan(self, **kwargs):
        return {'Items': list(self.items.values())}

    def update_item(self, Key, **kwargs):
        if Key['task_id'] not in self.items:
            raise ConditionalCheckFailedException()

        self.items[Key['task_id']]['status'] = 'complete'
        return {'Attributes' : self.items[Key['task_id']]}

    def delete_item(self, Key, **kwargs):
        if Key['task_id'] not in self.items:
            raise ConditionalCheckFailedException()
        
        task = self.items.pop(Key['task_id'])
        return {'Attributes' : task}
    

class TestLambda(unittest.TestCase):
    def setUp(self):
        self.table = FakeTable()
        patcher = patch('app._task_table', return_value=self.table)
        patcher.start()
        self.addCleanup(patcher.stop)

    def create_valid_task(self):
        response = app.lambda_handler({'action': 'create', 'title': 'test_task', 'description': 'A test task'}, None)
        return response
    
    def test_invalid_action(self):
        # Should be invalid because action must be in {'create', 'list', 'complete', 'delete'}
        response = app.lambda_handler({'action': 'something', 'title': 'something'}, None)
        self.assertEqual(response['statusCode'], 400)

    def test_create_list(self):
        response = self.create_valid_task()

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(response['body']['message'], 'Task created successfully')

        task = response['body']['task']
        self.assertEqual(task['title'], 'test_task')
        self.assertEqual(task['description'], 'A test task')
        self.assertEqual(task['status'], 'incomplete')


        list_response = app.lambda_handler({'action': 'list'}, None)

        self.assertEqual(list_response['statusCode'], 200)
        self.assertEqual(list_response['body']['tasks'], [task])

    def test_create_delete(self):
        create_response = self.create_valid_task()

        old_table_dict = self.table.scan()
        self.assertEqual(len(old_table_dict['Items']), 1)

        del_response = app.lambda_handler({"action": "delete", "task_id": create_response['body']['task']['task_id']}, None)
        new_table_dict = self.table.scan()
        self.assertEqual(len(new_table_dict['Items']), 0)   

        self.assertEqual(del_response['statusCode'], 200)

        task = del_response['body']['task']
        self.assertEqual(task['title'], 'test_task')
        self.assertEqual(task['description'], 'A test task')
        self.assertEqual(task['status'], 'incomplete')

    def test_invalid_delete(self):
        # Each test starts with an empty table, so this task does not exist.
        response = app.lambda_handler({'action': 'delete', 'task_id': 'missing-task'}, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['body']['error'], 'Task missing-task was not found')
        self.assertEqual(self.table.scan()['Items'], [])

if __name__ == '__main__':
    unittest.main()
