import chainlit as cl
from agents.data_visualization_agent import create_visualization
import asyncio

async def show_visualization():
    # Create the visualization
    data = 'date: 2025-06-01 volume: 2845, date: 2025-07-01 volume: 2843, date: 2025-08-01 volume: 2519, date: 2025-09-01 volume: 3499, date: 2025-10-01 volume: 3597, date: 2025-11-01 volume: 2780, date: 2025-12-01 volume: 3295, date: 2026-01-01 volume: 1921, date: 2026-02-01 volume: 3005, date: 2026-03-01 volume: 1144, date: 2026-04-01 volume: 2535, date: 2026-05-01 volume: 3758'
    result = create_visualization(data)
    
    if 'spec' in result:
        # Display the visualization
        await cl.Message(
            content="Here's the visualization of the forecast data:",
            elements=[cl.Plotly(result['spec'], name='forecast_viz')]
        ).send()
    else:
        await cl.Message(content=f"Error creating visualization: {result.get('error', 'Unknown error')}").send()

@cl.on_chat_start
async def start():
    await show_visualization() 