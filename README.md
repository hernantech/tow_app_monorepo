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

Copy the example environment file and fill in your keys:

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and set:
#   ANTHROPIC_API_KEY  — your Anthropic API key (required)
#   CHAT_API_KEY       — a random secret string (used to authenticate the mobile app)
```

You can generate a `CHAT_API_KEY` with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then paste the same key into `phoneapp/lib/services/api_service.dart` as the `_chatApiKey` value so the app can authenticate with the backend.

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

Operator endpoints require a JWT token in the `Authorization: Bearer <token>` header. The chat endpoint uses a separate API key and device-based rate limiting (see below).

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/login` | No | Returns a JWT token |
| GET | `/api/auth/me` | Yes | Returns the logged-in operator |
| POST | `/api/auth/register` | Admin | Creates a new operator account |
| GET | `/api/cases/` | Yes | Lists cases (optional `?status=` filter) |
| GET | `/api/cases/<id>` | Yes | Case detail with messages and notes |
| PATCH | `/api/cases/<id>` | Yes | Update case fields (status, customer info) |
| POST | `/api/cases/<id>/notes` | Yes | Add an operator note |
| POST | `/api/chat` | API Key | Send a message to the AI agent |
| GET | `/wechat/` | No | WeChat server verification |
| POST | `/wechat/` | No | WeChat incoming message webhook |

## Rate Limiting

The `/api/chat` endpoint is protected by two mechanisms:

- **API key** -- every request must include an `X-API-Key` header matching the `CHAT_API_KEY` in `.env`. Without it, the request is rejected with 401.
- **Per-device message limit** -- each device gets a unique ID (generated on first launch and stored on-device). The backend tracks how many messages each device has sent and returns 429 when the limit is reached. The default limit is 75 messages, which is roughly 10 full intake conversations. You can change it with the `CHAT_MSG_LIMIT_PER_DEVICE` environment variable.

The response includes a `remaining_messages` field so the app can show the user how many messages they have left.

## Environment Variables

See `backend/.env.example` for the full list. Required variables:

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Claude API key for the AI agent |
| `CHAT_API_KEY` | Shared secret between the app and backend (must match `_chatApiKey` in `api_service.dart`) |
| `CHAT_MSG_LIMIT_PER_DEVICE` | Max messages per device (default: 75) |

The WeChat variables (`WECHAT_APP_ID`, `WECHAT_APP_SECRET`, `WECHAT_TOKEN`) are only needed if you are connecting a real WeChat Official Account.

## Cost Note

The AI agent uses Claude Sonnet by default (`claude-sonnet-4-20250514` in `backend/app/services/llm_service.py`). For a production deployment where you want to keep costs low, consider switching to a cheaper model. The intake task (classifying intent, extracting fields, generating short responses) does not require a frontier model. Good alternatives:

- **Claude Haiku** (`claude-haiku-4-5-20251001`) -- roughly 10x cheaper than Sonnet, fast, and more than capable for structured data extraction
- **OpenAI GPT-4o-mini** -- similar price point to Haiku, would require swapping `langchain-anthropic` for `langchain-openai` in requirements and updating the `LLMService` class

To change the model, edit the `model` parameter in `LLMService.__init__` in `backend/app/services/llm_service.py`.

## Stopping the Backend

```bash
docker compose down
```

To also delete the database:

```bash
docker compose down -v
```

## Deploying to Production

Below is a rough guide for getting this running on an EC2 instance behind Cloudflare. This is not the only way to do it, but it is straightforward and cheap.

### Database Persistence

The SQLite database is already stored on a Docker named volume (`backend-data`), which survives container restarts and rebuilds. The data lives at `/app/data/intake.db` inside the container. A `docker compose down` preserves the volume. Only `docker compose down -v` deletes it.

If you want to back up the database, you can copy it out of the container:

```bash
docker cp demo-backend-1:/app/data/intake.db ./backup_intake.db
```

For a production deployment with heavier traffic, consider migrating from SQLite to PostgreSQL. SQLite works well for single-server setups but does not handle concurrent writes from multiple workers.

### EC2 Setup

1. Launch an EC2 instance. A `t3.micro` or `t3.small` is enough for low traffic. Use Ubuntu 22.04 or Amazon Linux 2023.

2. Install Docker and Docker Compose:
   ```bash
   # Ubuntu
   sudo apt update && sudo apt install -y docker.io docker-compose-v2
   sudo usermod -aG docker $USER
   # Log out and back in for the group change to take effect
   ```

3. Clone the repo and set up the environment:
   ```bash
   git clone https://github.com/hernantech/tow_app_monorepo.git
   cd tow_app_monorepo
   cp backend/.env.example backend/.env
   # Edit backend/.env with your real keys
   ```

4. Start the backend:
   ```bash
   docker compose up -d --build
   ```

5. Open port 5001 (or whichever port you use) in your EC2 security group. If you are putting Cloudflare in front, you only need to allow traffic from Cloudflare's IP ranges.

### Cloudflare Setup

Cloudflare sits between your users and your EC2 instance. It gives you HTTPS, DDoS protection, and caching for free.

1. Add your domain to Cloudflare and point your DNS to your EC2 instance's public IP. Create an A record (e.g., `api.yourdomain.com`) pointing to the EC2 IP with the orange cloud (proxied) enabled.

2. In Cloudflare's SSL/TLS settings, set the mode to "Full" (not "Full (strict)" unless you also install a cert on EC2).

3. On EC2, update your docker-compose port mapping to `80:5000` so Cloudflare can reach it over HTTP on the backend side:
   ```yaml
   ports:
     - "80:5000"
   ```

4. Update `baseUrl` in the Flutter app's `api_service.dart` to point to your Cloudflare domain:
   ```dart
   static const String baseUrl = 'https://api.yourdomain.com';
   ```

5. If you want to lock down the EC2 instance so only Cloudflare can reach it, restrict your security group's inbound rules to Cloudflare's published IP ranges: https://www.cloudflare.com/ips/

### References

- EC2 getting started: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html
- Install Docker on Ubuntu: https://docs.docker.com/engine/install/ubuntu/
- Cloudflare setup guide: https://developers.cloudflare.com/fundamentals/setup/
- Cloudflare SSL modes: https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/
- Cloudflare IP ranges (for security group lockdown): https://www.cloudflare.com/ips/
- Docker volumes (how persistence works): https://docs.docker.com/engine/storage/volumes/
