#!/usr/bin/env python
# -*- coding:utf-8 -*-

from cmd import Cmd
from tweepy import *
from datetime import timedelta
import time
import argparse
import urllib


parser = argparse.ArgumentParser()
parser.add_argument('--config', '-c', required=True, type=str, help='config path')
args = parser.parse_args()
tl_default_num = 20
tweet_format = "[{}] {} >> {}"

h = '''
tl [num] : show timeline default 20 tweets
tw [tweet] : tweet [tweet]
stream : streaming timeline
'''


def convert_time(t):
    t += timedelta(hours=9)
    time = str(t).split(" ")
    return time[1]


class StreamListener(StreamListener):
    def on_status(self, status):
        print(tweet_format.format(convert_time(status.created_at), status.user.name, status.text))

    def on_error(self, status):
        print("Error")
        twitter.cmdloop()

    def on_timeout(self):
        raise Exception

class PythonTwitterClient(Cmd):
    def __init__(self):
        Cmd.__init__(self)
        with open(args.config, 'rb') as f:
            data = f.read()
        f.close()
        lines = data.split(b'\n')
        consumer_key = lines[0]
        consumer_secret = lines[1]
        access_key = lines[2]
        access_secret = lines[3]
        self.auth = OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_key, access_secret)
        self.api = API(self.auth)
        self.intro ='\n========== Hello {} ==========\n'.format(self.api.me().name)
        self.prompt = "PTC >>> "

    def do_tw(self, tweet):
        try:
            if self.api:
                t = tweet.encode('utf-8')
                self.api.update_status(t)
                print("tweet successful")
            else:
                prtin("maybe config.txt format error")
        except Exception as err:
            print("tweet failed : ", err)

    def do_tl(self, line):
        l = line.split()

        try:
            num = tl_default_num
            if len(l) > 0:
                try:
                    num = int(l[0])
                except Exception as err:
                    print(err)

            timeline = self.api.home_timeline(count=num)
            timeline.reverse()
            for t in timeline:
                print(tweet_format.format(convert_time(t.created_at), t.user.name, t.text))
        except Exception as err:
            print(err)

    def do_stream(self, *args):
        stream = Stream(self.auth, StreamListener(), secure=True)
        try:
            stream.userstream()
        except Exception:
            time.sleep(60)
            stream = Stream(self.auth, StreamListener(), secure=True)


    def do_help(self, *args):
        print(h)

    def do_exit(self, *args):
        return True

if __name__ == '__main__':
    print('\nCUI Twitter Client written in Python\n\n' \
          'If you have trouble, type "help"\n' \
          'If you want to exit, type "exit"\n' \
          'If you want to streaming timeline, type "stream"'
          )
    twitter = PythonTwitterClient()
    twitter.cmdloop()
