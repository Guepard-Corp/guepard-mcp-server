# Guepard Deployment Server

This project provides a lightweight MCP-compatible server to list deployments from Supabase for the Guepard platform. It is designed to integrate with an MCP-based environment using VS Code or similar tooling.

## 📦 Project Structure
```
guepard/
├── GUEPARD-MCP-SERVER/
│ ├── list_db.py # Script to authenticate with Supabase and list deployments
│ └── venv/ # Virtual environment for dependencies
├── .vscode/
│ └── settings.json # VS Code settings for MCP servers
└── README.md # Project documentation
```

## 🚀 Features

- Lists deployments.
- Integrates into local environments via MCP (Multi Command Process).
- Supports launching from VS Code using a simple MCP configuration.
- Create a new Database
- Create a new Branch
- Create a new Snapshot (Still existing some error from API)
- Checkout Branch
- Start Compute
- Stop Compute


## 🛠 Requirements

- Python 3.8+
- Guepard Credentials

## 🔧 Setup

1. **Create a Virtual Environment**:

   ```bash
   cd guepard/GUEPARD-MCP-SERVER
   python3 -m venv venv
   source venv/bin/activate

2. **Test MCP SERVER**:
    ```json
   {
   "mcp": {
     "servers": {
       "guepard-deployment": {
         "command": "/full/path/to/venv/bin/python",
         "args": ["/full/path/to/list_db.py"],
         "env": {"access_token":"<your access token here>"}
       }
     }
    }
   }
```