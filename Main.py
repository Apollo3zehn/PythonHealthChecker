import argparse
import asyncio
import logging
import os
import pathlib
import sys
from logging import Logger
from threading import Thread
from typing import Dict

import cherrypy

from src import Utils
from src.BaseTypes import CheckResult
from src.ConfigReader import ConfigReader
from src.HealthChecker import HealthChecker
from src.HtmlWriter import HtmlWriter
from src.NotifyManager import NotifyManager
from src.Web import API, Application


async def HealthCheck(configFilePath: str, checkInterval: int, refreshInterval: int, cache: Dict[str, CheckResult], logger: Logger):

    folderPath = Utils.PrepareLocalAppdata()
    htmlFilePath = os.path.join(folderPath, "index.html")
    htmlWriter = HtmlWriter(htmlFilePath, refreshInterval)

    while True:

        try:

            logger.info("Load config.")
            config = ConfigReader().Read(configFilePath)

            logger.info("Load extensions.")
            extensions = Utils.LoadExtensions()

            logger.info("Check health.")
            healthChecker = HealthChecker(config, extensions, cache, logger)
            result = await healthChecker.CheckHealthAsync()

            logger.info("Throttle notifications.")
            filteredResult = Utils.ThrottleNotifications(result)

            logger.info("Notify.")
            notifyManager = NotifyManager(config, extensions, logger)
            await notifyManager.NotifyAsync(filteredResult)

            logger.info("Update html.")
            htmlWriter.WriteResult(result)
            
        except Exception as ex:
            logger.error(msg=str(ex), exc_info=ex)

        await asyncio.sleep(checkInterval)

def handle_error():
    from cherrypy import _cperror
    cherrypy.response.status = 500
    cherrypy.response.body = [
        f"<html><body>{_cperror.format_exc()}</body></html>"
    ]

def Serve(host: str, port: int, cache: Dict[str, CheckResult], logger: Logger):

    # mount "/"
    folderPath = Utils.PrepareLocalAppdata()
    htmlFilePath = os.path.join(folderPath, "index.html")

    appConfig = {
        "/": {
            "tools.staticdir.root": os.path.abspath(os.getcwd())
        },
        "/static": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "./src/wwwroot/"
        }
    }
 
    cherrypy.tree.mount(Application(htmlFilePath), "/", appConfig)

    # mount "/api/checkresult"
    apiConfig = {
        "/": {
            # the api uses restful method dispatching
            "tools.encode.on": True,
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            'request.error_response': handle_error
        }   
    }

    cherrypy.tree.mount(API(cache, logger), "/api/checkresults", apiConfig)

    # run
    logger.info(f"Starting web server on address {host}:{port}.")

    cherrypy.config.update({
        "engine.autoreload.on" : False,
        "log.screen": False,
        "server.socket_host": host,
        "server.socket_port": port
    })
    cherrypy.engine.start()
    cherrypy.engine.block()

async def Main():

    os.chdir(pathlib.Path(__file__).parent.absolute())

    parser = argparse.ArgumentParser()

    parser.add_argument("--config", type=str, default="testconfig.conf", help="The default config file is testconfig.conf.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="The default host is 127.0.0.1")
    parser.add_argument("--port", type=int, default=80, help="The default port is 80.")
    parser.add_argument("--check-interval", type=int, default=60, help="The check interval in seconds. Default is 60s.")
    parser.add_argument("--refresh-interval", type=int, default=15, help="The page refresh interval in seconds. Default is 15s.")

    args = parser.parse_args()

    # logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Health Checker")

    # exception handling
    def global_except_hook(exctype, value, traceback):
        logger.error("An unhandled exception occured.", exc_info=value)
        sys.__excepthook__(exctype, value, traceback)

    sys.excepthook = global_except_hook

    # create check result cache
    cache = {}

    # run web server
    thread = Thread(target=Serve, args=(args.host, args.port, cache, logger,))
    thread.start()

    # run health checks
    await HealthCheck(args.config, args.check_interval, args.refresh_interval, cache, logger)
    
# run main task
asyncio.run(Main())
