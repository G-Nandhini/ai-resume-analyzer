from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import RegisterForm


class RegisterFormTests(TestCase):
    def test_valid_form_saves_user_profile_fields(self):
        form = RegisterForm(data={
            'first_name': 'Nandhini',
            'last_name': 'Ravi',
            'username': 'nandhini',
            'email': 'nandhini@example.com',
            'password1': 'S3cure-Passphrase-2026',
            'password2': 'S3cure-Passphrase-2026',
        })

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertEqual(user.first_name, 'Nandhini')
        self.assertEqual(user.last_name, 'Ravi')
        self.assertEqual(user.email, 'nandhini@example.com')
        self.assertTrue(user.check_password('S3cure-Passphrase-2026'))

    def test_email_and_first_name_are_required(self):
        form = RegisterForm(data={
            'first_name': '',
            'last_name': 'Ravi',
            'username': 'nandhini',
            'email': '',
            'password1': 'S3cure-Passphrase-2026',
            'password2': 'S3cure-Passphrase-2026',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertIn('email', form.errors)

    def test_fields_include_bootstrap_class_and_placeholders(self):
        form = RegisterForm()

        self.assertEqual(form.fields['username'].widget.attrs['class'], 'form-control')
        self.assertEqual(
            form.fields['username'].widget.attrs['placeholder'],
            'Choose username',
        )
        self.assertEqual(
            form.fields['password1'].widget.attrs['placeholder'],
            'Create password',
        )


class AccountViewTests(TestCase):
    def setUp(self):
        self.password = 'S3cure-Passphrase-2026'
        self.user = User.objects.create_user(
            username='existinguser',
            password=self.password,
            email='existing@example.com',
        )

    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Priya',
            'last_name': '',
            'username': 'priya',
            'email': 'priya@example.com',
            'password1': self.password,
            'password2': self.password,
        })

        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='priya').exists())

    def test_authenticated_user_is_redirected_away_from_register_and_login(self):
        self.client.force_login(self.user)

        register_response = self.client.get(reverse('register'))
        login_response = self.client.get(reverse('login'))

        self.assertRedirects(register_response, reverse('dashboard'))
        self.assertRedirects(login_response, reverse('dashboard'))

    def test_login_authenticates_user_and_redirects_to_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': self.password,
        })

        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('profile')}",
        )

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)
