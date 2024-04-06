import threading
import webview
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ControleDeEstoque')))
from app import app  # Importe sua aplicação Flask

def run_flask():
    print("Iniciando servidor Flask...")
    app.run()

if __name__ == '__main__':
    print("Iniciando aplicação...")

    # Inicia o servidor Flask em um thread separado
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    print("Servidor Flask iniciado.")

    # Cria uma janela do PyWebView para exibir a aplicação Flask
    print("Criando janela do PyWebView...")
    webview.create_window('Minha Aplicação Desktop', 'http://localhost:5000', fullscreen=False, width=800, height=600, resizable=True)

    # Inicia a execução do loop de eventos do PyWebView
    webview.start()

    # Aguarda explicitamente o encerramento da aplicação pelo usuário
    input("Pressione Enter para encerrar o programa...")
