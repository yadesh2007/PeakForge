import os
import re
import sqlite3
from datetime import date, datetime, timedelta, timezone
from functools import wraps
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from category_workouts import attach_workout_details
from models import DATABASE_SCHEMA, db, User

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "instance", "fitness.db")


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
app.config["DATABASE"] = DATABASE_PATH
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fitness.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

PROFILE_IMAGE_UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "profile_images")
PROFILE_IMAGE_URL_PREFIX = "uploads/profile_images"
ALLOWED_PROFILE_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_PROFILE_IMAGE_BYTES = 2 * 1024 * 1024
try:
    LOCAL_TIMEZONE = ZoneInfo("Asia/Kolkata")
except ZoneInfoNotFoundError:
    LOCAL_TIMEZONE = timezone(timedelta(hours=5, minutes=30), name="Asia/Kolkata")


CATEGORY_PAGES = {
    "bulking": {
        "name": "Bulking",
        "tagline": "Build size with controlled surplus, heavy training, and steady recovery.",
        "frequency": "3-5 days/week",
        "focus": ["Progressive overload", "Calorie surplus", "Compound lifts", "Sleep consistency"],
        "starter_plan": [
            "Train 4-5 days per week with compounds first.",
            "Add weight or reps when sets feel controlled.",
            "Keep protein high and increase calories slowly.",
        ],
        "splits": [
            {
                "name": "Upper / Lower Split",
                "best_for": "Lifters who want high-quality volume with enough recovery between sessions.",
                "schedule": ["Mon: Upper", "Tue: Lower", "Thu: Upper", "Fri: Lower"],
            },
            {
                "name": "Push / Pull / Legs",
                "best_for": "Anyone who enjoys focused muscle-group sessions and can train 3-6 days weekly.",
                "schedule": ["Day 1: Push", "Day 2: Pull", "Day 3: Legs", "Repeat if recovery is strong"],
            },
            {
                "name": "Bro Split (Body Part Split)",
                "best_for": "Lifters who want dedicated muscle-group days with simple recovery spacing.",
                "schedule": ["Mon: Chest", "Tue: Back", "Wed: Legs", "Thu: Shoulders", "Fri: Arms"],
            },
        ],
        "golden_rules": [
            "Caloric surplus of 300-500 calories/day.",
            "Protein intake: 1.6-2.2 g/kg body weight.",
            "Use progressive overload on compound lifts.",
        ],
        "tips": [
            "Keep sleep consistent so the surplus turns into performance and recovery.",
            "Track scale trends weekly instead of reacting to one high or low day.",
            "Add volume gradually when lifts stall, not all at once.",
        ],
    },
    "cutting": {
        "name": "Cutting",
        "tagline": "Lean down while protecting strength, muscle, and energy.",
        "frequency": "3-5 days/week",
        "focus": ["Calorie deficit", "Strength retention", "High protein", "Daily steps"],
        "starter_plan": [
            "Keep lifting heavy enough to signal muscle retention.",
            "Use a small deficit before making aggressive changes.",
            "Track training trends, not single-session noise.",
        ],
        "splits": [
            {
                "name": "Upper / Lower Split",
                "best_for": "Maintaining strength while managing fatigue during a calorie deficit.",
                "schedule": ["Mon: Upper", "Tue: Lower", "Thu: Upper", "Fri: Lower"],
            },
            {
                "name": "Push / Pull / Legs",
                "best_for": "Intermediate lifters who want enough volume without exhausting recovery.",
                "schedule": ["Mon: Push", "Wed: Pull", "Fri: Legs", "Optional: repeat lighter sessions"],
            },
            {
                "name": "Bro Split (Body Part Split)",
                "best_for": "Lifters who prefer focused muscle-group sessions while managing deficit fatigue.",
                "schedule": ["Mon: Chest", "Tue: Back", "Wed: Legs", "Thu: Shoulders", "Fri: Arms"],
            },
        ],
        "golden_rules": [
            "Calorie deficit of 300-500 calories/day.",
            "Protein intake: 2.0-2.4 g/kg.",
            "Maintain heavy lifting where possible.",
            "Add NEAT and low-intensity cardio before cutting calories aggressively.",
        ],
        "tips": [
            "Keep rest days active with walking, mobility, or easy cardio.",
            "Expect some performance fluctuation, but protect your main lifts.",
            "Use sleep and hunger as early signs that the deficit may be too aggressive.",
        ],
    },
    "recomposition": {
        "name": "Recomposition",
        "tagline": "Build muscle and reduce fat with patient, balanced training.",
        "frequency": "3-5 days/week",
        "focus": ["Protein target", "Consistent lifting", "Training quality", "Recovery quality"],
        "starter_plan": [
            "Train each major muscle 2 times weekly.",
            "Keep calories near maintenance and prioritize protein.",
            "Use photos, measurements, and strength trends together.",
        ],
        "splits": [
            {
                "name": "Upper / Lower Split",
                "best_for": "Balanced muscle gain and fat loss with repeatable weekly structure.",
                "schedule": ["Mon: Upper", "Tue: Lower", "Thu: Upper", "Sat: Lower"],
            },
            {
                "name": "Push / Pull / Legs",
                "best_for": "Lifters who can recover from higher weekly frequency.",
                "schedule": ["Push", "Pull", "Legs", "Rest", "Repeat based on recovery"],
            },
            {
                "name": "Bro Split (Body Part Split)",
                "best_for": "Lifters who want focused body-part sessions with easy-to-track performance.",
                "schedule": ["Mon: Chest", "Tue: Back", "Wed: Legs", "Thu: Shoulders", "Fri: Arms"],
            },
        ],
        "golden_rules": [
            "Stay at maintenance calories or a small deficit of 200-300 calories.",
            "Protein intake: 1.6-2.2 g/kg.",
            "Progressive overload drives the muscle-gain side of recomposition.",
            "Use strategic low-intensity cardio without compromising lifts.",
        ],
        "tips": [
            "Use strength, photos, measurements, and body weight together.",
            "Be patient. Recomposition is slower but often more sustainable.",
            "Prioritize consistent training quality over chasing daily scale changes.",
        ],
    },
    "strength": {
        "name": "Strength",
        "tagline": "Move heavier with smart progression and crisp technique.",
        "frequency": "3-4 days/week",
        "focus": ["Low-rep compounds", "Technique practice", "Rest periods", "Load tracking"],
        "starter_plan": [
            "Anchor training around squat, press, pull, hinge, and carry patterns.",
            "Rest longer for heavy sets and keep reps clean.",
            "Plan lighter weeks before fatigue piles up.",
        ],
        "splits": [
            {
                "name": "Upper / Lower Split",
                "best_for": "Strength athletes who want frequent exposure to heavy upper and lower lifts.",
                "schedule": ["Mon: Upper heavy", "Tue: Lower heavy", "Thu: Upper volume", "Fri: Lower volume"],
            },
            {
                "name": "Bro Split (Body Part Split)",
                "best_for": "Strength-focused lifters who want dedicated body-part emphasis across the week.",
                "schedule": ["Mon: Chest", "Tue: Back", "Wed: Legs", "Thu: Shoulders", "Fri: Arms"],
            },
            {
                "name": "Push / Pull / Legs",
                "best_for": "Simple strength practice around movement patterns across 3 days.",
                "schedule": ["Mon: Push", "Wed: Pull", "Fri: Legs"],
            },
        ],
        "golden_rules": [
            "Main lifts should often live in the 1-5 rep range.",
            "Rest 3-5 minutes between heavy sets.",
            "Track systemic fatigue, not just muscle soreness.",
            "Eat at maintenance or a slight surplus for better performance.",
        ],
        "tips": [
            "Leave technical reps in reserve when form starts slipping.",
            "Use lighter back-off work to build practice without draining recovery.",
            "Plan deloads before joints and motivation force them on you.",
        ],
    },
    "endurance": {
        "name": "Endurance",
        "tagline": "Improve stamina, conditioning, and work capacity over time.",
        "frequency": "3-5 days/week",
        "focus": ["Zone 2 base", "Intervals", "Pacing", "Weekly volume"],
        "starter_plan": [
            "Build easy aerobic volume before adding intensity.",
            "Use one or two harder conditioning days per week.",
            "Progress total volume gradually to avoid burnout.",
        ],
        "splits": [
            {
                "name": "Upper / Lower Split",
                "best_for": "Balancing resistance training with aerobic sessions across the week.",
                "schedule": ["Mon: Upper", "Tue: Lower", "Thu: Upper circuit", "Sat: Lower + conditioning"],
            },
            {
                "name": "Push / Pull / Legs",
                "best_for": "Higher-frequency endurance work with either 3 or 6 weekly sessions.",
                "schedule": ["Push", "Pull", "Legs", "Rest or easy cardio", "Repeat if ready"],
            },
            {
                "name": "Bro Split (Body Part Split)",
                "best_for": "Dedicated muscle-endurance sessions with clear body-part focus.",
                "schedule": ["Mon: Chest", "Tue: Back", "Wed: Legs", "Thu: Shoulders", "Fri: Arms"],
            },
        ],
        "golden_rules": [
            "Use 15-25+ reps per set for endurance-focused work.",
            "Rest 30-60 seconds between most sets.",
            "Use circuits and supersets to build work capacity.",
            "Include aerobic conditioning alongside resistance training.",
        ],
        "tips": [
            "Build an easy base before stacking intense intervals.",
            "Progress total weekly volume gradually.",
            "Use pacing notes so hard sessions do not turn into random exhaustion.",
        ],
    },
    "stay-active": {
        "name": "Stay active",
        "tagline": "Keep movement consistent, simple, and sustainable.",
        "frequency": "3-5 days/week",
        "focus": ["Daily movement", "Mobility", "Light strength", "Habit rhythm"],
        "starter_plan": [
            "Pick a repeatable weekly movement schedule.",
            "Mix walking, mobility, and simple resistance training.",
            "Track consistency first, intensity second.",
        ],
        "splits": [
            {
                "name": "Upper / Lower Split",
                "best_for": "Simple weekly consistency with enough recovery between sessions.",
                "schedule": ["Mon: Upper", "Tue: Lower", "Thu: Upper", "Fri: Lower"],
            },
            {
                "name": "4-Day Hybrid Activity Split",
                "best_for": "Combining strength, cardio, and mobility without chasing max intensity.",
                "schedule": ["Mon: Strength", "Tue: Cardio", "Thu: Strength", "Sat: Mobility + easy cardio"],
            },
            {
                "name": "5-Day Push/Pull/Legs + Cardio",
                "best_for": "People who like frequent movement and varied sessions.",
                "schedule": ["Mon: Push", "Tue: Pull", "Wed: Cardio", "Thu: Legs", "Sat: Mobility or easy cardio"],
            },
        ],
        "golden_rules": [
            "Use moderate weights for 8-12 reps.",
            "Aim for 150 minutes of aerobic activity weekly.",
            "Prioritize mobility and comfortable range of motion.",
            "Focus on consistency over intensity.",
        ],
        "tips": [
            "Keep sessions short enough that you can repeat them next week.",
            "Use walks, stretching, and light resistance work as valid wins.",
            "Increase effort only after the habit feels stable.",
        ],
    },
}

attach_workout_details(CATEGORY_PAGES)

CATEGORY_SLUGS = {value["name"]: slug for slug, value in CATEGORY_PAGES.items()}
PREFERRED_SPLIT_OPTIONS = [
    "Push/Pull/Legs (PPL)",
    "Upper/Lower Split",
    "Bro Split (Body Part Split)",
    "Power/Strength Split",
]
DEFAULT_PREFERRED_SPLIT = "Upper/Lower Split"
WORKOUT_SPLIT_PROGRAMS = {
    "Push/Pull/Legs (PPL)": [
        {
            "day": "Push Day",
            "focus": "Chest, shoulders, triceps",
            "exercises": [
                {"name": "Bench Press", "sets": "4", "reps": "8-10", "rest": "2 min"},
                {"name": "Incline Dumbbell Press", "sets": "3", "reps": "10-12", "rest": "90 sec"},
                {"name": "Overhead Press", "sets": "3", "reps": "8-10", "rest": "2 min"},
                {"name": "Lateral Raise", "sets": "3", "reps": "12-15", "rest": "60 sec"},
                {"name": "Triceps Pushdown", "sets": "3", "reps": "12-15", "rest": "60 sec"},
            ],
        },
        {
            "day": "Pull Day",
            "focus": "Back, rear delts, biceps",
            "exercises": [
                {"name": "Lat Pulldown", "sets": "4", "reps": "8-12", "rest": "90 sec"},
                {"name": "Barbell Row", "sets": "4", "reps": "8-10", "rest": "2 min"},
                {"name": "Seated Cable Row", "sets": "3", "reps": "10-12", "rest": "90 sec"},
                {"name": "Face Pull", "sets": "3", "reps": "12-15", "rest": "60 sec"},
                {"name": "Dumbbell Curl", "sets": "3", "reps": "10-12", "rest": "60 sec"},
            ],
        },
        {
            "day": "Legs Day",
            "focus": "Quads, hamstrings, glutes, calves",
            "exercises": [
                {"name": "Back Squat", "sets": "4", "reps": "6-10", "rest": "2-3 min"},
                {"name": "Romanian Deadlift", "sets": "3", "reps": "8-10", "rest": "2 min"},
                {"name": "Leg Press", "sets": "3", "reps": "10-12", "rest": "90 sec"},
                {"name": "Leg Curl", "sets": "3", "reps": "12-15", "rest": "60 sec"},
                {"name": "Standing Calf Raise", "sets": "4", "reps": "12-15", "rest": "60 sec"},
            ],
        },
    ],
    "Upper/Lower Split": [
        {
            "day": "Upper Day",
            "focus": "Chest, back, shoulders, arms",
            "exercises": [
                {"name": "Bench Press", "sets": "4", "reps": "6-10", "rest": "2 min"},
                {"name": "Bent-Over Row", "sets": "4", "reps": "8-10", "rest": "2 min"},
                {"name": "Incline Dumbbell Press", "sets": "3", "reps": "10-12", "rest": "90 sec"},
                {"name": "Lat Pulldown", "sets": "3", "reps": "10-12", "rest": "90 sec"},
                {"name": "Lateral Raise", "sets": "3", "reps": "12-15", "rest": "60 sec"},
            ],
        },
        {
            "day": "Lower Day",
            "focus": "Quads, hamstrings, glutes, calves",
            "exercises": [
                {"name": "Back Squat", "sets": "4", "reps": "6-10", "rest": "2-3 min"},
                {"name": "Romanian Deadlift", "sets": "4", "reps": "8-10", "rest": "2 min"},
                {"name": "Walking Lunge", "sets": "3", "reps": "10-12", "rest": "90 sec"},
                {"name": "Leg Curl", "sets": "3", "reps": "12-15", "rest": "60 sec"},
                {"name": "Seated Calf Raise", "sets": "4", "reps": "12-15", "rest": "60 sec"},
            ],
        },
    ],
    "Bro Split (Body Part Split)": [
        {
            "day": "Chest Day",
            "focus": "Chest and pressing accessories",
            "exercises": [
                {"name": "Incline Bench Press", "sets": "4", "reps": "8-10", "rest": "2 min"},
                {"name": "Flat Dumbbell Press", "sets": "3", "reps": "10-12", "rest": "90 sec"},
                {"name": "Machine Chest Press", "sets": "3", "reps": "10-12", "rest": "90 sec"},
                {"name": "Cable Fly", "sets": "3", "reps": "12-15", "rest": "60 sec"},
            ],
        },
        {
            "day": "Back Day",
            "focus": "Lats, mid-back, rear delts",
            "exercises": [
                {"name": "Pull-Up or Lat Pulldown", "sets": "4", "reps": "8-10", "rest": "2 min"},
                {"name": "Barbell Row", "sets": "4", "reps": "8-10", "rest": "2 min"},
                {"name": "Chest-Supported Row", "sets": "3", "reps": "10-12", "rest": "90 sec"},
                {"name": "Straight-Arm Pulldown", "sets": "3", "reps": "12-15", "rest": "60 sec"},
            ],
        },
        {
            "day": "Legs Day",
            "focus": "Quads, hamstrings, glutes, calves",
            "exercises": [
                {"name": "Hack Squat", "sets": "4", "reps": "8-10", "rest": "2 min"},
                {"name": "Romanian Deadlift", "sets": "4", "reps": "8-10", "rest": "2 min"},
                {"name": "Leg Extension", "sets": "3", "reps": "12-15", "rest": "60 sec"},
                {"name": "Leg Curl", "sets": "3", "reps": "12-15", "rest": "60 sec"},
            ],
        },
        {
            "day": "Shoulders / Arms Day",
            "focus": "Delts, biceps, triceps",
            "exercises": [
                {"name": "Seated Dumbbell Press", "sets": "4", "reps": "8-10", "rest": "2 min"},
                {"name": "Cable Lateral Raise", "sets": "4", "reps": "12-15", "rest": "60 sec"},
                {"name": "EZ-Bar Curl", "sets": "3", "reps": "10-12", "rest": "60 sec"},
                {"name": "Overhead Triceps Extension", "sets": "3", "reps": "10-12", "rest": "60 sec"},
            ],
        },
    ],
    "Power/Strength Split": [
        {
            "day": "Power Day A",
            "focus": "Squat, press, row, core strength",
            "exercises": [
                {"name": "Back Squat", "sets": "5", "reps": "3-5", "rest": "3 min"},
                {"name": "Bench Press", "sets": "5", "reps": "3-5", "rest": "3 min"},
                {"name": "Barbell Row", "sets": "4", "reps": "5-6", "rest": "2 min"},
                {"name": "Romanian Deadlift", "sets": "3", "reps": "6-8", "rest": "2 min"},
                {"name": "Pallof Press", "sets": "3", "reps": "10 each side", "rest": "60 sec"},
            ],
        },
        {
            "day": "Power Day B",
            "focus": "Hinge, vertical pull, overhead strength",
            "exercises": [
                {"name": "Deadlift", "sets": "5", "reps": "2-4", "rest": "3 min"},
                {"name": "Overhead Press", "sets": "4", "reps": "4-6", "rest": "2-3 min"},
                {"name": "Pull-Up or Lat Pulldown", "sets": "4", "reps": "6-8", "rest": "2 min"},
                {"name": "Front Squat", "sets": "3", "reps": "5-6", "rest": "2 min"},
                {"name": "Farmer Carry", "sets": "3", "reps": "30-40 m", "rest": "90 sec"},
            ],
        },
        {
            "day": "Power Day C",
            "focus": "Speed practice and accessories",
            "exercises": [
                {"name": "Speed Bench Press", "sets": "6", "reps": "3", "rest": "90 sec"},
                {"name": "Box Squat", "sets": "5", "reps": "3", "rest": "2 min"},
                {"name": "Chest-Supported Row", "sets": "4", "reps": "8", "rest": "90 sec"},
                {"name": "Hip Thrust", "sets": "3", "reps": "6-8", "rest": "2 min"},
                {"name": "Face Pull", "sets": "3", "reps": "12-15", "rest": "60 sec"},
            ],
        },
    ],
}

SPLIT_PLANNER_CARDS = [
    {
        "name": "Upper/Lower Split",
        "slug": "upper-lower",
        "icon": "UL",
        "description": "Train upper and lower body on separate days.",
    },
    {
        "name": "Push/Pull/Legs (PPL)",
        "slug": "ppl",
        "icon": "PPL",
        "description": "Divide workouts into pushing, pulling, and leg movements.",
    },
    {
        "name": "Bro Split (Body Part Split)",
        "slug": "bro-split",
        "icon": "BRO",
        "description": "Focus on one major muscle group per day.",
    },
    {
        "name": "Power/Strength Split",
        "slug": "power-strength",
        "icon": "PWR",
        "description": "Build force output around heavy compound lifts.",
    },
]
SPLIT_SLUGS = {item["slug"]: item["name"] for item in SPLIT_PLANNER_CARDS}


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "custom-split"


def make_unique_split_slug(db, user_id, name, current_slug=None):
    base_slug = slugify(name)
    slug = base_slug
    counter = 2
    while True:
        existing = db.execute(
            "SELECT id FROM custom_splits WHERE user_id = ? AND slug = ?",
            (user_id, slug),
        ).fetchone()
        if not existing or slug == current_slug:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


def split_icon(name):
    words = re.findall(r"[A-Za-z0-9]+", name)
    return "".join(word[0] for word in words[:3]).upper() or "SP"


def get_custom_split_by_slug(user_id, slug):
    return get_db().execute(
        "SELECT * FROM custom_splits WHERE user_id = ? AND slug = ?",
        (user_id, slug),
    ).fetchone()


def get_custom_split_by_name(user_id, name):
    return get_db().execute(
        "SELECT * FROM custom_splits WHERE user_id = ? AND name = ?",
        (user_id, name),
    ).fetchone()


def load_custom_split_program(split_id):
    db = get_db()
    days = db.execute(
        """
        SELECT *
        FROM custom_split_days
        WHERE split_id = ?
        ORDER BY day_order, id
        """,
        (split_id,),
    ).fetchall()

    program = []
    for day in days:
        exercises = db.execute(
            """
            SELECT *
            FROM custom_split_exercises
            WHERE day_id = ?
            ORDER BY exercise_order, id
            """,
            (day["id"],),
        ).fetchall()
        program.append(
            {
                "day": day["day_name"],
                "focus": day["focus"] or "Custom training day",
                "exercises": [
                    {
                        "name": exercise["exercise_name"],
                        "sets": exercise["sets"] or "3",
                        "reps": exercise["reps"] or "8-12",
                        "rest": exercise["rest"] or "",
                    }
                    for exercise in exercises
                ],
            }
        )

    return program


def get_split_definition(user_id, slug):
    custom_split = get_custom_split_by_slug(user_id, slug)
    if custom_split:
        return {
            "name": custom_split["name"],
            "slug": custom_split["slug"],
            "program": load_custom_split_program(custom_split["id"]),
            "is_custom": True,
        }

    split_name = SPLIT_SLUGS.get(slug)
    if not split_name:
        return None
    return {
        "name": split_name,
        "slug": slug,
        "program": WORKOUT_SPLIT_PROGRAMS[split_name],
        "is_custom": False,
    }


def get_available_split_cards(user_id):
    cards = [dict(card) for card in SPLIT_PLANNER_CARDS]
    custom_splits = get_db().execute(
        """
        SELECT *
        FROM custom_splits
        WHERE user_id = ?
        ORDER BY base_slug IS NULL, name COLLATE NOCASE
        """,
        (user_id,),
    ).fetchall()

    for custom_split in custom_splits:
        if custom_split["base_slug"]:
            for card in cards:
                if card["slug"] == custom_split["slug"]:
                    card["name"] = custom_split["name"]
                    card["description"] = custom_split["description"] or "Your customized version of this split."
                    card["customized"] = True
                    break
            continue

        cards.append(
            {
                "name": custom_split["name"],
                "slug": custom_split["slug"],
                "icon": split_icon(custom_split["name"]),
                "description": custom_split["description"] or "Custom split built by you.",
                "custom": True,
            }
        )

    return cards


def get_selected_split(profile, user_id=None):
    split = profile["preferred_split"] if profile and "preferred_split" in profile.keys() else DEFAULT_PREFERRED_SPLIT
    if user_id and get_custom_split_by_name(user_id, split):
        return split
    return split if split in WORKOUT_SPLIT_PROGRAMS else DEFAULT_PREFERRED_SPLIT


def get_selected_program(user_id, profile):
    selected_split = get_selected_split(profile, user_id)
    custom_split = get_custom_split_by_name(user_id, selected_split)
    if custom_split:
        program = load_custom_split_program(custom_split["id"])
        if program:
            return selected_split, program
    return selected_split, WORKOUT_SPLIT_PROGRAMS[selected_split]


def get_today_workout(profile, user_id=None):
    if user_id:
        _split_name, program = get_selected_program(user_id, profile)
    else:
        selected_split = get_selected_split(profile)
        program = WORKOUT_SPLIT_PROGRAMS[selected_split]
    return program[get_calendar_workout_index(program)]


def get_calendar_workout_index(program):
    if not program:
        return 0
    return get_local_today().weekday() % len(program)


def get_program_day_names(program):
    return [day["day"] for day in program if day.get("day")]


def get_adaptive_split_workout_index(user_id, split_name, program):
    if not program:
        return 0

    day_names = get_program_day_names(program)
    if not day_names:
        return get_calendar_workout_index(program)

    placeholders = ", ".join("?" for _ in day_names)
    latest_session = get_db().execute(
        f"""
        SELECT split_day, session_date
        FROM workout_sessions
        WHERE user_id = ?
          AND split_type = ?
          AND split_day IN ({placeholders})
        ORDER BY session_date DESC, id DESC
        LIMIT 1
        """,
        (user_id, split_name, *day_names),
    ).fetchone()

    if not latest_session:
        return 0

    last_workout_date = parse_iso_date(latest_session["session_date"])
    last_split_day = latest_session["split_day"]
    if last_workout_date is None or last_split_day not in day_names:
        return get_calendar_workout_index(program)

    days_missed = (get_local_today() - last_workout_date).days
    if days_missed < 0:
        return get_calendar_workout_index(program)

    last_index = day_names.index(last_split_day)
    cycle_length = len(program)
    if days_missed == 0:
        return get_calendar_workout_index(program)
    if days_missed == 1:
        return (last_index + 1) % cycle_length
    return (last_index + (days_missed % cycle_length)) % cycle_length


def rotate_program_to_adaptive_split_day(user_id, split_name, program):
    if not program:
        return program
    due_index = get_adaptive_split_workout_index(user_id, split_name, program)
    return program[due_index:] + program[:due_index]


def allowed_profile_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_PROFILE_IMAGE_EXTENSIONS


def save_profile_image_upload(file_storage, user_id):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_profile_image(file_storage.filename):
        raise ValueError("Upload a JPG, JPEG, PNG, or WEBP image.")

    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > MAX_PROFILE_IMAGE_BYTES:
        raise ValueError("Profile image must be 2 MB or smaller.")

    header = file_storage.stream.read(16)
    file_storage.stream.seek(0)
    is_jpeg = header.startswith(b"\xff\xd8\xff")
    is_png = header.startswith(b"\x89PNG\r\n\x1a\n")
    is_webp = header.startswith(b"RIFF") and header[8:12] == b"WEBP"
    if not (is_jpeg or is_png or is_webp):
        raise ValueError("Upload a valid JPG, PNG, or WEBP image.")

    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    user_folder = os.path.join(PROFILE_IMAGE_UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    filename = f"profile_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.{extension}"
    file_storage.save(os.path.join(user_folder, filename))
    return f"{PROFILE_IMAGE_URL_PREFIX}/{user_id}/{filename}"


def parse_split_form(form):
    day_names = form.getlist("day_name[]")
    day_focuses = form.getlist("day_focus[]")
    exercise_day_indexes = form.getlist("exercise_day_index[]")
    exercise_names = form.getlist("exercise_name[]")
    exercise_sets = form.getlist("exercise_sets[]")
    exercise_reps = form.getlist("exercise_reps[]")
    exercise_rests = form.getlist("exercise_rest[]")

    days = []
    for index, raw_name in enumerate(day_names):
        day_name = raw_name.strip()
        if not day_name:
            continue
        days.append(
            {
                "source_index": str(index),
                "day": day_name,
                "focus": day_focuses[index].strip() if index < len(day_focuses) else "",
                "exercises": [],
            }
        )

    day_by_source_index = {day["source_index"]: day for day in days}
    for index, raw_name in enumerate(exercise_names):
        exercise_name = raw_name.strip()
        if not exercise_name:
            continue
        source_index = exercise_day_indexes[index] if index < len(exercise_day_indexes) else ""
        day = day_by_source_index.get(source_index)
        if not day:
            continue
        day["exercises"].append(
            {
                "name": exercise_name,
                "sets": exercise_sets[index].strip() if index < len(exercise_sets) else "",
                "reps": exercise_reps[index].strip() if index < len(exercise_reps) else "",
                "rest": exercise_rests[index].strip() if index < len(exercise_rests) else "",
            }
        )

    days = [day for day in days if day["exercises"]]
    if not days:
        raise ValueError("Add at least one workout day with one exercise.")
    return days


def upsert_custom_split(user_id, name, days, slug=None, base_slug=None, split_id=None):
    db = get_db()
    timestamp = datetime.utcnow().isoformat()
    name = name.strip()
    if not name:
        raise ValueError("Split name is required.")
    if base_slug is None and split_id is None and name in WORKOUT_SPLIT_PROGRAMS:
        raise ValueError("Choose a split name that is not already used by a default split.")

    duplicate = db.execute(
        """
        SELECT id
        FROM custom_splits
        WHERE user_id = ? AND lower(name) = lower(?) AND (? IS NULL OR id != ?)
        """,
        (user_id, name, split_id, split_id),
    ).fetchone()
    if duplicate:
        raise ValueError("You already have a split with that name.")

    if split_id:
        db.execute(
            """
            UPDATE custom_splits
            SET name = ?, description = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (name, "Your customized workout split.", timestamp, split_id, user_id),
        )
        db.execute(
            "DELETE FROM custom_split_exercises WHERE day_id IN (SELECT id FROM custom_split_days WHERE split_id = ?)",
            (split_id,),
        )
        db.execute("DELETE FROM custom_split_days WHERE split_id = ?", (split_id,))
        custom_split_id = split_id
    else:
        resolved_slug = slug or make_unique_split_slug(db, user_id, name)
        db.execute(
            """
            INSERT INTO custom_splits (user_id, name, slug, base_slug, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, resolved_slug, base_slug, "Your customized workout split.", timestamp, timestamp),
        )
        custom_split_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

    for day_order, day in enumerate(days):
        cursor = db.execute(
            """
            INSERT INTO custom_split_days (split_id, day_order, day_name, focus)
            VALUES (?, ?, ?, ?)
            """,
            (custom_split_id, day_order, day["day"], day["focus"]),
        )
        day_id = cursor.lastrowid
        for exercise_order, exercise in enumerate(day["exercises"]):
            db.execute(
                """
                INSERT INTO custom_split_exercises (
                    day_id, exercise_order, exercise_name, sets, reps, rest
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    day_id,
                    exercise_order,
                    exercise["name"],
                    exercise["sets"],
                    exercise["reps"],
                    exercise["rest"],
                ),
            )

    db.commit()
    return db.execute("SELECT * FROM custom_splits WHERE id = ?", (custom_split_id,)).fetchone()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    os.makedirs(PROFILE_IMAGE_UPLOAD_FOLDER, exist_ok=True)
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    db.executescript(DATABASE_SCHEMA)
    db.commit()

    user_columns = {
        row[1] for row in db.execute("PRAGMA table_info(users)").fetchall()
    }
    if "name" not in user_columns:
        db.execute("ALTER TABLE users ADD COLUMN name TEXT")
        db.commit()
        user_columns.add("name")
    if "age" not in user_columns:
        db.execute("ALTER TABLE users ADD COLUMN age INTEGER")
        db.commit()
        user_columns.add("age")
    if "profile_completed" not in user_columns:
        db.execute(
            "ALTER TABLE users ADD COLUMN profile_completed INTEGER NOT NULL DEFAULT 0"
        )
        db.commit()
        user_columns.add("profile_completed")
    if "onboarding_completed" not in user_columns:
        db.execute(
            "ALTER TABLE users ADD COLUMN onboarding_completed INTEGER NOT NULL DEFAULT 0"
        )
        db.execute(
            """
            UPDATE users
            SET onboarding_completed = 1
            WHERE id IN (SELECT user_id FROM profiles)
            """
        )
        db.commit()
        user_columns.add("onboarding_completed")
    if "profile_image_path" not in user_columns:
        db.execute("ALTER TABLE users ADD COLUMN profile_image_path TEXT")
        db.commit()
        user_columns.add("profile_image_path")

    profile_columns = {
        row[1] for row in db.execute("PRAGMA table_info(profiles)").fetchall()
    }
    if "preferred_split" not in profile_columns:
        db.execute(
            "ALTER TABLE profiles ADD COLUMN preferred_split TEXT NOT NULL DEFAULT 'Upper/Lower Split'"
        )
        db.commit()
        profile_columns.add("preferred_split")
    if "bio" not in profile_columns:
        db.execute("ALTER TABLE profiles ADD COLUMN bio TEXT")
        db.commit()
        profile_columns.add("bio")
    if "workout_streak_days" not in profile_columns:
        db.execute(
            "ALTER TABLE profiles ADD COLUMN workout_streak_days INTEGER NOT NULL DEFAULT 0"
        )
        db.commit()
        profile_columns.add("workout_streak_days")

    db.execute(
        """
        UPDATE users
        SET name = (
                SELECT profiles.full_name
                FROM profiles
                WHERE profiles.user_id = users.id
            ),
            age = (
                SELECT profiles.age
                FROM profiles
                WHERE profiles.user_id = users.id
            )
        WHERE EXISTS (
            SELECT 1
            FROM profiles
            WHERE profiles.user_id = users.id
              AND TRIM(COALESCE(profiles.full_name, '')) != ''
              AND profiles.age IS NOT NULL
              AND profiles.age > 0
        )
        """
    )
    db.execute(
        """
        UPDATE users
        SET profile_completed = CASE
                WHEN TRIM(COALESCE(name, '')) != ''
                 AND age IS NOT NULL
                 AND age > 0
                THEN 1
                ELSE 0
            END,
            onboarding_completed = CASE
                WHEN TRIM(COALESCE(name, '')) != ''
                 AND age IS NOT NULL
                 AND age > 0
                THEN 1
                ELSE 0
            END
        """
    )
    db.commit()

    workout_session_columns = {
        row[1] for row in db.execute("PRAGMA table_info(workout_sessions)").fetchall()
    }
    if "split_day" not in workout_session_columns:
        db.execute("ALTER TABLE workout_sessions ADD COLUMN split_day TEXT")
        db.commit()

    db.execute(
        """
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
        )
        """
    )
    db.execute(
        """
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
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS custom_split_days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            split_id INTEGER NOT NULL,
            day_order INTEGER NOT NULL,
            day_name TEXT NOT NULL,
            focus TEXT,
            FOREIGN KEY (split_id) REFERENCES custom_splits (id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS custom_split_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_id INTEGER NOT NULL,
            exercise_order INTEGER NOT NULL,
            exercise_name TEXT NOT NULL,
            sets TEXT,
            reps TEXT,
            rest TEXT,
            FOREIGN KEY (day_id) REFERENCES custom_split_days (id) ON DELETE CASCADE
        )
        """
    )
    db.commit()

    normalize_preferred_splits(db)
    migrate_legacy_workouts(db)
    for profile in db.execute("SELECT user_id FROM profiles").fetchall():
        sync_workout_streak_from_sessions(db, profile["user_id"])
    db.commit()
    db.close()


def normalize_preferred_splits(db):
    allowed_splits = tuple(PREFERRED_SPLIT_OPTIONS)
    placeholders = ", ".join("?" for _ in allowed_splits)
    db.execute(
        f"""
        UPDATE profiles
        SET preferred_split = ?
        WHERE preferred_split IS NULL
           OR preferred_split = ''
           OR (
                preferred_split NOT IN ({placeholders})
                AND NOT EXISTS (
                    SELECT 1
                    FROM custom_splits
                    WHERE custom_splits.user_id = profiles.user_id
                      AND custom_splits.name = profiles.preferred_split
                )
           )
        """,
        (DEFAULT_PREFERRED_SPLIT, *allowed_splits),
    )

    session_columns = {
        row[1] for row in db.execute("PRAGMA table_info(workout_sessions)").fetchall()
    }
    if "split_type" in session_columns:
        db.execute(
            """
            UPDATE workout_sessions
            SET split_type = ?
            WHERE split_type IS NULL OR split_type = ''
            """,
            (DEFAULT_PREFERRED_SPLIT,),
        )

    db.commit()


def migrate_legacy_workouts(db):
    session_columns = {
        row[1] for row in db.execute("PRAGMA table_info(workout_sessions)").fetchall()
    }
    if "legacy_workout_id" not in session_columns:
        return

    legacy_workouts = db.execute(
        """
        SELECT w.*
        FROM workouts w
        LEFT JOIN workout_sessions s ON s.legacy_workout_id = w.id
        WHERE s.id IS NULL
        ORDER BY w.id
        """
    ).fetchall()

    for workout in legacy_workouts:
        cursor = db.execute(
            """
            INSERT INTO workout_sessions (
                user_id, session_date, split_type,
                duration_minutes, notes, legacy_workout_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                workout["user_id"],
                workout["workout_date"],
                "Legacy workout",
                workout["duration_minutes"],
                workout["notes"],
                workout["id"],
                workout["created_at"],
            ),
        )
        db.execute(
            """
            INSERT INTO workout_exercises (
                session_id, exercise_name, sets_count, reps_count,
                weight_kg, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cursor.lastrowid,
                workout["exercise_name"],
                workout["sets_count"],
                workout["reps_count"],
                workout["weight_kg"],
                workout["notes"],
                workout["created_at"],
            ),
        )

    if legacy_workouts:
        db.commit()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def profile_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))

        user = get_current_user()
        profile = get_profile(session["user_id"])
        if not user or not has_completed_profile(user, profile):
            return redirect(url_for("onboarding"))

        return view(**kwargs)

    return wrapped_view


def get_profile(user_id):
    return get_db().execute(
        "SELECT * FROM profiles WHERE user_id = ?",
        (user_id,),
    ).fetchone()


def has_minimum_profile(profile):
    if not profile:
        return False

    full_name = str(profile["full_name"] or "").strip()
    try:
        age = int(profile["age"])
    except (TypeError, ValueError):
        return False

    return bool(full_name) and age > 0


def has_completed_profile(user, profile=None):
    if user:
        name = str(user["name"] or "").strip() if "name" in user.keys() else ""
        try:
            age = int(user["age"]) if "age" in user.keys() else 0
        except (TypeError, ValueError):
            age = 0
        if name and age > 0:
            return True

    return has_minimum_profile(profile)


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None

    return get_db().execute(
        """
        SELECT id, name, age, email, profile_completed, onboarding_completed,
               profile_image_path, created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()


def is_profile_incomplete(profile, user=None):
    return not has_completed_profile(user, profile)


def get_local_today():
    return datetime.now(LOCAL_TIMEZONE).date()


def parse_iso_date(value):
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def get_latest_workout_date(db, user_id):
    row = db.execute(
        """
        SELECT MAX(session_date) AS latest_date
        FROM workout_sessions
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()
    return parse_iso_date(row["latest_date"] if row else None)


def get_current_streak_days(db, user_id):
    today = get_local_today()
    latest_date = get_latest_workout_date(db, user_id)
    if latest_date is None or latest_date < today - timedelta(days=1):
        db.execute(
            """
            UPDATE profiles
            SET workout_streak_days = 0, updated_at = ?
            WHERE user_id = ? AND workout_streak_days != 0
            """,
            (datetime.utcnow().isoformat(), user_id),
        )
        db.commit()
        return 0

    profile = db.execute(
        "SELECT workout_streak_days FROM profiles WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return profile["workout_streak_days"] if profile else 0


def sync_workout_streak_from_sessions(db, user_id):
    today = get_local_today()
    workout_days = db.execute(
        """
        SELECT DISTINCT session_date AS activity_date
        FROM workout_sessions
        WHERE user_id = ?
        ORDER BY session_date DESC
        """,
        (user_id,),
    ).fetchall()
    streak_days = compute_streak([row["activity_date"] for row in workout_days], today)
    db.execute(
        """
        UPDATE profiles
        SET workout_streak_days = ?, updated_at = ?
        WHERE user_id = ?
        """,
        (streak_days, datetime.utcnow().isoformat(), user_id),
    )
    return streak_days


def user_has_workout_on_date(db, user_id, activity_date):
    row = db.execute(
        """
        SELECT 1
        FROM workout_sessions
        WHERE user_id = ? AND session_date = ?
        LIMIT 1
        """,
        (user_id, activity_date.isoformat()),
    ).fetchone()
    return row is not None


def update_workout_streak_after_session_save(db, user_id, saved_session_date, had_workout_today):
    today = get_local_today()
    saved_date = parse_iso_date(saved_session_date)
    if saved_date != today or had_workout_today:
        return get_current_streak_days(db, user_id)

    yesterday = today - timedelta(days=1)
    prior_row = db.execute(
        """
        SELECT MAX(session_date) AS prior_date
        FROM workout_sessions
        WHERE user_id = ? AND session_date < ?
        """,
        (user_id, today.isoformat()),
    ).fetchone()
    prior_date = parse_iso_date(prior_row["prior_date"] if prior_row else None)

    if prior_date is None:
        next_streak = 1
    elif prior_date == yesterday:
        current_streak = get_current_streak_days(db, user_id)
        next_streak = current_streak + 1
    else:
        next_streak = 1

    db.execute(
        """
        UPDATE profiles
        SET workout_streak_days = ?, updated_at = ?
        WHERE user_id = ?
        """,
        (next_streak, datetime.utcnow().isoformat(), user_id),
    )
    return next_streak


@app.context_processor
def inject_user():
    user = get_current_user()
    profile = get_profile(user["id"]) if user else None
    return {
        "current_user": user,
        "current_profile": profile,
        "current_profile_incomplete": is_profile_incomplete(profile, user),
    }


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = get_current_user()
    profile = get_profile(session["user_id"])
    if not user or not has_completed_profile(user, profile):
        return redirect(url_for("onboarding"))

    return redirect(url_for("home"))


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
        else:
            db = get_db()
            existing_user = db.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,),
            ).fetchone()
            if existing_user:
                flash("An account with that email already exists.", "error")
            else:
                db.execute(
                    """
                    INSERT INTO users (email, password_hash, onboarding_completed, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (email, generate_password_hash(password), 0, datetime.utcnow().isoformat()),
                )
                db.commit()
                flash("Account created. Please log in.", "success")
                return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            flash("Welcome back.", "success")
            profile = get_profile(user["id"])
            next_endpoint = "home" if has_completed_profile(user, profile) else "onboarding"
            return redirect(url_for(next_endpoint))

    return render_template("login.html")


@app.route("/logout", methods=("POST",))
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/onboarding", methods=("GET", "POST"))
@login_required
def onboarding():
    user = get_current_user()
    profile = get_profile(session["user_id"])
    if request.method == "GET" and has_completed_profile(user, profile):
        return redirect(url_for("home"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        age = request.form.get("age", "").strip()
        gender = profile["gender"] if profile else ""
        nationality = profile["nationality"] if profile else ""
        goal = profile["goal"] if profile else ""
        preferred_split = profile["preferred_split"] if profile else DEFAULT_PREFERRED_SPLIT
        height_value = float(profile["height_cm"]) if profile else 0
        start_weight_value = float(profile["start_weight_kg"]) if profile else 0
        goal_weight_value = float(profile["goal_weight_kg"]) if profile else 0
        accepted_terms = 1

        if preferred_split not in PREFERRED_SPLIT_OPTIONS:
            preferred_split = DEFAULT_PREFERRED_SPLIT

        if not all([full_name, age]):
            flash("Please enter your name and age.", "error")
        else:
            try:
                age_value = int(age)
            except ValueError:
                flash("Age must be a valid number.", "error")
            else:
                db = get_db()
                timestamp = datetime.utcnow().isoformat()
                values = (
                    session["user_id"],
                    full_name,
                    gender,
                    age_value,
                    nationality,
                    goal,
                    preferred_split,
                    height_value,
                    start_weight_value,
                    goal_weight_value,
                    accepted_terms,
                    timestamp,
                    timestamp,
                )

                if profile:
                    db.execute(
                        """
                        UPDATE profiles
                        SET full_name = ?, gender = ?, age = ?, nationality = ?, goal = ?, preferred_split = ?,
                            height_cm = ?, start_weight_kg = ?, goal_weight_kg = ?,
                            accepted_terms = ?, accepted_terms_at = ?, updated_at = ?
                        WHERE user_id = ?
                        """,
                        (
                            full_name,
                            gender,
                            age_value,
                            nationality,
                            goal,
                            preferred_split,
                            height_value,
                            start_weight_value,
                            goal_weight_value,
                            accepted_terms,
                            timestamp,
                            timestamp,
                            session["user_id"],
                        ),
                    )
                else:
                    db.execute(
                        """
                        INSERT INTO profiles (
                            user_id, full_name, gender, age, nationality, goal,
                            preferred_split, height_cm, start_weight_kg, goal_weight_kg,
                            accepted_terms, accepted_terms_at, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        values,
                    )

                db.execute(
                    """
                    UPDATE users
                    SET name = ?, age = ?, profile_completed = 1, onboarding_completed = 1
                    WHERE id = ?
                    """,
                    (full_name, age_value, session["user_id"]),
                )
                db.commit()
                flash("Profile saved. Your tracker is ready.", "success")
                return redirect(url_for("home"))

    return render_template("onboarding.html", profile=profile, preferred_split_options=PREFERRED_SPLIT_OPTIONS)


@app.route("/home", methods=("GET", "POST"))
@profile_required
def home():
    profile = get_profile(session["user_id"])
    return render_template(
        "home.html",
        profile=profile,
        selected_split=get_selected_split(profile, session["user_id"]),
        today_workout=get_today_workout(profile, session["user_id"]),
        split_cards=get_available_split_cards(session["user_id"]),
    )


@app.route("/categories/<slug>")
@profile_required
def category_page(slug):
    category = CATEGORY_PAGES.get(slug)
    if not category:
        flash("That workout plan does not exist yet.", "error")
        return redirect(url_for("home"))

    return render_template("category.html", category=category, slug=slug)


@app.route("/planner/<slug>", methods=("GET",))
@profile_required
def split_planner(slug):
    split_definition = get_split_definition(session["user_id"], slug)
    if not split_definition:
        flash("Choose a valid workout split.", "error")
        return redirect(url_for("home"))
    split_name = split_definition["name"]

    db = get_db()
    db.execute(
        "UPDATE profiles SET preferred_split = ?, updated_at = ? WHERE user_id = ?",
        (split_name, datetime.utcnow().isoformat(), session["user_id"]),
    )
    db.commit()

    return render_template(
        "planner.html",
        split_name=split_name,
        split_slug=slug,
        plan=rotate_program_to_adaptive_split_day(session["user_id"], split_name, split_definition["program"]),
    )


@app.route("/planner/<slug>/save", methods=("POST",))
@profile_required
def save_planner_log(slug):
    split_definition = get_split_definition(session["user_id"], slug)
    if not split_definition:
        flash("Choose a valid workout split.", "error")
        return redirect(url_for("home"))
    split_name = split_definition["name"]

    rows = []
    for index, exercise_name in enumerate(request.form.getlist("exercise_name[]")):
        day_name = request.form.getlist("day_name[]")[index].strip()
        prescribed_sets = request.form.getlist("prescribed_sets[]")[index].strip()
        prescribed_reps = request.form.getlist("prescribed_reps[]")[index].strip()
        weight_raw = request.form.getlist("weight_used[]")[index].strip()
        reps_raw = request.form.getlist("reps_completed[]")[index].strip()
        notes = request.form.getlist("notes[]")[index].strip()

        if not any([weight_raw, reps_raw, notes]):
            continue

        if not all([weight_raw, reps_raw]):
            flash("Weight used and reps completed are required for every logged exercise.", "error")
            return redirect(url_for("split_planner", slug=slug))

        try:
            rows.append(
                {
                    "split_name": split_name,
                    "day_name": day_name,
                    "exercise_name": exercise_name.strip(),
                    "prescribed_sets": prescribed_sets,
                    "prescribed_reps": prescribed_reps,
                    "weight_used": float(weight_raw),
                    "reps_completed": int(reps_raw),
                    "notes": notes,
                }
            )
        except ValueError:
            flash("Weight and reps must be valid numbers.", "error")
            return redirect(url_for("split_planner", slug=slug))

    if not rows:
        flash("Enter at least one exercise log before saving.", "warning")
        return redirect(url_for("split_planner", slug=slug))

    db = get_db()
    timestamp = datetime.utcnow().isoformat()
    today = get_local_today()
    had_workout_today = user_has_workout_on_date(db, session["user_id"], today)
    session_ids_by_day = {}
    db.execute(
        "UPDATE profiles SET preferred_split = ?, updated_at = ? WHERE user_id = ?",
        (split_name, timestamp, session["user_id"]),
    )
    for row in rows:
        db.execute(
            """
            INSERT INTO workout_logs (
                user_id, split_name, day_name, exercise_name, prescribed_sets,
                prescribed_reps, weight_used, reps_completed, notes, logged_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                row["split_name"],
                row["day_name"],
                row["exercise_name"],
                row["prescribed_sets"],
                row["prescribed_reps"],
                row["weight_used"],
                row["reps_completed"],
                row["notes"],
                timestamp,
            ),
        )

        if row["day_name"] not in session_ids_by_day:
            cursor = db.execute(
                """
                INSERT INTO workout_sessions (
                    user_id, session_date, split_type, split_day,
                    duration_minutes, notes, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    today.isoformat(),
                    split_name,
                    row["day_name"],
                    0,
                    None,
                    timestamp,
                ),
            )
            session_ids_by_day[row["day_name"]] = cursor.lastrowid

        db.execute(
            """
            INSERT INTO workout_exercises (
                session_id, exercise_name, sets_count, reps_count,
                weight_kg, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_ids_by_day[row["day_name"]],
                row["exercise_name"],
                int(row["prescribed_sets"]) if str(row["prescribed_sets"]).isdigit() else 1,
                row["reps_completed"],
                row["weight_used"],
                row["notes"],
                timestamp,
            ),
        )
    if session_ids_by_day:
        update_workout_streak_after_session_save(
            db,
            session["user_id"],
            today.isoformat(),
            had_workout_today,
        )
    db.commit()
    flash("Workout log saved.", "success")
    return redirect(url_for("split_planner", slug=slug))


@app.route("/profile")
@profile_required
def profile():
    user_id = session["user_id"]
    profile = get_profile(user_id)
    metrics = build_dashboard_metrics(user_id, profile)
    recent_sessions = get_recent_workout_sessions(user_id, limit=5)
    selected_split, selected_program = get_selected_program(user_id, profile)
    today_workout_index = get_calendar_workout_index(selected_program)
    today_workout = selected_program[today_workout_index]
    next_workout = selected_program[(today_workout_index + 1) % len(selected_program)]
    goal_progress = min(100, round((metrics["weekly_workouts"] / 4) * 100)) if metrics["weekly_workouts"] else 0

    return render_template(
        "profile.html",
        profile=profile,
        selected_split=selected_split,
        today_workout=today_workout,
        next_workout=next_workout,
        metrics=metrics,
        recent_sessions=recent_sessions,
        goal_progress=goal_progress,
    )


@app.route("/edit-profile", methods=("GET", "POST"))
@profile_required
def edit_profile():
    user_id = session["user_id"]
    user = get_current_user()
    profile = get_profile(user_id)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        bio = request.form.get("bio", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        nationality = request.form.get("nationality", "").strip()
        goal = request.form.get("goal", "").strip()
        height_cm = request.form.get("height_cm", "").strip()
        start_weight_kg = request.form.get("start_weight_kg", "").strip()
        goal_weight_kg = request.form.get("goal_weight_kg", "").strip()

        if not full_name or not email or not age:
            flash("Username, email, and age are required.", "error")
            return redirect(url_for("edit_profile"))

        try:
            age_value = int(age)
            height_value = float(height_cm) if height_cm else 0
            start_weight_value = float(start_weight_kg) if start_weight_kg else 0
            goal_weight_value = float(goal_weight_kg) if goal_weight_kg else 0
        except ValueError:
            flash("Age, height, and weight fields must be valid numbers.", "error")
            return redirect(url_for("edit_profile"))

        db = get_db()
        existing_email = db.execute(
            "SELECT id FROM users WHERE email = ? AND id != ?",
            (email, user_id),
        ).fetchone()
        if existing_email:
            flash("That email is already in use.", "error")
            return redirect(url_for("edit_profile"))

        try:
            image_path = save_profile_image_upload(request.files.get("profile_image"), user_id)
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("edit_profile"))

        timestamp = datetime.utcnow().isoformat()
        db.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
        if image_path:
            db.execute("UPDATE users SET profile_image_path = ? WHERE id = ?", (image_path, user_id))
        db.execute(
            """
            UPDATE profiles
            SET full_name = ?, age = ?, gender = ?, nationality = ?, goal = ?,
                height_cm = ?, start_weight_kg = ?, goal_weight_kg = ?,
                bio = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (
                full_name,
                age_value,
                gender,
                nationality,
                goal,
                height_value,
                start_weight_value,
                goal_weight_value,
                bio,
                timestamp,
                user_id,
            ),
        )
        db.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("profile"))

    return render_template("edit_profile.html", user=user, profile=profile)


@app.route("/customize-splits", methods=("GET", "POST"))
@profile_required
def customize_splits():
    user_id = session["user_id"]

    if request.method == "POST":
        action = request.form.get("action", "")
        try:
            days = parse_split_form(request.form)
            if action == "create_split":
                created_split = upsert_custom_split(
                    user_id=user_id,
                    name=request.form.get("split_name", ""),
                    days=days,
                )
                flash("Custom split created.", "success")
                return redirect(url_for("customize_splits", split=created_split["slug"]))

            if action == "save_existing":
                selected_slug = request.form.get("selected_slug", "").strip()
                split_definition = get_split_definition(user_id, selected_slug)
                if not split_definition:
                    flash("Choose a valid split to customize.", "error")
                    return redirect(url_for("customize_splits"))

                existing_custom = get_custom_split_by_slug(user_id, selected_slug)
                saved_split = upsert_custom_split(
                    user_id=user_id,
                    name=request.form.get("split_name", split_definition["name"]),
                    days=days,
                    slug=selected_slug,
                    base_slug=selected_slug if not existing_custom else existing_custom["base_slug"],
                    split_id=existing_custom["id"] if existing_custom else None,
                )
                flash("Split customization saved.", "success")
                return redirect(url_for("customize_splits", split=saved_split["slug"]))
        except ValueError as error:
            flash(str(error), "error")

    split_cards = get_available_split_cards(user_id)
    selected_slug = request.args.get("split") or (split_cards[0]["slug"] if split_cards else "")
    selected_definition = get_split_definition(user_id, selected_slug) if selected_slug else None

    return render_template(
        "customize_splits.html",
        split_cards=split_cards,
        selected_slug=selected_slug,
        selected_split=selected_definition,
    )


@app.route("/workout-history")
@profile_required
def workout_history():
    return render_template(
        "workout_history.html",
        workout_sessions=get_recent_workout_sessions(session["user_id"]),
    )


@app.route("/dashboard")
@profile_required
def dashboard():
    return redirect(url_for("profile"))


@app.route("/api/selected-split", methods=("POST",))
@profile_required
def selected_split_api():
    payload = request.get_json(silent=True) or {}
    selected_split = payload.get("split", DEFAULT_PREFERRED_SPLIT)
    custom_split = get_custom_split_by_name(session["user_id"], selected_split)
    if selected_split not in WORKOUT_SPLIT_PROGRAMS and not custom_split:
        return jsonify({"ok": False, "message": "Choose a valid workout split."}), 400

    db = get_db()
    db.execute(
        "UPDATE profiles SET preferred_split = ?, updated_at = ? WHERE user_id = ?",
        (selected_split, datetime.utcnow().isoformat(), session["user_id"]),
    )
    db.commit()

    program = load_custom_split_program(custom_split["id"]) if custom_split else WORKOUT_SPLIT_PROGRAMS[selected_split]
    return jsonify({"ok": True, "split": selected_split, "program": program})


@app.route("/api/log-split-session", methods=("POST",))
@profile_required
def log_split_session_api():
    payload = request.get_json(silent=True) or {}
    selected_split = payload.get("split", DEFAULT_PREFERRED_SPLIT)
    split_day = payload.get("day", "").strip()
    exercises = payload.get("exercises", [])

    custom_split = get_custom_split_by_name(session["user_id"], selected_split)
    if selected_split not in WORKOUT_SPLIT_PROGRAMS and not custom_split:
        return jsonify({"ok": False, "message": "Choose a valid workout split."}), 400
    if not split_day:
        return jsonify({"ok": False, "message": "Choose a workout day."}), 400
    if not isinstance(exercises, list) or not exercises:
        return jsonify({"ok": False, "message": "Log at least one exercise."}), 400

    logged_exercises = []
    for exercise in exercises:
        if not isinstance(exercise, dict):
            continue

        name = str(exercise.get("name", "")).strip()
        sets = str(exercise.get("sets", "")).strip()
        reps = str(exercise.get("reps", "")).strip()
        weight = str(exercise.get("weight", "")).strip()
        notes = str(exercise.get("notes", "")).strip()

        if not any([sets, reps, weight, notes]):
            continue
        if not all([name, sets, reps, weight]):
            return jsonify({"ok": False, "message": "Each logged exercise needs sets, reps, and weight."}), 400

        try:
            logged_exercises.append(
                {
                    "name": name,
                    "sets": int(sets),
                    "reps": int(reps),
                    "weight": float(weight),
                    "notes": notes,
                }
            )
        except ValueError:
            return jsonify({"ok": False, "message": "Sets, reps, and weight must be valid numbers."}), 400

    if not logged_exercises:
        return jsonify({"ok": False, "message": "Log at least one exercise before saving."}), 400

    db = get_db()
    timestamp = datetime.utcnow().isoformat()
    today = get_local_today()
    had_workout_today = user_has_workout_on_date(db, session["user_id"], today)
    cursor = db.execute(
        """
        INSERT INTO workout_sessions (
            user_id, session_date, split_type, split_day,
            duration_minutes, notes, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            today.isoformat(),
            selected_split,
            split_day,
            0,
            None,
            timestamp,
        ),
    )
    session_id = cursor.lastrowid

    for exercise in logged_exercises:
        db.execute(
            """
            INSERT INTO workout_exercises (
                session_id, exercise_name, sets_count, reps_count,
                weight_kg, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                exercise["name"],
                exercise["sets"],
                exercise["reps"],
                exercise["weight"],
                exercise["notes"],
                timestamp,
            ),
        )

    db.execute(
        "UPDATE profiles SET preferred_split = ?, updated_at = ? WHERE user_id = ?",
        (selected_split, timestamp, session["user_id"]),
    )
    update_workout_streak_after_session_save(
        db,
        session["user_id"],
        today.isoformat(),
        had_workout_today,
    )
    db.commit()

    return jsonify(
        {
            "ok": True,
            "message": f"{split_day} saved.",
            "sessions": serialize_workout_sessions(get_recent_workout_sessions(session["user_id"], limit=20)),
        }
    )


@app.route("/workouts", methods=("POST",))
@profile_required
def add_workout():
    user_id = session["user_id"]
    wants_json = request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.accept_mimetypes.best == "application/json"

    def workout_error(message):
        if wants_json:
            return jsonify({"ok": False, "message": message}), 400
        flash(message, "error")
        return redirect(url_for("profile"))

    session_date = request.form.get("session_date", request.form.get("workout_date", "")).strip()
    profile = get_profile(user_id)
    preferred_split = profile["preferred_split"] if profile and "preferred_split" in profile.keys() else DEFAULT_PREFERRED_SPLIT
    split_type = request.form.get("split_type", "").strip()
    split_day = request.form.get("split_day", "").strip() or None
    session_notes = request.form.get("session_notes", request.form.get("notes", "")).strip()

    if not split_type:
        split_type = preferred_split

    exercise_names = request.form.getlist("exercise_name[]") or request.form.getlist("exercise_name")
    sets_counts = request.form.getlist("sets_count[]") or request.form.getlist("sets_count")
    reps_counts = request.form.getlist("reps_count[]") or request.form.getlist("reps_count")
    weights = request.form.getlist("weight_kg[]") or request.form.getlist("weight_kg")
    exercise_notes = request.form.getlist("exercise_notes[]") or request.form.getlist("exercise_notes")

    exercise_rows = []
    row_count = max(len(exercise_names), len(sets_counts), len(reps_counts), len(weights))

    if not all([session_date, split_type]):
        return workout_error("Please complete the workout session details.")

    for index in range(row_count):
        exercise_name = exercise_names[index].strip() if index < len(exercise_names) else ""
        sets_count = sets_counts[index].strip() if index < len(sets_counts) else ""
        reps_count = reps_counts[index].strip() if index < len(reps_counts) else ""
        weight_kg = weights[index].strip() if index < len(weights) else ""
        note = exercise_notes[index].strip() if index < len(exercise_notes) else ""

        if not any([exercise_name, sets_count, reps_count, weight_kg, note]):
            continue

        if not all([exercise_name, sets_count, reps_count, weight_kg]):
            return workout_error("Each exercise needs a name, sets, reps, and weight.")

        try:
            exercise_rows.append(
                {
                    "exercise_name": exercise_name,
                    "sets_count": int(sets_count),
                    "reps_count": int(reps_count),
                    "weight_kg": float(weight_kg),
                    "notes": note,
                }
            )
        except ValueError:
            return workout_error("Exercise sets, reps, and weight must be valid numbers.")

    if not exercise_rows:
        return workout_error("Add at least one exercise to save the workout session.")

    db = get_db()
    timestamp = datetime.utcnow().isoformat()
    today = get_local_today()
    had_workout_today = user_has_workout_on_date(db, user_id, today)
    workout_session_columns = {
        row[1] for row in db.execute("PRAGMA table_info(workout_sessions)").fetchall()
    }
    has_split_day = "split_day" in workout_session_columns
    if has_split_day:
        cursor = db.execute(
            """
            INSERT INTO workout_sessions (
                user_id, session_date, split_type, split_day,
                duration_minutes, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                session_date,
                split_type,
                split_day,
                0,
                session_notes,
                timestamp,
            ),
        )
    else:
        cursor = db.execute(
            """
            INSERT INTO workout_sessions (
                user_id, session_date, split_type,
                duration_minutes, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                session_date,
                split_type,
                0,
                session_notes,
                timestamp,
            ),
        )
    session_id = cursor.lastrowid

    for exercise in exercise_rows:
        db.execute(
            """
            INSERT INTO workout_exercises (
                session_id, exercise_name, sets_count, reps_count,
                weight_kg, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                exercise["exercise_name"],
                exercise["sets_count"],
                exercise["reps_count"],
                exercise["weight_kg"],
                exercise["notes"],
                timestamp,
            ),
        )

    update_workout_streak_after_session_save(
        db,
        user_id,
        session_date,
        had_workout_today,
    )
    db.commit()

    if wants_json:
        return jsonify(
            {
                "ok": True,
                "message": "Workout session logged successfully.",
                "sessions": serialize_workout_sessions(get_recent_workout_sessions(user_id, limit=20)),
            }
        )

    flash("Workout session logged successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/api/workout-sessions")
@profile_required
def workout_sessions_api():
    return jsonify({"sessions": serialize_workout_sessions(get_recent_workout_sessions(session["user_id"], limit=20))})


@app.route("/api/latest-sessions")
@profile_required
def latest_sessions_api():
    return jsonify({"sessions": serialize_workout_sessions(get_recent_workout_sessions(session["user_id"], limit=20))})


def get_recent_workout_sessions(user_id, limit=None):
    db = get_db()
    limit_clause = "LIMIT ?" if limit else ""
    params = [user_id]
    if limit:
        params.append(limit)
    sessions = db.execute(
        f"""
        SELECT
            s.*,
            COUNT(e.id) AS exercise_count
        FROM workout_sessions s
        LEFT JOIN workout_exercises e ON e.session_id = s.id
        WHERE s.user_id = ?
        GROUP BY s.id
        ORDER BY s.session_date DESC, s.id DESC
        {limit_clause}
        """,
        params,
    ).fetchall()

    session_items = []
    for session_row in sessions:
        exercises = db.execute(
            """
            SELECT *
            FROM workout_exercises
            WHERE session_id = ?
            ORDER BY id
            """,
            (session_row["id"],),
        ).fetchall()
        session_items.append({"session": session_row, "exercises": exercises})

    return session_items


def serialize_workout_sessions(session_items):
    return [
        {
            "id": item["session"]["id"],
            "session_id": item["session"]["id"],
            "date": item["session"]["session_date"],
            "split": item["session"]["split_type"],
            "split_name": item["session"]["split_type"],
            "split_type": item["session"]["split_type"],
            "split_day": item["session"]["split_day"] if "split_day" in item["session"].keys() else None,
            "notes": item["session"]["notes"],
            "exercise_count": item["session"]["exercise_count"],
            "exercises": [
                {
                    "id": exercise["id"],
                    "exercise_name": exercise["exercise_name"],
                    "sets": exercise["sets_count"],
                    "reps": exercise["reps_count"],
                    "weight": exercise["weight_kg"],
                    "notes": exercise["notes"],
                }
                for exercise in item["exercises"]
            ],
        }
        for item in session_items
    ]


def get_workout_logs(user_id, split_name=None, limit=20):
    db = get_db()
    params = [user_id]
    where_clause = "WHERE user_id = ?"
    if split_name:
        where_clause += " AND split_name = ?"
        params.append(split_name)
    params.append(limit)

    return db.execute(
        f"""
        SELECT *
        FROM workout_logs
        {where_clause}
        ORDER BY logged_at DESC, id DESC
        LIMIT ?
        """,
        params,
    ).fetchall()


def build_dashboard_metrics(user_id, profile):
    db = get_db()
    today = get_local_today()
    start_of_week = today - timedelta(days=6)

    workouts_week = db.execute(
        """
        SELECT COUNT(*) AS count
        FROM workout_sessions
        WHERE user_id = ? AND session_date >= ?
        """,
        (user_id, start_of_week.isoformat()),
    ).fetchone()

    exercises_week = db.execute(
        """
        SELECT COUNT(e.id) AS count
        FROM workout_sessions s
        LEFT JOIN workout_exercises e ON e.session_id = s.id
        WHERE s.user_id = ? AND s.session_date >= ?
        """,
        (user_id, start_of_week.isoformat()),
    ).fetchone()

    streak_days = get_current_streak_days(db, user_id)

    return {
        "weekly_workouts": workouts_week["count"],
        "weekly_exercises": exercises_week["count"],
        "streak_days": streak_days,
    }


def compute_streak(activity_dates, today):
    unique_dates = set()
    for value in activity_dates:
        try:
            unique_dates.add(datetime.strptime(value, "%Y-%m-%d").date())
        except (TypeError, ValueError):
            continue
    streak = 0
    cursor = today if today in unique_dates else today - timedelta(days=1)

    while cursor in unique_dates:
        streak += 1
        cursor -= timedelta(days=1)

    return streak


with app.app_context():
    init_db()
    db.create_all()


if __name__ == "__main__":
    app.run()
