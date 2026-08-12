import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.product import Base, ProductORM, ProductResponse

logger = logging.getLogger(__name__)

# Sample Mock Seed Data
SAMPLE_PRODUCTS = [
    {
        "id": 1,
        "name": "DevOps Handbook (2nd Ed)",
        "description": "How to Create World-Class Agility, Reliability, & Security in Technology Organizations.",
        "price": 29.99,
        "stock": 50,
        "created_at": datetime.utcnow()
    },
    {
        "id": 2,
        "name": "Docker & Kubernetes Masterclass",
        "description": "Comprehensive practical guide to containerizing microservices.",
        "price": 49.50,
        "stock": 100,
        "created_at": datetime.utcnow()
    },
    {
        "id": 3,
        "name": "Cloud Native Go Microservices",
        "description": "Build high performance microservices in Go and Python.",
        "price": 39.00,
        "stock": 25,
        "created_at": datetime.utcnow()
    },
    {
        "id": 4,
        "name": "DevSecOps Pipeline Blueprint",
        "description": "Integrating security scanning into automated CI/CD pipelines.",
        "price": 59.99,
        "stock": 15,
        "created_at": datetime.utcnow()
    }
]

class ProductRepository:
    def __init__(self):
        self.db_available = False
        self.engine = None
        self.SessionLocal = None

        try:
            self.engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 3})
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # Test connection
            with self.engine.connect() as conn:
                self.db_available = True
                logger.info("✅ Connected to PostgreSQL successfully!")

            Base.metadata.create_all(bind=self.engine)
            self._seed_data()
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL not reachable ({e}). Operating with in-memory sample seed data.")
            self.db_available = False

    def _seed_data(self):
        if not self.db_available or not self.SessionLocal:
            return

        session = self.SessionLocal()
        try:
            count = session.query(ProductORM).count()
            if count == 0:
                for item in SAMPLE_PRODUCTS:
                    product = ProductORM(
                        id=item["id"],
                        name=item["name"],
                        description=item["description"],
                        price=item["price"],
                        stock=item["stock"]
                    )
                    session.add(product)
                session.commit()
                logger.info("🌱 Seeded sample products into PostgreSQL database!")
        except Exception as e:
            logger.error(f"Failed seeding data: {e}")
            session.rollback()
        finally:
            session.close()

    def get_all(self):
        if not self.db_available or not self.SessionLocal:
            return [ProductResponse(**p) for p in SAMPLE_PRODUCTS]

        session = self.SessionLocal()
        try:
            products = session.query(ProductORM).all()
            return [ProductResponse.model_validate(p) for p in products]
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return [ProductResponse(**p) for p in SAMPLE_PRODUCTS]
        finally:
            session.close()

    def get_by_id(self, product_id: int):
        if not self.db_available or not self.SessionLocal:
            match = next((p for p in SAMPLE_PRODUCTS if p["id"] == product_id), None)
            return ProductResponse(**match) if match else None

        session = self.SessionLocal()
        try:
            product = session.query(ProductORM).filter(ProductORM.id == product_id).first()
            return ProductResponse.model_validate(product) if product else None
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            match = next((p for p in SAMPLE_PRODUCTS if p["id"] == product_id), None)
            return ProductResponse(**match) if match else None
        finally:
            session.close()
