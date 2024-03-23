# Controle de Mercadorias
Este projeto é um sistema de controle de mercadorias destinado a pequenas e médias empresas. Ele permite aos usuários gerenciar seu inventário de produtos, incluindo adição, edição, exclusão e visualização de itens. O sistema também suporta o rastreamento de vendas e estoque em tempo real.

## Requisitos do Sistema
Para executar o sistema de controle de mercadorias, você precisará dos seguintes requisitos:

Python 3.x: Certifique-se de ter o Python 3.x instalado em seu sistema. Você pode baixar e instalar a versão mais recente do Python no site oficial: python.org.

Flask: O sistema utiliza o framework Flask para desenvolvimento web em Python. Você pode instalar o Flask usando o pip, o gerenciador de pacotes do Python. Execute o seguinte comando no terminal para instalar o Flask: pip install Flask

SQLite3: O sistema utiliza o SQLite como banco de dados. O SQLite geralmente já está incluído na instalação padrão do Python. Se não estiver instalado, você pode instalá-lo separadamente ou usar o suporte SQLite integrado ao Python.

Certifique-se de que todos esses requisitos estejam instalados corretamente em seu sistema antes de prosseguir com a instalação e execução do sistema de controle de mercadorias.

## Instalação
1. Clone o repositório: git clone https://github.com/Alunos-univesp/projeto-integrador-univesp.git
2. Navegue até a pasta do projeto: cd projeto-integrador-univesp
3. Instale as dependências: pip install -r requirements.txt
4. Inicialize o banco de dados: Execute o arquivo create_db.py para criar o banco de dados SQLite necessário para o funcionamento do sistema; python create_db.py
5. Inicie o servidor local: python app.py
6. Acesse o sistema.

## Dicas adicionais:

Certifique-se de ter o Python instalado em seu sistema antes de prosseguir com a instalação.
Ao executar o servidor local, verifique se não há erros no terminal. Se ocorrerem erros, verifique se todas as dependências estão instaladas corretamente.
Caso encontre problemas durante a instalação ou execução, consulte a documentação do projeto ou entre em contato com a equipe de suporte para obter assistência.
Seguindo estas instruções, você poderá instalar, executar e acessar o sistema de controle de mercadorias em sua máquina local.

## Uso

Após concluir a instalação:
Para acessar o sistema de controle de mercadorias, abra o navegador da web de sua preferência e digite o seguinte endereço na barra de URL: http://127.0.0.1:5000/login.

Adicionando um novo produto ao inventário:

1. Após fazer login no sistema, navegue até a seção "Adicionar Produto".

2. Preencha o formulário com as informações necessárias para o novo produto. Certifique-se de fornecer detalhes precisos, como nome, marca, código, custo, quantidade, data de inclusão e data de validade.

3. Após preencher todos os campos obrigatórios do formulário, clique no botão "Adicionar" ou "Salvar" para registrar o novo produto no inventário.

Visualizando produtos no inventário:

Após adicionar novos produtos, você pode visualizá-los na página estoque. Aqui estão algumas etapas para encontrar os produtos:

1. Navegue até a página principal do sistema após fazer login.

2. Procure por uma seção intitulada "Estoque" ou "Lista de Produtos". Você deve encontrar uma lista de todos os produtos disponíveis, incluindo os que você adicionou recentemente.

3.Utilize qualquer funcionalidade de filtro ou pesquisa fornecida pelo sistema para encontrar produtos específicos, se necessário. Por exemplo, você pode filtrar por nome, código, marca, etc.

Dicas adicionais:

Certifique-se de revisar todas as informações antes de adicionar um novo produto para garantir que estejam corretas e atualizadas.
Se precisar editar ou remover um produto existente, navegue até a página de detalhes do produto e utilize as opções fornecidas pelo sistema.
Mantenha seu inventário organizado e atualizado regularmente para refletir com precisão os produtos disponíveis.
Seguindo essas orientações, você poderá navegar pelo sistema, adicionar novos produtos com facilidade e gerenciar seu inventário de forma eficaz.

## Contribuindo

Contribuições são sempre bem-vindas! Se você deseja contribuir, por favor:

1. Faça um fork do projeto:

Fazer um fork significa criar uma cópia do projeto original em sua própria conta do GitHub. Isso permite que você trabalhe em suas próprias alterações sem afetar o projeto original. Para fazer um fork, basta clicar no botão "Fork" no canto superior direito da página do projeto no GitHub.

2. Crie uma nova branch para suas modificações:

Uma branch é uma ramificação do código que permite que você trabalhe em novas funcionalidades ou correções de bugs sem interferir no código principal. Você deve criar uma nova branch para cada conjunto de modificações que você fizer. Por exemplo, você pode nomear a branch de acordo com a funcionalidade que está implementando ou o problema que está corrigindo. Você pode criar uma nova branch usando o comando git checkout -b nome-da-sua-branch.

3. Faça commit das suas alterações:

Depois de fazer suas alterações no código, você precisa confirmá-las localmente usando o comando git commit. Certifique-se de adicionar uma mensagem de commit descritiva que explique as alterações que você fez. Isso ajudará outras pessoas a entenderem suas modificações quando revisarem seu código.

4. Faça push para a branch:

Depois de confirmar suas alterações localmente, você precisa enviá-las para o seu fork no GitHub usando o comando git push. Isso atualizará sua branch remota com as alterações que você fez localmente.

5. Abra um Pull Request:

Depois de enviar suas alterações para o seu fork no GitHub, você pode abrir um Pull Request (PR) para solicitar que suas modificações sejam mescladas ao projeto original. No GitHub, vá para a página do seu fork e clique no botão "New Pull Request". Escolha a branch que você acabou de enviar e a branch principal do projeto original. Forneça uma descrição detalhada das alterações que você fez e clique em "Create Pull Request" para abrir o PR.

Depois de abrir o PR, outros colaboradores poderão revisar suas alterações, fazer comentários e sugerir modificações. Uma vez revisado e aprovado, seu PR poderá ser mesclado ao projeto original pelo mantenedor do projeto.

Seguindo esses passos, você estará contribuindo de forma eficaz para o projeto, ajudando a melhorá-lo e a torná-lo mais robusto para todos os usuários.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para detalhes.

--- 

Espero que isso atenda às suas necessidades! Se precisar de mais alguma coisa, estou à disposição.
