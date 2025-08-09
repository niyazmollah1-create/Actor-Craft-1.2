# Discord Bot with Token Economy System

A powerful Discord bot built with Python 3.11 featuring a comprehensive token-based economy system, AI integration, and utility commands.

## Features

### 🪙 Token Economy System
- **Currency**: Tokens (T) - Universal currency for the bot
- **Earning Methods**:
  - `!daily` - Daily reward (1,000-5,000 T every 24 hours)
  - `!quiz` - Trivia questions for 50,000 T (every 3 hours)
  - `!flip <amount>` - Coin flip gambling (unlimited)

### 🛒 Token Shop
- **Roles**: Prestigious server roles (High Roller, Quiz Master, The Millionaire, The Jackpot)
- **Titles**: Profile titles (The Lucky, The Unlucky, The All-In, etc.)
- **Pets**: Daily bonus companions (Rabbit's Foot, Golden Dragon, Fortune Cat, Phoenix)
- **Artifacts**: Special one-use items (Lucky Coin, The Cheat, Insurance)

### 💰 Economy Commands
- `!bal` - Check token balance
- `!inv` - View inventory
- `!give <@user> <amount>` - Transfer tokens
- `!leaderboard` - Top 10 richest users
- `!shop [category]` - Browse shop categories
- `!buy <category> <item>` - Purchase items

### 🤖 Bot Features
- AI personality integration with Gemini
- Music commands
- Moderation tools
- Image manipulation
- Utility commands with trigger system
- Server management tools

## Setup Instructions

### 1. Discord Application Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create bot
4. Copy the bot token
5. Enable "Message Content Intent" and "Server Members Intent"

### 2. Environment Variables
Create a `.env` file with:
```
DISCORD_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here
OPENWEATHER_API_KEY=your_weather_api_key_here
```

### 3. Run the Bot
```bash
python main.py
```

## Economy Pricing

### Roles
- High Roller: 500,000 T
- Quiz Master: 1,000,000 T  
- The Millionaire: 2,500,000 T
- The Jackpot: 5,000,000 T

### Titles
- The Lucky: 100,000 T
- The Unlucky: 150,000 T
- High Stakes: 500,000 T
- The Risk Taker: 750,000 T
- The All-In: 1,000,000 T

### Pets
- Rabbit's Foot: 200,000 T (luck boost for coin flips)
- Golden Dragon: 1,500,000 T (10,000 T daily bonus)
- Fortune Cat: 3,000,000 T (50,000 T daily bonus)
- Phoenix: 10,000,000 T (100,000 T daily bonus)

### Artifacts
- Lucky Coin: 50,000 T (guaranteed !flip win)
- The Cheat: 250,000 T (guaranteed !gamble win)
- Insurance: 1,000,000 T (10% refund on losses)

## Administrative Commands
- `!get_tokens <amount>` - Owner only: Add tokens to balance

## Trigger System
The bot responds to exact word matches in messages:
- "ip" → "Madaripur"
- "hello" → "Hello there!"
- "ping" → "Pong!"
- "test" → "Test successful!"

Only responds to exact words, not partial matches within words.