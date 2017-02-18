import re
import sys
import glob
import pickle
from collections import Counter


# format for baseball named entity
team = r"日本ハム|広島|オリックス|楽天|ロッテ|ソフトバンク|西武|巨人|中日|阪神|ヤクルト|DeNA|ＤｅＮＡ"

place = r"マツダスタジアム|札幌ドーム|京セラドーム大阪|QVCマリン|西武プリンスドーム|甲子園|東京ドーム|ナゴヤドーム|ヤフオクドーム"

day = r"[0-9]{1,2}日"

state = r"(無|1|2)+死(1塁|2塁|3塁|1、2塁|1、3塁|2、3塁|満塁)" #+|得点圏"

batting_order = r"[1-9]番"
batting_position = r"(((右|中|左)翼|ライト|センター|レフト|ピッチャー|キャッチャー|ファースト|セカンド|サード|ショート)(前|越え|間)?)|((右|左|中|遊|遊撃|投|捕|1|2|3|遊){1,2}(前|越え|間))"
batting_result = r"(([1-3]塁)?適時打)|(適時([1-3]塁)打)|犠飛|(押し出し)?4球|(セーフティ)?スクイズ|(セーフティ)?バント|犠打|死球|ゴロ|フライ" # 3振を抜いた
batting_pos_res = r"(右|左|中|遊|遊撃|投|捕|1|2|3|遊)(犠打|犠飛|飛)"

count = r"(\d+|初|延長(10|11|12))回"

homerun_result = r"[0-9]+号((ランニング|満塁)(ホームラン|本塁打)|満塁弾|(([23]ラン|ソロ)(ホームラン|本塁打)?))"

#point = r"同点|無(失|得)点|勝ち越し|先制|逆転|追?加点|サヨナラ"

pitcher = r"先発|中継ぎ|抑え|継投"

game_result = r"[0-9]+－[0-9]+"


def format_text(text):
    # fix number format
    text = re.sub(r'０', "0", text)
    text = re.sub(r'一|１', "1", text)
    text = re.sub(r'二|２', "2", text)
    text = re.sub(r'三|３', "3", text)
    text = re.sub(r'四|４', "4", text)
    text = re.sub(r'五|５', "5", text)
    text = re.sub(r'六|６', "6", text)
    text = re.sub(r'七|７', "7", text)
    text = re.sub(r'八|８', "8", text)
    text = re.sub(r'九|９', "9", text)

    # fix string format
    text = re.sub(team, "[チーム名]", text)
    text = re.sub(place, "[試合会場]", text)
    text = re.sub(batting_order, "[打順]", text)
    text = re.sub(batting_position, "[打撃位置]", text)
    text = re.sub(homerun_result, "[本塁打結果]", text)
    text = re.sub(batting_result, "[打撃結果]", text)
    text = re.sub(batting_pos_res, "[打撃位置][打撃結果]", text)
    #text = re.sub(point, "[得点]", text)
    #text = re.sub(pitcher, "[投手]", text)
    text = re.sub(day, "[日付]", text)
    text = re.sub(state, "[状況]", text)
    text = re.sub(count, "[回数]", text)
    text = re.sub(game_result, "[試合結果]", text)
    text = re.sub(r"[0-9]+", "[数字]", text)
    text = re.sub(r"奪[数字]振", "奪三振", text) # 奪三振用
    return text

def read_files():
    files = glob.glob("./data/*")
    items = []
    for file_path in files:
        with open(file_path, "rb") as f:
            item = pickle.load(f)
        items.append(item)
    return items

def format_players(item, text):
    players = []
    for team_name, team_players in item.items():
        if team_name in text:
            players.extend(team_players)
        if team_name == "DeNA" and "ＤｅＮＡ" in text:
            players.extend(team_players)

    long_name_list = [] # 大谷翔平
    middle_name_list = [] # 大谷翔
    short_name_list = [] # 大谷
    for player in players:
        if len(player) > 1:
            long_name_list.append(player[0]+player[1])
            middle_name_list.append(player[0]+player[1][0])
        short_name_list.append(player[0])

    for name in long_name_list+middle_name_list+short_name_list:
        text = re.sub(name, "[選手名]", text)
    return text

def read_players_name():
    with open("./players_dataset.pickle", "rb") as f:
        item = pickle.load(f)
    return item

items = read_files()
players_item = read_players_name()
cnt = 0
sentence_count = Counter()
for item in items:
    text = item["body"]
    norm_text = format_players(players_item, text)
    norm_text = format_text(norm_text)
    sentences = norm_text.split("。")
    for sentence in sentences:
        sentence_count[sentence] += 1

    """
    print(text)
    print("*****************************************************")
    print(norm_text)
    print("*****************************************************")
    cnt += 1
    if cnt > 10:
        break
    """

data_str = "文,カウント\n"
for sent, count in sorted(sentence_count.items(), key=lambda x:x[1], reverse=True):
    if not sent.strip():
        continue
    data_str += "{0},{1}\n".format(sent, count)

with open("./rank.csv", "w") as f:
    f.write(data_str)
