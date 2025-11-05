# Example Key Files

This directory shows the structure of key files that ESP expects.
Create your actual key files here with your real API keys.

## File Structure

```
~/Documents/GitHub/keys/
├── google_service.json
├── vertex_key.json
└── backup_keys.json
```

## Example Formats

### google_service.json
```json
{
  "api_key": "your-google-api-key-here",
  "project_id": "your-project-id",
  "client_email": "your-service-account@project.iam.gserviceaccount.com"
}
```

### vertex_key.json
```json
{
  "api_key": "your-vertex-api-key-here",
  "project_id": "your-project-id",
  "region": "us-central1"
}
```

### backup_keys.json
```json
{
  "api_key": "your-backup-api-key-here",
  "provider": "backup-provider"
}
```

## Security Notes

- **NEVER** commit actual API keys to version control
- Keep key files in secure locations with restricted permissions
- Use environment variables for the most sensitive keys
- Rotate keys regularly
