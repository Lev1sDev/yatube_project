import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    def setUp(self):
        self.user = User.objects.create_user('leo')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        group = Group.objects.create(
            title='Котики',
            description='О котиках',
            slug='test-slug',
        )
        form_data = {
            'group': group.id,
            'text': 'Текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertIsNotNone(Post.objects.get(id=1).image.name)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_edit(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=small_gif,
            content_type='image/gif'
        )
        group = Group.objects.create(
            title='Котики',
            description='О котиках',
            slug='test-slug',
        )
        Post.objects.create(
            id=1,
            text='Какой-то текст',
            author=self.user
        )
        posts_count = Post.objects.count()
        form_data = {
            'group': group.id,
            'text': 'Текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'leo', 'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
                'post', kwargs={'username': 'leo', 'post_id': 1}
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.get(id=1).text, 'Текст')
        self.assertEqual(Post.objects.get(id=1).group.title, 'Котики')
        self.assertIsNotNone(Post.objects.get(id=1).image)
