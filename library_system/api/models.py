from django.db import models
from django.contrib.auth.models import User
from manager.models import Book
class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


class Return(models.Model):
    borrow = models.ForeignKey(Borrow, on_delete=models.CASCADE)
    return_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Return: {self.borrow.book.title} by {self.borrow.user.username}"


class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.created_at}] {self.user} - {self.action}"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Borrow)
def update_book_when_borrow(sender, instance, created, **kwargs):
    if created:
        instance.book.available = False
        instance.book.save()

@receiver(post_save, sender=Return)
def update_book_when_return(sender, instance, created, **kwargs):
    if created:
        instance.borrow.book.available = True
        instance.borrow.book.save()
