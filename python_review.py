"""
Python基礎復習
Day 6-7: 案件で必要な最低限の文法
"""

# ========================================
# 1. データ型
# ========================================

# リスト（List）- 複数の値を順序付きで保存
print("=== リスト ===")
numbers = [1, 2, 3, 4, 5]
print(f"リスト: {numbers}")
print(f"最初の要素: {numbers[0]}")
print(f"最後の要素: {numbers[-1]}")

# リストに要素を追加
numbers.append(6)
print(f"追加後: {numbers}")

# ブロックチェーンでの実例
# blockchain.py の self.chain = [] がリスト
# self.chain.append(block) で新しいブロックを追加


# 辞書（Dictionary）- キーと値のペアで保存
print("\n=== 辞書 ===")
user = {
    'name': 'Tatsu',
    'age': 30,
    'role': 'Python Developer'
}
print(f"辞書: {user}")
print(f"名前: {user['name']}")
print(f"年齢: {user['age']}")

# キーを追加
user['email'] = 'tatsu@example.com'
print(f"追加後: {user}")

# ブロックチェーンでの実例
# blockchain.py の transaction は辞書
# transaction = {
#     'sender_blockchain_address': '...',
#     'recipient_blockchain_address': '...',
#     'value': 1.0
# }

# === 練習問題1: リストと辞書 ===
print("\n=== 練習問題1 ===")

# Q1: リストから偶数だけを抽出
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even_numbers = []
for num in numbers:
    if num % 2 == 0:  # 2で割り切れる = 偶数
        even_numbers.append(num)
print(f"偶数: {even_numbers}")

# Q2: 辞書から特定のキーの値を取得
wallet = {
    'address': '1DzTkS93N6i3CLrFqgTMtwkpnvjNeXDoGb',
    'balance': 10.5,
    'transactions': 3
}
print(f"残高: {wallet['balance']}")
print(f"トランザクション数: {wallet['transactions']}")

# Q3: 文字列の操作
text = "Hello,GitHub,Python"
words = text.split(',')  # カンマで分割
print(f"分割結果: {words}")
joined = ' '.join(words)  # スペースで結合
print(f"結合結果: {joined}")


# ========================================
# 2. 条件分岐とループ
# ========================================

# if文 - 条件によって処理を分岐
print("\n=== if文 ===")
value = 15

if value > 10:
    print("値は10より大きい")
elif value > 5:
    print("値は5より大きい")
else:
    print("値は5以下")

# ブロックチェーンでの実例
# blockchain.py の add_transaction で使用
# if sender_blockchain_address == MINING_SENDER:
#     # マイニング報酬の場合の処理
# if self.calculate_total_amount(...) < float(value):
#     # 残高不足の場合

# for ループ - リストの各要素を処理
print("\n=== forループ ===")
transactions = [
    {'from': 'Alice', 'to': 'Bob', 'amount': 10},
    {'from': 'Bob', 'to': 'Charlie', 'amount': 5},
    {'from': 'Charlie', 'to': 'Alice', 'amount': 3}
]

for transaction in transactions:
    print(f"{transaction['from']} → {transaction['to']}: {transaction['amount']}円")

# ブロックチェーンでの実例
# blockchain.py の calculate_total_amount で使用
# for block in self.chain:
#     for transaction in block['transactions']:
#         # 各トランザクションを処理

# リスト内包表記 - for文を1行で書く
print("\n=== リスト内包表記 ===")
numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers]
print(f"元のリスト: {numbers}")
print(f"2乗したリスト: {squared}")

# 条件付きリスト内包表記
even_squared = [x**2 for x in numbers if x % 2 == 0]
print(f"偶数だけ2乗: {even_squared}")



# ========================================
# 3. 関数
# ========================================

# 基本的な関数
print("\n=== 基本的な関数 ===")

def calculate_total(price, tax_rate=0.1):
    """
    合計金額を計算する関数
    
    Args:
        price (float): 商品の価格
        tax_rate (float): 税率（デフォルト: 0.1）
    
    Returns:
        float: 税込み価格
    """
    return price * (1 + tax_rate)

total = calculate_total(1000)
print(f"1000円の税込み価格: {total}円")

total_with_custom_tax = calculate_total(1000, 0.08)
print(f"1000円の税込み価格（税率8%）: {total_with_custom_tax}円")

# ブロックチェーンでの実例
# blockchain.py の hash 関数
# def hash(self, block):
#     """ブロックのハッシュ値を計算"""
#     sorted_block = json.dumps(block, sort_keys=True)
#     return hashlib.sha256(sorted_block.encode()).hexdigest()

# 複数の戻り値
print("\n=== 複数の戻り値 ===")

def get_user_info():
    """ユーザー情報を返す"""
    return "Tatsu", 30, "Tokyo"

name, age, city = get_user_info()
print(f"名前: {name}, 年齢: {age}, 都市: {city}")

# 実践的な例: トランザクションの検証
print("\n=== 実践例: トランザクション検証 ===")

def validate_transaction(sender, recipient, amount, balance):
    """
    トランザクションが有効かチェック
    
    Args:
        sender (str): 送信者
        recipient (str): 受信者
        amount (float): 送金額
        balance (float): 送信者の残高
    
    Returns:
        tuple: (有効かどうか, エラーメッセージ)
    """
    if not sender or not recipient:
        return False, "送信者または受信者が指定されていません"
    
    if amount <= 0:
        return False, "送金額は0より大きい必要があります"
    
    if balance < amount:
        return False, f"残高不足です（残高: {balance}円, 必要: {amount}円）"
    
    return True, "OK"

# テスト
is_valid, message = validate_transaction("Alice", "Bob", 100, 50)
print(f"結果: {is_valid}, メッセージ: {message}")

is_valid, message = validate_transaction("Alice", "Bob", 30, 50)
print(f"結果: {is_valid}, メッセージ: {message}")


# ========================================
# 4. クラス
# ========================================

# 基本的なクラス
print("\n=== 基本的なクラス ===")

class User:
    """ユーザークラス"""
    
    def __init__(self, name, age):
        """
        初期化メソッド
        
        Args:
            name (str): ユーザー名
            age (int): 年齢
        """
        self.name = name
        self.age = age
    
    def greet(self):
        """挨拶する"""
        return f"こんにちは、私は{self.name}です。{self.age}歳です。"
    
    def is_adult(self):
        """成人かどうか判定"""
        return self.age >= 18

# クラスのインスタンス作成
user1 = User("Tatsu", 30)
print(user1.greet())
print(f"成人? {user1.is_adult()}")

user2 = User("Yuki", 16)
print(user2.greet())
print(f"成人? {user2.is_adult()}")

# ブロックチェーンでの実例
print("\n=== 実践例: シンプルなウォレットクラス ===")

class SimpleWallet:
    """シンプルなウォレットクラス"""
    
    def __init__(self, owner_name):
        """
        ウォレットの初期化
        
        Args:
            owner_name (str): オーナーの名前
        """
        self.owner_name = owner_name
        self.balance = 0  # 初期残高は0
        self.transactions = []  # トランザクション履歴
    
    def deposit(self, amount):
        """入金する"""
        if amount <= 0:
            return False, "入金額は0より大きい必要があります"
        
        self.balance += amount
        self.transactions.append({
            'type': 'deposit',
            'amount': amount
        })
        return True, f"{amount}円を入金しました"
    
    def withdraw(self, amount):
        """出金する"""
        if amount <= 0:
            return False, "出金額は0より大きい必要があります"
        
        if self.balance < amount:
            return False, f"残高不足です（残高: {self.balance}円）"
        
        self.balance -= amount
        self.transactions.append({
            'type': 'withdraw',
            'amount': amount
        })
        return True, f"{amount}円を出金しました"
    
    def get_balance(self):
        """残高を取得"""
        return self.balance
    
    def show_transactions(self):
        """トランザクション履歴を表示"""
        print(f"\n{self.owner_name}のトランザクション履歴:")
        for i, tx in enumerate(self.transactions, 1):
            print(f"  {i}. {tx['type']}: {tx['amount']}円")

# ウォレットを使ってみる
wallet = SimpleWallet("Tatsu")
print(f"\n初期残高: {wallet.get_balance()}円")

success, message = wallet.deposit(1000)
print(message)

success, message = wallet.deposit(500)
print(message)

print(f"現在の残高: {wallet.get_balance()}円")

success, message = wallet.withdraw(300)
print(message)

print(f"現在の残高: {wallet.get_balance()}円")

success, message = wallet.withdraw(2000)
print(message)

wallet.show_transactions()

# ブロックチェーンのWalletクラスとの比較
print("\n=== ブロックチェーンのWalletクラスとの比較 ===")
print("wallet.py の Wallet クラス:")
print("- __init__: 秘密鍵・公開鍵を生成")
print("- generate_blockchain_address: アドレスを生成")
print("- @property: 鍵を取得するプロパティ")
print("\nこのように、クラスは関連する機能をまとめる便利な仕組みです")


# ========================================
# 5. エラー処理
# ========================================

# try-except - エラーをキャッチして処理
print("\n=== エラー処理 ===")

# 例1: ZeroDivisionError
print("\n例1: ゼロ除算")
try:
    result = 10 / 0
    print(f"結果: {result}")
except ZeroDivisionError:
    print("エラー: ゼロで割ることはできません")

# 例2: 一般的なエラー処理
print("\n例2: 一般的なエラー")
try:
    number = int("abc")  # 文字列を数値に変換（失敗する）
    print(f"数値: {number}")
except ValueError as e:
    print(f"エラー: 数値に変換できません - {e}")
except Exception as e:
    print(f"予期しないエラー: {e}")

# 例3: finally - 必ず実行される処理
print("\n例3: finally")
try:
    result = 10 / 2
    print(f"結果: {result}")
except ZeroDivisionError:
    print("エラー: ゼロ除算")
finally:
    print("処理が完了しました")

# 実践例: 安全なトランザクション処理
print("\n=== 実践例: 安全なトランザクション処理 ===")

def safe_transfer(from_wallet, to_wallet, amount):
    """
    安全にトランザクションを実行する
    
    Args:
        from_wallet: 送信元ウォレット
        to_wallet: 送信先ウォレット
        amount: 送金額
    
    Returns:
        bool: 成功したらTrue
    """
    try:
        # 入力値の検証
        if amount <= 0:
            raise ValueError("送金額は0より大きい必要があります")
        
        if from_wallet.get_balance() < amount:
            raise ValueError(f"残高不足です（残高: {from_wallet.get_balance()}円）")
        
        # トランザクション実行
        success, message = from_wallet.withdraw(amount)
        if not success:
            raise Exception(f"出金失敗: {message}")
        
        success, message = to_wallet.deposit(amount)
        if not success:
            # 出金をロールバック
            from_wallet.deposit(amount)
            raise Exception(f"入金失敗: {message}")
        
        print(f"✓ 送金成功: {amount}円")
        return True
        
    except ValueError as e:
        print(f"✗ 検証エラー: {e}")
        return False
    except Exception as e:
        print(f"✗ 送金エラー: {e}")
        return False
    finally:
        print(f"  送信元残高: {from_wallet.get_balance()}円")
        print(f"  送信先残高: {to_wallet.get_balance()}円")

# テスト
alice_wallet = SimpleWallet("Alice")
bob_wallet = SimpleWallet("Bob")

alice_wallet.deposit(1000)
bob_wallet.deposit(500)

print("\nテスト1: 正常な送金")
safe_transfer(alice_wallet, bob_wallet, 300)

print("\nテスト2: 残高不足")
safe_transfer(alice_wallet, bob_wallet, 2000)

print("\nテスト3: 無効な金額")
safe_transfer(alice_wallet, bob_wallet, -100)

# ブロックチェーンでの実例
print("\n=== ブロックチェーンでのエラー処理 ===")
print("blockchain.py の verify_transaction_signature で使用:")
print("- try-except で署名検証のエラーをキャッチ")
print("- エラーログを記録")
print("- 安全にFalseを返す")



