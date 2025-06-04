#!/usr/bin/env python3
"""
Enterprise Workforce Management System - Database Setup
Initializes ChromaDB collections for the multi-agent system
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from vector_database.chroma import get_chroma_client
    from config import llm_config
    print("✅ Successfully imported project modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

def setup_collections():
    """Initialize ChromaDB collections for the workforce management system"""
    
    print("\n🏢 Enterprise Workforce Management System - Database Setup")
    print("=" * 60)
    
    try:
        # Get ChromaDB client
        print("\n📊 Connecting to ChromaDB...")
        client = get_chroma_client()
        print("✅ ChromaDB connection established")
        
        # List existing collections
        existing_collections = [col.name for col in client.list_collections()]
        print(f"📋 Existing collections: {existing_collections}")
        
        # Collection configurations
        collections_config = {
            "forecast_data": {
                "description": "Workforce volume forecasting data with business metadata",
                "metadata": {
                    "type": "forecast",
                    "description": "Contains workforce volume predictions with business unit, substream, and team hierarchies",
                    "hnsw:space": "cosine",
                    "created_date": datetime.now().isoformat()
                }
            },
            "kpi_data": {
                "description": "Performance metrics and KPI data",
                "metadata": {
                    "type": "kpi",
                    "description": "Historical and current KPI metrics across departments and teams",
                    "hnsw:space": "cosine",
                    "created_date": datetime.now().isoformat()
                }
            }
        }
        
        # Create or verify collections
        for collection_name, config in collections_config.items():
            print(f"\n🔧 Setting up collection: {collection_name}")
            
            try:
                if collection_name in existing_collections:
                    collection = client.get_collection(name=collection_name)
                    count = collection.count()
                    print(f"✅ Collection '{collection_name}' already exists with {count} documents")
                else:
                    collection = client.create_collection(
                        name=collection_name,
                        metadata=config["metadata"]
                    )
                    print(f"✅ Created new collection: {collection_name}")
                    
                # Verify collection accessibility
                try:
                    collection.peek()
                    print(f"✅ Collection '{collection_name}' is accessible")
                except Exception as e:
                    print(f"⚠️  Collection access test failed: {e}")
                    
            except Exception as e:
                print(f"❌ Error setting up collection '{collection_name}': {e}")
                return False
        
        print(f"\n🎉 Database setup completed successfully!")
        print(f"📍 ChromaDB location: Check your configuration in config.py")
        print(f"🔧 Collections ready for multi-agent system")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print(f"💡 Troubleshooting tips:")
        print(f"   - Check ChromaDB installation: pip install chromadb")
        print(f"   - Verify configuration in config.py")
        print(f"   - Ensure write permissions to database directory")
        return False

def verify_system_requirements():
    """Verify that all system requirements are met"""
    
    print("\n🔍 Verifying System Requirements...")
    print("-" * 40)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 12):
        print("⚠️  Warning: Python 3.12+ recommended for optimal performance")
    else:
        print("✅ Python version requirement met")
    
    # Check key dependencies
    required_modules = [
        'chromadb',
        'chainlit', 
        'plotly',
        'autogen',
        'google.generativeai'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing dependencies: {', '.join(missing_modules)}")
        print("📦 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All system requirements verified")
    return True

def main():
    """Main setup function"""
    
    print("🚀 Starting Enterprise Workforce Management System Setup...")
    
    # Verify requirements
    if not verify_system_requirements():
        print("\n❌ System requirements not met. Please install missing dependencies.")
        sys.exit(1)
    
    # Setup database
    if not setup_collections():
        print("\n❌ Database setup failed. Please check the error messages above.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎯 SETUP COMPLETE!")
    print("🏢 Enterprise Workforce Management System is ready!")
    print("\n🚀 Next steps:")
    print("   1. Configure your Google Gemini API key in .env file")
    print("   2. Run: chainlit run app.py --port 8270")
    print("   3. Access: http://localhost:8270")
    print("\n📚 Documentation: See README.md for detailed usage guide")
    print("=" * 60)

if __name__ == "__main__":
    main() 