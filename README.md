# QuickTow — Auto-Accident Intake Platform

A two-part system that uses AI to collect information from car accident victims and route them to the right service (tow truck or body shop). The backend handles conversations through an AI agent powered by Claude. The Flutter app lets customers chat with the agent and lets operators manage incoming cases.

## How It Works

1. A customer opens the app and taps "Report an Accident"
2. The AI agent asks them questions one at a time: name, phone, location, vehicle info, damage description
3. Once all info is collected, the case moves to "Pending Review"
4. An operator logs into the dashboard, reviews cases, updates statuses, and adds notes

The backend also exposes a WeChat webhook, so the same AI agent can handle conversations from WeChat users.

## Tech Stack

- **Backend:** Python, Flask, SQLite, LangGraph (workflow engine), Claude Sonnet (via langchain-anthropic)
- **Mobile App:** Flutter (Dart), Provider for state management
- **Infrastructure:** Docker, docker-compose, Gunicorn

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── models/         # Database models and data access (case, message, operator, note)
│   │   ├── routes/         # API endpoints (auth, cases, wechat webhook)
│   │   ├── services/       # LLM service (Claude) and WeChat message handling
│   │   └── workflow/       # LangGraph state machine (classify intent, collect info)
│   ├── tests/              # 49 tests (all use mocked LLM, no API key needed)
│   ├── Dockerfile
│   ├── config.py
│   └── requirements.txt
├── phoneapp/
│   └── lib/
│       ├── screens/        # Home, chat, login, case list, case detail, tow request
│       ├── providers/      # State management (auth, cases, tow request)
│       ├── services/       # HTTP client that talks to the backend
│       └── models/         # Data classes
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Docker (for the backend)
- Flutter SDK (for the mobile app)
- An Anthropic API key (for the AI agent)

### 1. Start the Backend

Copy the example environment file and add your API key:

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and set ANTHROPIC_API_KEY to your real key
```

Build and run with Docker:

```bash
docker compose up -d --build
```

This starts the backend on `localhost:5001`. It automatically creates an admin user (`admin` / `admin123`).

To verify it is running:

```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

You should get back a JSON response with an `access_token`.

### 2. Run the Flutter App

```bash
cd phoneapp
flutter pub get
flutter run
```

The app connects to `localhost:5001`. This works out of the box on iOS Simulator and desktop. If you are running on a physical device or Android emulator, you will need to update the `baseUrl` in `lib/services/api_service.dart` to point to your machine's IP address.

### 3. Run Tests

Backend (no API key needed, all LLM calls are mocked):

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v
```

Flutter:

```bash
cd phoneapp
flutter test
```

## API Endpoints

All endpoints except login and chat require a JWT token in the `Authorization: Bearer <token>` header.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/login` | No | Returns a JWT token |
| GET | `/api/auth/me` | Yes | Returns the logged-in operator |
| POST | `/api/auth/register` | Admin | Creates a new operator account |
| GET | `/api/cases/` | Yes | Lists cases (optional `?status=` filter) |
| GET | `/api/cases/<id>` | Yes | Case detail with messages and notes |
| PATCH | `/api/cases/<id>` | Yes | Update case fields (status, customer info) |
| POST | `/api/cases/<id>/notes` | Yes | Add an operator note |
| POST | `/api/chat` | No | Send a message to the AI agent |
| GET | `/wechat/` | No | WeChat server verification |
| POST | `/wechat/` | No | WeChat incoming message webhook |

## Environment Variables

See `backend/.env.example` for the full list. The only required variable for local development is `ANTHROPIC_API_KEY`. The WeChat variables are only needed if you are connecting a real WeChat Official Account.

## Stopping the Backend

```bash
docker compose down
```

To also delete the database:

```bash
docker compose down -v
```
