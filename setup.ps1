param(
    [string]$Action = "all"
)

function Start-Database {
    Write-Host "Starting PostgreSQL via Docker..." -ForegroundColor Cyan
    docker compose up -d
    if ($?) {
        Write-Host "PostgreSQL is running on port 5432" -ForegroundColor Green
    } else {
        Write-Host "Failed to start PostgreSQL. Is Docker running?" -ForegroundColor Red
        exit 1
    }
}

function Install-Deps {
    Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
    python -m pip install -r requirements.txt
}

function Run-Migrations {
    param([string]$Env = ".env")
    Write-Host "Running database migrations..." -ForegroundColor Cyan
    python manage.py migrate --settings=config.settings
    if ($?) {
        Write-Host "Migrations complete" -ForegroundColor Green
    } else {
        Write-Host "Migration failed. Check your .env file." -ForegroundColor Red
        exit 1
    }
}

function Create-Superuser {
    Write-Host "Creating superuser..." -ForegroundColor Cyan
    python manage.py createsuperuser --settings=config.settings
}

function Start-Server {
    Write-Host "Starting development server on http://localhost:8000" -ForegroundColor Cyan
    python manage.py runserver --settings=config.settings
}

switch ($Action) {
    "db" { Start-Database }
    "migrate" { Run-Migrations }
    "superuser" { Create-Superuser }
    "run" { Start-Server }
    "all" {
        if (-not (Test-Path ".env")) {
            Write-Host "Copying .env.example to .env - edit it first!" -ForegroundColor Yellow
            Copy-Item ".env.example" ".env"
            Write-Host "Open .env and set SECRET_KEY, DB_NAME, DB_USER, DB_PASSWORD" -ForegroundColor Yellow
            exit 0
        }
        Install-Deps
        Start-Database
        Start-Sleep -Seconds 3
        Run-Migrations
        Create-Superuser
        Start-Server
    }
    default {
        Write-Host "Usage: .\setup.ps1 [db|migrate|superuser|run|all]" -ForegroundColor Yellow
    }
}
