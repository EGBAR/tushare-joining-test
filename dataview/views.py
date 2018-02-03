from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from util.http_response import response_json
import random
from django.views.decorators.gzip import gzip_page
from psycopg2.pool import ThreadedConnectionPool
import datetime

conn_pool = ThreadedConnectionPool(
    minconn=4, maxconn=32,
    dbname="stockdata",
    user="tusharer", password="tushare@979323",
    host="postgresql.lovezhangbei.top", port=15432
)


def randomly_fail(fail_ratio: float = 0.1, message: str = "Failed caused by random ratio"):
    assert 0 <= fail_ratio <= 1, "Invalid fail ratio"

    def wrapper(func):
        def wrapper_inner(request):
            lucky_value = random.random()
            if lucky_value < fail_ratio:
                raise Exception(message + "{}<{}".format(lucky_value, fail_ratio))
            else:
                return func(request)

        return wrapper_inner

    return wrapper


@gzip_page
@response_json
@randomly_fail(0.1, "Failed caused by unknown reason ^_^")
def query_data(request: HttpRequest):
    code = int(request.GET["code"])
    conn = conn_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT code, tick, volume, open, close, high, low FROM public.stock_daily_tick WHERE code='%06d' and tick>='2017-12-01' and tick<='2017-12-31'" % code
        )
        data = [{
            "tick": row[1].strftime("%Y-%m-%d"),
            "volume": row[2],
            "open": row[3],
            "close": row[4],
            "high": row[5],
            "low": row[6]
        } for row in cursor.fetchall()]
        cursor.close()

        return {
            "status": "success",
            "data": data,
            "code": "%06d" % code
        }
    finally:
        conn_pool.putconn(conn)


@gzip_page
@response_json
def query_all_code(request: HttpRequest):
    conn = conn_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT distinct code FROM public.stock_daily_tick WHERE tick>='2017-12-01' and tick<='2017-12-31'")
        data = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return {
            "status": "success",
            "codes": data
        }
    finally:
        conn_pool.putconn(conn)


def index_page(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")
