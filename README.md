# CaseRep — AI-Powered Case Interview Practice App

CaseRep is a Streamlit application designed to help candidates practice 10-minute business case interviews. The app generates realistic case prompts, reveals structured data, starts a timed solving session, and provides AI-generated feedback on the candidate's answer.

## Features

- AI-generated business case prompts
- Multiple case types: total cost of ownership, breakeven, market sizing, investment decisions, pricing, and profitability
- Industry selection: energy, aviation, retail, SaaS, logistics, healthcare, and more
- 10-minute timed solving mode
- Auto-submit when the timer reaches zero
- AI feedback on structure, arithmetic, recommendation, and communication
- Attempt history saved locally
- Hidden solution with relevant data, irrelevant data, formula, caveats, and final recommendation

## Tech Stack

- Python
- Streamlit
- Anthropic Claude API
- JSON parsing
- Local file storage
- Conda environment

## Why I Built This

I built this project to practice structured problem-solving for research, analytics, consulting, and strategy interviews. The goal was to create a tool that simulates realistic interview pressure while giving detailed feedback on business reasoning and communication.

## Setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/case-rep-ai-interview-practice.git
cd case-rep-ai-interview-practice
