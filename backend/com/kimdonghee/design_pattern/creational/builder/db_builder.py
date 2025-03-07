import os
import asyncpg
from dotenv import load_dotenv
from com.kimdonghee.design_pattern.creational.singleton.db_singleton import db_singleton

# ✅ 환경 변수 강제 로드
load_dotenv()

class DatabaseBuilder:
    def __init__(self):
        # ✅ db_url 확인 및 초기화
        if not hasattr(db_singleton, "db_url") or not db_singleton.db_url:
            print("⚠️ db_singleton이 올바르게 초기화되지 않았습니다. 환경 변수를 다시 로드합니다.")
            db_singleton.db_url = os.getenv("DB_URL")

        if not db_singleton.db_url:
            raise AttributeError("❌ 'db_url'이 설정되지 않았습니다. .env 파일을 확인하세요.")

        print(f"✅ DatabaseBuilder 초기화 완료: {db_singleton.db_url}")  # 디버깅 로그

        self.database_url = db_singleton.db_url
        self.min_size = 1
        self.max_size = 10
        self.timeout = 60
        self.pool = None

    def pool_size(self, min_size: int = 1, max_size: int = 10):
        self.min_size = min_size
        self.max_size = max_size
        return self

    def set_timeout(self, timeout: int = 60):  # ✅ 메서드 이름 중복 방지
        self.timeout = timeout
        return self

    async def build(self):
        if not self.database_url:
            raise ValueError("⚠️ Database URL must be set before building the database")

        print(f"🚀 Connecting to PostgreSQL: {self.database_url}")  # ✅ 디버깅 로그

        self.pool = await asyncpg.create_pool(
            dsn=self.database_url,
            min_size=self.min_size,
            max_size=self.max_size,
            timeout=self.timeout,
        )
        return AsyncDatabase(self.pool)
    
class AsyncDatabase:
    def __init__(self, pool):
        self.pool = pool

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def close(self):
        await self.pool.close()
    
async def get_db():
    # ✅ db_url 다시 확인 및 초기화
    if not hasattr(db_singleton, "db_url") or not db_singleton.db_url:
        print("⚠️ db_singleton이 올바르게 초기화되지 않았습니다. 환경 변수를 다시 로드합니다.")
        db_singleton.db_url = os.getenv("DB_URL")

        if not db_singleton.db_url:
            raise AttributeError("❌ 환경 변수를 다시 로드했지만 'db_url'이 설정되지 않았습니다. .env 파일을 확인하세요.")

    print(f"✅ db_singleton 초기화 확인: {db_singleton.db_url}")  # ✅ 디버깅 로그

    builder = DatabaseBuilder()
    db = await builder.build()

    try:
        yield db  # ✅ FastAPI의 Depends()에서 사용할 수 있도록 yield로 반환
    finally:
        await db.close()
