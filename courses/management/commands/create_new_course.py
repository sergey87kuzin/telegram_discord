from django.core.management.base import BaseCommand

from courses.models import Course, Lesson, LessonTextBlock


class Command(BaseCommand):

    def handle(self, *args, **options):
        lessons_to_copy = [3, 13, 6, 18, 11, 17, 36, 21, 22, 2, 14, 15, 24, 7, 25, 26, 35, 28, 27, 29, 30, 31, 33]
        initial_course = Course.objects.filter(id=2).first()
        new_course = Course.objects.create(
            name=initial_course.name,
            cover=initial_course.cover,
            cost=initial_course.cost,
            duration=initial_course.duration,
            is_active=True
        )
        for initial_lesson in initial_course.lessons.filter(id__in=lessons_to_copy):
            new_lesson = Lesson.objects.create(
                course=new_course,
                name=initial_lesson.name,
                description=initial_lesson.description,
                cover=initial_lesson.cover,
                cover_blocked=initial_lesson.cover_blocked,
                is_free=False,
                video_url=initial_lesson.video_url,
                previous_lesson_id=initial_lesson.previous_lesson_id,
                is_active=True,
                order=initial_lesson.order
            )
            for initial_block in initial_lesson.blocks.all():
                LessonTextBlock.objects.create(
                    lesson=new_lesson,
                    image=initial_block.image,
                    text=initial_block.text,
                    order=initial_block.order,
                    is_active=True
                )
