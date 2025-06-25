import random

from faker import Faker
from sqlmodel import Session

from app.core.session import engine
from app.models.blog_web_post import BlogWebPost
from app.models.entity import Entity
from app.models.enums.platform import PlatformEnum
from app.models.enums.url import URLTypeEnum
from app.models.post import Post
from app.models.url import URL

fake = Faker()


def seed_entities(session: Session, count: int = 5) -> list[Entity]:
    entities = []
    for _ in range(count):
        entity = Entity(
            username=fake.user_name(),
            fullname=fake.name(),
            followers=random.randint(100, 100000),
            platform=random.choice(list(PlatformEnum)),
        )
        session.add(entity)
        entities.append(entity)
    session.commit()
    return entities


def seed_urls(session: Session, entities: list[Entity], count: int = 10) -> list[URL]:
    urls = []
    for _ in range(count):
        url = URL(
            url=fake.url(),
            type=random.choice(list(URLTypeEnum)),
            entityId=random.choice(entities).id
        )
        session.add(url)
        urls.append(url)
    session.commit()
    return urls


def seed_posts(session: Session, urls: list[URL]):
    post_urls = [url for url in urls if url.type == URLTypeEnum.POST]

    for url in post_urls:
        for _ in range(random.randint(1, 10)):
            post = Post(
                comments=random.randint(0, 500),
                likes=random.randint(0, 10000),
                views=random.randint(0, 100000),
                engagementRate=random.randint(0, 100),
                dateAnalysed=random.randint(20220101, 20250624),
                isBrokenOrDeleted=fake.boolean(),
                isFetched=fake.boolean(),
                urlId=url.id
            )
            session.add(post)

    session.commit()


def seed_blog_web_posts(session: Session, urls: list[URL]):
    web_post_urls = [url for url in urls if url.type == URLTypeEnum.WEB_POST]

    for url in web_post_urls:
        for _ in range(random.randint(1, 10)):
            blog = BlogWebPost(
                trafficCount=random.randint(0, 10000),
                engagementRate=random.randint(0, 100),
                dateAnalysed=random.randint(20220101, 20250624),
                isBrokenOrDeleted=fake.boolean(),
                isFetched=fake.boolean(),
                urlId=url.id
            )
            session.add(blog)

    session.commit()


def seed_all():
    with Session(engine) as session:
        print("🌱 Seeding database...")
        entities = seed_entities(session)
        urls = seed_urls(session, entities)
        seed_posts(session, urls)
        seed_blog_web_posts(session, urls)
        print("✅ Database seeded successfully.")
