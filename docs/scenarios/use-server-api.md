# LDX Server API Examples

## Overview

The LDX server automatically loads all `.toml` config files from `~/.ldx/runner/configs/` on startup:
- **Configs with `[schedule]` section**: Scheduled via APScheduler
- **Configs without `[schedule]`**: Ignored (use CLI mode instead)
- **Same configs work in both modes**: CLI runs immediately, server schedules

## Starting the Server

```bash
# Default (host=0.0.0.0, port=5000)
python -m ldx.ldx_server.server

# On startup, loads from ~/.ldx/runner/configs/
# Schedules all configs that have a [schedule] section

# Custom configuration
FLASK_HOST=localhost FLASK_PORT=8080 MAX_WORKERS=5 python -m ldx.ldx_server.server
```

## Config Directory Setup

Create configs in `~/.ldx/runner/configs/`:

```toml
# ~/.ldx/runner/configs/daily_task.toml
[ld]
name = "MyEmulator"
pkg = "com.example.app"

[lifetime]
lifetime = 3600

[schedule]  # This makes it scheduled on server startup
trigger = "cron"
hour = 10
minute = 30
```

**Without schedule section**: Config is ignored by server (use CLI)
**With schedule section**: Auto-scheduled on server startup

## API Endpoints

### 1. Register an On-Demand Job (No Schedule)

Jobs without a schedule are **registered** but not executed automatically.
They must be triggered manually via API.

```bash
curl -X POST http://localhost:5000/api/scheduler/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "on_demand_job",
    "config": {
      "ld": {
        "name": "MyEmulator",
        "pkg": "com.example.app"
      },
      "lifetime": {
        "lifetime": 3600
      }
    }
  }'
```

**Response:**
```json
{
  "job_id": "on_demand_job",
  "status": "registered",
  "on_demand": true,
  "hint": "Trigger execution via POST /api/scheduler/jobs/on_demand_job/trigger"
}
```

### 1b. Trigger an On-Demand Job

```bash
curl -X POST http://localhost:5000/api/scheduler/jobs/on_demand_job/trigger
```

**Response:**
```json
{
  "job_id": "on_demand_job",
  "execution_id": "on_demand_job_20251022_143015",
  "status": "triggered",
  "message": "Job 'on_demand_job' triggered for immediate execution"
}
```

### 2. Schedule a Job (With Cron Schedule)

```bash
curl -X POST http://localhost:5000/api/scheduler/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "daily_job",
    "config": {
      "ld": {
        "name": "MyEmulator",
        "pkg": "com.example.app"
      },
      "lifetime": {
        "lifetime": 1800
      }
    },
    "schedule": {
      "trigger": "cron",
      "hour": 10,
      "minute": 30
    }
  }'
```

**Response:**
```json
{
  "job_id": "daily_job",
  "status": "scheduled",
  "schedule": {
    "trigger": "cron",
    "hour": 10,
    "minute": 30,
    "second": 0,
    "day_of_week": "*"
  },
  "next_run": "2025-10-22T10:30:00"
}
```

### 3. Schedule a Job (With Interval)

```bash
curl -X POST http://localhost:5000/api/scheduler/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "recurring_job",
    "config": {
      "ld": {
        "name": "TestEmulator"
      }
    },
    "schedule": {
      "trigger": "interval",
      "interval_seconds": 3600
    }
  }'
```

**Response:**
```json
{
  "job_id": "recurring_job",
  "status": "scheduled",
  "schedule": {
    "trigger": "interval",
    "seconds": 3600
  },
  "next_run": "2025-10-22T11:30:00"
}
```

### 4. Check for Overlaps (Will Fail)

```bash
# This will fail if a job is already scheduled at 10:30
curl -X POST http://localhost:5000/api/scheduler/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "overlapping_job",
    "config": {
      "ld": {"name": "Test"}
    },
    "schedule": {
      "trigger": "cron",
      "hour": 10,
      "minute": 30
    }
  }'
```

**Response (Error):**
```json
{
  "error": "Schedule overlaps with existing jobs: Cron job 'daily_job' scheduled at same time"
}
```

### 5. List All Jobs

```bash
curl http://localhost:5000/api/scheduler/jobs
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "test_job_1",
      "status": "completed",
      "start_time": "2025-10-22T10:15:00",
      "end_time": "2025-10-22T10:20:00",
      "error": null,
      "plugin_count": 2,
      "scheduled": false
    },
    {
      "job_id": "daily_job",
      "status": "pending",
      "start_time": null,
      "end_time": null,
      "error": null,
      "plugin_count": 2,
      "next_run_time": "2025-10-22T10:30:00",
      "scheduled": true
    }
  ],
  "count": 2
}
```

### 6. List Active Jobs

```bash
curl http://localhost:5000/api/scheduler/jobs/active
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "currently_running_job",
      "status": "running",
      "start_time": "2025-10-22T10:25:00",
      "end_time": null,
      "error": null,
      "plugin_count": 2,
      "scheduled": true
    }
  ],
  "count": 1
}
```

### 7. Get Job Status

```bash
curl http://localhost:5000/api/scheduler/jobs/test_job_1
```

**Response:**
```json
{
  "job_id": "test_job_1",
  "status": "completed",
  "start_time": "2025-10-22T10:15:00",
  "end_time": "2025-10-22T10:20:00",
  "error": null,
  "plugin_count": 2,
  "scheduled": false
}
```

### 8. Cancel a Scheduled Job

```bash
curl -X DELETE http://localhost:5000/api/scheduler/jobs/daily_job
```

**Response:**
```json
{
  "message": "Job 'daily_job' cancelled successfully"
}
```

**Error Response (if running):**
```json
{
  "error": "Cannot cancel running job",
  "hint": "Running jobs cannot be stopped mid-execution"
}
```

### 9. Remove Completed Job

```bash
curl -X POST http://localhost:5000/api/scheduler/jobs/test_job_1/remove
```

**Response:**
```json
{
  "message": "Job 'test_job_1' removed successfully"
}
```

### 10. List Registry

List all registered jobs (both scheduled and on-demand).

```bash
# All jobs
curl http://localhost:5000/api/scheduler/registry

# Only scheduled jobs
curl http://localhost:5000/api/scheduler/registry?type=scheduled

# Only on-demand jobs
curl http://localhost:5000/api/scheduler/registry?type=on_demand
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "on_demand_job",
      "config": {...},
      "schedule": null,
      "source": "api",
      "registered_at": "2025-10-22T14:30:00",
      "last_triggered": "2025-10-22T14:35:00",
      "execution_count": 3
    },
    {
      "job_id": "daily_task",
      "config": {...},
      "schedule": {
        "trigger": "cron",
        "hour": 10,
        "minute": 30
      },
      "source": "config:daily_task.toml",
      "registered_at": "2025-10-22T10:00:00",
      "last_triggered": null,
      "execution_count": 0
    }
  ],
  "count": 2,
  "filter": "all"
}
```

### 11. Get Registry Entry

```bash
curl http://localhost:5000/api/scheduler/registry/on_demand_job
```

**Response:**
```json
{
  "job_id": "on_demand_job",
  "config": {...},
  "schedule": null,
  "source": "api",
  "registered_at": "2025-10-22T14:30:00",
  "last_triggered": "2025-10-22T14:35:00",
  "execution_count": 3
}
```

### 12. Unregister Job

Remove a job from registry (also cancels scheduled execution).

```bash
curl -X DELETE http://localhost:5000/api/scheduler/registry/on_demand_job
```

**Response:**
```json
{
  "message": "Job 'on_demand_job' unregistered successfully"
}
```

### 13. Health Check

```bash
curl http://localhost:5000/api/scheduler/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ldx-scheduler"
}
```

## Job Status Values

- `pending`: Job is scheduled but hasn't run yet
- `running`: Job is currently executing
- `completed`: Job finished successfully
- `failed`: Job encountered an error

## Error Handling

### Overlap Detection

The server prevents scheduling conflicts:
- **Cron overlaps**: Same hour/minute combination
- **Interval overlaps**: Warning if multiple interval jobs exist

### Job Constraints

- Cannot cancel running jobs
- Cannot remove active (pending/running) jobs
- Job IDs must be unique (unless `replace_existing: true`)

## Python Usage

```python
from ldx.ldx_server.server import create_app

# Create app
app = create_app(max_workers=5)

# Run server
app.run(host='0.0.0.0', port=5000)
```

## Integration with Webhooks

You can trigger job scheduling via webhooks:

```python
import requests

def on_webhook_event(event_data):
    response = requests.post(
        'http://localhost:5000/api/scheduler/jobs',
        json={
            'job_id': f'webhook_{event_data["id"]}',
            'config': {
                'ld': {'name': event_data['emulator']},
                'lifetime': {'lifetime': 600}
            }
        }
    )
    return response.json()
```
