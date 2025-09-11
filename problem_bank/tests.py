from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile
from problem.models import Problem, Tag
from problem_bank.recommend import tag_ranker

class RecommendTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.user_profile = UserProfile.objects.create(user=self.user)
        
        # Create Tags
        self.tag1 = Tag.objects.create(name="Dynamic Programming")
        self.tag2 = Tag.objects.create(name="Graphs")

        # Create Problems and associate them with Tags
        self.problem1 = Problem.objects.create(title="Problem 1", creator=self.user)  # Set creator
        self.problem2 = Problem.objects.create(title="Problem 2", creator=self.user)  # Set creator
        self.problem1.tags.add(self.tag1)
        self.problem2.tags.add(self.tag2)
        
        # Add a Tag to the UserProfile
        self.user_profile.tags.add(self.tag1)

    def test_recommend_problems_for_user(self):
        recommended = tag_ranker(self.user)  # Pass self.user_profile
        self.assertIn(self.problem1, recommended)
        self.assertNotIn(self.problem2, recommended)