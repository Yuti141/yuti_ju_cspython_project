# PRD v2 — Hard Requirements Guide
## Product Requirements Document (Version 2)

**This is not a suggestion. This is a specification.**

Your PRD v2 is the blueprint that you (and your AI coding assistant) will use to build your project. A weak PRD = a weak project. A strong PRD = a strong project. The difference between an A and a C is often the PRD.

---

## Part 1: Project Identity (1-2 paragraphs)

**Required:**
- [ ] Project name (your own, not just "Habit Tracker" — brand it)
- [ ] One-sentence pitch: "[Name] is a [type of app] that helps [user] to [solve what problem] by [how it works]."
- [ ] Target user: Who exactly will use this? Be specific (age, context, motivation)
- [ ] Why this project? Why did you pick it? What makes it yours?

**Example (GOOD):**
> **StreakKeeper** is a CLI habit tracker that helps busy high school students build consistent daily routines by tracking streaks across multiple habits, rewarding consistency with visual fire emojis, and storing everything locally in JSON. I picked this because I struggle with consistency myself and want a tool that works offline and feels motivating, not punitive.

**Example (BAD):**
> I am making a habit tracker. It tracks habits.

---

## Part 2: Feature Scope — The "Must-Have" List

**You must have EXACTLY 3-5 core features. No more, no less.**

For each feature, write:

```
### Feature N: [Feature Name]
**What it does:** (1-2 sentences)
**Why it matters:** (1 sentence — what problem does this solve?)
**User flow:** (step by step — what does the user type/see?)
**Edge cases:** (at least 2 — what could go wrong? how does your app handle it?)
```

**Example:**
```
### Feature 1: Add a New Habit
**What it does:** Lets the user create a new habit to track with a custom name and optional daily reminder time.
**Why it matters:** Without this, the app is useless — it's the entry point for all tracking.
**User flow:**
  1. App shows menu → user selects "Add habit"
  2. App prompts: "What habit?" → user types: "Drink 8 glasses of water"
  3. App prompts: "Reminder time? (HH:MM or skip)" → user types: "08:00"
  4. App confirms: "Habit 'Drink 8 glasses of water' added with 8:00 AM reminder!"
**Edge cases:**
  - User enters empty habit name → App rejects: "Habit name cannot be empty. Try again."
  - User enters duplicate habit → App warns: "You already track 'Drink 8 glasses of water'. Overwrite? (yes/no)"
```

---

## Part 3: Data Architecture

**You must define ALL data your app stores.**

### 3a: Data Structure (JSON or Python dict)

Show the EXACT structure with realistic example data (not placeholder "value" or "example"). Use data that looks real.

**Example (GOOD):**
```json
{
  "user": {
    "name": "Alex",
    "joined_date": "2025-05-08",
    "total_habits_completed": 47
  },
  "habits": [
    {
      "id": "habit_001",
      "name": "Drink 8 glasses of water",
      "created": "2025-05-01",
      "streak": 5,
      "longest_streak": 12,
      "last_completed": "2025-05-07",
      "reminder_time": "08:00",
      "history": [
        {"date": "2025-05-01", "completed": true},
        {"date": "2025-05-02", "completed": true},
        {"date": "2025-05-03", "completed": false},
        {"date": "2025-05-04", "completed": true},
        {"date": "2025-05-05", "completed": true},
        {"date": "2025-05-06", "completed": true},
        {"date": "2025-05-07", "completed": true}
      ]
    },
    {
      "id": "habit_002",
      "name": "Read for 30 minutes",
      "created": "2025-05-03",
      "streak": 3,
      "longest_streak": 3,
      "last_completed": "2025-05-07",
      "reminder_time": null,
      "history": [
        {"date": "2025-05-03", "completed": true},
        {"date": "2025-05-04", "completed": true},
        {"date": "2025-05-05", "completed": false},
        {"date": "2025-05-06", "completed": true},
        {"date": "2025-05-07", "completed": true}
      ]
    }
  ]
}
```

**Example (BAD):**
```json
{
  "habits": [{"name": "example", "streak": 0}]
}
```

### 3b: Data Flow Diagram

Describe how data moves through your app. Answer these:
- Where does data come FROM? (user input? file? API?)
- Where does data get STORED? (JSON file? variable?)
- When does data get READ? (on startup? on command?)
- When does data get WRITTEN? (after every action? on exit?)

---

## Part 4: Function Specifications

**You must define EVERY function your app will have.**

For each function, write:

```python
def function_name(parameter: type) -> return_type:
    """
    What this function does (1 sentence)
    
    Args:
        parameter: what it is and what values it accepts
    
    Returns:
        what the function returns
    
    Example:
        >>> function_name("example_input")
        "example_output"
    
    Edge cases handled:
        - edge case 1 → how it's handled
        - edge case 2 → how it's handled
    """
```

**Example (GOOD):**
```python
def add_habit(name: str, reminder_time: str = None) -> dict:
    """
    Creates a new habit and adds it to the habits list.
    
    Args:
        name: The habit name (e.g., "Drink water"). Must be non-empty.
        reminder_time: Optional time string in "HH:MM" format.
    
    Returns:
        The newly created habit dict with generated ID.
    
    Example:
        >>> add_habit("Drink water", "08:00")
        {"id": "habit_003", "name": "Drink water", "streak": 0, ...}
    
    Edge cases handled:
        - Empty name → raises ValueError: "Habit name cannot be empty"
        - Duplicate name → asks user: "Overwrite existing? (yes/no)"
        - Invalid time format → retries: "Please use HH:MM format (e.g., 08:00)"
    """
```

**You must have at least 5 functions. Each must have:**
- [ ] Function signature (name, parameters, return type)
- [ ] Docstring with description
- [ ] Args documented
- [ ] Return value documented
- [ ] At least 2 edge cases handled

---

## Part 5: User Interface & Interaction Design

### 5a: Main Menu

Show the EXACT text the user sees when they open your app:

```
====================================
      WELCOME TO STREAKKEEPER
====================================
1. View today's habits
2. Add a new habit
3. Mark habit as done
4. View streak leaderboard
5. View habit history
6. Delete a habit
7. Exit

What would you like to do? (1-7): 
```

### 5b: Screen-by-Screen Flow

For EVERY menu option, show the full screen output:

**Option 1 — View today's habits:**
```
--- Today's Habits (May 8, 2025) ---
[✓] Drink 8 glasses of water     Streak: 5🔥  (Done today!)
[ ] Read for 30 minutes          Streak: 3🔥  (Not done yet)
[✓] Morning workout              Streak: 12🔥 (Longest streak!)

2 of 3 habits completed today.
Keep the momentum going!
```

Do this for ALL menu options. Every screen your user sees must be specified.

---

## Part 6: Error Handling & Edge Cases

**This is where most PRDs fail.** You must think about what goes wrong.

List at least 5 specific error scenarios and how your app responds:

| # | Error Scenario | App Response |
|---|---------------|-------------|
| 1 | User types a letter when a number is expected | "Please enter a number between 1 and 7." |
| 2 | User tries to mark a habit done twice in one day | "You already completed this today! Come back tomorrow." |
| 3 | Data file is corrupted or missing | "No data found. Starting fresh. Create your first habit!" |
| 4 | User enters a habit name with only spaces | "Habit name cannot be empty. Try again." |
| 5 | App hasn't been used in 3+ days, streak should break | "Streak broken! You missed 3 days. Starting fresh streak today." |

---

## Part 7: Testing Plan

**How will you know your app works?** Define at least 3 test cases:

```
Test 1: Add habit → Mark complete → Check streak = 1
Test 2: Mark same habit complete twice → Should reject with message
Test 3: Delete only habit → View habits → Should show "No habits yet!"
Test 4: Corrupt data file → Launch app → Should recover gracefully
```

---

## Part 8: Stretch Goals (Optional but Encouraged)

If you finish early, what could make this project even better?

- [ ] Data visualization (matplotlib chart of habit completion over time)
- [ ] Sound effects or color coding in the terminal
- [ ] Export data to CSV
- [ ] Weekly summary report
- [ ] Gamification (badges, levels, achievements)

---

## PRD v2 Grading Rubric

| Criteria | Needs Work (1) | Good (2) | Excellent (3) |
|----------|---------------|----------|---------------|
| **Project Identity** | Vague, generic description | Clear pitch and user defined | Compelling story, specific user, personal motivation |
| **Features (3-5)** | Listed but no detail | Each has description + flow | Each has full user flow + edge cases + why it matters |
| **Data Architecture** | Basic structure shown | JSON with realistic data + data flow described | Complete JSON with realistic data, clear data flow, all storage decisions explained |
| **Function Specs (5+)** | Named but no detail | Signature + description for each | Full docstring, args, returns, edge cases, examples for each |
| **UI/Interaction** | Menu mentioned | Menu shown, some screens | Every screen specified with exact text user sees |
| **Error Handling** | 1-2 cases | 3-4 cases with responses | 5+ cases, thoughtful responses, recovery paths |
| **Testing Plan** | Not included | 2-3 test cases | 4+ test cases covering normal + edge scenarios |
| **Overall** | PRD is a rough draft | PRD is usable as a build guide | PRD is so detailed that an AI could build the entire app from it alone |

---

## Submission Instructions

1. Write your PRD v2 in a file called `PRD_V2.md` in your project repo
2. Commit it: `git add PRD_V2.md && git commit -m "Add PRD v2 with full specifications"`
3. Push it: `git push origin main`
4. Submit the GitHub link to Canvas

**This PRD v2 replaces your v1. It should be 3-5x more detailed.**
