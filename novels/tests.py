from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Novel, Chapter, Rating, Wishlist, ReadingHistory


class LightNovelPlatformTests(TestCase):
    def setUp(self):
        self.writer = User.objects.create_user(
            username='author1', password='password123')
        self.reader = User.objects.create_user(
            username='reader1', password='password123')

    def test_writer_can_publish_novel_and_chapters(self):
        self.client.login(username='author1', password='password123')

        # 1. Create a novel
        response = self.client.post(reverse('writer_dashboard'), {
            'title': 'Solo Coding',
            'synopsis': 'A developer levels up.',
            'cover_url': ''
        })
        self.assertEqual(Novel.objects.count(), 1)
        novel = Novel.objects.first()

        # 2. Add Chapter 1
        self.client.post(reverse('add_chapter', args=[novel.id]), {
            'chapter_number': 1,
            'title': 'The Awakening',
            'content': 'It started with a terminal window...'
        })
        self.assertEqual(novel.chapters.count(), 1)

        # 3. Ensure duplicate Chapter 1 is blocked cleanly (no crash)
        response = self.client.post(reverse('add_chapter', args=[novel.id]), {
            'chapter_number': 1,
            'title': 'Duplicate Chapter',
            'content': 'Should not save.'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(novel.chapters.count(), 1)

    def test_reader_history_wishlist_and_rating(self):
        novel = Novel.objects.create(
            title='Reincarnated as a Router',
            author=self.writer,
            synopsis='Dropping packets in another world.'
        )
        Chapter.objects.create(novel=novel, chapter_number=1,
                               title='BGP Peers', content='Hello world')

        self.client.login(username='reader1', password='password123')

        # 1. Reading the novel adds it to ReadingHistory ("My Novels")
        self.client.get(reverse('read_novel', args=[novel.id]))
        self.assertTrue(ReadingHistory.objects.filter(
            user=self.reader, novel=novel).exists())

        # 2. Toggle Wishlist (Add & Remove)
        self.client.get(reverse('toggle_wishlist', args=[novel.id]))
        self.assertTrue(Wishlist.objects.filter(
            user=self.reader, novel=novel).exists())
        self.client.get(reverse('toggle_wishlist', args=[novel.id]))
        self.assertFalse(Wishlist.objects.filter(
            user=self.reader, novel=novel).exists())

        # 3. Vote 5 out of 5 stars
        self.client.post(reverse('rate_novel', args=[novel.id]), {'score': 5})
        self.assertEqual(novel.average_rating(), 5.0)
