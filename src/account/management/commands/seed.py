from typing import List
from pathlib import Path
from django.core.management.base import BaseCommand
import json
import random
from Curriculum.models import Curriculum, CurriculumSyllabi, SyllabiTopic
from Resource.models import Resource
from Quiz.models import Quiz, QOption
from django.db.transaction import atomic


CURRICULUMS_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent.parent / "curriculums"
)


class ResourceType:
    name: str
    url: str
    description: str
    author: str
    rtype: str
    provider: str


class OptionType:
    option: str
    reason: str
    is_correct: bool


class QuizType:
    question: str
    options: List[OptionType]


class ResourcesType:
    resources: List[ResourceType]


class TopicType:
    order: int
    title: str
    slug: str
    description: str
    resources: List[ResourceType]
    quizzes: List[QuizType]


class SyllabiType:
    order: int
    title: str
    slug: str
    description: str
    topics: List[TopicType]


class CurriculumType:
    name: str
    slug: str
    description: str
    objective: str
    prerequisites: str
    difficulty: str
    syllabi: List[SyllabiType]


class RootType:
    curriculum: CurriculumType


class Command(BaseCommand):
    help = "Create curriculum smartly"

    def add_arguments(self, parser):
        parser.add_argument(
            "--name", type=str, help="Name of curriculum json file", required=True
        )

    def handle(self, *args, **options):
        name = options.get("name")
        with atomic():
            self.run_seed(name)

    def load_seed_data(self, file: str) -> RootType:
        seed_data = None
        with open(CURRICULUMS_DIR / f"{file}.json", "r", encoding='utf-8') as f:
            seed_data = json.load(f)
        if not seed_data:
            self.stderr.write(self.style.ERROR("No seed data found"))
            return
        return seed_data
    
    def write_seed_data(self, file: str, data: RootType):
        with open(CURRICULUMS_DIR / f"{file}.json", "w") as f:
            json.dump(data, f, indent=4)

    def run_seed(self, name: str):
        self.stdout.write(self.style.HTTP_INFO("Creating curriculum..."))
        data = self.load_seed_data(name)

        try:
            curriculum = Curriculum.objects.get(slug=data["curriculum"]["slug"])
            curriculum.name = data["curriculum"]["name"]
            curriculum.description = data["curriculum"]["description"]
            curriculum.objective = data["curriculum"]["objective"]
            curriculum.prerequisites = data["curriculum"]["prerequisites"]
            curriculum.difficulty = data["curriculum"]["difficulty"]
            curriculum.save()
        except Curriculum.DoesNotExist:
            curriculum = Curriculum.objects.create(
                name=data["curriculum"]["name"],
                slug=data["curriculum"]["slug"],
                description=data["curriculum"]["description"],
                objective=data["curriculum"]["objective"],
                prerequisites=data["curriculum"]["prerequisites"],
                difficulty=data["curriculum"]["difficulty"],
            )
            data["curriculum"]["slug"] = curriculum.slug

        self.stdout.write(
            self.style.SUCCESS(f"Curriculum {curriculum.name} created successfully.")
        )

        for syllabi_order, syllabi in enumerate(data["curriculum"]["syllabi"]):
            try:
                syllabi_obj = CurriculumSyllabi.objects.get(
                    curriculum=curriculum, slug=syllabi["slug"]
                )
                syllabi_obj.order = syllabi_order + 1
                syllabi_obj.title = syllabi["title"]
                syllabi_obj.description = syllabi["description"]
                syllabi_obj.save()
            except CurriculumSyllabi.DoesNotExist:
                syllabi_obj = CurriculumSyllabi.objects.create(
                    curriculum=curriculum,
                    order=syllabi_order + 1,
                    title=syllabi["title"],
                    slug=syllabi["slug"],
                    description=syllabi["description"],
                )
                data["curriculum"]["syllabi"][syllabi_order]["slug"] = syllabi_obj.slug

            self.stdout.write(
                self.style.SUCCESS(f"Syllabi {syllabi_obj.title} created successfully.")
            )

            for topic_order, topic in enumerate(syllabi["topics"]):
                try:
                    topic_obj = SyllabiTopic.objects.get(
                        syllabi=syllabi_obj, slug=topic["slug"]
                    )
                    topic_obj.order = topic_order + 1
                    topic_obj.title = topic["title"]
                    topic_obj.description = topic["description"]
                    topic_obj.save()
                except SyllabiTopic.DoesNotExist:
                    topic_obj = SyllabiTopic.objects.create(
                        syllabi=syllabi_obj,
                        order=topic_order + 1,
                        title=topic["title"],
                        slug=topic["slug"],
                        description=topic["description"],
                    )
                    data["curriculum"]["syllabi"][syllabi_order]["topics"][topic_order][
                        "slug"
                    ] = topic_obj.slug

                self.stdout.write(
                    self.style.SUCCESS(f"Topic {topic_obj.title} created successfully.")
                )

                resources = []
                for resource in topic["resources"]:
                    try:
                        resource_obj = Resource.objects.get(name=resource["name"])
                        resource_obj.url = resource["url"]
                        resource_obj.description = resource["description"]
                        resource_obj.author = resource["author"]
                        resource_obj.rtype = resource["rtype"]
                        resource_obj.provider = resource["provider"]
                        resource_obj.save()
                    except Resource.DoesNotExist:
                        resource_obj = Resource.objects.create(
                            name=resource["name"],
                            url=resource["url"],
                            description=resource["description"],
                            author=resource["author"],
                            rtype=resource["rtype"],
                            provider=resource["provider"],
                        )
                    resources.append(resource_obj)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Resource {resource_obj.name} created successfully."
                        )
                    )

                topic_obj.resources.set(resources)

                for quiz in topic["quizzes"]:
                    try:
                        quiz_obj = Quiz.objects.get(question=quiz["question"])
                    except Quiz.DoesNotExist:
                        quiz_obj = Quiz.objects.create(
                            question=quiz["question"], topic=topic_obj
                        )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Quiz {quiz_obj.question} created successfully."
                        )
                    )

                    random.shuffle(quiz["options"])
                    for option in quiz["options"]:
                        try:
                            QOption.objects.get(option=option["option"])
                        except QOption.DoesNotExist:
                            QOption.objects.create(
                                quiz=quiz_obj,
                                option=option["option"],
                                reason=option["reason"],
                                is_correct=option["is_correct"],
                            )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Options for {quiz_obj.question} created successfully."
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Done."))

        self.write_seed_data(name, data)
        
        self.stdout.write(self.style.SUCCESS("Saved data to file."))
