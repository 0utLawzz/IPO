# Hourly Workflow (Windows Task Scheduler)

This workflow runs the scraper every hour in non-interactive mode.

## 1) One-time setup

- Run once manually:

```bash
python main.py
```

- Login in the browser and complete captcha.
- Press Enter in the terminal.
- Confirm `cookies.json` is created.

## 2) Create the scheduled task

Open **Task Scheduler**:

- **Create Task...**
- **General**
  - Name: `IPO TM Scraper Hourly`
  - Configure for: your Windows version
- **Triggers**
  - New...
  - Begin the task: `On a schedule`
  - Daily
  - Repeat task every: `1 hour`
  - For a duration of: `Indefinitely`
- **Actions**
  - New...
  - Action: `Start a program`
  - Program/script: path to your Python, e.g.

```text
C:\Users\brand\AppData\Local\Programs\Python\Python314\python.exe
```

  - Add arguments:

```text
main.py --all
```

  - Start in:

```text
i:\Pythons\IPO
```

- **Settings**

- Allow task to be run on demand
- If the task is already running, then the following rule applies: `Do not start a new instance`

## 3) Notes

- If cookies expire, the hourly run may fail because it cannot do manual captcha. In that case:
  - Run `python main.py` manually again.
  - Login and re-generate `cookies.json`.
