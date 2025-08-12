from problem.models import Problem, Tag

def migrate_tags():
    for problem in Problem.objects.all():
        # Assuming the old tags were stored in a temporary field called `old_tags`
        # Replace `old_tags` with the actual field name where the comma-separated tags are stored
        if hasattr(problem, 'old_tags') and problem.old_tags:
            tag_names = [tag.strip() for tag in problem.old_tags.split(',')]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                problem.tags.add(tag)  # Add the tag to the ManyToManyField
    print("Tags migrated successfully!")