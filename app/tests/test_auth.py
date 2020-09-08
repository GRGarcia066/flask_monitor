from test_basic import BasicTests
import unittest
 

class AuthTest(BasicTests):

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
 

    def test_valid_user_registration(self):
        response = self.register('g.cabrera', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)


    def test_invalid_user_registration_different_passwords(self):
        response = self.register('g.cabrera', 'FlaskIsAwesome', 'FlaskIsNotAwesome')
        self.assertIn(b'Field must be equal to password.', response.data)


    def test_invalid_user_registration_duplicate_username(self):
        response = self.register('g.cabrera', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)
        response = self.register('g.cabrera', 'FlaskIsReallyAwesome', 'FlaskIsReallyAwesome')
        self.assertIn(b'El nombre de usuario ya existe', response.data)


    def test_login(self):
        self.register('g.cabrera', 'FlaskIsAwesome', 'FlaskIsAwesome')
        response = self.login('g.cabrera', 'FlaskIsAwesome')
        self.assertNotIn(b'Nombre de usuario o contrase\xc3\xb1a incorrectos', response.data)
        self.assertEqual(response.status_code, 200)


    def test_login_wrong_username(self):
        self.register('g.cabrera', 'FlaskIsAwesome', 'FlaskIsAwesome')
        response = self.login('g.cabrera2', 'FlaskIsAwesome')
        self.assertIn(b'Nombre de usuario o contrase\xc3\xb1a incorrectos', response.data)
        self.assertEqual(response.status_code, 200)


    def test_login_wrong_password(self):
        self.register('g.cabrera', 'FlaskIsAwesome', 'FlaskIsAwesome')
        response = self.login('g.cabrera', 'FlaskIsNotAwesome')
        self.assertIn(b'Nombre de usuario o contrase\xc3\xb1a incorrectos', response.data)
        self.assertEqual(response.status_code, 200)


    def test_logout(self):
        self.register('g.cabrera', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.login('g.cabrera', 'FlaskIsAwesome')
        response = self.logout()
        self.assertEqual(response.status_code, 200)


    def test_profile(self):
        response = self.profile('Username')
        self.assertEqual(response.status_code, 404)


    def test_profile_no_existing_user(self):
        response = self.profile('Username')
        self.assertEqual(response.status_code, 404)

    # helper methods    
    def register(self, username, password, confirm):
        return self.app.post(
            '/auth/register',
            data=dict(username=username, password=password, password2=confirm),
            follow_redirects=True
        )
    

    def login(self, username, password):
        return self.app.post(
            '/auth/login',
            data=dict(username=username, password=password),
            follow_redirects=True
        )
    

    def profile(self, username):
        return self.app.get(
            '/auth/profile',
            data=dict(username=username),
            follow_redirects=True
        )
    

    def edit(self, username):
        return self.app.get(
            '/auth/profile/{}'.format(username),
            follow_redirects=True
        )
    

    def logout(self):
        return self.app.get(
            '/auth/logout',
            follow_redirects=True
        )


if __name__ == "__main__":
    unittest.main()
