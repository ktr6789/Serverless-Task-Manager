import unittest
import app_old


class Tasktests(unittest.TestCase):
    def setUp(self):
        # Each test starts from the same known state.
        app_old.tasks = {}
        app_old.next_task_id = 0
    
    def test_create_task_stores_task_and_returns_id(self):
        task_id = app_old.create_task('Comp3411', 'Study for assignment discussion')

        self.assertEqual(task_id, 0)
        self.assertEqual(
            app_old.tasks,
            {
                0: {
                    'title': 'Comp3411',
                    'description': 'Study for assignment discussion',
                    'status': 'incomplete',
                }
            },
        )

    def test_create_tasks_receive_different_ids(self):
        first_id = app_old.create_task('First task', 'First description')
        second_id = app_old.create_task('Second task', 'Second description')

        self.assertEqual(first_id, 0)
        self.assertEqual(second_id, 1)
        self.assertEqual(len(app_old.tasks), 2)

    def test_list_tasks_returns_all_tasks(self):
        first_id = app_old.create_task('First task', 'First description')
        second_id = app_old.create_task('Second task', 'Second description')

        result = app_old.list_tasks()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[first_id]['title'], 'First task')
        self.assertEqual(result[second_id]['title'], 'Second task')

    def test_list_tasks_is_empty_when_no_tasks_exist(self):
        self.assertEqual(app_old.list_tasks(), {})

    def test_mark_task_complete_changes_status(self):
        task_id = app_old.create_task('Finish tests', 'Check task completion')

        result = app_old.mark_task_complete(task_id)

        self.assertTrue(result)
        self.assertEqual(app_old.tasks[task_id]['status'], 'complete')

    def test_mark_nonexistent_task_complete_returns_false(self):
        result = app_old.mark_task_complete(999)

        self.assertFalse(result)

    def test_delete_task_removes_and_returns_task(self):
        task_id = app_old.create_task('Remove me', 'Test deletion')

        deleted_task = app_old.delete_task(task_id)

        self.assertEqual(
            deleted_task,
            {
                'title': 'Remove me',
                'description': 'Test deletion',
                'status': 'incomplete',
            },
        )
        self.assertNotIn(task_id, app_old.tasks)

    def test_delete_nonexistent_task_returns_none(self):
        self.assertIsNone(app_old.delete_task(999))

if __name__ == "__main__":
    unittest.main()

