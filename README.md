# Darwin Challenge

A Telegram bot for expense tracking powered by AI.

## Architecture

- **Bot Service** (Python/FastAPI): Processes messages and manages expense parsing
- **Connector Service** (Node.js/NestJS): Handles Telegram webhook integration  
- **PostgreSQL**: Database for users and expenses
- **Supabase Queue**: Message queue for service communication [[memory:6663473]]

## Development

```bash
# Setup development environment
npm run setup

# Run all services locally
npm run dev
```

## Deployment

Uses **Railway GitHub Integration** with `railway.toml` defining all services.

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway Dashboard
3. Railway auto-deploys on every push

### Environment Variables

Set in Railway Dashboard:

**Bot Service:** `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`

**Connector Service:** `TELEGRAM_BOT_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`