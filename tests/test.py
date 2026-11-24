import unittest
import app

class FakeTable:
    def __init__(self):
        # {Task["task_id"]: Task, ...}
        self.items = {}

    def put_item(self, Item):
        self.items[Item["task_id"]] = Item

    def scan(self, **kwargs):
        return {'Items': self.items}

    def update_item(self, Key, **kwargs):
        self.items[Key['task_id']['status']] = 'complete'
        return {'Attributes' : self.items[Key['task_id']]}

    def delete_item(self, Key):
        self.items.pop(Key['task_id'])
        return {'Attributes' : self.items[Key['task_id']]}

class TestLambda(unittest.TestCase):
    def test_invalid_action(self):
        # Should be invalid because action must be in {'create', 'list', 'complete', 'delete'}
        response = app.lambda_handler({'action': 'something', 'title': 'something'}, None)
        self.assertEqual(response['statusCode'], 400)

    def test_create_list(self):
        response = app.lambda_handler({'action': 'create', 'title': 'test_task', 'description': 'A test task'}, None)
        
        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(response['body']['message'], 'Task created successfully')

        task = response['body']['task']
        self.assertEqual(task['title'], 'test_task')
        self.assertEqual(task['description'], 'A test task')
        self.assertEqual(task['status'], 'incomplete')

    # def test_create_delete(self):
    
    # def test_invalid_delete(self)

if __name__ == '__main__':
    unittest.main()
