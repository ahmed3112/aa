# Cisco Switch Backup Tool (Ultra UI)

A polished web UI prototype for a **C# ASP.NET backup application** that targets Cisco switches.

## What it does

- Queue a backup job with Cisco connection details (IP, credentials, protocol, config type).
- Show a live API payload preview for `POST /api/backups`.
- Track backup history in browser storage.
- Download a generated `.cfg` file for each backup entry.

## Run locally

```bash
python3 -m http.server 4173
```

Open <http://localhost:4173>.

## Suggested C# backend contract

```csharp
app.MapPost("/api/backups", async (BackupRequest request, IBackupService svc) =>
{
    var result = await svc.RunCiscoBackupAsync(request);
    return Results.Ok(result);
});

public record BackupRequest(
    string DeviceName,
    string IpAddress,
    string Username,
    string Password,
    string EnableSecret,
    string Protocol,
    string ConfigType,
    string ScheduleType);
```

## Tests

```bash
node -c script.js
npm test
```
