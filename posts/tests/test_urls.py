from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Котики',
            slug='test-slug',
        )
        Post.objects.create(
            id=1,
            text='Текст',
            author=cls.author,
            group=cls.group
        )
        cls.site = Site.objects.get(pk=1)
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
        self.authorized_client_author = Client()
        self.authorized_client = Client()
        self.authorized_client_author.force_login(StaticURLTests.author)
        self.authorized_client.force_login(StaticURLTests.user)

    def test_url_for_all_users(self):
        """Страницы доступны любому пользователю."""
        url_status_code = [
            reverse('index'),
            reverse('author'),
            reverse('spec'),
            reverse('group', kwargs={'slug': 'test-slug'}),
            reverse('profile', kwargs={'username': 'author'}),
            reverse('post', kwargs={'username': 'author', 'post_id': 1}),
        ]
        for url in url_status_code:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_url_redirect_anonymous_on_login(self):
        """
        Страница по адресу /new/ и
        /<str:username>/<int:post_id>/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        login_url = reverse('login')
        new_post_url = reverse('new_post')
        post_edit_url = reverse(
                'post_edit', kwargs={'username': 'author', 'post_id': 1}
        )
        comment_url = reverse(
                'add_comment', kwargs={'username': 'author', 'post_id': 1}
        )
        url_to_login = {
            new_post_url: f"{login_url}?next={new_post_url}",
            post_edit_url: f"{login_url}?next={post_edit_url}",
            comment_url: f"{login_url}?next={comment_url}",
        }
        for url, next_url in url_to_login.items():
            with self.subTest():
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, next_url)

    def test_edit_for_authorized_user_author(self):
        """
        Страница /<str:username>/<int:post_id>/edit/ доступна
        авторизованному пользователю-автору поста и недоступна для
        пользователя-не автора.
        """
        url_status_code = {
            reverse(
                'post_edit', kwargs={'username': 'author', 'post_id': 1}
            ): 200,
            reverse(
                'post_edit', kwargs={'username': 'user', 'post_id': 1}
            ): 302,
        }
        for url, status_code in url_status_code.items():
            with self.subTest():
                response = self.authorized_client_author.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_new_for_authorized_user(self):
        """
        Страница /new/ и /<str:username>/<int:post_id>/comment/ доступна
        авторизованному пользователю.
        """
        url_status_code = {
            reverse('new_post'),
            reverse(
                'add_comment', kwargs={'username': 'author', 'post_id': 1}
            ),
        }
        for url in url_status_code:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_uses_templates = {
            reverse('index'): 'index.html',
            reverse('group', kwargs={'slug': 'test-slug'}): 'group.html',
            reverse('new_post'): 'new_post.html',
            reverse('profile', kwargs={'username': 'author'}): 'profile.html',
            reverse(
                'post', kwargs={'username': 'author', 'post_id': 1}
            ): 'post.html',
            reverse('follow_index'): 'follow.html',
        }
        for url, template in url_uses_templates.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_edit_redirect_authorized_user(self):
        """
        Перенаправляет пользователя на страницу /<str:username>/<int:post_id>/,
        если он не является автором поста
        """
        response = self.authorized_client.get(reverse(
                'post_edit', kwargs={'username': 'author', 'post_id': 1}
        ))
        self.assertRedirects(response, reverse(
                'post', kwargs={'username': 'author', 'post_id': 1}
        ))

    def test_page_not_found(self):
        """
        Проверяет, возвращает ли сервер код 404, если страница не найдена.
        """
        response = self.guest_client.get('/not-found/')
        self.assertEqual(response.status_code, 404)

    def test_auth_user_follow_unfollow(self):
        """
        Авторизованный пользователь может подписываться
         на других пользователей и удалять их из подписок
        """
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': 'author'}
        ))
        self.assertEqual(
            Follow.objects.filter(user=StaticURLTests.user).count(),
            1
        )
        self.authorized_client.get(reverse(
            'profile_unfollow', kwargs={'username': 'author'}
        ))
        self.assertEqual(
            Follow.objects.filter(user=StaticURLTests.user).count(),
            0
        )

    def test_show_follow_posts(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан на него.
        """
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': 'author'}
        ))
        self.assertEqual(
            Post.objects.filter(
                author__following__user=StaticURLTests.user).count(), 1
        )
        self.assertEqual(
            Post.objects.filter(
                author__following__user=StaticURLTests.author).count(), 0
        )


