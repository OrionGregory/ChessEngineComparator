Setting Up Celery for ChessEngineComparator
This document explains how to set up and run the Celery worker for background task processing.

Installation Requirements
First, install the necessary Python packages:

Redis Setup
Redis is required as the message broker for Celery:

Running the Celery Worker
Start the Celery worker process with:

This will launch the worker that processes background tasks for chess engine comparisons.