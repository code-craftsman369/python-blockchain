"""
ウォレットとトランザクション管理モジュール

このモジュールは、暗号通貨ウォレットの機能を提供します：
- 秘密鍵・公開鍵の生成
- ブロックチェーンアドレスの生成
- トランザクションのデジタル署名
"""

import binascii

import base58
import codecs
import hashlib

from ecdsa import NIST256p
from ecdsa import SigningKey

import utils

class Wallet(object):
    """
    暗号通貨ウォレットクラス
    
    機能:
    - 秘密鍵・公開鍵のペア生成
    - ブロックチェーンアドレスの生成
    - トランザクションの署名
    """

    def __init__(self):
        """
        ウォレットの初期化
        
        秘密鍵と公開鍵のペアを生成し、
        ブロックチェーンアドレスを作成する
        """
        # ECDSA（楕円曲線暗号）で秘密鍵を生成
        self._private_key = SigningKey.generate(curve=NIST256p)
        # 秘密鍵から公開鍵を導出
        self._public_key = self._private_key.get_verifying_key()
        # ブロックチェーンアドレスを生成
        self._blockchain_address = self.generate_blockchain_address()

    @property
    def private_key(self):
        """秘密鍵を16進数文字列で取得"""
        return self._private_key.to_string().hex()

    @property
    def public_key(self):
        """公開鍵を16進数文字列で取得"""
        return self._public_key.to_string().hex()

    @property
    def blockchain_address(self):
        """ブロックチェーンアドレスを取得"""
        return self._blockchain_address

    def generate_blockchain_address(self):
        """
        公開鍵からブロックチェーンアドレスを生成する
        
        Bitcoinのアドレス生成アルゴリズムを使用:
        1. 公開鍵をSHA-256でハッシュ化
        2. RIPEMD-160でハッシュ化
        3. ネットワークバイトを追加
        4. チェックサムを計算
        5. Base58エンコード
        
        Returns:
            str: 生成されたブロックチェーンアドレス
        """
        # 2. 公開鍵をSHA-256でハッシュ化
        public_key_bytes = self._public_key.to_string()
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        
        # 3. RIPEMD-160でハッシュ化
        ripemed160_bpk = hashlib.new('ripemd160')
        ripemed160_bpk.update(sha256_bpk_digest)
        ripemed160_bpk_digest = ripemed160_bpk.digest()
        ripemed160_bpk_hex = codecs.encode(ripemed160_bpk_digest, 'hex')
        
        # 4. ネットワークバイトを追加（'00'はメインネット）
        network_byte = b'00'
        network_bitcoin_public_key = network_byte + ripemed160_bpk_hex
        network_bitcoin_public_key_bytes = codecs.decode(network_bitcoin_public_key, 'hex')
        
        # 5. チェックサム計算（2重SHA-256）
        sha256_bpk = hashlib.sha256(network_bitcoin_public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        sha256_2_nbpk = hashlib.sha256(sha256_bpk_digest)
        sha256_2_nbpk_digest = sha256_2_nbpk.digest()
        sha256_hex = codecs.encode(sha256_2_nbpk_digest, 'hex')
        
        # 6. チェックサムの最初の4バイト（8文字）を取得
        checksum = sha256_hex[:8]
        
        # 7. ネットワークバイト + ハッシュ + チェックサムを結合
        address_hex = (network_bitcoin_public_key + checksum).decode('utf-8')
        
        # 8. Base58エンコードしてアドレス生成
        blockchain_address = base58.b58encode(binascii.unhexlify(address_hex)).decode('utf-8')
        return blockchain_address

class Transaction(object):
    """
    トランザクションクラス
    
    送金トランザクションを作成し、デジタル署名を生成する
    """

    def __init__(self, sender_private_key, sender_public_key, sender_blockchain_address, recipient_blockchain_address, value):
        """
        トランザクションの初期化
        
        Args:
            sender_private_key (str): 送信者の秘密鍵
            sender_public_key (str): 送信者の公開鍵
            sender_blockchain_address (str): 送信者のアドレス
            recipient_blockchain_address (str): 受信者のアドレス
            value (float): 送金額
        """
        self.sender_private_key = sender_private_key
        self.sender_public_key = sender_public_key
        self.sender_blockchain_address = sender_blockchain_address
        self.recipient_blockchain_address = recipient_blockchain_address
        self.value = value

    def generate_signature(self):
        """
        トランザクションのデジタル署名を生成する
        
        トランザクション内容をハッシュ化し、
        秘密鍵で署名することで、送信者の正当性を証明する
        
        Returns:
            str: デジタル署名（16進数文字列）
        """
        # トランザクション内容をハッシュ化
        sha256 = hashlib.sha256()
        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': self.sender_blockchain_address,
            'recipient_blockchain_address': self.recipient_blockchain_address,
            'value': float(self.value)
        })
        sha256.update(str(transaction).encode('utf-8'))
        message = sha256.digest()

        # 秘密鍵で署名
        private_key = SigningKey.from_string(bytes().fromhex(self.sender_private_key), curve=NIST256p)
        private_key_sign = private_key.sign(message)
        signature = private_key_sign.hex()
        return signature


if __name__ == '__main__':
    """
    テスト実行部分
    
    3つのウォレット（M, A, B）を作成し、
    AからBへの送金トランザクションをテストする
    """
    # 3つのウォレットを作成
    wallet_M = Wallet()
    wallet_A = Wallet()
    wallet_B = Wallet()

    # AからBへのトランザクションを作成
    t = Transaction(
        wallet_A.private_key, wallet_A.public_key, wallet_A.blockchain_address, wallet_B.blockchain_address, 1.0)

    # ブロックチェーンノードを作成
    import blockchain
    block_chain = blockchain.BlockChain(
        blockchain_address=wallet_M.blockchain_address)
    
    # トランザクションを追加
    is_added = block_chain.add_transaction(
        wallet_A.blockchain_address,
        wallet_B.blockchain_address,
        1.0,
        wallet_A.public_key,
        t.generate_signature())
    print('Added?', is_added)

    # マイニング実行
    block_chain.mining()
    utils.pprint(block_chain.chain)

    # 残高を確認
    print('A', block_chain.calculate_total_amount(wallet_A.blockchain_address))
    print('B', block_chain.calculate_total_amount(wallet_B.blockchain_address))