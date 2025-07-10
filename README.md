
# Distributed PokeAPI Game

A distributed Pokemon game with Flask API backend and MongoDB database.

## Architecture

- **EC2 Instance 1**: Flask API + MongoDB (Docker containers)
- **EC2 Instance 2**: Pokemon Game Client

## Quick Start

### Local Development

1. Clone the repository
2. Start the backend services:
   ```bash
   cd docker
   docker-compose up -d