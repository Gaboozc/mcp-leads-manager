🇬🇧 English · [🇪🇸 Español](SETUP.es.md)

# How to start the app, step by step

This guide has 4 parts:

1. [Get ready (only once)](#part-1--get-ready-only-once)
2. [Start the app](#part-2--start-the-app)
3. [Sign in](#part-3--sign-in)
4. [Connect the AI assistant](#part-4--connect-the-ai-assistant)

If something goes wrong, jump to [If something goes wrong](#if-something-goes-wrong).

> **What does this word mean?**
> - **Terminal:** a window where you type commands. On Windows it is called **PowerShell**. On Mac it is called **Terminal**.
> - **API:** the part of the app that keeps the data and the rules. You don't see it; the screen talks to it.
> - **Screen:** the part you see in the browser.

---

## Part 1 — Get ready (only once)

### Step 1. Install three programs

| Program | Where to get it | How to check it works |
|---|---|---|
| Python 3.11 or newer | https://www.python.org/downloads/ | type `python --version` |
| Node.js 20 or newer | https://nodejs.org/ | type `node --version` |
| Git | https://git-scm.com/ | type `git --version` |

On Windows, when you install Python, tick the box **"Add Python to PATH"**.

**What you'll see:** each check prints a version number, like `Python 3.12.4`.

### Step 2. Download the project

Open a terminal and type:

```bash
git clone https://github.com/gaboozc/mcp-leads-manager.git
cd mcp-leads-manager
```

**What you'll see:** a new folder called `mcp-leads-manager`. From now on, always work inside it.

### Step 3. Prepare Python

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Mac:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**What you'll see:** the line starts with `(.venv)`, and the install ends with `Successfully installed ...`.

If Windows says scripts are disabled, type this once and try again:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Step 4. Prepare the screen

```bash
cd frontend
npm install
cd ..
```

**What you'll see:** it takes a minute or two. Yellow warnings are normal.

---

## Part 2 — Start the app

You need **two terminals open at the same time**: one for the API and one for the screen.

### Step 5. Terminal 1: start the API

Inside the project folder:

**Windows:** `.venv\Scripts\Activate.ps1` · **Mac:** `source .venv/bin/activate`

Then:

```bash
python -m backend.app
```

**What you'll see:** `Running on http://127.0.0.1:5050`.

The first time, the app creates the example data by itself: 1 user, 3 courses and 15 leads.

**Leave this window open.** If you close it, the app stops.

### Step 6. Terminal 2: start the screen

Open a **new** terminal, go to the project folder, and type:

```bash
cd frontend
npm run dev
```

**What you'll see:** `Local: http://localhost:5173/`.

**Leave this window open too.**

---

## Part 3 — Sign in

### Step 7. Open the app

Open **http://localhost:5173** in your browser.

### Step 8. Type the test user

| Email | Password |
|---|---|
| `operator@school.test` | `demo1234` |

Press **Sign in**.

**What you'll see:** the inbox, with "15 to contact today".

### What can happen when you sign in?

| You see | What it means | What to do |
|---|---|---|
| The inbox | It worked 🎉 | Start working |
| *Wrong email or password.* | A typo | Type them again, exactly as above |
| *Can't reach the API…* | Terminal 1 is not running | Start it again (step 5) |
| *Your session expired. Sign in again.* | More than 8 hours passed, or the API restarted | Sign in again |

**Good to know:**

- You stay signed in for 8 hours, even if you reload the page.
- To leave, press **Sign out** (top right).
- There is no "sign up" page. This is an internal tool, so accounts are created by whoever runs it. For the test, there is one user.

---

## Part 4 — Connect the AI assistant

The assistant (Claude Desktop or Cursor) starts our helper program by itself. You only have to tell it where the program is.

### Step 9. Find the folder path

**Windows:** `(Get-Location).Path` · **Mac:** `pwd`

**What you'll see:** something like `C:\Users\you\mcp-leads-manager` or `/Users/you/mcp-leads-manager`. Copy it.

### Step 10a. With Claude Desktop

1. Open Claude Desktop → **Settings** → **Developer** → **Edit Config**.
2. A file called `claude_desktop_config.json` opens. Open it with Notepad (Windows) or TextEdit (Mac).
3. Add this block **at the top, right after the first `{`**. Do not delete anything that is already there. Change `you` to your real folder.

**Windows:**

```json
  "mcpServers": {
    "leads-inbox": {
      "command": "C:\\Users\\you\\mcp-leads-manager\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\you\\mcp-leads-manager\\mcp_server\\server.py"],
      "env": {
        "DATABASE_URL": "sqlite:///C:/Users/you/mcp-leads-manager/backend/leads.db",
        "APP_TZ": "America/New_York",
        "OPERATOR_EMAIL": "operator@school.test"
      }
    }
  },
```

**Mac:**

```json
  "mcpServers": {
    "leads-inbox": {
      "command": "/Users/you/mcp-leads-manager/.venv/bin/python",
      "args": ["/Users/you/mcp-leads-manager/mcp_server/server.py"],
      "env": {
        "DATABASE_URL": "sqlite:////Users/you/mcp-leads-manager/backend/leads.db",
        "APP_TZ": "America/New_York",
        "OPERATOR_EMAIL": "operator@school.test"
      }
    }
  },
```

If the file was empty, put `{` before the block and `}` after it, and remove the last comma.

4. Save. You can paste the whole file on https://jsonlint.com to check it says **"Valid JSON"**.
5. **Close Claude Desktop completely.** On Windows, use the little arrow next to the clock → right click on Claude → **Quit**. Then open it again.
6. Go to **Settings → Developer**.

**What you'll see:** **leads-inbox** with the word **Running**.

### Step 10b. With Cursor

Create a folder `.cursor` inside the project, and inside it a file `mcp.json`. Put the same block in it, wrapped in `{ }`. Then go to **Cursor Settings → MCP**.

**What you'll see:** **leads-inbox** with a green dot and 3 tools.

### Step 11. Try it

In a **new chat**, write: *"Who should I contact first today?"*

When it asks for permission to use the tool, press **Allow**.

**What you'll see:** the assistant answers with today's list, starting with Ana Lopez.

**Tips:**

- Open a **new chat** for each test. In an old chat, the assistant remembers old answers.
- The assistant asks for permission before saving anything. Press **Allow** quickly, or the request times out.
- While you use the assistant, don't type in the browser tab of the app. The numbers `1` to `5` are shortcuts there and would save results.

---

## Everyday tasks

**Start again with fresh example data** (useful if days have passed):

1. Stop the API (`Ctrl + C` in terminal 1).
2. Type `python -m backend.seed --reset`
3. Start the API again (step 5).

**Get the latest version of the project:**

1. `git pull`
2. Restart the API (`Ctrl + C`, then `python -m backend.app`).
3. Restart the screen (`Ctrl + C`, then `npm run dev`) and reload the browser with `Ctrl + F5`.

**Run the automatic tests:** `pytest -q backend/tests`. You should see `34 passed`.

---

## If something goes wrong

| What you see | Why | Fix |
|---|---|---|
| `python is not recognized` | Python is missing, or not in the PATH | Install it (step 1) and tick "Add Python to PATH" |
| `No module named 'flask'` | The `(.venv)` is not active | Activate it (step 3) |
| `No time zone found with key America/New_York` | Windows is missing time zone data | Run `pip install -r requirements.txt` again |
| `Address already in use` | Another program uses port 5050 | Close it, or use another port: `API_PORT=5051` before both commands (Windows: `$env:API_PORT=5051`) |
| The page is all white | The browser kept an old copy | Stop the screen, delete the folder `frontend/node_modules/.vite`, run `npm run dev` again, reload with `Ctrl + F5` |
| *Can't reach the API…* | Terminal 1 is not running | Start it (step 5) |
| Claude/Cursor shows leads-inbox in red | A path in the config is wrong | Check the 3 paths, and that `command` points to the Python inside `.venv` |
| The assistant does not see what you saved | `DATABASE_URL` points to another file | It must be the `backend/leads.db` of this project |
| "Today" leads look old | The example data was created days ago | Start again with fresh data (see Everyday tasks) |
