"""
ブロックチェーン実装のメインモジュール

このモジュールは、ブロックチェーンの基本的な機能を提供します：
- ブロック生成
- トランザクション管理
- マイニング（Proof of Work）
- ネットワーク同期
"""


import contextlib
import hashlib
import json
import logging
import sys
import time
import threading

from ecdsa import NIST256p
from ecdsa import VerifyingKey
import requests

import utils

# マイニングの難易度（先頭にこの数だけ0が必要）
MINING_DIFFICULTY = 3
# マイニング報酬の送信者アドレス
MINING_SENDER = 'THE BLOCKCHAIN'
# マイニング報酬の額
MINING_REWARD = 1.0
# マイニングの間隔（秒）
MINING_TIMER_SEC = 20

# ブロックチェーンノードのポート範囲
BLOCKCHAIN_PORT_RANGE = (5001, 5004)
# 近隣ノードのIP範囲
NEIGHBOURS_IP_RANGE = (0, 1)
# 近隣ノードとの同期間隔（秒）
BLOCKCHAIN_NEIGHBOURS_SYNC_TIME_SEC = 20


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class BlockChain(object):
    """
    ブロックチェーンを管理するメインクラス
    
    機能:
    - ブロックの生成と管理
    - トランザクションプールの管理
    - マイニング（Proof of Work）
    - ネットワークノードとの同期
    """

    def __init__(self, blockchain_address=None, port=None):
        """
        ブロックチェーンの初期化
        
        Args:
            blockchain_address (str): このノードのブロックチェーンアドレス
            port (int): このノードのポート番号
        """
        self.transaction_pool = []  # トランザクションプール
        self.chain = []  # ブロックチェーン本体
        self.neighbours = []  # 近隣ノードのリスト
        self.create_block(0, self.hash({}))  # ジェネシスブロック作成
        self.blockchain_address = blockchain_address
        self.port = port
        # マイニングの排他制御用
        self.mining_semaphore = threading.Semaphore(1)
        # 近隣ノード同期の排他制御用
        self.sync_neighbours_semaphore = threading.Semaphore(1)

    def run(self):
        self.sync_neighbours()
        self.resolve_conflicts()
        self.start_mining()

    def set_neighbours(self):
        self.neighbours = utils.find_neighbours(
            utils.get_host(), self.port,
            NEIGHBOURS_IP_RANGE[0], NEIGHBOURS_IP_RANGE[1],
            BLOCKCHAIN_PORT_RANGE[0], BLOCKCHAIN_PORT_RANGE[1])
        logger.info({'aciton': 'self_neighbours', 'neighbours': self.neighbours})

    def sync_neighbours(self):
        is_acquire = self.sync_neighbours_semaphore.acquire(blocking=False)
        if is_acquire:
            with contextlib.ExitStack() as stack:
                stack.callback(self.sync_neighbours_semaphore.release)
                self.set_neighbours()
                loop = threading.Timer(BLOCKCHAIN_NEIGHBOURS_SYNC_TIME_SEC, self.sync_neighbours)
                loop.start()


    def create_block(self, nonce, previous_hash):
        """
        新しいブロックを作成してチェーンに追加する
        
        Args:
            nonce (int): Proof of Workで見つけた値
            previous_hash (str): 前のブロックのハッシュ値
        
        Returns:
            dict: 作成されたブロック
        """
        block = utils.sorted_dict_by_key({
            'timestamp': time.time(), # タイムスタンプ
            'transactions': self.transaction_pool, # 現在のトランザクション
            'nonce': nonce, # Proof of Workの値
            'previous_hash': previous_hash # 前のブロックのハッシュ
        })
        self.chain.append(block) # チェーンに追加
        self.transaction_pool = [] # トランザクションプールをクリア

        # すべての近隣ノードのトランザクションプールもクリア
        for node in self.neighbours:
            requests.delete(f'http://{node}/transactions')
        return block

    def hash(self, block):
        """
        ブロックのハッシュ値を計算する
        
        Args:
            block (dict): ブロックのデータ
        
        Returns:
            str: SHA-256ハッシュ値（16進数文字列）
        """
        # ブロックをJSON形式に変換（キーをソート）
        sorted_block = json.dumps(block, sort_keys=True)
        # SHA-256でハッシュ化
        return hashlib.sha256(sorted_block.encode()).hexdigest()

    def add_transaction(self, sender_blockchain_address, recipient_blockchain_address, value,
                        sender_public_key=None, signature=None):
        """
        トランザクションをトランザクションプールに追加する
        
        Args:
            sender_blockchain_address (str): 送信者のアドレス
            recipient_blockchain_address (str): 受信者のアドレス
            value (float): 送金額
            sender_public_key (str): 送信者の公開鍵
            signature (str): デジタル署名
        
        Returns:
            bool: 追加に成功したらTrue
        """

        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': sender_blockchain_address,
            'recipient_blockchain_address': recipient_blockchain_address,
            'value': float(value)
        })

        # マイニング報酬の場合は署名検証不要
        if sender_blockchain_address == MINING_SENDER:
            self.transaction_pool.append(transaction)
            return True

        # デジタル署名を検証
        if self.verify_transaction_signature(
            sender_public_key, signature, transaction):

            # 送信者の残高が十分か確認
            if self.calculate_total_amount(sender_blockchain_address) < float(value):
                 logger.error({'action': 'add_transaction', 'error': 'no_value'})
                 return False

            self.transaction_pool.append(transaction)
            return True
        return False

    def create_transaction(self, sender_blockchain_address,
                           recipient_blockchain_address, value, sender_public_key, signature):
        is_transacted = self.add_transaction(
            sender_blockchain_address, recipient_blockchain_address, value, sender_public_key, signature)

        if is_transacted:
            for node in self.neighbours:
                requests.put(
                    f'http://{node}/transactions',
                    json={
                        'sender_blockchain_address': sender_blockchain_address,
                        'recipient_blockchain_address': recipient_blockchain_address,
                        'value': float(value),
                        'sender_public_key': sender_public_key,
                        'signature': signature,
                    }


                )



        return is_transacted

    def verify_transaction_signature(
            self, sender_public_key, signature, transaction):
        """
        トランザクションのデジタル署名を検証する
        
        Args:
            sender_public_key (str): 送信者の公開鍵
            signature (str): デジタル署名
            transaction (dict): トランザクションデータ
        
        Returns:
            bool: 署名が正しければTrue
        """
        # トランザクションをハッシュ化
        sha256 = hashlib.sha256()
        sha256.update(str(transaction).encode('utf-8'))
        message = sha256.digest()

        # 署名と公開鍵をバイト列に変換
        signature_bytes = bytes().fromhex(signature)
        verifying_key = VerifyingKey.from_string(
            bytes.fromhex(sender_public_key), curve=NIST256p)
        
        # 署名を検証
        verified_key = verifying_key.verify(signature_bytes, message)
        return verified_key

    def valid_proof(self, transactions, previous_hash, nonce,difficulty=MINING_DIFFICULTY):
        """
        Proof of Workの条件を満たすか検証する
        
        Args:
            transactions (list): トランザクションリスト
            previous_hash (str): 前のブロックのハッシュ
            nonce (int): 検証するnonce値
            difficulty (int): 難易度（先頭の0の個数）
        
        Returns:
            bool: 条件を満たせばTrue
        """
        guess_block = utils.sorted_dict_by_key({
            'transactions': transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        })
        guess_hash = self.hash(guess_block)
        # ハッシュの先頭がdifficulty個の0で始まるか確認
        return guess_hash[:difficulty] == '0'*difficulty

    def proof_of_work(self):
        """
        Proof of Workアルゴリズムでnonceを見つける
        
        先頭にMINING_DIFFICULTY個の0が並ぶハッシュ値になるまで
        nonceを1ずつ増やして試行する
        
        Returns:
            int: 見つかったnonce値
        """
        transactions = self.transaction_pool.copy()
        previous_hash = self.hash(self.chain[-1])
        nonce = 0
        # 条件を満たすnonceが見つかるまでループ
        while self.valid_proof(transactions, previous_hash, nonce) is False:
            nonce += 1
        return nonce

    def mining(self):
        """
        マイニングを実行する
        
        1. Proof of Workでnonceを見つける
        2. マイニング報酬をトランザクションに追加
        3. 新しいブロックを作成
        4. 近隣ノードに通知
        
        Returns:
            bool: マイニングに成功したらTrue
        """
        # Proof of Workを実行
        nonce = self.proof_of_work()

        # マイニング報酬を追加
        self.add_transaction(
            sender_blockchain_address=MINING_SENDER,
            recipient_blockchain_address=self.blockchain_address,
            value=MINING_REWARD)
        
        # 報酬追加後に再度Proof of Work
        nonce = self.proof_of_work()
        previous_hash = self.hash(self.chain[-1])

        # 新しいブロックを作成
        self.create_block(nonce, previous_hash)
        logger.info({'action': 'mining', 'status': 'success'})

         # すべての近隣ノードにコンセンサスを要求
        for node in self.neighbours:
            requests.put(
                f'http://{node}/consensus',)
        return True

    def start_mining(self):
        is_acquire = self.mining_semaphore.acquire(blocking=False)
        if is_acquire:
            with contextlib.ExitStack() as stack:
                stack.callback(self.mining_semaphore.release)
                self.mining()
                loop = threading.Timer(MINING_TIMER_SEC, self.start_mining)
                loop.start()

    def calculate_total_amount(self, blockchain_address):
        """
        指定されたアドレスの残高を計算する
        
        Args:
            blockchain_address (str): 残高を計算するアドレス
        
        Returns:
            float: 現在の残高
        """
        total_amount = 0.0
        # すべてのブロックのトランザクションを確認
        for block in self.chain:
            for transaction in block['transactions']:
                value = float(transaction['value'])
                # 受信者の場合は加算
                if blockchain_address == transaction['recipient_blockchain_address']:
                    total_amount += value
                # 送信者の場合は減算
                if blockchain_address == transaction['sender_blockchain_address']:
                    total_amount -= value
        return total_amount

    def valid_chain(self, chain):
        pre_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(pre_block):
                return False

            if not self.valid_proof(
                block['transactions'], block['previous_hash'],
                block['nonce'], MINING_DIFFICULTY):
                return False

            pre_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        logest_chain = None
        max_length = len(self.chain)
        for node in self.neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                response_json = response.json()
                chain = response_json['chain']
                chain_length = len(chain)
                if chain_length > max_length and self.valid_chain(chain):
                    max_length = chain_length
                    logest_chain = chain

        if logest_chain:
            self.chain = logest_chain
            logger.info({'action': 'resolve_conflicts', 'status': 'replaced'})
            return True

        logger.info({'action': 'resolve_conflicts', 'status': 'not replaced'})
        return False
