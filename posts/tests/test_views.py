import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='my.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create(
            username='leo',
            first_name='Лев',
            last_name='Толстой',
        )
        cls.user2 = User.objects.create_user('user')
        cls.group = Group.objects.create(
            title='Котики',
            description='О котиках',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Коммент',
            author=cls.user2
        )
        cls.site = Site.objects.first()
        cls.flatpages1 = FlatPage.objects.create(
            url='/about-author/',
            title='Об авторе',
            content='<b>content</b>',
        )
        cls.flatpages2 = FlatPage.objects.create(
            url='/about-spec/',
            title='Технологии',
            content='<b>content</b>',
        )
        cls.flatpages1.sites.add(cls.site)
        cls.flatpages2.sites.add(cls.site)

    def setUp(self):
        self.guest_client = Client()
        self.user = PostsPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = (
            ('index.html', reverse('index')),
            ('new_post.html', reverse('new_post')),
            ('new_post.html', reverse(
                'post_edit', kwargs={'username': 'leo', 'post_id': 1}
            )),
            ('group.html', reverse('group', kwargs={'slug': 'test-slug'})),
            ('profile.html', reverse('profile', kwargs={'username': 'leo'})),
            ('post.html', reverse(
                'post', kwargs={'username': 'leo', 'post_id': 1}
            )),
            ('follow.html', reverse('follow_index')),
        )
        for template, reverse_name in templates_page_names:
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_show_correct_context(self):
        """
        В шаблон index, group, profile переданы правильные значения
        page и paginator из контекста
        """
        html_used_context = (
            reverse('group', kwargs={'slug': 'test-slug'}),
            reverse('index'),
            reverse('profile', kwargs={'username': 'leo'})
        )
        for html in html_used_context:
            with self.subTest():
                response = self.guest_client.get(html)
                pub_date = PostsPagesTests.post.pub_date
                self.assertEqual(response.context.get('page')[0].text, 'Текст')
                self.assertEqual(
                    response.context.get('page')[0].id, 1
                )
                self.assertEqual(
                    response.context.get('page')[0].pub_date, pub_date
                )
                self.assertEqual(
                    response.context.get('page')[0].author.username, 'leo'
                )
                self.assertIsNotNone(response.context.get('page')[0].image)
                self.assertEqual(response.context.get('paginator').count, 1)
                self.assertEqual(
                    response.context.get('page').has_next(), False
                )

    def test_group_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('group', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(response.context.get('group').title, 'Котики')
        self.assertEqual(
            response.context.get('group').description, 'О котиках'
        )

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('profile', kwargs={'username': 'leo'})
        )
        self.assertEqual(response.context.get('author').username, 'leo')
        self.assertEqual(
            response.context.get('author').get_full_name(), 'Лев Толстой'
        )

    def test_post_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('post', kwargs={'username': 'leo', 'post_id': 1})
        )
        pub_date = PostsPagesTests.post.pub_date
        self.assertEqual(response.context.get('author').username, 'leo')
        self.assertEqual(
            response.context.get('author').get_full_name(), 'Лев Толстой'
        )
        self.assertEqual(response.context.get('post').id, 1)
        self.assertEqual(response.context.get('post').text, 'Текст')
        self.assertEqual(response.context.get('post').pub_date, pub_date)
        self.assertEqual(
            response.context.get('comments').first().text, 'Коммент'
        )
        self.assertIsNotNone(response.context.get('post').image)

    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'post_edit', kwargs={'username': 'leo', 'post_id': 1}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_about_author_show_correct_context(self):
        """Проверка содержимого context для страницы /about-author/."""
        response = self.guest_client.get(reverse('author'))
        self.assertEqual(response.context.get('flatpage').title, 'Об авторе')
        self.assertEqual(
            response.context.get('flatpage').content, '<b>content</b>'
        )

    def test_about_spec_show_correct_context(self):
        """Проверка содержимого context для страницы /about-spec/."""
        response = self.guest_client.get(reverse('spec'))
        self.assertEqual(response.context.get('flatpage').title, 'Технологии')
        self.assertEqual(
            response.context.get('flatpage').content, '<b>content</b>'
        )

    def test_index_cache(self):
        """Проверка работы кэша на странице index"""
        PostsPagesTests.post.text = 'Кэш'
        PostsPagesTests.post.save()
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.context.get('page')[0].text, 'Кэш')
        PostsPagesTests.post.text = 'Текст'
        PostsPagesTests.post.save()
        self.assertEqual(response.context.get('page')[0].text, 'Кэш')