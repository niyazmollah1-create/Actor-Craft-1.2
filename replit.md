# Discord Bot with Token Economy System

## Overview

This is a comprehensive Discord bot built with Python 3.11 featuring a complete token-based economy system, AI integration with Google Gemini, and extensive utility commands. The bot uses discord.py with a cog-based architecture and includes advanced features like music, moderation, image manipulation, and server management tools.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (August 09, 2025)

- **Fixed Bot Prefix**: Changed from "/" to "!" for proper economy command functionality
- **Updated AI System**: Fixed Gemini integration to use new google-genai library (v2.0+)
- **Improved Quiz System**: Enhanced answer detection to accept multiple answer formats
- **Implemented Token Economy System**: Complete overhaul using Tokens (T) as currency with ! prefix
- **Fixed Trigger System**: Responds only to exact word matches (e.g., "ip" → "Madaripur")
- **Database Migration**: SQLite-based economy database with proper cooldown management
- **Shop System**: Comprehensive shop with exact pricing - roles, titles, pets, and artifacts

## System Architecture

### Bot Architecture
- **Main Entry Point**: main.py serves as the primary bot runner with GeminiBot class
- **Command System**: Uses discord.py's command extension with cog-based architecture
- **Event Handling**: Comprehensive event handling including message processing and command error handling
- **Intents Configuration**: All intents enabled for full functionality

### Economy System
- **Database**: SQLite-based economy database (economy.db) with users and inventory tables
- **Currency**: Tokens (T) as universal currency
- **Earning Methods**: Daily rewards, quiz competitions, coin flip gambling
- **Shop System**: Four categories - roles, titles, pets, artifacts
- **Cooldown Management**: Proper time-based restrictions for daily and quiz commands

### Configuration Management
- **Environment Variables**: Uses config.py with extensive environment variable support
- **Multi-Service Integration**: Supports Discord, Gemini AI, GitHub, OpenWeather APIs
- **Database Integration**: Centralized database management through database.py

### Command Structure
- **Cog Organization**: Multiple specialized cogs for different functionality
  - economy.py: Complete token economy system
  - utility_info.py: Utility commands with trigger system
  - ai_personality.py: Gemini AI integration
  - moderation.py: Server moderation tools
  - music.py: Music playback functionality
  - image_manipulation.py: Image processing commands
  - server_management.py: Server administration tools
  - fun_engagement.py: Entertainment commands

### Economy Features
- **Commands**: !bal, !daily, !quiz, !flip, !shop, !buy, !inv, !give, !leaderboard, !get_tokens
- **Shop Categories**: 
  - Roles: High Roller (500K T), Quiz Master (1M T), The Millionaire (2.5M T), The Jackpot (5M T)
  - Titles: The Lucky (100K T), The Unlucky (150K T), High Stakes (500K T), The Risk Taker (750K T), The All-In (1M T)
  - Pets: Rabbit's Foot (200K T), Golden Dragon (1.5M T), Fortune Cat (3M T), Phoenix (10M T)
  - Artifacts: Lucky Coin (50K T), The Cheat (250K T), Insurance (1M T)

### Trigger System
- **Exact Word Matching**: Responds only to complete word matches, not partial text
- **Current Triggers**: "ip" → "Madaripur", "hello" → "Hello there!", "ping" → "Pong!", "test" → "Test successful!"
- **Implementation**: Message listener in utility_info.py cog

## External Dependencies

### Core Dependencies
- **discord.py**: Primary Discord API library
- **aiosqlite**: Async SQLite database operations
- **google-generativeai**: Gemini AI integration
- **wikipedia**: Wikipedia API access
- **PyGithub**: GitHub API integration
- **aiohttp**: HTTP client for API requests

### API Integrations
- **Google Gemini**: AI personality and text generation
- **GitHub API**: Repository information and statistics
- **OpenWeather API**: Weather information lookup
- **Wikipedia API**: Encyclopedia searches

### Environment Configuration
- **Required Secrets**: DISCORD_BOT_TOKEN, GEMINI_API_KEY, GITHUB_TOKEN, OPENWEATHER_API_KEY
- **Optional Configuration**: Various bot settings and feature toggles