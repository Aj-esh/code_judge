from django.db import models

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Problem(models.Model):
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag, blank=True, related_name='problems')

    description = models.TextField()
    difficulty = models.CharField(max_length=6) # Easy, Medium, Hard
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    creator = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='created_problems', default="leo",
    )

    submissions = models.IntegerField(default=0)
    
    constraints = models.TextField(blank=True, null=True)

    time_limit = models.FloatField(default=1.0, blank=True)  # In seconds
    memory_limit = models.IntegerField(default=256, blank=True)  # In MB
    
    embedding = models.BinaryField(null=True, blank=True)
    @property
    def tags_list(self) -> list[str]:
        return [tag.name for tag in self.tags.all()]

    def __str__(self):
        return self.title

