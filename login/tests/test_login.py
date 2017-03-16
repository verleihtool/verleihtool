from verleihtool.test import ClientTestCase


class LoginTestCase(ClientTestCase):

    def test_login_form(self):
        response = self.as_guest.get('/login/')
        self.assertSuccess(response, 'login/login.html')

    def test_login_with_correct_password(self):
        response = self.as_guest.post('/login/', {
            'username': 'user',
            'password': 'password',
        })
        self.assertRedirects(response, '/')

    def test_login_case_insensitive(self):
        response = self.as_guest.post('/login/', {
            'username': 'User',
            'password': 'password',
        })
        self.assertContains(
            response,
            'Please enter a correct username and password.'
        )

    def test_login_invalid_password(self):
        response = self.as_guest.post('/login/', {
            'username': 'user',
            'password': 'p4ssword',
        })
        self.assertContains(
            response,
            'Please enter a correct username and password.'
        )

    def test_login_non_existing_user(self):
        response = self.as_guest.post('/login/', {
            'username': 'max',
            'password': 'moritz',
        })
        self.assertContains(
            response,
            'Please enter a correct username and password.'
        )

    def test_logged_out_displays_login_and_not_logout(self):
        response = self.as_guest.get('/')
        self.assertContains(
            response,
            'Login'
        )
        self.assertNotContains(
            response,
            'Logout'
        )

    def test_logged_in_displays_logout_and_not_login(self):
        response = self.as_user.get('/')
        self.assertContains(
            response,
            'Logout'
        )
        self.assertNotContains(
            response,
            'Login'
        )
