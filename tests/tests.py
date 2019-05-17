import json

from django.contrib.auth.models import User
from django.test import TestCase

from wagtail.core.models import Page, Site


class TestChooseView(TestCase):
    def setUp(self):
        User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        self.assertTrue(
            self.client.login(username='admin', password='password')
        )

    def test_get(self):
        response = self.client.get('/admin/site-chooser/chooser/')
        self.assertEqual(response.status_code, 200)

        response_json = json.loads(response.content)
        self.assertEqual(response_json['step'], 'choose')
        self.assertInHTML(
            '<h1 class="icon icon-site">Choose a site</h1>',
            response_json['html']
        )
        self.assertInHTML(
            '<a class="item-choice" href="/admin/site-chooser/chooser/1/">localhost [default]</a>',
            response_json['html']
        )

    def test_pagination(self):
        page = Page.objects.first()
        for i in range(0, 25):
            Site.objects.create(hostname='%d.example.com' % i, root_page=page)

        # fetch page 1
        response = self.client.get('/admin/site-chooser/chooser/')
        self.assertEqual(response.status_code, 200)

        response_json = json.loads(response.content)
        self.assertEqual(response_json['step'], 'choose')
        self.assertInHTML(
            '<p>Page 1 of 3.</p>',
            response_json['html']
        )
        self.assertInHTML(
            '<a href="#" data-page="2" class="icon icon-arrow-right-after">Next</a>',
            response_json['html']
        )

        # fetch page 2
        response = self.client.get('/admin/site-chooser/chooser/?p=2')
        self.assertEqual(response.status_code, 200)

        response_json = json.loads(response.content)
        self.assertEqual(response_json['step'], 'choose')
        self.assertInHTML(
            '<p>Page 2 of 3.</p>',
            response_json['html']
        )
        self.assertInHTML(
            '<a href="#" data-page="1" class="icon icon-arrow-left">Previous</a>',
            response_json['html']
        )
        self.assertInHTML(
            '<a href="#" data-page="3" class="icon icon-arrow-right-after">Next</a>',
            response_json['html']
        )


class TestChosenView(TestCase):
    def setUp(self):
        User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        self.assertTrue(
            self.client.login(username='admin', password='password')
        )

    def test_get(self):
        response = self.client.get('/admin/site-chooser/chooser/1/')
        self.assertEqual(response.status_code, 200)

        response_json = json.loads(response.content)
        self.assertEqual(response_json['step'], 'chosen')
        self.assertEqual(
            response_json['result'],
            {"id": "1", "string": "localhost [default]", "edit_link": "/admin/sites/1/"}
        )