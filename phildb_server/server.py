import argparse

import tornado.httpserver
import tornado.ioloop
import tornado.web

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import logging
logger = logging.getLogger(__name__)

from phildb.database import PhilDB

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        output = "<ul>"
        for ts in self.db.ts_list():
            output += '<li><a href="/{0}">{0}<a></li>'.format(ts)
        output += "</ul>"

        self.write(output)

class ListHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, list_type, ftype):

        kwargs = {}
        for kwarg in ['source', 'measurand']:
            kwargs[kwarg] = self.get_argument(kwarg, None)

        callback = self.get_argument('callback', None)

        if list_type == 'timeseries':
            _list = self.db.ts_list(**kwargs)
        elif list_type == 'sources':
            _list = self.db.list_sources()
        elif list_type == 'measurands':
            _list = self.db.list_measurands()

        logger.debug(_list)
        if ftype == 'json':
            json_data = json.dumps(_list)
            if callback:
                json_data = "{0}({1});".format(callback, json_data)
                self.set_header("Content-type",  "application/javascript")
            else:
                self.set_header("Content-type",  "application/json")

            self.write(json_data)
        elif ftype == 'csv':
            csv_output = StringIO()
            for ts_id in _list:
                csv_output.write(ts_id)
                csv_output.write('\n')
            self.set_header("Content-type",  "text/csv")
            self.write(csv_output.getvalue())
        elif ftype == 'msgpack':
            msg_data = pd.Series(_list).to_msgpack()
            self.write(msg_data)
        else:
            raise NotImplementedError("Unsupported format {0}".format(ftype))

class TimeseriesInstanceHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, ftype):

        kwargs = {}
        for kwarg in ['source', 'measurand']:
            kwargs[kwarg] = self.get_argument(kwarg, None)

        callback = self.get_argument('callback', None)

        _list = self.db.list_timeseries_instances(**kwargs)

        if ftype == 'json':
            json_data = _list.to_json(orient = 'records')
            if callback:
                json_data = "{0}({1});".format(callback, json_data)
                self.set_header("Content-type",  "application/javascript")
            else:
                self.set_header("Content-type",  "application/json")

            self.write(json_data)

        elif ftype == 'msgpack':
            msg_data = _list.to_msgpack(orient = 'records')
            self.write(msg_data)

        elif ftype == 'csv':
            csv_output = StringIO()
            for row in _list.iterrows():
                csv_output.write(','.join(row[1].values))
                csv_output.write('\n')
            self.set_header("Content-type",  "text/csv")
            self.write(csv_output.getvalue())
        else:
            raise NotImplementedError("Unsupported format {0}".format(ftype))

class TimeseriesHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, ts_id, ftype = None):

        instances = self.db.list_timeseries_instances(timeseries=ts_id)

        callback = self.get_argument('callback', None)
        if ftype == 'json':
            json_data = instances.to_json(date_format='iso')
            if callback:
                json_data = "{0}({1});".format(callback, json_data)
                self.set_header("Content-type",  "application/javascript")
            else:
                self.set_header("Content-type",  "application/json")

            self.write(json_data)
            return

        elif ftype == 'msgpack':
            msg_data = instances.to_msgpack()
            self.write(msg_data)
            return

        elif ftype == 'csv':
            csv_output = StringIO()
            instances.to_csv(csv_output)
            self.set_header("Content-type",  "text/csv")
            self.write(csv_output.getvalue())
            return
        else:
            output = "<h1>{0}</h1>\n".format(ts_id)

            for instance in instances.to_dict('records'):
                output += "<h2>Frequency: {freq}, Measurand: {measurand}, Source: {source}</h2>\n".format(**instance)
                output += '<img src="plot/{ts_id}/{freq}?measurand={measurand}&amp;source={source}"/>\n'.format(**instance)

            self.write(output)

class ReadAllHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, freq, ftype):

        logger.debug("Called ReadAllHandler.get()")

        kwargs = {}
        for kwarg in ['source', 'measurand']:
            kwargs[kwarg] = self.get_argument(kwarg, None)

        kwargs['excludes'] = self.get_query_arguments('excludes')

        callback = self.get_argument('callback', None)

        logger.debug(kwargs)
        data = self.db.read_all(freq, **kwargs)

        if ftype == 'json':
            json_data = data.to_json(date_format='iso')
            if callback:
                json_data = "{0}({1});".format(callback, json_data)
                self.set_header("Content-type",  "application/javascript")
            else:
                self.set_header("Content-type",  "application/json")

            self.write(json_data)

        elif ftype == 'msgpack':
            msg_data = data.to_msgpack()
            self.write(msg_data)

        elif ftype == 'csv':
            csv_output = StringIO()
            data.to_csv(csv_output)
            self.set_header("Content-type",  "text/csv")
            self.write(csv_output.getvalue())
        else:
            raise NotImplementedError("Unsupported format {0}".format(ftype))

class ReadHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, ts_id, freq, ftype):

        kwargs = {}
        for kwarg in ['source', 'measurand']:
            kwargs[kwarg] = self.get_argument(kwarg, None)

        callback = self.get_argument('callback', None)

        data = self.db.read(ts_id, freq, **kwargs)

        if ftype == 'json':
            json_data = data.to_json(date_format='iso')
            if callback:
                json_data = "{0}({1});".format(callback, json_data)
                self.set_header("Content-type",  "application/javascript")
            else:
                self.set_header("Content-type",  "application/json")

            self.write(json_data)

        elif ftype == 'msgpack':
            msg_data = data.to_msgpack()
            self.write(msg_data)
            return


        elif ftype == 'csv':
            csv_output = StringIO()
            data.to_csv(csv_output)
            self.set_header("Content-type",  "text/csv")
            self.write(csv_output.getvalue())
        else:
            raise NotImplementedError("Unsupported format {0}".format(ftype))

class PlotHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, ts_id, freq):

        kwargs = {}
        for kwarg in ['source', 'measurand']:
            kwargs[kwarg] = self.get_argument(kwarg, None)

        data = self.db.read(ts_id, freq, **kwargs)
        fig = plt.Figure()
        ax = fig.add_subplot(111)

        data.plot(ax=ax, drawstyle = 'steps-mid')
        fig.set_tight_layout(True)

        canvas = FigureCanvas(fig)

        png_output = StringIO()
        canvas.print_png(png_output)
        self.write(png_output.getvalue())
        self.set_header("Content-type",  "image/png")

def main():
    logging.basicConfig(format = "%(asctime)s:%(levelname)s:%(message)s")
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description='Run tsdb server instance.')
    parser.add_argument('PhilDB', type=str,
                        help='PhilDB to run the server for.')
    parser.add_argument('--port', type=str,
                        default = 8888,
                        help='Set port to run the server on. Default: 8888')
    parser.add_argument('--processes', type=str,
                        default = 0,
                        help='Number of processes to run, defaults to zero which means use all available CPUs.')
    parser.add_argument('--debug',
                        action='store_true',
                        help='PhilDB to run the server for.')

    args = parser.parse_args()
    num_processes = args.processes

    db_dict = dict(db = PhilDB(args.PhilDB))
    application = tornado.web.Application([
            (r"/", MainHandler, db_dict),
            (r"/favicon.ico", MainHandler, db_dict),
            (r"/plot/(.+)/(.+)", PlotHandler, db_dict),
            (r"/list/timeseries_instances\.(json|csv|msgpack)", TimeseriesInstanceHandler, db_dict),
            (r"/list/(.+)\.(json|csv|msgpack)", ListHandler, db_dict),
            (r"/read_all/(.+)\.(json|csv|msgpack)", ReadAllHandler, db_dict),
            (r"/(.+)/(.+)\.(json|csv|msgpack)", ReadHandler, db_dict),
            (r"/(.+)\.(json|csv|msgpack)?", TimeseriesHandler, db_dict),
            (r"/(.+)", TimeseriesHandler, db_dict),
        ],
        compress_response = True,
        debug = args.debug,
    )

    if args.debug:
        # Can only have a single process when running tornado in debug mode.
        num_processes = 1

        logger.setLevel(logging.DEBUG)
        logger.debug("Running debug mode with a single process.")

    logger.info("Starting PhilDB server on port {0}".format(args.port))
    server = tornado.httpserver.HTTPServer(application)
    server.bind(args.port)
    server.start(num_processes)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
