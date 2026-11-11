# RondoPesca

Projeto Django para reunir pescadores e informações sobre pesca em Rondônia. O sistema conecta informações sobre peixes, locais de pesca e eventos, e também oferece dicas e uma área para a comunidade compartilhar experiências.

O RondoPesca é organizado em aplicativos Django. O site já oferece comunidade, dicas, eventos, locais de pesca, perfis de usuário e formulário de contato. O código também possui modelos para peixes e tipos de peixe, embora ainda não exista uma página de catálogo dessas informações.

**Objetivo**

Criar um sistema de pesca com informações sobre peixes, tipos de peixe, locais e eventos, utilizando Django para organizar e conectar todas essas partes.

**O que instalar**

Instale o Python 3.12 ou mais recente e o Git. O projeto usa Django 6.1.1 e Pillow 13.0.0. As demais bibliotecas estão listadas em `requeriments.txt` e serão instaladas junto com o projeto.

O banco de dados padrão é SQLite, que já vem com o Python. Não é necessário instalar outro banco para executar o projeto localmente. O site carrega Bootstrap e Bootstrap Icons pela internet, então alguns estilos e ícones precisam de conexão.

**Como baixar o projeto**

Abra o PowerShell ou um terminal na pasta em que deseja guardar o projeto e execute:

```powershell
git clone https://github.com/Thigas3Bti/RPDjango.git
cd RPDjango
```

Se o projeto já estiver baixado, abra o terminal na pasta `RPDjango`, onde está o arquivo `manage.py`.

**Criar e ativar o ambiente virtual**

A `.venv` é um ambiente isolado de Python para este projeto. Ela guarda as dependências do RondoPesca sem misturá-las com as de outros projetos.

Crie o ambiente virtual uma vez, dentro da pasta do projeto:

```powershell
python -m venv .venv
```

Se o comando `python` não funcionar no Windows, tente:

```powershell
py -m venv .venv
```

No PowerShell, ative a `.venv` com:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Prompt de Comando do Windows, use:

```cmd
.venv\Scripts\activate.bat
```

No macOS ou Linux, use:

```bash
source .venv/bin/activate
```

Quando o ambiente estiver ativo, normalmente `(.venv)` aparece no começo da linha do terminal. Sempre ative a `.venv` antes de instalar dependências ou executar o site. Se fechar o terminal, abra outro e ative-a novamente; não precisa criá-la de novo. Para sair do ambiente, digite `deactivate`.

Se o PowerShell bloquear a ativação, permita scripts somente na janela atual e tente novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**Instalar as dependências**

Com `(.venv)` aparecendo no terminal, execute:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requeriments.txt
```

O arquivo tem o nome `requeriments.txt` no projeto; use esse nome exatamente como está escrito.

**Preparar o banco e iniciar o site**

Aplique as migrações para criar as tabelas do banco:

```powershell
python manage.py migrate
```

Crie uma conta de administrador para acessar as áreas administrativas:

```powershell
python manage.py createsuperuser
```

Depois, inicie o servidor local:

```powershell
python manage.py runserver
```

Abra `http://127.0.0.1:8000/` no navegador. 

**Como usar o site**

Na página inicial, você pode conhecer o projeto, entrar na sua conta ou acessar o contato. Crie uma conta e entre para usar os recursos que exigem autenticação. Depois de entrar, use o menu lateral para abrir Início, Comunidade, Dicas, Locais de pesca e Eventos. O menu do usuário permite acessar o perfil ou sair.

Na Comunidade, é possível consultar publicações. Pescadores autorizados podem publicar, comentar e curtir. O autor pode editar ou remover as próprias publicações e comentários.

Em Dicas, consulte conteúdos organizados por nível. A inclusão de novas dicas é uma função administrativa.

Em Locais de pesca, consulte descrições, fotos e links de mapas. Pescadores autorizados podem cadastrar locais e contribuir com informações adicionais e imagens.

Em Eventos, usuários conectados podem consultar eventos públicos, confirmar ou cancelar participação e criar eventos. Cada organizador pode editar ou excluir seus próprios eventos. Eventos pessoais são visíveis somente para quem os criou.

A página Fale conosco permite enviar uma mensagem à equipe. As mensagens ficam registradas no sistema. O envio de uma notificação por e-mail depende da configuração SMTP.

**Contas e permissões**

Uma conta nova é um usuário comum. Para publicar na comunidade e contribuir com locais, ela deve receber o grupo Django `Pescador`. Uma pessoa administradora pode atribuir esse grupo pela página Gerenciar pescadores.

O acesso ao Django Admin, ao gerenciamento de pescadores, às mensagens de contato e à inclusão de dicas é reservado a contas com permissão de equipe (`is_staff`). A conta criada com `createsuperuser` tem essas permissões.

**Configurar o envio de e-mail**

A configuração é opcional. Sem SMTP, as mensagens do formulário de contato continuam sendo salvas no banco. Para ativar o envio usando PowerShell, configure as variáveis antes de iniciar o servidor:

```powershell
$env:EMAIL_HOST_USER = "seu-endereco@example.com"
$env:EMAIL_HOST_PASSWORD = "sua-senha-de-aplicativo"
$env:CONTACT_EMAIL = "destino@example.com"
python manage.py runserver
```

O padrão do projeto é Gmail (`smtp.gmail.com`), porta `587`, com TLS. Para contas Google, use uma senha de aplicativo, não a senha normal da conta. Nunca salve credenciais no código nem as envie ao GitHub. Essas variáveis duram enquanto a janela atual do PowerShell estiver aberta.

**Estrutura do projeto**

```text
RPDjango/
  config/       Configurações e URLs principais do Django
  web/          Páginas gerais, login, contato, dicas e perfil
  usuarios/     Perfis e gerenciamento de pescadores
  forum/        Comunidade, publicações, comentários e eventos
  locais/       Cadastro e consulta de locais de pesca
  templates/    Templates globais do site
  static/       CSS, JavaScript e imagens
  media/        Arquivos enviados, como fotos
  manage.py     Comandos de administração do Django
  requeriments.txt
```

**Equipe e contribuições**

As contribuições foram identificadas no histórico de commits do repositório. Como o projeto recebeu merges entre as branches, os exemplos abaixo destacam mudanças encontradas nos commits e não indicam autoria exclusiva de todas as partes relacionadas.

**Thiago** trabalhou na apresentação e nas páginas do site. Entre suas contribuições estão a página de locais de pesca, melhorias de CSS, ajustes na página inicial e no contato, links de mapa nos eventos e ações para editar e excluir publicações. Exemplos: [1fb40e9](https://github.com/Thigas3Bti/RPDjango/commit/1fb40e9), [78defdb](https://github.com/Thigas3Bti/RPDjango/commit/78defdb) e [0f39dfd](https://github.com/Thigas3Bti/RPDjango/commit/0f39dfd).

**Dhiogo Dainese** contribuiu para o cadastro e as permissões de usuários, validações de e-mail, moderação da comunidade, consulta de mensagens de contato, níveis de usuário e eventos. Exemplos: [4589ee2](https://github.com/Thigas3Bti/RPDjango/commit/4589ee2), [1e961cc](https://github.com/Thigas3Bti/RPDjango/commit/1e961cc) e [ae1f64e](https://github.com/Thigas3Bti/RPDjango/commit/ae1f64e).

**Gabriel** trabalhou na página de dicas, em sua apresentação com cartões interativos, na organização do código relacionado às dicas, em um atalho para acessá-las e em ajustes da página surpresa e da moderação. Exemplos: [75c2de7](https://github.com/Thigas3Bti/RPDjango/commit/75c2de7), [8658388](https://github.com/Thigas3Bti/RPDjango/commit/8658388) e [c2fe3a2](https://github.com/Thigas3Bti/RPDjango/commit/c2fe3a2).

**Rafael S. S.** contribuiu para os perfis e a organização do código, incluindo a opção de biografia, ajustes na foto e na página de perfil, separação de CSS e JavaScript do HTML, formulários e testes. Exemplos: [55046db](https://github.com/Thigas3Bti/RPDjango/commit/55046db) e [e5a4e29](https://github.com/Thigas3Bti/RPDjango/commit/e5a4e29).

**Comandos úteis**

Para verificar a configuração do projeto:

```powershell
python manage.py check
```

Para executar os testes:

```powershell
python manage.py test
```

O `runserver` é para desenvolvimento local. Antes de publicar o site, configure as opções de segurança, o domínio permitido, os arquivos estáticos e os arquivos enviados. Não use credenciais de desenvolvimento em produção.
