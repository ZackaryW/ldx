# LDX Server Client CLI

Command-line interface for interacting with the LDX scheduler server.

## Installation

```bash
# Install with client dependencies
pip install ldx[ldx-client]

# Or with uv
uv pip install -e .[ldx-client]
```

## Usage

### General Options

```bash
ldx-client --help
ldx-client --server http://remote-server:5000 <command>
```

### Commands

#### 1. Register a Job

Register a job from a TOML config file.

```bash
# Register with auto-generated job_id (from filename)
ldx-client register my_automation.toml

# Register with custom job_id
ldx-client register my_automation.toml --job-id custom_name

# Replace existing job
ldx-client register my_automation.toml --replace
```

**If config has `[schedule]` section**: Job is scheduled automatically  
**If no `[schedule]` section**: Job is registered as on-demand (trigger manually)

#### 2. Trigger On-Demand Job

Execute a registered on-demand job immediately.

```bash
ldx-client trigger my_job
```

#### 3. List Jobs

```bash
# List all jobs with status
ldx-client list jobs

# List currently running jobs
ldx-client list active

# List registered jobs
ldx-client list registry

# Filter registry
ldx-client list registry --type scheduled
ldx-client list registry --type on_demand
```

#### 4. Get Job Status

```bash
ldx-client status my_job
```

Shows execution status, start time, end time, errors, etc.

#### 5. Get Job Info

```bash
ldx-client info my_job
```

Shows registry information: config, schedule, execution count, last triggered, etc.

#### 6. Cancel Job

Cancel a scheduled job (cannot cancel running jobs).

```bash
ldx-client cancel my_job
```

#### 7. Unregister Job

Remove a job from registry (also cancels if scheduled).

```bash
ldx-client unregister my_job
```

#### 8. Health Check

Check if server is running.

```bash
ldx-client health
```

## Example Workflow

### Register and Trigger On-Demand Job

```bash
# 1. Create config file
cat > my_job.toml << EOF
[ld]
name = "MyEmulator"
pkg = "com.example.app"

[lifetime]
lifetime = 3600
EOF

# 2. Register job (no schedule = on-demand)
ldx-client register my_job.toml

# 3. Trigger when needed
ldx-client trigger my_job

# 4. Check status
ldx-client status my_job_20251022_143015

# 5. View execution history
ldx-client info my_job
```

### Register Scheduled Job

```bash
# 1. Create config with schedule
cat > daily_task.toml << EOF
[ld]
name = "DailyEmulator"

[lifetime]
lifetime = 1800

[schedule]
trigger = "cron"
hour = 10
minute = 30
EOF

# 2. Register (automatically scheduled)
ldx-client register daily_task.toml

# 3. Check it's scheduled
ldx-client list registry --type scheduled

# 4. View next run time
ldx-client status daily_task
```

### Remote Server

```bash
# Connect to remote server
ldx-client --server http://remote-server:5000 list jobs

# Or set environment variable
export LDX_SERVER=http://remote-server:5000
ldx-client list jobs
```

## Output Format

All commands return JSON output with color coding:
- **Green**: Success
- **Red**: Error
- **Yellow**: Hints/warnings

Example output:

```json
{
  "job_id": "my_job",
  "status": "registered",
  "on_demand": true,
  "hint": "Trigger execution via POST /api/scheduler/jobs/my_job/trigger"
}
```

## Error Handling

```bash
# Job not found
ldx-client status nonexistent_job
# Error (404): Job 'nonexistent_job' not found

# Cannot cancel running job
ldx-client cancel running_job
# Error (400): Cannot cancel running job
# Hint: Running jobs cannot be stopped mid-execution

# Server not running
ldx-client health
# Request failed: Connection refused
```

## Tips

1. **Use `--replace`** to update existing jobs
2. **Check registry** before triggering to see execution history
3. **Use custom job_id** for better organization
4. **Remote connections** require server URL via `--server` flag
5. **Health check** first to verify server is running
