from django.db import models

# Create your models here.
class Problem(models.Model):
    title = models.CharField(max_length=200)
    tags = models.CharField(max_length=100, blank=True, null=True)  # Comma-separated tags
    
    description = models.TextField()
    difficulty = models.CharField(max_length=6) # Easy, Medium, Hard
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    creator = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='created_problems', default=5,
    )

    submissions = models.IntegerField(default=0)
    
    constraints = models.TextField(blank=True, null=True)

    time_limit = models.FloatField(default=1.0, blank=True)  # In seconds
    memory_limit = models.IntegerField(default=256, blank=True)  # In MB

    examples = models.TextField(blank=True, null=True)  # JSON or plain text

    hints = models.TextField(blank=True, null=True)

    def get_tags(self) -> list[str]:
        return self.tags.split(',') if  self.tags else []

    def __str__(self):
        return self.title

