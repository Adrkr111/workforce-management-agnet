#!/bin/bash
# Teams Environment Export Script
# Usage: source export_teams_env.sh

echo "🔧 Setting Teams environment variables..."

# Export Teams App ID and Password
export TEAMS_APP_ID=21c8dd86-fc50-46c8-a368-5cd2a9519cf9
export TEAMS_APP_PASSWORD=LTj8Q~2oPpJUF4R8gKFLw7Ojjzwax_vRDxkzEah9

# Also set Microsoft App variables (for compatibility)
export MicrosoftAppId=$TEAMS_APP_ID
export MicrosoftAppPassword=$TEAMS_APP_PASSWORD

echo "✅ Teams environment variables exported:"
echo "   TEAMS_APP_ID=$TEAMS_APP_ID"
echo "   TEAMS_APP_PASSWORD=***hidden***"
echo "   MicrosoftAppId=$MicrosoftAppId"
echo "   MicrosoftAppPassword=***hidden***"
echo ""
echo "🚀 Ready to run Teams app:"
echo "   python run_teams_app.py"
echo "   OR"
echo "   chainlit run app_teams.py -h --port 8270" 