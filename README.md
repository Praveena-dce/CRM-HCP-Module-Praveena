# AI-First CRM HCP Module – Log Interaction Screen

## Project Overview

This project is an AI-powered Healthcare Professional (HCP) CRM module designed for life science and pharmaceutical field representatives.

The application enables users to log and manage HCP interactions using either:

- A structured form-based interface
- An AI conversational chat interface

The system leverages AI to intelligently extract, summarize, and populate interaction details automatically.

---

# Objective

The goal of this project is to conceptualize and implement an AI-first CRM experience focused on HCP engagement management.

The application helps sales representatives:

- Log interactions efficiently
- Capture discussion insights
- Track materials shared
- Record HCP sentiment
- Maintain structured interaction history
- Edit and update interactions through AI-assisted workflows

---

# Key Features

## AI Chat-Based Interaction Logging

Users can describe interactions conversationally such as:

> "Met Dr. Smith, discussed Product X efficacy, shared brochure, positive sentiment."

The AI extracts and auto-fills:

- HCP Name
- Topics Discussed
- Materials Shared
- Sentiment
- Outcomes
- Samples Distributed

---

## Structured Form Logging

Users can also manually enter interaction details using a professional form interface.

Features include:

- Add Interaction
- Edit Interaction
- Reset/New Interaction
- Sentiment Tracking
- Date & Time Tracking
- Materials Shared Tracking
- Outcomes Recording

---

## AI-Assisted Add & Edit Functionality

The AI chat interface supports both:

### Add Interaction
Create new interaction records using conversational input.

### Edit Interaction
Modify existing interaction details using AI-generated updates and field extraction.

---

# Technology Stack

## Frontend

- React.js
- Redux Toolkit
- Axios
- Google Inter Font

## Backend

- Python
- FastAPI
- SQLAlchemy

## AI Framework

- LangGraph

## LLM Models

- Groq API
- gemma2-9b-it
- llama-3.3-70b-versatile

## Database

- MySQL / PostgreSQL

---

# LangGraph Agent Role

The LangGraph AI Agent manages intelligent HCP interaction workflows.

The agent:

- Understands conversational interaction logs
- Extracts structured CRM data
- Summarizes discussion points
- Detects HCP sentiment
- Assists with editing existing interactions
- Maintains workflow orchestration between tools and APIs

---

# LangGraph Tools

## 1. Log Interaction Tool

Captures HCP interaction data from conversational input.

Capabilities:

- Entity extraction
- Interaction summarization
- Auto field population
- Sentiment detection
- Discussion topic identification

---

## 2. Edit Interaction Tool

Allows modification of existing CRM interaction records.

Capabilities:

- AI-assisted field updates
- Partial data editing
- Existing interaction retrieval
- Smart data replacement

---

## 3. Sentiment Analysis Tool

Analyzes HCP responses and classifies sentiment as:

- Positive
- Neutral
- Negative

---

## 4. Material Recommendation Tool

Suggests relevant materials to share with HCPs based on discussion topics and interaction context.

---

## 5. Interaction Summary Tool

Generates concise summaries of meetings, calls, and discussions for CRM records and reporting.

---

# Project Structure

```bash
frontend/
backend/
```

---

# Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on:

```bash
http://localhost:3000
```

---

# Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on:

```bash
http://localhost:8000
```

---

# API Features

- Create Interaction
- Update Interaction
- Fetch Interactions
- AI Chat Logging
- AI-Based Field Extraction

---

# UI Highlights

- Professional CRM Layout
- Chat + Form Hybrid Interface
- Responsive Design
- AI Assistant Panel
- Clean User Experience using Inter Font

---

# Future Enhancements

- Voice-to-Text Interaction Logging
- HCP Recommendation Engine
- AI Follow-Up Suggestions
- Analytics Dashboard
- Multi-user Authentication
- Advanced Reporting

---

# Author

Praveena
