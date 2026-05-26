from dataclasses import dataclass

try:
    from flask_sqlalchemy import SQLAlchemy
except ModuleNotFoundError:
    class _SQLAlchemyFallback:
        Model = object
        Integer = int
        Boolean = bool

        def __init__(self):
            self._app = None

        def init_app(self, app):
            self._app = app

        def create_all(self):
            return None

        def String(self, _length=None):
            return str

        def Column(self, *_args, **_kwargs):
            return None

    SQLAlchemy = _SQLAlchemyFallback


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    onboarding_completed = db.Column(db.Boolean, nullable=False, default=False)
    profile_image_path = db.Column(db.String(255))
    created_at = db.Column(db.String(64), nullable=False)

    @property
    def profile_completed(self):
        return self.onboarding_completed

    @profile_completed.setter
    def profile_completed(self, value):
        self.onboarding_completed = bool(value)


DATABASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    onboarding_completed INTEGER NOT NULL DEFAULT 0,
    profile_image_path TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    age INTEGER NOT NULL,
    nationality TEXT NOT NULL,
    goal TEXT NOT NULL,
    preferred_split TEXT NOT NULL DEFAULT 'Upper/Lower Split',
    height_cm REAL NOT NULL,
    start_weight_kg REAL NOT NULL,
    goal_weight_kg REAL NOT NULL,
    bio TEXT,
    workout_streak_days INTEGER NOT NULL DEFAULT 0,
    accepted_terms INTEGER NOT NULL DEFAULT 0,
    accepted_terms_at TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    workout_date TEXT NOT NULL,
    exercise_name TEXT NOT NULL,
    sets_count INTEGER NOT NULL,
    reps_count INTEGER NOT NULL,
    weight_kg REAL NOT NULL,
    duration_minutes INTEGER NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS workout_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_date TEXT NOT NULL,
    split_type TEXT NOT NULL,
    split_day TEXT,
    duration_minutes INTEGER NOT NULL,
    notes TEXT,
    legacy_workout_id INTEGER UNIQUE,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (legacy_workout_id) REFERENCES workouts (id)
);

CREATE TABLE IF NOT EXISTS workout_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    exercise_name TEXT NOT NULL,
    sets_count INTEGER NOT NULL,
    reps_count INTEGER NOT NULL,
    weight_kg REAL NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES workout_sessions (id)
);

CREATE TABLE IF NOT EXISTS workout_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    split_name TEXT NOT NULL,
    day_name TEXT NOT NULL,
    exercise_name TEXT NOT NULL,
    prescribed_sets TEXT NOT NULL,
    prescribed_reps TEXT NOT NULL,
    weight_used REAL NOT NULL,
    reps_completed INTEGER NOT NULL,
    notes TEXT,
    logged_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS custom_splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    base_slug TEXT,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, slug),
    UNIQUE(user_id, name),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS custom_split_days (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    split_id INTEGER NOT NULL,
    day_order INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    focus TEXT,
    FOREIGN KEY (split_id) REFERENCES custom_splits (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS custom_split_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_id INTEGER NOT NULL,
    exercise_order INTEGER NOT NULL,
    exercise_name TEXT NOT NULL,
    sets TEXT,
    reps TEXT,
    rest TEXT,
    FOREIGN KEY (day_id) REFERENCES custom_split_days (id) ON DELETE CASCADE
);

"""


@dataclass(frozen=True)
class UserRecord:
    id: int
    email: str
    password_hash: str
    onboarding_completed: bool
    created_at: str
    profile_image_path: str | None = None


@dataclass(frozen=True)
class Profile:
    user_id: int
    full_name: str
    gender: str
    age: int
    nationality: str
    fitness_goal: str
    height_cm: float
    weight_kg: float
    goal_weight_kg: float
    terms_accepted: bool
    preferred_split: str = "Upper/Lower Split"
    bio: str | None = None


@dataclass(frozen=True)
class WorkoutLog:
    id: int
    user_id: int
    split_name: str
    day_name: str
    exercise_name: str
    prescribed_sets: str
    prescribed_reps: str
    weight_used: float
    reps_completed: int
    logged_at: str
    notes: str | None = None


@dataclass(frozen=True)
class WorkoutSession:
    id: int
    user_id: int
    date: str
    split_type: str
    duration: int
    split_day: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class WorkoutExercise:
    id: int
    session_id: int
    exercise_name: str
    sets: int
    reps: int
    weight: float
    notes: str | None = None
