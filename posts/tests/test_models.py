from django.test import TestCase

from posts.models import Group, Post, User


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Котики',
        )
        cls.group = Group.objects.first()

    def test_object_name_is_title_field(self):
        """
        В поле __str__  объекта group записано значение поля group.title
        """
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='new_user'
        )
        Post.objects.create(
            author=cls.user,
            text='Какой-то текст',
        )
        cls.post = Post.objects.first()

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Изображение',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Напишите что-нибудь',
            'group': 'Укажите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_object_name_is_text_field(self):
        """
        В поле __str__  объекта post записано значение поля post.text
        с ограничением в 15 символов.
        """
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
