#!/home/kchoi/anaconda2/bin/python
# Dedicated Worker checking poke status
# Structure:
# * Threaded running (check every 3 seconds)
#  - check who newly poked and save that stat into db
#  - poke back if that person is on poke war with the user.
# * Consume RabbitMQ message for actions (start poke war, end poke war)

# Imports:
from datetime import datetime
from threading import Thread, Event

import logging
import pymongo

from facebook_poke_manager import FacebookPokeManager
from pymongo import MongoClient
import pika
import shlex  # For Quoted String Split
import sys

db = MongoClient().pokewar

# DB Structure:
# db.curPokes
# db.pokeHistory


# ---Code Starts---
class RepeatThread(Thread):
    def __init__(self, event, wait_sec, fun):
        Thread.__init__(self)
        self.stopped = event
        self.wait_sec = wait_sec
        self.fun = fun
        fun()

    def run(self):
        while not self.stopped.wait(self.wait_sec):
            self.fun()


def process_poke_works():
    poker_data = pk.find_who_poked_and_poke_back(s_poke_back_group)
    datetime_now = datetime.now()
    # Save current pokes into db
    db.curPokes.update_one({'flag': 1},
                           {'$set': {'pokers': poker_data['pokers'], 'timestamp': datetime_now}}, upsert=True)
    # Save new pokes into db
    if len(poker_data['new_pokers']) > 0:
        bulk = db.pokeNewHistory.initialize_ordered_bulk_op()
        for str_name in poker_data['new_pokers']:
            bulk.insert({'name': str_name, 'timestamp': datetime_now})
        bulk.execute()
    # Save poke backs into db
    if len(poker_data['poked_back']) > 0:
        bulk = db.pokeBackHistory.initialize_ordered_bulk_op()
        for str_name in poker_data['poked_back']:
            bulk.find({'name': str_name}).upsert().update({'$addToSet': {'timestamp': datetime_now}})
        bulk.execute()

def ensure_mongodb_indices():
    db.pokeNewHistory.create_index([('name', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)], background=True)
    db.pokeNewHistory.create_index([('timestamp', pymongo.DESCENDING)], background=True)
    db.pokeBackHistory.create_index([('name', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)], background=True)
    db.pokeBackHistory.create_index([('timestamp', pymongo.DESCENDING)], background=True)

def init_logging():
    # Logging Setting
    new_logger = logging.getLogger('pokewar')
    new_logger.handlers = []
    new_logger.setLevel(level=logging.DEBUG)
    # Set Logger handle into the stream
    # create console handler and set level to debug
    for ch in [logging.StreamHandler(), logging.FileHandler(filename='pokewar.log')]:
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        new_logger.addHandler(ch)
    return new_logger

logger = init_logging()

# Initialize
ensure_mongodb_indices()
s_poke_back_group = set()
pk = FacebookPokeManager()

stopFlag = Event()
thread = RepeatThread(stopFlag, 3, process_poke_works)
thread.start()

# Todo: Change the behavior as messages arrive
# Todo: - update s_poke_back_group

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='poke_war')


def callback(ch, method, properties, body):
    global s_poke_back_group
    # Body Format:
    #  add "Zilla Go"
    #  remove "Zilla Go"
    # Use a standard parameter parser to handle the message
    args = shlex.split(body)
    logger.info(" [x] Received %r. Conducting the action." % body)
    try:
        if "add" == args[0]:
            s_poke_back_group |= {args[1]}
            logger.info("Current Poke Back Group: {}".format(s_poke_back_group))
        elif "remove" == args[0]:
            s_poke_back_group -= {args[1]}
            logger.info("Current Poke Back Group: {}".format(s_poke_back_group))
        elif "stop" == args[0]:
            stopFlag.set()
            channel.stop_consuming()
        else:
            # Undefined behavior
            sys.stderr.write("worker.py:callback:Undefined message received in the queue")
            pass
    finally:
        pass

channel.basic_consume(callback, queue='poke_war', no_ack=True)
channel.start_consuming()
