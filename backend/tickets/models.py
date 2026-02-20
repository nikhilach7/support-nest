from django.db import models


class Ticket(models.Model):
    """
    Support ticket model with database-level constraints
    """
    CATEGORY_CHOICES = [
        ('billing', 'Billing'),
        ('technical', 'Technical'),
        ('account', 'Account'),
        ('general', 'General'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        db_index=True
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['priority', 'status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(category__in=['billing', 'technical', 'account', 'general']),
                name='valid_category'
            ),
            models.CheckConstraint(
                check=models.Q(priority__in=['low', 'medium', 'high', 'critical']),
                name='valid_priority'
            ),
            models.CheckConstraint(
                check=models.Q(status__in=['open', 'in_progress', 'resolved', 'closed']),
                name='valid_status'
            ),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.status})"
