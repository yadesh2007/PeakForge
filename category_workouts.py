def _exercise(name, sets, reps):
    return {"name": name, "sets": sets, "reps": reps}


def _plan(day_name, muscles, exercises, rest, notes):
    return {
        "day_name": day_name,
        "muscles": muscles,
        "exercises": exercises,
        "rest": rest,
        "notes": notes,
    }


WORKOUT_PLANS = {
    "bulking": {
        "Upper": _plan(
            "Upper",
            "Chest, back, shoulders, biceps, triceps",
            [
                _exercise("Bench Press", "4", "6-8"),
                _exercise("Bent-Over Row", "4", "6-8"),
                _exercise("Overhead Press", "3", "8-10"),
                _exercise("Pull-Ups or Lat Pulldown", "3", "8-12"),
                _exercise("Dumbbell Curl", "3", "10-12"),
                _exercise("Triceps Pushdown", "3", "10-12"),
            ],
            ["Compound lifts: 2-3 minutes", "Isolation exercises: 60-90 seconds"],
            "Add reps first, then load when every set lands cleanly.",
        ),
        "Lower": _plan(
            "Lower",
            "Quads, hamstrings, glutes, calves, core",
            [
                _exercise("Back Squat", "4", "6-8"),
                _exercise("Romanian Deadlift", "4", "8-10"),
                _exercise("Leg Press", "3", "10-12"),
                _exercise("Walking Lunge", "3", "10-12/leg"),
                _exercise("Seated Calf Raise", "4", "12-15"),
                _exercise("Cable Crunch", "3", "12-15"),
            ],
            ["Squat and hinge patterns: 2-3 minutes", "Accessories: 60-90 seconds"],
            "Keep one hard quad and one hard hinge pattern each lower day.",
        ),
        "Push": _plan("Push", "Chest, shoulders, triceps", [_exercise("Incline Bench Press", "4", "6-10"), _exercise("Seated Dumbbell Press", "3", "8-10"), _exercise("Machine Chest Press", "3", "8-12"), _exercise("Cable Fly", "3", "12-15"), _exercise("Lateral Raise", "4", "12-15"), _exercise("Overhead Triceps Extension", "3", "10-12")], ["Presses: 2-3 minutes", "Raises/extensions: 60-90 seconds"], "Progress one main press and one accessory each week."),
        "Pull": _plan("Pull", "Back, rear delts, biceps", [_exercise("Weighted Pull-Up or Lat Pulldown", "4", "6-10"), _exercise("Barbell Row", "4", "6-10"), _exercise("Chest-Supported Row", "3", "8-12"), _exercise("Face Pull", "3", "12-15"), _exercise("Incline Dumbbell Curl", "3", "10-12"), _exercise("Hammer Curl", "3", "10-12")], ["Rows and pulldowns: 2 minutes", "Curls/rear delts: 60-90 seconds"], "Use straps if grip limits back volume before the target muscles fatigue."),
        "Legs": _plan("Legs", "Quads, hamstrings, glutes, calves", [_exercise("Front Squat", "4", "6-8"), _exercise("Hip Thrust", "4", "8-10"), _exercise("Leg Curl", "3", "10-15"), _exercise("Bulgarian Split Squat", "3", "8-12/leg"), _exercise("Standing Calf Raise", "4", "12-15")], ["Squats/deadlifts: 2-3 minutes", "Accessories: 60-90 seconds"], "Keep reps controlled and chase tension, not just load."),
    },
    "cutting": {
        "Upper": _plan("Upper", "Chest, back, shoulders, arms", [_exercise("Bench Press", "3", "6-8"), _exercise("One-Arm Dumbbell Row", "3", "8-10"), _exercise("Overhead Press", "3", "6-10"), _exercise("Lat Pulldown", "3", "10-12"), _exercise("Cable Curl", "3", "10-15"), _exercise("Rope Triceps Pushdown", "3", "10-15")], ["Compounds: 2-3 minutes", "Accessories: 60-90 seconds"], "Keep loads heavy enough to preserve strength while volume stays recoverable."),
        "Lower": _plan("Lower", "Quads, hamstrings, glutes, calves", [_exercise("Back Squat", "3", "6-8"), _exercise("Romanian Deadlift", "3", "8-10"), _exercise("Leg Press", "3", "10-12"), _exercise("Leg Curl", "3", "10-15"), _exercise("Calf Raise", "3", "12-15")], ["Main lifts: 2-3 minutes", "Accessories: 60-90 seconds"], "Optional cardio: 15-25 minutes low-intensity work after lifting."),
        "Push": _plan("Push", "Chest, shoulders, triceps", [_exercise("Incline Dumbbell Press", "3", "6-10"), _exercise("Machine Shoulder Press", "3", "8-10"), _exercise("Push-Up", "3", "AMRAP leaving 1-2 reps"), _exercise("Cable Lateral Raise", "3", "12-15"), _exercise("Triceps Pressdown", "3", "10-15")], ["Presses: 2 minutes", "Accessories: 60-90 seconds"], "Keep one heavy press in the plan even as calories drop."),
        "Pull": _plan("Pull", "Back, rear delts, biceps", [_exercise("Pull-Up or Lat Pulldown", "3", "6-10"), _exercise("Seated Cable Row", "3", "8-12"), _exercise("Dumbbell Row", "3", "8-10/side"), _exercise("Rear-Delt Fly", "3", "12-15"), _exercise("EZ-Bar Curl", "3", "10-12")], ["Rows/pulls: 2 minutes", "Accessories: 60-90 seconds"], "Use clean reps and avoid turning every set into a grinder."),
        "Legs": _plan("Legs", "Lower body and core", [_exercise("Trap Bar Deadlift", "3", "5-8"), _exercise("Front Squat", "3", "6-10"), _exercise("Reverse Lunge", "3", "10/leg"), _exercise("Seated Leg Curl", "3", "10-15"), _exercise("Plank", "3", "45-60 sec")], ["Compounds: 2-3 minutes", "Accessories: 60-90 seconds"], "Optional finish: 10-15 minutes incline walking."),
    },
    "recomposition": {
        "Upper": _plan("Upper", "Chest, back, shoulders, arms", [_exercise("Incline Bench Press", "4", "8-10"), _exercise("Chest-Supported Row", "4", "8-10"), _exercise("Dumbbell Shoulder Press", "3", "8-12"), _exercise("Lat Pulldown", "3", "10-12"), _exercise("Cable Curl", "3", "10-12"), _exercise("Triceps Rope Extension", "3", "10-12")], ["Compounds: 2 minutes", "Accessories: 60-90 seconds"], "Push performance while keeping 1-2 reps in reserve."),
        "Lower": _plan("Lower", "Quads, hamstrings, glutes, core", [_exercise("Back Squat", "4", "8-10"), _exercise("Romanian Deadlift", "3", "8-12"), _exercise("Leg Press", "3", "10-12"), _exercise("Hip Thrust", "3", "10-12"), _exercise("Hanging Knee Raise", "3", "10-15")], ["Main lifts: 2 minutes", "Accessories: 60-90 seconds"], "Keep tempo controlled to build muscle without maximal loads."),
        "Push": _plan("Push", "Chest, shoulders, triceps", [_exercise("Dumbbell Bench Press", "3", "8-12"), _exercise("Arnold Press", "3", "8-12"), _exercise("Cable Fly", "3", "12-15"), _exercise("Lateral Raise", "3", "12-15"), _exercise("Dip or Assisted Dip", "3", "8-12")], ["Presses: 90-120 seconds", "Accessories: 60 seconds"], "Use low-intensity cardio on separate days or after shorter sessions."),
        "Pull": _plan("Pull", "Back, rear delts, biceps", [_exercise("Lat Pulldown", "4", "8-12"), _exercise("Seated Row", "3", "8-12"), _exercise("Single-Arm Cable Row", "3", "10-12/side"), _exercise("Face Pull", "3", "12-15"), _exercise("Hammer Curl", "3", "10-12")], ["Rows/pulls: 90-120 seconds", "Accessories: 60 seconds"], "Progress by adding clean reps before adding weight."),
        "Legs": _plan("Legs", "Lower body and core", [_exercise("Front Squat", "3", "8-10"), _exercise("Leg Curl", "3", "10-12"), _exercise("Bulgarian Split Squat", "3", "10/leg"), _exercise("Cable Pull-Through", "3", "12-15"), _exercise("Calf Raise", "3", "12-15")], ["Main lifts: 2 minutes", "Accessories: 60-90 seconds"], "Finish with an easy walk if fat-loss progress is slow."),
    },
}

WORKOUT_PLANS["strength"] = {
    "Upper": _plan("Upper", "Pressing and pulling strength", [_exercise("Bench Press", "5", "1-5"), _exercise("Weighted Pull-Up", "4", "3-6"), _exercise("Overhead Press", "4", "3-5"), _exercise("Barbell Row", "4", "5-8"), _exercise("Close-Grip Bench Press", "3", "5-8")], ["Main lifts: 3-5 minutes", "Accessories: 2 minutes"], "Stop heavy sets before technique breaks."),
    "Lower": _plan("Lower", "Squat, deadlift pattern, posterior chain", [_exercise("Back Squat", "5", "1-5"), _exercise("Deadlift", "4", "1-5"), _exercise("Pause Squat", "3", "3-5"), _exercise("Romanian Deadlift", "3", "5-8"), _exercise("Weighted Plank", "3", "30-45 sec")], ["Squat/deadlift: 3-5 minutes", "Accessories: 2 minutes"], "Track bar speed and fatigue across the session."),
    "Squat focus": _plan("Squat focus", "Squat strength, quads, trunk", [_exercise("Back Squat", "6", "1-5"), _exercise("Paused Squat", "3", "3-5"), _exercise("Leg Press", "3", "6-10"), _exercise("Back Extension", "3", "8-10"), _exercise("Ab Wheel", "3", "8-12")], ["Main lift: 3-5 minutes", "Accessories: 2 minutes"], "Keep every squat crisp and repeatable."),
    "Bench focus": _plan("Bench focus", "Bench strength, upper back, triceps", [_exercise("Bench Press", "6", "1-5"), _exercise("Paused Bench Press", "3", "3-5"), _exercise("Barbell Row", "4", "5-8"), _exercise("Overhead Press", "3", "5-8"), _exercise("Triceps Extension", "3", "8-10")], ["Main lift: 3-5 minutes", "Accessories: 90-120 seconds"], "Treat every bench rep like skill practice."),
    "Deadlift or press focus": _plan("Deadlift or press focus", "Deadlift or overhead press priority", [_exercise("Deadlift", "5", "1-5"), _exercise("Overhead Press", "4", "3-6"), _exercise("Pull-Up", "4", "5-8"), _exercise("Romanian Deadlift", "3", "5-8"), _exercise("Farmer Carry", "3", "30-45 sec")], ["Main lift: 3-5 minutes", "Accessories: 2 minutes"], "Alternate emphasis if fatigue builds quickly."),
    "Push": _plan("Push", "Pressing strength", [_exercise("Bench Press", "5", "1-5"), _exercise("Overhead Press", "4", "3-5"), _exercise("Close-Grip Bench", "3", "5-8"), _exercise("Dips", "3", "5-10")], ["Main press: 3-5 minutes", "Accessories: 2 minutes"], "Keep pressing volume heavy but controlled."),
    "Pull": _plan("Pull", "Pulling strength", [_exercise("Weighted Pull-Up", "5", "3-5"), _exercise("Barbell Row", "4", "5-8"), _exercise("Rack Pull", "3", "3-5"), _exercise("Face Pull", "3", "10-12"), _exercise("Hammer Curl", "3", "6-10")], ["Heavy pulls: 3 minutes", "Accessories: 90-120 seconds"], "Brace hard and avoid loose rowing reps."),
    "Legs": _plan("Legs", "Squat and hinge strength", [_exercise("Back Squat", "5", "1-5"), _exercise("Deadlift", "4", "1-5"), _exercise("Front Squat", "3", "3-6"), _exercise("Leg Curl", "3", "6-10"), _exercise("Calf Raise", "3", "8-12")], ["Main lifts: 3-5 minutes", "Accessories: 2 minutes"], "Use lower-body accessories to support main lifts."),
}

WORKOUT_PLANS["endurance"] = {
    "Upper": _plan("Upper", "Upper-body endurance", [_exercise("Incline Push-Up", "3", "15-25"), _exercise("Seated Row", "3", "15-20"), _exercise("Dumbbell Shoulder Press", "3", "15-20"), _exercise("Lat Pulldown", "3", "15-20"), _exercise("Band Curl + Pressdown", "2", "20 each")], ["Sets: 30-60 seconds"], "Superset pushes and pulls to build density."),
    "Lower": _plan("Lower", "Lower-body endurance", [_exercise("Leg Press", "3", "20-25"), _exercise("Romanian Deadlift", "3", "15-20"), _exercise("Step-Up", "3", "15/leg"), _exercise("Leg Curl", "3", "15-20"), _exercise("Calf Raise", "3", "20-25")], ["Sets: 30-60 seconds"], "Keep loads moderate and reps continuous."),
    "Push": _plan("Push", "Push endurance", [_exercise("Machine Chest Press", "3", "15-25"), _exercise("Dumbbell Shoulder Press", "3", "15-20"), _exercise("Cable Fly", "3", "15-20"), _exercise("Lateral Raise", "3", "20"), _exercise("Rope Pressdown", "3", "15-20")], ["Sets: 30-60 seconds"], "Use lighter loads and steady tempo."),
    "Pull": _plan("Pull", "Pull endurance", [_exercise("Lat Pulldown", "3", "15-20"), _exercise("Seated Row", "3", "15-20"), _exercise("Straight-Arm Pulldown", "3", "15-20"), _exercise("Rear-Delt Fly", "3", "20"), _exercise("Cable Curl", "3", "15-20")], ["Sets: 30-60 seconds"], "Keep shoulder blades moving well."),
    "Legs": _plan("Legs", "Leg endurance", [_exercise("Leg Press", "4", "20-25"), _exercise("Walking Lunge", "3", "20 steps"), _exercise("Leg Curl", "3", "15-20"), _exercise("Calf Raise", "3", "20-25"), _exercise("Bike Sprint", "5", "20 sec")], ["Sets: 30-60 seconds"], "Use circuits or supersets if time is limited."),
    "Lower + conditioning": _plan("Lower + conditioning", "Leg endurance and aerobic conditioning", [_exercise("Goblet Squat", "4", "20"), _exercise("Reverse Lunge", "3", "15/leg"), _exercise("Kettlebell Swing", "3", "20"), _exercise("Sled Push", "4", "30 sec"), _exercise("Incline Walk", "1", "20 min")], ["Lifts: 45-60 seconds", "Conditioning: easy pace"], "Do not turn conditioning into a max-effort test every week."),
}

WORKOUT_PLANS["stay-active"] = {
    "Strength": _plan("Strength", "General strength", [_exercise("Leg Press", "3", "10-12"), _exercise("Chest Press", "3", "10-12"), _exercise("Lat Pulldown", "3", "10-12"), _exercise("Dumbbell RDL", "3", "10-12"), _exercise("Side Plank", "2", "30 sec/side")], ["Sets: 60-90 seconds"], "Choose loads that feel controlled and repeatable."),
    "Cardio": _plan("Cardio", "Aerobic system", [_exercise("Brisk Walk or Bike", "1", "25-35 min"), _exercise("Step-Up", "2", "12/leg"), _exercise("Farmer Carry", "3", "30 sec"), _exercise("Mobility Flow", "1", "8-10 min")], ["As needed"], "Keep pace conversational for most of the session."),
    "Mobility + easy cardio": _plan("Mobility + easy cardio", "Mobility, hips, shoulders, easy aerobic work", [_exercise("Incline Walk", "1", "20-30 min"), _exercise("World's Greatest Stretch", "2", "5/side"), _exercise("Hip Balance Drill", "2", "6/side"), _exercise("Band Pull-Apart", "2", "15-20"), _exercise("Breathing Reset", "1", "3 min")], ["Move gently between drills"], "This day should restore energy, not drain it."),
    "Push": _plan("Push", "Chest, shoulders, triceps", [_exercise("Incline Push-Up", "3", "8-15"), _exercise("Dumbbell Shoulder Press", "3", "8-12"), _exercise("Cable Fly", "2", "12-15"), _exercise("Lateral Raise", "2", "12-15"), _exercise("Triceps Rope Pressdown", "2", "12-15")], ["Sets: 60-90 seconds"], "Keep pressing smooth and joint-friendly."),
    "Pull": _plan("Pull", "Back, rear delts, biceps", [_exercise("Lat Pulldown", "3", "8-12"), _exercise("Seated Row", "3", "10-12"), _exercise("Face Pull", "2", "12-15"), _exercise("Dumbbell Curl", "2", "10-15"), _exercise("Suitcase Carry", "2", "30 sec/side")], ["Sets: 60-90 seconds"], "Use controlled reps and avoid shrugging through pulls."),
    "Legs": _plan("Legs", "Lower body and balance", [_exercise("Goblet Squat", "3", "8-12"), _exercise("Step-Up", "3", "8-12/leg"), _exercise("Glute Bridge", "3", "10-15"), _exercise("Leg Curl", "2", "12-15"), _exercise("Calf Raise", "2", "12-15")], ["Sets: 60-90 seconds"], "Use pain-free range of motion and steady tempo."),
}

BRO_SPLIT_PLANS = {
    "Chest": _plan("Chest", "Chest, front delts, triceps", [_exercise("Incline Bench Press", "4", "6-10"), _exercise("Flat Dumbbell Press", "3", "8-12"), _exercise("Machine Chest Press", "3", "10-12"), _exercise("Cable Fly", "3", "12-15"), _exercise("Push-Up", "2", "AMRAP")], ["Presses: 2 minutes", "Flyes and finishers: 60-90 seconds"], "Keep pressing controlled and finish with a strong chest contraction."),
    "Back": _plan("Back", "Lats, mid-back, rear delts", [_exercise("Pull-Up or Lat Pulldown", "4", "6-10"), _exercise("Barbell Row", "4", "6-10"), _exercise("Chest-Supported Row", "3", "8-12"), _exercise("Straight-Arm Pulldown", "3", "12-15"), _exercise("Face Pull", "3", "12-15")], ["Rows and pulldowns: 2 minutes", "Rear-delt work: 60-90 seconds"], "Drive elbows with control instead of chasing momentum."),
    "Shoulders": _plan("Shoulders", "Side delts, rear delts, pressing strength", [_exercise("Seated Dumbbell Press", "4", "6-10"), _exercise("Cable Lateral Raise", "4", "12-15"), _exercise("Rear-Delt Fly", "3", "12-15"), _exercise("Machine Shoulder Press", "3", "8-12"), _exercise("Face Pull", "3", "12-15")], ["Presses: 2 minutes", "Raises: 60-90 seconds"], "Keep lateral raise reps smooth and strict."),
    "Arms": _plan("Arms", "Biceps, triceps, forearms", [_exercise("Close-Grip Bench Press", "3", "6-10"), _exercise("EZ-Bar Curl", "3", "8-12"), _exercise("Overhead Triceps Extension", "3", "10-12"), _exercise("Incline Dumbbell Curl", "3", "10-12"), _exercise("Rope Pressdown", "3", "12-15"), _exercise("Hammer Curl", "3", "10-12")], ["Heavy arm work: 90-120 seconds", "Pump work: 60 seconds"], "Use full range of motion and avoid swinging reps."),
}

for plans in WORKOUT_PLANS.values():
    plans.update(BRO_SPLIT_PLANS)


def _schedule_name(label):
    return label.split(":", 1)[1].strip() if ":" in label else label


def _find_plan(slug, day_name):
    plans = WORKOUT_PLANS[slug]
    for name in sorted(plans, key=len, reverse=True):
        if name.lower() in day_name.lower():
            return plans[name]
    return plans[next(iter(plans))]


def attach_workout_details(categories):
    for slug, category in categories.items():
        for split in category["splits"]:
            split["schedule_details"] = []
            for label in split["schedule"]:
                day_name = _schedule_name(label)
                plan = _find_plan(slug, day_name)
                split["schedule_details"].append({"label": label, **plan})
