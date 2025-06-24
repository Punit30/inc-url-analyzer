from sqlmodel import Session, SQLModel, create_engine

from app.core.configs import settings

engine = create_engine(str(settings.DATABASE_URL), echo=True)


def init_db():
    """Initialize the database and create tables."""
    try:
        from app.models.entity import Entity
        from app.models.url import URL
        from app.models.post import Post
        from app.models.blog_web_post import BlogWebPost

        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print("Ererer", e)


def get_session():
    """Get a new SQLModel session."""
    with Session(engine) as session:
        yield session
