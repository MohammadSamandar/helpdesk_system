from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class TicketStatus(models.TextChoices):
    open = 'Open', _('باز')
    in_Rreview = 'In Review', _('در حال بررسی')
    awaiting_customer_response = 'Awaiting Customer Response', _('در انتظار پاسخ مشتری')
    closed = 'Closed', _('بسته شده')


class Ticket(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان')

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_tickets', null=True, blank=True)

    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='اختصاص یافته به')

    status = models.CharField(max_length=80, choices=TicketStatus.choices, default=TicketStatus.open, verbose_name='وضعیت تیکت')

    description = models.TextField(verbose_name='توضیحات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ساخته شده در')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='به روز رسانی شده در')
    last_activity = models.DateTimeField(default=timezone.now, verbose_name='آخرین فعالیت')



    def __str__(self):
        return self.title
    


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"پاسخ درج شده توسط: {self.author.username} در {self.ticket.title}"
    
    class meta: 
        ordering = ['created_at']
    










