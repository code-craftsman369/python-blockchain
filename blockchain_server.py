"""
ブロックチェーンノードのWebサーバー

Flaskを使用したREST APIサーバー。
ブロックチェーンネットワークのノードとして動作し、
以下の機能を提供：
- チェーンの取得
- トランザクションの管理
- マイニング
- ネットワークコンセンサス
- 残高照会
"""

from flask import Flask
from flask import jsonify
from flask import request


import blockchain
import wallet

app = Flask(__name__)

cache = {}
def get_blockchain():
    """
    ブロックチェーンインスタンスを取得（シングルトンパターン）
    
    初回呼び出し時にブロックチェーンとマイナーのウォレットを作成し、
    以降はキャッシュから取得する
    
    Returns:
        BlockChain: ブロックチェーンインスタンス
    """

    cached_blockchain = cache.get('blockchain')
    if not cached_blockchain:
        # マイナー用のウォレットを作成
        miners_wallet = wallet.Wallet()
        # ブロックチェーンを初期化
        cache['blockchain'] = blockchain.BlockChain(
            blockchain_address=miners_wallet.blockchain_address,
            port=app.config['port'])
        # マイナーの鍵情報をログ出力
        app.logger.warning({
            'private_key': miners_wallet.private_key,
            'public_key': miners_wallet.public_key,
            'blockchain_address': miners_wallet.blockchain_address})
    return cache['blockchain']

@app.route('/chain', methods=['GET'])
def get_chain():
    """
    ブロックチェーン全体を取得するAPI
    
    GET /chain
    
    Returns:
        JSON: ブロックチェーンの全ブロック
        Status: 200
    """
    block_chain = get_blockchain()
    response = {
        'chain': block_chain.chain
    }
    return jsonify(response), 200

@app.route('/transactions', methods=['GET', 'POST', 'PUT', 'DELETE'])
def transaction():
    """
    トランザクション管理API
    
    GET /transactions: トランザクションプールを取得
    POST /transactions: 新しいトランザクションを作成（他ノードに伝播）
    PUT /transactions: トランザクションをプールに追加（他ノードから受信）
    DELETE /transactions: トランザクションプールをクリア
    
    Returns:
        JSON: 実行結果
    """
    block_chain = get_blockchain()
    if request.method == 'GET':
        # トランザクションプールの取得
        transactions = block_chain.transaction_pool
        response = {
            'transactions': transactions,
            'length': len(transactions)
        }
        return jsonify(response), 200

    if request.method == 'POST':
        # 新しいトランザクションを作成（このノードから）
        request_json = request.json
        required = (
            'sender_blockchain_address',
            'recipient_blockchain_address',
            'value',
            'sender_public_key',
            'signature',)
        if not all(k in request_json for k in required):
            return jsonify({'message': 'missing values'}), 400

        # トランザクションを作成し、他のノードに伝播
        is_created = block_chain.create_transaction(
            request_json['sender_blockchain_address'],
            request_json['recipient_blockchain_address'],
            request_json['value'],
            request_json['sender_public_key'],
            request_json['signature']
        )
        if not is_created:
            return jsonify({'message': 'fail'}), 400
        return jsonify({'message': 'success'}), 201


    if request.method == 'PUT':
        # トランザクションを追加（他ノードから受信）
        request_json = request.json
        required = (
            'sender_blockchain_address',
            'recipient_blockchain_address',
            'value',
            'sender_public_key',
            'signature',)
        if not all(k in request_json for k in required):
            return jsonify({'message': 'missing values'}), 400

        # トランザクションプールに追加
        is_updated = block_chain.add_transaction(
            request_json['sender_blockchain_address'],
            request_json['recipient_blockchain_address'],
            request_json['value'],
            request_json['sender_public_key'],
            request_json['signature']
        )
        if not is_updated:
            return jsonify({'message': 'fail'}), 400
        return jsonify({'message': 'success'}), 200

    if request.method == 'DELETE':
        # トランザクションプールをクリア
        block_chain.transaction_pool = []
        return jsonify({'message': 'success'}), 200

@app.route('/mine', methods=['GET'])
def mine():
    """
    マイニングを1回実行するAPI
    
    GET /mine
    
    Returns:
        JSON: マイニング結果
        Status: 200（成功）/ 400（失敗）
    """
    block_chain = get_blockchain()
    is_mined = block_chain.mining()
    if is_mined:
        return jsonify({'message': 'success'}), 200
    return jsonify({'message': 'fail'}), 400

@app.route('/mine/start', methods=['GET'])
def start_mine():
    """
    自動マイニングを開始するAPI
    
    GET /mine/start
    
    定期的にマイニングを実行するスレッドを開始
    
    Returns:
        JSON: 実行結果
        Status: 200
    """
    get_blockchain().start_mining()
    return jsonify({'message': 'success'}), 200

@app.route('/consensus', methods=['PUT'])
def consensus():
    """
    コンセンサスアルゴリズムを実行するAPI
    
    PUT /consensus
    
    近隣ノードのチェーンと比較し、
    より長い有効なチェーンがあれば置き換える
    
    Returns:
        JSON: チェーンが置き換えられたかどうか
        Status: 200
    """
    block_chain = get_blockchain()
    replaced = block_chain.resolve_conflicts()
    return jsonify({'replaced': replaced}), 200

@app.route('/amount', methods=['GET'])
def get_total_amount():
    """
    指定されたアドレスの残高を取得するAPI
    
    GET /amount?blockchain_address=<address>
    
    Args:
        blockchain_address (query): 残高を照会するアドレス
    
    Returns:
        JSON: 残高
        Status: 200
    """
    blockchain_address = request.args['blockchain_address']
    return jsonify({
        'amount': get_blockchain().calculate_total_amount(blockchain_address)
    }), 200

if __name__ == '__main__':
    """
    サーバーのメイン実行部分
    
    コマンドライン引数でポート番号を指定して起動:
    python blockchain_server.py -p 5001
    """
    from argparse import ArgumentParser

    # コマンドライン引数のパース
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    # ポート番号を設定
    app.config['port'] = port

    # ブロックチェーンノードを起動
    get_blockchain().run()

    # Flaskサーバーを起動
    app.run(host='0.0.0.0', port=port, threaded=True, debug=True)









