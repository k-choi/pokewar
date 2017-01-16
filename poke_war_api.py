# Interface for poke war API.
# Internally communicate with worker and MongoDB
import datetime
import re

from pymongo import MongoClient
import pika

db = MongoClient().pokewar

def send_rabbitmq_message(str_body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='poke_war')
    channel.basic_publish(exchange='', routing_key='poke_war', body=str_body)
    connection.close()

def find_who_poked():
    cur_pokes = db.curPokes.find_one()
    return cur_pokes['pokers']

def start_poke_war(str_name):
    # Start Poke War with the given person
    # - Send a message to the worker using RabbitMQ
    send_rabbitmq_message('add "{name}"'.format(name=str_name))

def end_poke_war(str_name):
    # End Poke War with the given person
    # - Send a message to the worker using RabbitMQ
    send_rabbitmq_message('remove "{name}"'.format(name=str_name))

def see_poke_stat(str_name):
    # Retrieve Poke Statistics for the last 24 hours.
    # How many times the given person poked in the last 24 hours.
    # Ex. Zilla Go has poked you 13 times in the last 24 hours. It was 51 times in the previous 24 hrs before that.
    # Todo: make a way to send status graph to a user. (Send an email link? push?)
    # add 24 hour filter
    time_stamp_24hrs_ago = datetime.datetime.now() - datetime.timedelta(hours=24)
    num_pokes = db.pokeNewHistory.count({'name': re.compile(str_name, re.IGNORECASE),
                                         'timestamp': {'$gte': time_stamp_24hrs_ago}})
    return num_pokes

def stop_worker():
    send_rabbitmq_message('stop')
