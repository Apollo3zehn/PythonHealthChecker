import argparse
import asyncio
import os
import sys
from threading import Thread

import cherrypy

from src import Utils
from src.ConfigReader import ConfigReader
from src.HealthChecker import HealthChecker
from src.HtmlWriter import HtmlWriter
from src.NotifyManager import NotifyManager
from src.Web import Controller


async def HealthCheck(configFilePath):

    folderPath = Utils.PrepareLocalAppdata()
    htmlFilePath = os.path.join(folderPath, "index.html")
    htmlWriter = HtmlWriter(htmlFilePath)

    while True:

        try:
            # load config
            config = ConfigReader().Read(configFilePath)

            # load extensions
            extensions = Utils.LoadExtensions()

            # check health
            healthChecker = HealthChecker(config, extensions)
            result = await healthChecker.CheckHealthAsync()

            # throttle notifications
            filteredResult = Utils.ThrottleNotifications(result)

            # notify
            notifyManager = NotifyManager(config, extensions)
            await notifyManager.NotifyAsync(filteredResult)

            # update html
            htmlWriter.WriteResult(result)
        except Exception as ex:
            print(ex)

        await asyncio.sleep(10)

def Serve(host: str, port: int):

    # configure CherryPy
    folderPath = Utils.PrepareLocalAppdata()
    htmlFilePath = os.path.join(folderPath, "index.html")

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
    cherrypy.quickstart(Controller(htmlFilePath), "/", config)

async def Main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--config", type=str, default="testconfig.conf", help="The default config file is testconfig.conf.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="The default host is 127.0.0.1")
    parser.add_argument("--port", type=int, default=80, help="The default port is 80.")

    args = parser.parse_args()

    # run web server
    thread = Thread(target = Serve, args=(args.host, args.port,))
    thread.start()

    # run health checks
    await HealthCheck(args.config)
    
# run main task
asyncio.run(Main())
