from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Novel(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='published_novels')
    synopsis = models.TextField()
    cover_image = models.ImageField(
        upload_to='covers/',
        blank=True,
        null=True,
        help_text="Upload a cover image from your device (JPG, PNG, WEBP)"
    )
    cover_url = models.URLField(
        blank=True,
        null=True,
        help_text="Or paste an external image link (optional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def cover_src(self):
        if self.cover_image:
            return self.cover_image.url
        if self.cover_url:
            return self.cover_url
        return None

    def average_rating(self):
        avg = self.ratings.aggregate(Avg('score'))['score__avg']
        return round(avg, 1) if avg else "New"

    def __str__(self):
        return self.title


class Chapter(models.Model):
    novel = models.ForeignKey(
        Novel, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chapter_number']
        unique_together = ('novel', 'chapter_number')

    def __str__(self):
        return f"{self.novel.title} - Ch. {self.chapter_number}: {self.title}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    novel = models.ForeignKey(
        Novel, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'novel')


class Wishlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='wishlist')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'novel')
        ordering = ['-added_at']


class ReadingHistory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reading_history')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    last_read_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'novel')
        ordering = ['-last_read_at']


class WriterRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='writer_request')
    reason = models.TextField(
        help_text="Tell the admins about the stories you want to publish.")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def is_rejected(self):
        return self.status == 'rejected'

    def __str__(self):
        return f"{self.user.username} ({self.get_status_display()})"
