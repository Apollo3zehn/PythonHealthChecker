import asyncio
import os
from threading import Thread

import cherrypy

from HealthChecker import HealthChecker
from HtmlWriter import HtmlWriter
from Web import Controller


async def HealthCheck():
    htmlWriter = HtmlWriter("./src/wwwroot")

    while True:

        try:
            healthChecker = HealthChecker("config")
            result = await healthChecker.CheckHealthAsync()
            htmlWriter.WriteResult(result)
        except Exception as ex:
            print(ex)

        await asyncio.sleep(10)

def Serve():
    # settings
    host = "0.0.0.0"
    port = 8080

    # configure CherryPy
    config = {
        "global": {
            "engine.autoreload.on" : False,
            "log.screen": False,
            "server.socket_host": host,
            "server.socket_port": port
        },
        "/": {
            "tools.staticdir.root": os.path.abspath(os.getcwd())
        },
        "/static": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "./src/wwwroot/"
        }
    }
    
    print(f"Starting web server on address {host}:{port}.")
    cherrypy.quickstart(Controller(), "/", config)

async def Main():

    # run web server
    thread = Thread(target = Serve)
    thread.start()

    # run health checks
    await HealthCheck()
    
# run main task
asyncio.run(Main())
