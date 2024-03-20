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
    # Se nenhum banco de dados for especificado, usa o banco de dados principal
    if database is None:
        database = DATABASE
    # Tenta recuperar uma conexão de banco de dados existente do contexto global 'g'
    db = getattr(g, '_database_' + database, None)
    # Se não houver conexão existente, cria uma nova
    if db is None:
        db = sqlite3.connect(database)
        db.row_factory = sqlite3.Row  # Configura a fábrica de linhas para retornar dicionários
        setattr(g, '_database_' + database, db)  # Salva a conexão no contexto global 'g' para reuso
    return db

# Função para inicializar o banco de dados dos produtos que saíram
def init_saidas_db():
    with app.app_context():  # Usa o contexto da aplicação para garantir acesso aos recursos do Flask
        db = get_db(SAIDAS_DATABASE)  # Obtém a conexão com o banco de dados de saídas
        # Cria a tabela de saídas de produtos, se ainda não existir
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
        db.commit()  # Salva as mudanças no banco de dados


# Função para adicionar produtos que saíram ao banco de dados de saída
def add_produto_saida(produto_id, nome, marca, custo, quantidade):
    with app.app_context():  # Garante que a função seja executada no contexto da aplicação Flask
        db = get_db(SAIDAS_DATABASE)  # Obtém a conexão com o banco de dados de saídas
        # Formata a data atual no formato apropriado para armazenamento
        data_saida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Insere o registro da saída do produto na tabela de saídas
        db.execute('INSERT INTO produtos_saidas (produto_id, nome, marca, custo, quantidade, data_saida) VALUES (?, ?, ?, ?, ?, ?)',
                   (produto_id, nome, marca, custo, quantidade, data_saida))
        db.commit()  # Salva as alterações no banco de dados

def init_db():
    with app.app_context():  # Usa o contexto da aplicação para garantir o acesso aos recursos do Flask
        db = get_db()  # Obtém a conexão com o banco de dados principal
        # Cria a tabela de produtos no banco de dados, se ainda não existir
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
        # Cria a tabela de saídas no banco de dados, se ainda não existir
        # Essa tabela armazena os registros de produtos que saíram do estoque
        db.execute('''
            CREATE TABLE IF NOT EXISTS saidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                data_saida TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            );
        ''')
        # Chama a função para inicializar o banco de dados de produtos que saíram
        init_saidas_db()
        db.commit()  # Salva as alterações no banco de dados
# Fecha a conexão com o banco de dados quando o contexto da aplicação termina
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)  # Tenta obter a conexão com o banco de dados do contexto global
    if db is not None:
        db.close()  # Fecha a conexão se existir

# Rota para a página inicial
@app.route('/')
def index():
    # Renderiza o template da página inicial
    return render_template('index.html')

# Rota para a página de login
@app.route('/login')
def login():
    # Renderiza o template da página de login
    return render_template('login.html')

# Rota para a página home após login
@app.route('/home')
def home():
    # Renderiza o template da página home
    return render_template('home.html')

# Rota para visualizar e filtrar o estoque
@app.route('/estoque', methods=['GET', 'POST'])
def estoque():
    db = get_db()  # Obtém a conexão com o banco de dados
    # Diferencia ação baseada no tipo de requisição: POST para filtro, GET para exibição geral
    if request.method == 'POST':
        filtro_nome = request.form.get('filtro_nome', '')
        filtro_codigo = request.form.get('filtro_codigo', '')
    else:
        filtro_nome = request.args.get('filtro_nome', '')
        filtro_codigo = request.args.get('filtro_codigo', '')

    # Consulta SQL básica para selecionar produtos
    query = '''
    SELECT id, nome, codigo, custo, marca, informacoes, quantidade, data_inclusao, data_validade,
    ROUND(JulianDay(data_validade) - JulianDay('now')) AS dias_ate_vencimento
    FROM produtos
    '''
    conditions = []  # Lista para condições dinâmicas de filtro
    params = []  # Parâmetros para a consulta SQL

    # Adiciona condições de filtro se necessário
    if filtro_nome:
        conditions.append("nome LIKE ?")
        params.append('%' + filtro_nome + '%')

    if filtro_codigo:
        conditions.append("codigo LIKE ?")
        params.append('%' + filtro_codigo + '%')

    # Compõe a consulta final com as condições de filtro
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    produtos = db.execute(query, params).fetchall()  # Executa a consulta

    # Renderiza o template do estoque com os produtos filtrados
    return render_template('estoque.html', produtos=[dict(produto) for produto in produtos])

# Rota para excluir um produto específico
@app.route('/excluir-produto/<int:id>', methods=['GET', 'POST'])
def excluir_produto(id):
    db = get_db()
    db.execute('DELETE FROM produtos WHERE id = ?', (id,))  # Executa a exclusão
    db.commit()
    return redirect(url_for('estoque'))  # Redireciona de volta para a página de estoque

# Rota para editar as informações de um produto específico
@app.route('/editar-produto/<int:produto_id>', methods=['GET', 'POST'])
def editar_produto(produto_id):
    db = get_db()
    produto = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()  # Obtém o produto pelo ID
    if request.method == 'POST':  # Atualiza os dados do produto se a requisição for POST
        # Obtém os dados atualizados do formulário
        nome_produto = request.form['nomeProduto']
        marca_produto = request.form['marcaProduto']
        informacoes_produto = request.form['informacoesProduto']
        codigo = request.form['codigo']
        custo = request.form['custo']
        quantidade = request.form['quantidadeProduto']
        data_cadastro = request.form['dataCadastro']
        data_validade = request.form['dataValidade']
        
        # Atualiza o produto no banco de dados
        db.execute('''UPDATE produtos SET nome = ?, marca = ?, informacoes = ?, codigo = ?, custo = ?, 
                      quantidade = ?, data_inclusao = ?, data_validade = ? WHERE id = ?''',
                   (nome_produto, marca_produto, informacoes_produto, codigo, custo, quantidade, data_cadastro, data_validade, produto_id))
        db.commit()
        return redirect(url_for('estoque'))  # Redireciona para a página de estoque
    # Renderiza o template de edição de produto com os dados atuais do produto
    return render_template('editar_produto.html', produto=produto)

# Rota para cadastrar uma nova mercadoria
@app.route('/cadastro-mercadoria', methods=['GET', 'POST'])
def cadastro_mercadoria():
    if request.method == 'POST':  # Processa o cadastro de uma nova mercadoria
        # Obtém os dados do formulário
        nome_produto = request.form.get('nomeProduto')
        marca_produto = request.form.get('marcaProduto')
        informacoes_produto = request.form.get('informacoesProduto')
        codigo = request.form.get('codigo')
        custo = request.form.get('custo')
        quantidade = request.form.get('quantidadeProduto')
        data_cadastro = request.form.get('dataCadastro')
        data_validade = request.form.get('dataValidade')
        
        db = get_db()
        # Insere a nova mercadoria no banco de dados
        db.execute('''INSERT INTO produtos (nome, marca, informacoes, custo, quantidade, data_inclusao, data_validade, codigo) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (nome_produto, marca_produto, informacoes_produto, custo, quantidade, data_cadastro, data_validade, codigo))
        db.commit()
        return redirect(url_for('cadastro_mercadoria'))  # Redireciona para a página de cadastro
    # Renderiza o template de cadastro de mercadoria
    return render_template('cadastro-mercadoria.html')

# Rota para listar produtos próximos ao vencimento
@app.route('/lista-produtos-proximo-vencimento')
def lista_produtos_proximo_vencimento():
    db = get_db()  # Obtém a conexão com o banco de dados
    # Consulta produtos com data de validade próxima
    query = '''
    SELECT id, nome, codigo, custo, marca, informacoes, quantidade, data_inclusao, data_validade,
    ROUND(JulianDay(data_validade) - JulianDay('now')) AS dias_ate_vencimento
    FROM produtos
    WHERE JulianDay(data_validade) - JulianDay('now') <= 30
    '''
    produtos = db.execute(query).fetchall()  # Executa a consulta
    # Renderiza o template da lista de produtos próximos ao vencimento
    return render_template('lista_produtos_proximo_vencimento.html', produtos=[dict(produto) for produto in produtos])

# Rota para a página de registro de saída de mercadorias
@app.route('/saida-mercadorias')
def saida_mercadorias():
    # Renderiza o template da página de saída de mercadorias
    return render_template('saida_mercadorias.html')

# Rota para registrar a saída de um produto
@app.route('/registrar_saida', methods=['POST'])
def registrar_saida():
    # Obtém os dados do formulário
    produto_id = request.form.get('produto_id')
    codigo = request.form.get('codigo')
    quantidade = int(request.form.get('quantidade'))

    db = get_db()  # Obtém a conexão com o banco de dados
    # Encontra o produto correspondente baseado no ID ou código
    if produto_id and codigo:
        produto = db.execute('SELECT * FROM produtos WHERE id = ? AND codigo = ?', (produto_id, codigo)).fetchone()
    elif produto_id:
        produto = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
    elif codigo:
        produto = db.execute('SELECT * FROM produtos WHERE codigo = ?', (codigo,)).fetchone()
    else:
        return "Produto não especificado corretamente."

    # Verifica se a quantidade solicitada está disponível e registra a saída
    if produto and quantidade <= produto['quantidade']:
        nova_quantidade = produto['quantidade'] - quantidade
        db.execute('UPDATE produtos SET quantidade = ? WHERE id = ?', (nova_quantidade, produto['id']))
        db.commit()
        # Adiciona o registro de saída no banco de dados
        add_produto_saida(produto['id'], produto['nome'], produto['marca'], produto['custo'], quantidade)
        mensagem = 'Saída de mercadoria registrada com sucesso.'
    else:
        mensagem = 'Erro: Quantidade solicitada maior do que a disponível ou produto não encontrado.'

    # Renderiza o template de saída de mercadorias com a mensagem de resultado
    return render_template('saida_mercadorias.html', mensagem=mensagem)

# Rota para selecionar o intervalo de datas para o relatório de saídas de produtos
@app.route('/selecionar-intervalo-datas')
def selecionar_intervalo_datas():
    # Renderiza o template para selecionar o intervalo de datas
    return render_template('selecionar_intervalo_datas.html')

# Rota para filtrar saídas de produtos baseado no intervalo de datas selecionado
@app.route('/filtro-saida-produtos', methods=['GET'])
def filtro_saida_produtos():
    # Calcula a data inicial como hoje menos 90 dias
    data_inicio = datetime.now() - timedelta(days=90)
    data_fim = datetime.now()  # Data final é a data atual

    db = get_db(SAIDAS_DATABASE)  # Obtém a conexão com o banco de dados de saídas
    # Consulta para selecionar saídas de produtos no intervalo de datas
    query = '''
    SELECT nome, marca, custo, quantidade, data_saida
    FROM produtos_saidas
    WHERE data_saida BETWEEN ? AND ?
    ORDER BY data_saida
    '''
    produtos = db.execute(query, (data_inicio, data_fim)).fetchall()  # Executa a consulta

    # Renderiza o template do filtro de saída de produtos com os resultados
    return render_template('filtro_saida_produtos.html', data_inicio=data_inicio, data_fim=data_fim, produtos=produtos)


# Verifica se o script está sendo executado diretamente (não importado)
if __name__ == '__main__':
    # Executa o bloco de código dentro do contexto da aplicação Flask
    with app.app_context():
        init_db()  # Chama a função para inicializar o banco de dados
    # Inicia o servidor web da aplicação Flask
    app.run(debug=True)  # O parâmetro debug=True ativa o modo de depuração
