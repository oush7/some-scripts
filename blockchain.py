
import time
import copy
import random
from hashlib import sha256
from flask import Flask
from flask import jsonify, request


network_diff = 4

nodes = {}
nodes_names = set()

class Transaction(object):

    def __init__(self, from_address, to_address, amount):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.hash = self.transaction_hash(from_address, to_address, amount)

    def transaction_hash(self, from_address, to_address, amount):
        transaction_string = str(from_address) + str(to_address) + str(amount)
        return sha256(transaction_string.encode()).hexdigest()

    def print_transaction(self):
        print("transaction : " + '{'  + " " +  self.from_address + " -> " + self.to_address + "  (" + str(self.amount) + ")" + ", hash :" + str(self.hash) + " }")


class Block(object):

    def __init__(self, index, timestamp, transactions, prev_hash, hash="0", proof=0):
        self.__data = {
            "index": index,
            "timestamp": timestamp,
            "transactions": transactions,
            "prev_hash": prev_hash,
            "proof": proof,
            "hash": hash
        }

    def get_data(self):
        return self.__data

    def get_copy_data(self):
        data = self.__data
        return data

    def print_block(self):
        data = self.get_data()
        print("{")
        print("   " + "hash : " + " " + str(data["hash"]))
        print("   " + "index : " + " " + str(data["index"]))
        print("   " + "timestamp : " + " " + str(data["timestamp"]))
        print("   transactions : " + "{")
        for i in data["transactions"]:
          #  print("      ", end='')
            i.print_transaction()
        print("   " + "}")
        print("   " + "prev_hash : " + " " + str(data["prev_hash"]))
        print("   " + "proof : " + " " + str(data["proof"]))
        print("}")

    def block_hash(self, prev_hash, proof):
        block_string = str(prev_hash)
        for i in self.get_data()["transactions"]:
            block_string += str(i.hash)
        block_string += str(proof)
        return sha256(block_string.encode()).hexdigest()

    def proof_of_work(self):
        data = self.get_data()
        data["proof"] = 0
        curr_try = self.block_hash(data["prev_hash"], data["proof"])
        while not curr_try.startswith('0' * network_diff):
            data["proof"] += 1
            curr_try = self.block_hash(data["prev_hash"], data["proof"])
        data["hash"] = curr_try
        return curr_try


def register_node(address):
    nodes.update({address: copy.deepcopy(blockchain)})

class Blockchain(object):
    def __init__(self, blockchain, new_transactions):
        self.__blockchain = blockchain
        self.__new_transactions = new_transactions

    def __get_blockchain(self):
        return self.__blockchain

    def __get_new_transactions(self):
        return self.__new_transactions


    def create_first_block(self):
        first_block = Block(0, time.time(), [], "0")
        first_block.get_data()["hash"] = first_block.block_hash(random.randint(0, 1000000), random.randint(0, 1000000))
        first_block.proof_of_work()
        self.__get_blockchain().append(first_block)

    def last_block(self):
        return self.__get_blockchain()[-1]

    def add_transaction(self, transaction, num_of_transactions):
        if (num_of_transactions == 1):
            self.__get_new_transactions().append(transaction)
        else:
            for i in transaction:
                self.__get_new_transactions().append(i)

    def add_block(self, block):
        self.__get_blockchain().append(block)
        self.__new_transactions = []
        return block

    def clear_transactions(self):
        self.__get_new_transactions().clear()

    def mine_block(self):
        if (self.__get_new_transactions() == []):
            return
        else:
            block = Block(index=self.last_block().get_data()["index"] + 1, timestamp=time.time(), transactions=self.__get_new_transactions(), prev_hash=self.last_block().get_data()["hash"])
            block.proof_of_work()
            self.add_block(block)
            self.__get_new_transactions().clear()
            return block

    def verify_block(self, block):
        data = block.get_data()
        if (data["index"] == 0):
            return True
        else:
            block_hash = block.block_hash(prev_hash=block.get_data()["prev_hash"], proof=block.get_data()["proof"])
            if (data["prev_hash"] == (self.__get_blockchain()[data["index"] - 1].get_data()["hash"]) and block_hash.startswith('0' * network_diff)):
                return True
            return False

    def verify_blockchain(self):
        for block in self.__get_blockchain()[1:]:
            if(self.verify_block(block) == False):
                return False
        return True

    def get_chain(self):
        return copy.deepcopy(self.__get_blockchain())

    def get_transactions(self):
        return copy.deepcopy(self.__get_new_transactions())

    def print_blockchain(self):
        k = 0
        for i in self.__get_blockchain():
           # print("Block  " + str(k) + "  ", end='')
            i.print_block()
            k = k + 1
        print("\n")


#теперь консенсус(прохожу по всем нодам, чекаю ноду с максимальной цепочкой блоков, меняю блокчейны у всех челов, меняю сам блокчейн).-- в целом очев


app = Flask(__name__)


blockchain = Blockchain([],[])
blockchain.create_first_block()

t1 = Transaction("1", "2", 10000)
t2 = Transaction("2", "3", 10000)

blockchain.add_transaction([t1,t2], 2)

blockchain.mine_block()

blockchain.add_transaction([t1,t2, Transaction("ISLAM", "aas", 1000000000)], 3)

blockchain.mine_block()

blockchain.mine_block()

blockchain.add_transaction([t1,t2, Transaction("ISLAM", "asdfas", 1000000000), Transaction("ISLAM", "asdf", 1000000000)], 4)


def new_blockchain(blocks, transactions):
    blockchain = Blockchain(blocks, transactions)

@app.route('/blockchain', methods=['GET'])
def full_chain():
    chain = []
    for block in blockchain.get_chain():
        tmp = block.get_data()["transactions"]
        block.get_data()["transactions"] = []
        for transaction in tmp:
            if (transaction != []):
                block.get_data()["transactions"].append(transaction.__dict__)
        chain.append(block.get_data())
    return jsonify(chain), 200


@app.route('/addtransaction', methods=['POST'])
def new_transaction():
    global nodes
    new_nodes = {}
    values = request.get_json()
    blockchain.add_transaction(Transaction(values['from_address'], values['to_address'], values['amount']), 1)
    for name in nodes_names:
        new_nodes.update({name : Blockchain(nodes[name].get_chain(), blockchain.get_transactions())})
    nodes = new_nodes
    return "new transaction created"


@app.route('/users', methods=['GET'])
def print_nodes():
    tmp = []
    for node in nodes:
        tmp.append(node)
    return jsonify(tmp)

@app.route('/consensus')
def consensus():
    global blockchain
    global nodes
    new_nodes = {}
    max = -1
    tmp = []
    for name, chain in nodes.items():
        if(chain.last_block().get_data()["index"] > max):
            max = chain.last_block().get_data()["index"]
            address = name
            tmp = Blockchain(chain.get_chain(), chain.get_transactions())
    blockchain = Blockchain(tmp.get_chain(), tmp.get_transactions())
    blockchain.clear_transactions()
    for name in nodes_names:
        new_nodes.update({name: copy.deepcopy(blockchain)})
    nodes = new_nodes
    return "consensus done"

@app.route('/active_transactions')
def all_transactions():
    transactions = []
    tmp = blockchain.get_transactions()
    for trans in tmp:
        transactions.append(trans.__dict__)
    return jsonify(transactions), 200


@app.route('/mine/<string:name>', methods=['GET'])
def mine(name):
    if (name in nodes):
        nodes.get(name).mine_block()
    return "New block created"


@app.route('/register', methods=['POST'])
def register_nodes():
    global nodes_names
    values = request.get_json()
    nodes = values['address']
    register_node(nodes)
    nodes_names.add(nodes)
    return "new node registered"


@app.route('/blockchain/<string:name>')
def personal_blockchain(name):
    chain = []
    t = nodes.get(name).get_chain()
    for block in t:
        tmp = block.get_data()["transactions"]
        block.get_data()["transactions"] = []
        for transaction in tmp:
            if (transaction != []):
                block.get_data()["transactions"].append(transaction.__dict__)
        chain.append(block.get_data())
    return jsonify(chain), 200


app.run(debug=True, host='0.0.0.0', port=5000)
