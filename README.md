# Expensio - Telegram Expense Tracker Bot 🤖💰

An intelligent expense tracking system that allows users to manage their expenses through a Telegram bot powered by LLMs.

## 🏗️ Project Structure

This is a monorepo containing two main services that work together to provide expense tracking functionality:

```
darwin-challenge/
├── apps/
│   ├── bot/                    # Python FastAPI service for expense processing
│   │
│   └── connector/              # NestJS service for Telegram integration
│
├── scripts/
│   └── dev-setup.sh           # Development environment setup script
├── docker-compose.yml         # Local development services
└── package.json              # Root package.json with Turbo scripts
```

## 🛠️ Tech Stack

### Backend Services
- **Connector**: NestJS (TypeScript) with Fastify
- **Bot**: FastAPI (Python) with async support
- **Database**: PostgreSQL 15
- **Message Queue**: RabbitMQ with management UI
- **AI Integration**: OpenAI API for expense parsing
- **Monorepo**: Turbo for orchestration

### Key Libraries
- **Python**: FastAPI, LangChain, OpenAI, asyncpg, aio-pika
- **TypeScript**: NestJS, RxJS, amqplib, axios
- **Database**: Knex.js for migrations, asyncpg for Python

## 📋 Prerequisites

Before setting up the project, make sure you have the following installed:

- **Docker & Docker Compose** (required for databases and message queue)
- **Node.js** (v18 or higher) and npm
- **Python 3.8+** and pip

### Required API Keys

You'll need to obtain these API keys before running the application:

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Telegram Bot Token**: Create a bot via [@BotFather](https://t.me/botfather) on Telegram

## 🚀 Quick Setup

1. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   Edit the `.env` file and add your API keys:
   ```env
   OPENAI_API_KEY=sk-your_openai_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

2. **Run the setup script**
   ```bash
   ./scripts/dev-setup.sh
   ```

   This script will:
   - ✅ Check that Docker is running
   - 🐳 Start PostgreSQL and RabbitMQ containers
   - 📦 Install Node.js dependencies
   - 🐍 Install Python dependencies
   - 🗄️ Set up the database and message queue

3. **Run database migrations**
   ```bash
   cd apps/bot
   npm run migrate
   cd ../..
   ```

4. **Start the development services**
   ```bash
   npm run dev
   ```

   This starts both services:
   - **Connector**: http://localhost:3001
   - **Bot**: http://localhost:3002

## 🎯 Demo

### Try the Live Bot

You can test the expense tracking functionality by chatting with our Telegram bot:

**Bot**: [@ExpensioTrackerBot](https://t.me/ExpensioTrackerBot)

### Registration

To register as a new user, send the following password as a message:

```
12345678
```

### Usage Examples

Once registered, you can start tracking expenses by sending messages like:

- "I spent $25 on coffee at Starbucks"
- "Paid 15 EUR for lunch today"
- "Gas station: $45.50"
- "Movie tickets for 2 people: $30"

The AI-powered system will automatically parse your messages and extract:
- Amount and currency
- Category (food, transport, entertainment, etc.)
- Description and location when available

## 🧩 Development

### Infrastructure Services

The development environment includes:

- **PostgreSQL**: localhost:5432
  - Database: `expensio`
  - Username: `expensio_user`
  - Password: `expensio_password`

- **RabbitMQ**: 
  - AMQP: localhost:5672
  - Management UI: http://localhost:15672
  - Username: `expensio_user`
  - Password: `expensio_password`

## 🏗️ Architecture

The system follows a clean architecture pattern with:

1. **Message Flow**: Telegram → Connector → RabbitMQ → Bot → Database
2. **AI Processing**: OpenAI API parses natural language expense descriptions
3. **Data Storage**: PostgreSQL stores users and expenses
4. **Async Processing**: RabbitMQ handles message queuing between services

### Service Communication

- **Connector**: Receives Telegram webhooks (on production) / polling (on development), forwards to message queue
- **Bot**: Processes messages from queue, uses AI to parse expenses, stores in database
- **Database**: PostgreSQL with migrations for schema management
- **Queue**: RabbitMQ for reliable async message processing

## 📝 Environment Variables

Key environment variables (see `env.example` for complete list):

- `OPENAI_API_KEY`: Your OpenAI API key
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token  
- `TELEGRAM_POLLING_ENABLED`: Set to `true` for development
- `DATABASE_URL`: PostgreSQL connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `REGISTRATION_PASSWORD`: Password to register on telegram bot.

## 🧪 Testing

**Note**: Unit tests in python were not implemented in this project due to time constraints. In a production environment, comprehensive test coverage would include:

- Unit tests for services and repositories
- Integration tests for API endpoints
- End-to-end tests for the complete expense processing flow
- Mock tests for external API integrations (OpenAI, Telegram)

Future improvements should prioritize adding test coverage to ensure reliability and maintainability.

**Happy expense tracking! 💰📊**
