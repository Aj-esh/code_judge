from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Problem(models.Model):
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag, blank=True)  # Many-to-many relationship with Tag model

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

<<<<<<< Updated upstream
    def get_tags(self) -> list[str]:
        return self.tags.split(',') if  self.tags else []
=======
    @property
    def tags_list(self) -> list[str]:
        return list(self.tags.values_list('name', flat=True))
>>>>>>> Stashed changes

    def __str__(self):
        return self.title

class UserSolvedProblems(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    solved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} solved {self.problem.title} on {self.solved_at.strftime('%Y-%m-%d %H:%M:%S')}"
