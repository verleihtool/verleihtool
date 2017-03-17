from verleihtool.test import ClientTestCase


class AdminLinkTestCase(ClientTestCase):

    def test_admin_loggedin(self):
        response = self.as_superuser.get('/')
        self.assertContains(
            response,
            'Administration'
        )

    def test_admin_not_loggedin(self):
        response = self.as_guest.get('/')
        self.assertNotContains(
            response,
            'Administration'
        )
