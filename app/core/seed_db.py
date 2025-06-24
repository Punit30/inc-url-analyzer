from sqlmodel import Session
from app.core.session import engine
from app.models.entity import Entity
from app.models.url import URL
from app.models.post import Post
from app.models.blog_web_post import BlogWebPost
from app.models.enums.platform import PlatformEnum
from faker import Faker
import random

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
            entityId=random.choice(entities).id
        )
        session.add(url)
        urls.append(url)
    session.commit()
    return urls

def seed_posts(session: Session, urls: list[URL]):
    # Ensure unique urlId per Post
    selected_urls = random.sample(urls, min(len(urls), 5))
    for url in selected_urls:
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
    selected_urls = random.sample(urls, min(len(urls), 5))
    for url in selected_urls:
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
