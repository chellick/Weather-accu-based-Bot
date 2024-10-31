from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from bot import bot, dp



def startup():
    app = web.Application()
    rq_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    rq_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    web.run_app(app=app, host="localhost", port=8080)


if __name__ == "__main__":
    startup()
    
