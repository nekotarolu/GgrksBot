import time
import urllib.parse
import urllib.request

import tweepy
from tweepy import TweepError

import ggrksbot_twitter_config

# 定数クラスファイルからTwitterに必要情報をSet.
consumerKey: str = ggrksbot_twitter_config.CONSUMER_KEY
consumerSecret: str = ggrksbot_twitter_config.CONSUMER_SECRET
accessToken: str = ggrksbot_twitter_config.ACCESS_TOKEN
accessTokenSecret: str = ggrksbot_twitter_config.ACCESS_TOKEN_SECRET

# SetしたApplication ConfigからOAuthを取得.
auth = tweepy.OAuthHandler(consumer_key=consumerKey, consumer_secret=consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)

# 取得したOAuthでtweepyのAPIインスタンスを生成.
api = tweepy.API(auth)

# twitter replay用のMainLoop Properties.
# TODO: properties file化する.
breakCount = 100
breakCounter = 0
beforeText = "before"
nowText = "now"
sleepSec = 5

# twitter replyのMainLoop
# TODO: リアルタイムに反応するようにする.
while 1:
    # https://www.google.co.jp/search?q=hoge でGoogle検索URL.
    print("Loop Top:" + time.ctime())

    # 自分へのリプ一覧を取得.
    replyTimeLine = api.mentions_timeline()
    print(replyTimeLine[0].text)

    # 自分へのリプの一番新しいものを取得.
    status = replyTimeLine[0]
    nowText = status.text

    # 自分がすでにリプライ済みのもの(1つ前のリプ)でなければreplyする.
    if nowText != beforeText:
        print("Debug::reply ggrks " + nowText)
        # @xxx をsplitで除去.
        try:
            nowTextSplit = nowText.split(" ")
        except ValueError:
            # splitエラー時は後段の配列操作でInvalidになるので, エラー処理.
            # TODO: もともとlen(nowTextSplit) > 0 を判定していた. これで正しいか要確認.
            print("Debug::Split failed...")
        else:
            # split成功時.
            print("Debug::Split success!")

            # 全角文字の可能性があるので, URL用文字(ASCII)へ変換.
            urlQuery = urllib.parse.quote(nowTextSplit[1])
            print(urlQuery)

            # 変換した文字列をGoogle検索用URLのクエリにセット.
            urlStr = "https://www.google.co.jp/search?q=" + urlQuery
            print(urlStr)

            # リプしてきた相手の情報を取得.
            statusId = status.id
            screenName = status.author.screen_name.encode("UTF-8")

            # ggrksbotのreply文字列を生成.
            replyText = "@".encode("UTF-8") + screenName + " ggrks! ".encode("UTF-8") + urlStr.encode("UTF-8")

            # tweepyのAPIを使って, 生成したreplyをツイート!!
            try:
                api.update_status(status=replyText, in_reply_to_status_id=statusId)
            except TweepError:
                # replyエラー時は, 何もしない (だいたい実行前のリプライと同じツイートしてるエラー)
                print("Debug::TweepError reply failed...")
    else:
        # 煽り耐性:前回リプライ済みであろうリプには反応しない.
        print("Debug::no action.")
    beforeText = nowText  # 次回リプライ判定用.

    # Twitter Applicationの上限管理.
    breakCounter + 1
    if breakCounter > breakCount:
        print("Debug::break Counter over limit.")
        break
    else:
        print("Debug::" + str(sleepSec) + " sec sleep.")
        print(time.ctime())
        time.sleep(sleepSec)

    print("Debug::Loop End" + time.ctime())

print("Debug::Exit... " + time.ctime())
