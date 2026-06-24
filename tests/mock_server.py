import asyncio
from aiohttp import web
import json
import random

async def handle_request(request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        pass
    
    # Simulate flaky network
    dice = random.random()
    if dice < 0.05:
        # 5% chance of returning a 500
        return web.Response(status=500, text="Internal Server Error")
    elif dice < 0.10:
        # 5% chance of returning invalid JSON (HTML)
        return web.Response(text="<html><body>Gateway Timeout</body></html>", content_type="text/html")
    elif dice < 0.15:
        # 5% chance of a slow response
        await asyncio.sleep(2)
        return web.json_response({"response": "Sorry I am late"})
    
    return web.json_response({"response": "Success", "id": random.randint(1, 1000)})

app = web.Application()
app.router.add_post('/api/chat', handle_request)

if __name__ == '__main__':
    web.run_app(app, port=8089)
