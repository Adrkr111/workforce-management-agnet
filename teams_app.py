#!/usr/bin/env python3
"""
Teams App Server for Workforce Management Bot
Main application server that hosts the Teams bot integration
"""

import os
import sys
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    UserState,
    MemoryStorage
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

# Import the Teams bot
from teams_bot import WorkforceManagementBot

class TeamsAppServer:
    """Teams App Server for Workforce Management Bot"""
    
    def __init__(self):
        # Load configuration from environment
        self.app_id = os.environ.get("MicrosoftAppId", "")
        self.app_password = os.environ.get("MicrosoftAppPassword", "")
        self.port = int(os.environ.get("PORT", 3978))
        
        # Create Bot Framework adapter
        settings = BotFrameworkAdapterSettings(
            app_id=self.app_id,
            app_password=self.app_password
        )
        self.adapter = BotFrameworkAdapter(settings)
        
        # Error handler for the adapter
        async def on_error(context, error):
            print(f"❌ Bot Framework Error: {error}")
            # Send error message to user
            await context.send_activity("Sorry, an error occurred. Please try again.")
        
        self.adapter.on_turn_error = on_error
        
        # Create storage and state management
        memory_storage = MemoryStorage()
        self.conversation_state = ConversationState(memory_storage)
        self.user_state = UserState(memory_storage)
        
        # Create the bot instance
        self.bot = WorkforceManagementBot(
            self.conversation_state, 
            self.user_state
        )
        
        # Create the web application
        self.app = web.Application(middlewares=[aiohttp_error_middleware])
        self.app.router.add_post("/api/messages", self.messages_handler)
        self.app.router.add_get("/", self.health_check)
        self.app.router.add_get("/health", self.health_check)
        
        print(f"🚀 Teams App Server initialized")
        print(f"📱 App ID: {self.app_id or 'Not configured'}")
        print(f"🌐 Port: {self.port}")

    async def messages_handler(self, request: Request) -> Response:
        """
        Handle incoming messages from Teams
        """
        try:
            # Parse the incoming activity
            if "application/json" in request.headers["Content-Type"]:
                body = await request.json()
            else:
                return Response(status=415, text="Unsupported Media Type")
            
            # Create activity from the request
            activity = Activity().deserialize(body)
            
            # Get authentication header
            auth_header = request.headers.get("Authorization", "")
            
            # Process the activity with the bot
            response = await self.adapter.process_activity(
                activity, 
                auth_header, 
                self.bot.on_turn
            )
            
            if response:
                return json_response(data=response.body, status=response.status)
            return Response(status=200)
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            return Response(status=500, text=str(e))

    async def health_check(self, request: Request) -> Response:
        """Health check endpoint"""
        health_data = {
            "status": "healthy",
            "service": "Workforce Management Teams Bot",
            "version": "2.0.0",
            "app_id": self.app_id or "not_configured",
            "agents_loaded": len(self.bot.agents) if hasattr(self.bot, 'agents') else 0
        }
        return json_response(health_data)

    def run(self):
        """Start the Teams app server"""
        try:
            print(f"\n🎉 Starting Workforce Management Teams Bot Server")
            print(f"🌐 Listening on http://localhost:{self.port}")
            print(f"📨 Bot endpoint: http://localhost:{self.port}/api/messages")
            print(f"🔍 Health check: http://localhost:{self.port}/health")
            print(f"\n💡 Next steps:")
            print(f"   1. Configure your Azure Bot Service endpoint to: http://localhost:{self.port}/api/messages")
            print(f"   2. Use ngrok for public endpoint: ngrok http {self.port}")
            print(f"   3. Update Azure Bot Service with ngrok URL")
            print(f"   4. Test in Teams!")
            
            web.run_app(self.app, host="localhost", port=self.port)
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create and run the server
    server = TeamsAppServer()
    server.run() 