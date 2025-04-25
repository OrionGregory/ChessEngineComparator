---
layout: default
---

# Chess Engine Comparator

Welcome to the Chess Engine Comparator — a platform where students and developers can compete by building bots that battle it out in tournament-style chess matches.

---

## Project Goals

- Build a competitive environment for custom chess bots
- Encourage beginner AI and algorithm design
- Provide an educational tool for classrooms and clubs

---

## Team Bios

- [Orion Gregory](./bios.md)
- [Tejas Bhadoria](./tejas.md)
- [Sebastian Shirk](./sebastian.md)

---

## Deliverables

- [Project Presentation](./initialPresentation.pptx)
- [Project Repository](https://github.com/OrionGregory/ChessEngineComparator)
- [Project Website](https://oriongregory.github.io/ChessEngineComparator/)

---

## Sprint Deliverables

### Sprint 1

| File Name                             | Download Link                                                                |
|--------------------------------------|-------------------------------------------------------------------------------|
| OnlineChessEngineComparatorSlides    | [Download](Sprint1Dev/Online%20Chess%20Engine%20Comparator%20(1).pptx)        |
| ProjectSprintGoals.xlsx              | [Download](Sprint1Dev/ProjectSprintGoals%20(1)%20(1).xlsx)                    |
| Sprint Daily Journal.pdf             | [Download](Sprint1Dev/Sprint%20Daily%20Journal%20(1).pdf)                     |
| Sprint Retrospective.pdf             | [Download](Sprint1Dev/Sprint%20Retrospective%20(1).pdf)                       |
| Sprint1GoalBacklog.pdf               | [Download](Sprint1Dev/Sprint1GoalBacklog%20(1).docx%20(1).pdf)                |

### Sprint 2

| File Name                            | Download Link                                                                |
|-------------------------------------|-------------------------------------------------------------------------------|
| OnlineChessEngineComparatorSlides   | [Download](Sprint2Dev/OnlineChessEngineComparator(Sprint2).pdf)               |
| Sprint Planning Document (Sprint 2) | [Download](Sprint2Dev/SprintPlanningDocument(Sprint2).pdf)                    |
| Sprint2Goals.pdf                    | [Download](Sprint2Dev/Sprint2Goals.pdf)                                       |
| Sprint2Retrospective.pdf            | [Download](Sprint2Dev/Sprint2Retrospective.pdf)                               |
| SprintDailyJournal.pdf              | [Download](Sprint2Dev/SprintDailyJournal.pdf)                                 |

### Sprint 3

| File Name                            | Download Link                                                                |
|-------------------------------------|-------------------------------------------------------------------------------|
| OnlineChessEngineComparatorSlides   | [Download](Sprint3Dev/OnlineChessEngineComparator(Sprint3).pdf)               |
| Sprint Planning Document (Sprint 3) | [Download](Sprint3Dev/SprintPlanningDocument(Sprint3).pdf)                    |
| Sprint3Backlog.pdf                  | [Download](Sprint3Dev/Sprint3Backlog.pdf)                                     |
| ProjectGoals.pdf                    | [Download](Sprint3Dev/ProjectGoals.pdf)                                       |
| SprintDailyJournal.pdf              | [Download](Sprint3Dev/SprintDailyJournal.pdf)                                 |
| ContributionList.pdf                | [Download](Sprint3Dev/ContributionList.pdf)                                   |
| CyberSecurity.pdf                   | [Download](Sprint3Dev/CyberSecurity.pdf)                                      |
| ChessBotTournament.mp4              | [Download](Sprint3Dev/ChessBotTournament.mp4)                                 |

---

## Installation

Follow the [Installation Guide](./installation.md) for full setup instructions.

---

## Usage Guides

- [Teacher Guide](./docs/TeacherUsage.md)
- [Student Guide](./docs/StudentsUsage.md)

---

## Technical Docs

- [Restrict Signups by Email Domain](./docs/EmailDomainEnforcement.md)
- [Using Stockfish Bots](./docs/EvilFish(StockfishBots).md)

## Development Docs

- [DeveloperDoc](./docs/DevDocs.md)

## Frequently Asked Questions

### Why is my Django server not starting?
Ensure you’ve activated your virtual environment and installed all dependencies using:
```bash
pip install -r requirements.txt
```
Also, verify that the manage.py file is in the correct directory and run the server with:
```bash
python ChessApp/manage.py runserver
```

### How can I debug issues with Redis or Celery?
Check if Redis is running and accessible on the default port (6379). Ensure the CELERY_BROKER_URL and CELERY_RESULT_BACKEND in your settings are correctly configured to point to your Redis instance. Also, confirm that the Celery worker is running in a separate terminal.

- For Redis: Run `redis-cli ping` to check if Redis is running. If it’s not, start it with `redis-server.`

- For Celery: Check the Celery worker logs for errors by running the worker with `--loglevel=debug`.

### How do I resolve "Database connection failed" or "Invalid Password" errors?
Ensure that PostgreSQL is running and the credentials in the `.env` file match your database setup. Verify that the database user has the correct permissions and that the database exists.

You can edit the `.env` file in the project root directory to add or update environment variables. Restart the Django server and Celery worker after making changes.

## Demo Video
<video
  style="width:100%; max-width:800px; height:auto;"
  controls
  src="Sprint3Dev/ChessBotTournament.mp4"
  title="Demo">
</video>