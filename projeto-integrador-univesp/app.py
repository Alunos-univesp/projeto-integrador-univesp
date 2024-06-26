import sys
import logging
from flask import Flask, render_template, request, redirect, url_for, g, flash, jsonify
import os
import sqlite3
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

def get_cred_file_path():
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    cred_file_name = 'controle-de-mercadoria-firebase-adminsdk-z1zlf-036e096d97.json'
    return os.path.join(application_path, cred_file_name)

logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Restante do código...


cred_path = get_cred_file_path()
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.secret_key = 'UNIVESP'

DATABASE = os.path.join(os.getcwd(), 'meu_banco_de_dados.db')
SAIDAS_DATABASE = os.path.join(os.getcwd(), 'produtos_que_sairam.db')

def get_db(database=None):
    if database is None:
        database = DATABASE
    db = getattr(g, '_database_' + database, None)
    if db is None:
        db = sqlite3.connect(database)
        db.row_factory = sqlite3.Row
        setattr(g, '_database_' + database, db)
    return db

def init_db():
    with app.app_context():
        db_main = get_db()
        db_main.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                codigo REAL NOT NULL DEFAULT 0.0,
                custo REAL,
                marca TEXT,
                informacoes TEXT,
                quantidade INTEGER,
                data_inclusao TEXT,
                data_validade TEXT
            );
        ''')
        db_main.execute('''
            CREATE TABLE IF NOT EXISTS saidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                data_saida TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            );
        ''')
        db_main.commit()

        db_saidas = get_db(SAIDAS_DATABASE)
        db_saidas.execute('''
            CREATE TABLE IF NOT EXISTS produtos_saidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                marca TEXT NOT NULL,
                custo REAL NOT NULL,
                quantidade INTEGER NOT NULL,
                data_saida TEXT NOT NULL
            )
        ''')
        db_saidas.commit()

@app.teardown_appcontext
def close_connection(exception):
    db_main = getattr(g, '_database', None)
    if db_main is not None:
        db_main.close()
    db_saidas = getattr(g, '_database_' + SAIDAS_DATABASE, None)
    if db_saidas is not None:
        db_saidas.close()

def sincronizar_produtos_com_sqlite():
    produtos_ref = db.collection('produtos')
    docs = produtos_ref.stream()
    db_sqlite = get_db()
    for doc in docs:
        produto = doc.to_dict()
        existe = db_sqlite.execute('SELECT id FROM produtos WHERE id = ?', (doc.id,)).fetchone()
        if not existe:
            db_sqlite.execute('''INSERT INTO produtos (id, nome, codigo, custo, marca, informacoes, quantidade, data_inclusao, data_validade) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                (doc.id, produto.get('nome'), produto.get('codigo'), produto.get('custo'), produto.get('marca'), produto.get('informacoes'), produto.get('quantidade'), produto.get('data_inclusao'), produto.get('data_validade')))
        else:
            db_sqlite.execute('''UPDATE produtos SET nome=?, codigo=?, custo=?, marca=?, informacoes=?, quantidade=?, data_inclusao=?, data_validade=? WHERE id=?''',
                                (produto.get('nome'), produto.get('codigo'), produto.get('custo'), produto.get('marca'), produto.get('informacoes'), produto.get('quantidade'), produto.get('data_inclusao'), produto.get('data_validade'), doc.id))
        db_sqlite.commit()

def add_produto_saida(produto_id, nome, marca, custo, quantidade):
    with app.app_context():
        db = get_db(SAIDAS_DATABASE)
        data_saida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute('INSERT INTO produtos_saidas (produto_id, nome, marca, custo, quantidade, data_saida) VALUES (?, ?, ?, ?, ?, ?)',
                   (produto_id, nome, marca, custo, quantidade, data_saida))
        db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/estoque', methods=['GET', 'POST'])
def estoque():
    db = get_db()
    if request.method == 'POST':
        filtro_nome = request.form.get('filtro_nome', '')
        filtro_codigo = request.form.get('filtro_codigo', '')
        filtro_marca = request.form.get('filtro_marca', '')
    else:
        filtro_nome = request.args.get('filtro_nome', '')
        filtro_codigo = request.args.get('filtro_codigo', '')
        filtro_marca = request.args.get('filtro_marca', '')

    query = '''
    SELECT id, nome, codigo, custo, marca, informacoes, quantidade, data_inclusao, data_validade,
    ROUND(JulianDay(data_validade) - JulianDay('now')) AS dias_ate_vencimento
    FROM produtos
    '''
    conditions = []
    params = []

    if filtro_nome:
        conditions.append("nome LIKE ?")
        params.append('%' + filtro_nome + '%')

    if filtro_codigo:
        conditions.append("codigo LIKE ?")
        params.append('%' + filtro_codigo + '%')

    if filtro_marca:
        conditions.append("marca LIKE ?")
        params.append('%' + filtro_marca + '%')

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    produtos = db.execute(query, params).fetchall()

    return render_template('estoque.html', produtos=[dict(produto) for produto in produtos])

@app.route('/excluir-produto/<int:id>', methods=['POST'])
def excluir_produto(id):
    db = get_db()
    db.execute('DELETE FROM produtos WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('estoque'))

@app.route('/editar-produto/<string:produto_id>', methods=['GET', 'POST'])
def editar_produto(produto_id):
    if request.method == 'GET':
        produto_ref = db.collection('produtos').document(produto_id)
        produto_data = produto_ref.get().to_dict()
        return render_template('editar_produto.html', produto=produto_data)
    elif request.method == 'POST':
        nome_produto = request.form['nomeProduto']
        marca_produto = request.form['marcaProduto']
        informacoes_produto = request.form['informacoesProduto']
        codigo = request.form['codigo']
        custo = float(request.form['custo'])
        quantidade = int(request.form['quantidadeProduto'])
        data_cadastro = request.form['dataCadastro']
        data_validade = request.form['dataValidade']
        produto_ref = db.collection('produtos').document(produto_id)
        produto_ref.update({
            'nome': nome_produto,
            'marca': marca_produto,
            'informacoes': informacoes_produto,
            'codigo': codigo,
            'custo': custo,
            'quantidade': quantidade,
            'data_inclusao': data_cadastro,
            'data_validade': data_validade
        })
        return redirect(url_for('estoque'))

@app.route('/cadastro-mercadoria', methods=['GET', 'POST'])
def cadastro_mercadoria():
    if request.method == 'POST':
        nome_produto = request.form.get('nomeProduto')
        marca_produto = request.form.get('marcaProduto')
        informacoes_produto = request.form.get('informacoesProduto')
        codigo = request.form.get('codigo')
        custo = request.form.get('custo')
        quantidade = request.form.get('quantidadeProduto')
        data_cadastro = request.form.get('dataCadastro')
        data_validade = request.form.get('dataValidade')
        
        db_sqlite = get_db()
        db_sqlite.execute('''INSERT INTO produtos (nome, marca, informacoes, custo, quantidade, data_inclusao, data_validade, codigo) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (nome_produto, marca_produto, informacoes_produto, custo, quantidade, data_cadastro, data_validade, codigo))
        db_sqlite.commit()
        flash('Produto cadastrado com sucesso.', 'success')
        return redirect(url_for('estoque'))
    return render_template('cadastro-mercadoria.html')

@app.route('/lista-produtos-proximo-vencimento')
def lista_produtos_proximo_vencimento():
    db = get_db()
    query = '''
    SELECT id, nome, codigo, custo, marca, informacoes, quantidade, data_inclusao, data_validade,
    ROUND(JulianDay(data_validade) - JulianDay('now')) AS dias_ate_vencimento
    FROM produtos
    WHERE JulianDay(data_validade) - JulianDay('now') <= 30
    '''
    produtos = db.execute(query).fetchall()
    return render_template('lista_produtos_proximo_vencimento.html', produtos=[dict(produto) for produto in produtos])

@app.route('/saida-mercadorias')
def saida_mercadorias():
    return render_template('saida_mercadorias.html')

@app.route('/processar-venda', methods=['POST'])
def processar_venda():
    produto_id = request.form.get('produto_id')
    quantidade_vendida = int(request.form.get('quantidade'))
    db = get_db()
    produto = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
    if produto and produto['quantidade'] >= quantidade_vendida:
        nova_quantidade = produto['quantidade'] - quantidade_vendida
        db.execute('UPDATE produtos SET quantidade = ? WHERE id = ?', (nova_quantidade, produto_id))
        db.commit()
        add_produto_saida(produto_id, produto['nome'], produto['marca'], produto['custo'], quantidade_vendida)
        flash('Venda processada com sucesso!', 'success')
    else:
        flash('Erro: Quantidade insuficiente em estoque.', 'danger')
    return redirect(url_for('estoque'))

@app.route('/registrar_saida', methods=['POST'])
def registrar_saida():
    produto_id = request.form.get('produto_id')
    quantidade = int(request.form.get('quantidade'))
    db = get_db()
    produto = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
    if produto and produto['quantidade'] >= quantidade:
        nova_quantidade = produto['quantidade'] - quantidade
        db.execute('UPDATE produtos SET quantidade = ? WHERE id = ?', (nova_quantidade, produto_id))
        db.commit()
        add_produto_saida(produto_id, produto['nome'], produto['marca'], produto['custo'], quantidade)
        flash('Saída de produto registrada com sucesso!', 'success')
    else:
        flash('Erro: Produto não encontrado ou quantidade insuficiente.', 'danger')
    return redirect(url_for('estoque'))



@app.route('/diminuir-quantidade', methods=['POST'])
def diminuir_quantidade():
    produto_id = request.form['produto_id']
    quantidade_a_diminuir = int(request.form['quantidade'])

    # Obtém a referência do documento do produto
    produto_ref = db.collection('produtos').document(produto_id)
    produto_doc = produto_ref.get()

    if produto_doc.exists:
        produto_data = produto_doc.to_dict()
        quantidade_atual = produto_data.get('quantidade', 0)

        # Se a quantidade a diminuir for maior que a disponível, ajusta para o máximo possível
        quantidade_a_diminuir = min(quantidade_a_diminuir, quantidade_atual)
        nova_quantidade = quantidade_atual - quantidade_a_diminuir

        # Atualiza a quantidade no Firestore
        produto_ref.update({'quantidade': nova_quantidade})

        return jsonify({
            "sucesso": True,
            "mensagem": f"Quantidade do produto {produto_id} atualizada com sucesso. Nova quantidade: {nova_quantidade}.",
            "quantidade_diminuida": quantidade_a_diminuir,
            "nova_quantidade": nova_quantidade
        }), 200

    return jsonify({"sucesso": False, "mensagem": "Produto não encontrado."}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
