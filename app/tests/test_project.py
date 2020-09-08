from test_basic import BasicTests
import unittest


class ProjectTests(BasicTests):

    def test_get_projects(self):
        self.get_projects()
        response = self.create_project('ProjectName')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ProjectName', response.data)


    def test_get_existing_projects(self):
        self.create_project('ProjectWithNoName')
        response = self.get_projects()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ProjectWithNoName', response.data)


    def test_project_creation(self):
        response = self.create_project('ProjectName')
        self.assertEqual(response.status_code, 200)


    def test_project_elimination(self):
        self.create_project('ProjectName')
        response = self.delete_project(1)
        self.assertEqual(response.status_code, 200)


    def test_project_elimination_error(self):
        response = self.delete_project(1)
        self.assertEqual(response.status_code, 404)


    def test_get_project_error(self):
        response = self.get_project('ProjectName')
        self.assertEqual(response.status_code, 404)


    def test_get_project(self):
        self.create_project('ProjectName')
        response = self.get_project('ProjectName')
        self.assertEqual(response.status_code, 200)


    def test_get_project_assets(self):
        self.create_project('ProjectName')
        response = self.get_project('ProjectName', 'assets')
        self.assertEqual(response.status_code, 200)


    def test_get_project_clients(self):
        self.create_project('ProjectName')
        response = self.get_project('ProjectName', 'clients')
        self.assertEqual(response.status_code, 200)


    def test_get_project_categories(self):
        self.create_project('ProjectName')
        response = self.get_project('ProjectName', 'categories')
        self.assertEqual(response.status_code, 200)

    # helper methods
    def get_projects(self):
        return self.app.get(
            '/projects',
            follow_redirects=True
        )


    def create_project(self, name):
        return self.app.post(
            '/projects/new',
            data=dict(name=name),
            follow_redirects=True
        )


    def delete_project(self, id):
        return self.app.delete(
            '/projects/{}'.format(id),
            follow_redirects=True
        )


    def get_project(self, name, optional=None):
        url = '/projects/{}'.format(name)
        if optional is not None:
            url = '{}/{}'.format(url, optional)
        return self.app.get(
            url,
            follow_redirects=True
        )


if __name__ == "__main__":
    unittest.main()
