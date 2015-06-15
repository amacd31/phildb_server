import argparse

import tornado.httpserver
import tornado.ioloop
import tornado.web

import StringIO

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from phildb.database import PhilDB

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        output = "<ul>"
        for ts in self.db.ts_list():
            output += '<li><a href="{0}">{0}<a></li>'.format(ts)
        output += "</ul>"

        self.write(output)

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

        elif ftype == 'csv':
            csv_output = StringIO.StringIO()
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

        elif ftype == 'csv':
            csv_output = StringIO.StringIO()
            data.to_csv(csv_output)
            self.set_header("Content-type",  "text/csv")
            self.write(csv_output.getvalue())

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

        png_output = StringIO.StringIO()
        canvas.print_png(png_output)
        self.write(png_output.getvalue())
        self.set_header("Content-type",  "image/png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run tsdb server instance.')
    parser.add_argument('PhilDB', type=str,
                        help='PhilDB to run the server for.')
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
            (r"/plot/(.+)/(.+)", PlotHandler, db_dict),
            (r"/(.+)/(.+)\.(json|csv)", ReadHandler, db_dict),
            (r"/(.+)\.(json|csv)?", TimeseriesHandler, db_dict),
            (r"/(.+)", TimeseriesHandler, db_dict),
        ],
        compress_response = True,
        debug = args.debug,
    )

    if args.debug:
        # Can only have a single process when running tornado in debug mode.
        num_processes = 1

    server = tornado.httpserver.HTTPServer(application)
    server.bind(8888)
    server.start(num_processes)
    tornado.ioloop.IOLoop.current().start()