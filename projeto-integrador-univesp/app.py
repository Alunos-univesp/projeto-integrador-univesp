from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Define o caminho para o banco de dados SQLite principal
DATABASE = os.path.join(os.getcwd(), 'meu_banco_de_dados.db')

# Define o caminho para o banco de dados SQLite dos produtos que saíram
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

# Função para inicializar o banco de dados dos produtos que saíram
def init_saidas_db():
    with app.app_context():
        db = get_db(SAIDAS_DATABASE)
        db.execute('''
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
        db.commit()


def add_produto_saida(produto_id, nome, marca, custo, quantidade):
    with app.app_context():
        db = get_db(SAIDAS_DATABASE)
        data_saida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute('INSERT INTO produtos_saidas (produto_id, nome, marca, custo, quantidade, data_saida) VALUES (?, ?, ?, ?, ?, ?)',
                   (produto_id, nome, marca, custo, quantidade, data_saida))
        db.commit()


def init_db():
    with app.app_context():
        db = get_db()
        # Criar tabela de produtos, se não existir
        db.execute('''
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
        # Criar tabela de saidas, se não existir
        db.execute('''
            CREATE TABLE IF NOT EXISTS saidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                data_saida TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            );
        ''')
        # Inicializar o banco de dados de produtos que saíram
        init_saidas_db()
        db.commit()

# Função para adicionar produtos que saíram ao banco de dados de saída
def add_produto_saida(produto_id, nome, marca, custo, quantidade):
    with app.app_context():
        db = get_db(SAIDAS_DATABASE)
        data_saida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute('INSERT INTO produtos_saidas (produto_id, nome, marca, custo, quantidade, data_saida) VALUES (?, ?, ?, ?, ?, ?)',
                   (produto_id, nome, marca, custo, quantidade, data_saida))
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        # Criar tabela de produtos, se não existir
        db.execute('''
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
        # Criar tabela de saidas, se não existir
        db.execute('''
            CREATE TABLE IF NOT EXISTS saidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                data_saida TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            );
        ''')
        # Inicializar o banco de dados de produtos que saíram
        init_saidas_db()
        db.commit()

def init_saidas_db():
    with app.app_context():
        db = get_db(SAIDAS_DATABASE)
        db.execute('''
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
    else:
        filtro_nome = request.args.get('filtro_nome', '')
        filtro_codigo = request.args.get('filtro_codigo', '')

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

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    produtos = db.execute(query, params).fetchall()

    return render_template('estoque.html', produtos=[dict(produto) for produto in produtos])

@app.route('/excluir-produto/<int:id>', methods=['GET', 'POST'])
def excluir_produto(id):
    db = get_db()
    db.execute('DELETE FROM produtos WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('estoque'))

@app.route('/editar-produto/<int:produto_id>', methods=['GET', 'POST'])
def editar_produto(produto_id):
    db = get_db()
    produto = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
    if request.method == 'POST':
        nome_produto = request.form['nomeProduto']
        marca_produto = request.form['marcaProduto']
        informacoes_produto = request.form['informacoesProduto']
        codigo = request.form['codigo']
        custo = request.form['custo']
        quantidade = request.form['quantidadeProduto']
        data_cadastro = request.form['dataCadastro']
        data_validade = request.form['dataValidade']
        
        db.execute('''UPDATE produtos SET nome = ?, marca = ?, informacoes = ?, codigo = ?, custo = ?, 
                      quantidade = ?, data_inclusao = ?, data_validade = ? WHERE id = ?''',
                   (nome_produto, marca_produto, informacoes_produto, codigo, custo, quantidade, data_cadastro, data_validade, produto_id))
        db.commit()
        return redirect(url_for('estoque'))
    return render_template('editar_produto.html', produto=produto)

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
        
        db = get_db()
        db.execute('''INSERT INTO produtos (nome, marca, informacoes, custo, quantidade, data_inclusao, data_validade, codigo) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (nome_produto, marca_produto, informacoes_produto, custo, quantidade, data_cadastro, data_validade, codigo))
        db.commit()
        return redirect(url_for('cadastro_mercadoria'))  
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

@app.route('/registrar_saida', methods=['POST'])
def registrar_saida():
    produto_id = request.form.get('produto_id')
    codigo = request.form.get('codigo')
    quantidade = int(request.form.get('quantidade'))

    db = get_db()
    # Verifica se ambos, ID e Código, foram fornecidos e encontra o produto correspondente
    if produto_id and codigo:
        produto = db.execute('SELECT * FROM produtos WHERE id = ? AND codigo = ?', (produto_id, codigo)).fetchone()
    elif produto_id:
        produto = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
    elif codigo:
        produto = db.execute('SELECT * FROM produtos WHERE codigo = ?', (codigo,)).fetchone()
    else:
        return "Produto não especificado corretamente."

    if produto and quantidade <= produto['quantidade']:
        nova_quantidade = produto['quantidade'] - quantidade
        db.execute('UPDATE produtos SET quantidade = ? WHERE id = ?', (nova_quantidade, produto['id']))
        db.commit()
        # Adiciona a saída do produto ao banco de dados de saídas
        add_produto_saida(produto['id'], produto['nome'], produto['marca'], produto['custo'], quantidade)
        mensagem = 'Saída de mercadoria registrada com sucesso.'
    else:
        mensagem = 'Erro: Quantidade solicitada maior do que a disponível ou produto não encontrado.'

    return render_template('saida_mercadorias.html', mensagem=mensagem)

@app.route('/selecionar-intervalo-datas')
def selecionar_intervalo_datas():
    return render_template('selecionar_intervalo_datas.html')


from datetime import datetime, timedelta

@app.route('/filtro-saida-produtos', methods=['GET'])
def filtro_saida_produtos():
    # Calcula a data atual menos 90 dias
    data_inicio = datetime.now() - timedelta(days=90)
    data_fim = datetime.now()

    db = get_db(SAIDAS_DATABASE)
    query = '''
    SELECT nome, marca, custo, quantidade, data_saida
    FROM produtos_saidas
    WHERE data_saida BETWEEN ? AND ?
    ORDER BY data_saida
    '''
    produtos = db.execute(query, (data_inicio, data_fim)).fetchall()

    return render_template('filtro_saida_produtos.html', data_inicio=data_inicio, data_fim=data_fim, produtos=produtos)



if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
