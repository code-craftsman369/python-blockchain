"""
ユーティリティ関数モジュール

ブロックチェーンで使用する汎用的な関数を提供：
- 辞書のソート
- チェーンの表示
- ネットワークノードの検索
- ホスト情報の取得
"""

import collections
import logging
import re
import socket

logger = logging.getLogger(__name__)

# IPアドレスを解析するための正規表現
# 例: "192.168.1.100" → prefix_host="192.168.1." + last_ip="100"
RE_IP = re.compile('(?P<prefix_host>^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.)(?P<last_ip>\\d{1,3}$)')

def sorted_dict_by_key(unsorted_dict):
    """
    辞書をキーでソートして順序付き辞書を返す
    
    ハッシュ計算の一貫性を保つために使用
    
    Args:
        unsorted_dict (dict): ソートされていない辞書
    
    Returns:
        OrderedDict: キーでソートされた順序付き辞書
    """
    return collections.OrderedDict(sorted(unsorted_dict.items(), key=lambda d: d[0]))


def pprint(chains):
    """
    ブロックチェーンを見やすく表示する
    
    各ブロックの情報を整形して出力。
    トランザクションは詳細に展開して表示。
    
    Args:
        chains (list): ブロックチェーン（ブロックのリスト）
    """
    for i, chain in enumerate(chains):
        print(f'{"="*25}Chain{i}{"="*25}')
        for k, v in chain.items():
            # トランザクションは詳細に表示
            if k == 'transactions':
                print(k)
                for d in v:
                    print(f'{"-"*40}')
                    for kk, vv in d.items():
                        print(f' {kk:30}{vv}')
            else:
                print(f'{k:15}{v}')
        print(f'{"*"*25}')

def is_found_host(target, port):
    """
    指定されたホストとポートに接続可能か確認する
    
    Args:
        target (str): 対象ホストのIPアドレス
        port (int): 対象ポート番号
    
    Returns:
        bool: 接続可能ならTrue、それ以外はFalse
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)  # タイムアウト1秒
        try:
            sock.connect((target, port))
            return True
        except Exception as ex:
            # 接続失敗時はログに記録
            logger.error({
                'action': 'is_found_host',
                'target': target,
                'port': port,
                'ex': ex,
            })
            return False

def find_neighbours(my_host, my_port, start_ip_range, end_ip_range, start_port, end_port):
    """
    近隣のブロックチェーンノードを検索する
    
    自分のIPアドレスの近くのIPとポートの範囲をスキャンし、
    応答があるノードを近隣ノードとして返す
    
    Args:
        my_host (str): 自分のIPアドレス
        my_port (int): 自分のポート番号
        start_ip_range (int): IPアドレスの検索開始オフセット
        end_ip_range (int): IPアドレスの検索終了オフセット
        start_port (int): ポート番号の検索開始
        end_port (int): ポート番号の検索終了
    
    Returns:
        list: 近隣ノードのアドレスリスト（例: ["192.168.1.101:5001"]）
        None: IPアドレスの形式が不正な場合
    """
    address = f'{my_host}:{my_port}'
    # IPアドレスを正規表現で解析
    m = RE_IP.search(my_host)
    if not m:
        return None

    # IPアドレスのプレフィックスと最後のオクテットを取得
    # 例: "192.168.1.100" → prefix="192.168.1." last="100"
    prefix_host = m.group('prefix_host')
    last_ip = m.group('last_ip')

    neighbours = []
    # ポート範囲をスキャン
    for guess_port in range(start_port, end_port):
        # IP範囲をスキャン
        for ip_range in range(start_ip_range, end_ip_range):
            # 推測されるホストアドレスを生成
            guess_host = f'{prefix_host}{int(last_ip)+int(ip_range)}'
            guess_address = f'{guess_host}:{guess_port}'
            # ホストが存在し、自分自身でない場合に追加
            if is_found_host(guess_host, guess_port) and not guess_address == address:
                neighbours.append(guess_address)
    return neighbours

def get_host():
    """
    自分のホストのIPアドレスを取得する
    
    Returns:
        str: 自分のIPアドレス（取得失敗時は '127.0.0.1'）
    """
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as ex:
        logger.debug({'action': 'get_host', 'ex': ex})
    return '127.0.0.1'


if __name__ == '__main__':
    """
    テスト実行部分
    
    各関数の動作確認用
    """
    # print(is_found_host('127.0.0.1', 5001))
    # print(find_neighbours('192.168.1.71', 5001, 0, 3, 5001,5004))
    print(get_host())






