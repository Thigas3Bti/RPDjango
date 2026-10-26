Apresentação do Projeto RondoPesca
RondoPesca é um projeto desenvolvido em Django, voltado para informações e recursos relacionados à pesca em Rondônia. O sistema utiliza HTML, CSS, Templates, Apps e Models.

Thiago – HTML
Ficarei responsável pelo HTML, criando a estrutura das páginas do RondoPesca, como textos, botões, imagens, menus e formulários.

Dhiogo – CSS
Ficarei responsável pelo CSS, cuidando da aparência do projeto, como cores, fontes, tamanhos, espaçamentos e organização das páginas.

Gabriel – Templates
Ficarei responsável pelos Templates do Django, organizando as páginas e fazendo a ligação entre o HTML e o Django.

Rafael – App e Models
Ficarei responsável pelos Apps e Models, organizando as funcionalidades do projeto e os dados que serão utilizados no banco de dados.

Projeto
O objetivo do RondoPesca é criar um sistema de pesca com informações sobre peixes, tipos de peixe, locais e eventos, utilizando Django para organizar e conectar todas essas partes.

Envio de e-mails
O projeto usa o SMTP do Gmail para enviar a confirmação de cadastro. Para habilitar o envio, gere uma senha de app na Conta do Google (com a verificação em duas etapas ativada) e configure-a no PowerShell antes de iniciar o Django:

```powershell
$env:EMAIL_HOST_PASSWORD = "SUA_SENHA_DE_APP"
python manage.py runserver
```

Não use a senha normal da conta Google nem compartilhe ou versione a senha de app. As demais configurações SMTP já usam `smtp.gmail.com`, porta `587`, TLS e `rondopescacontato@gmail.com` como remetente por padrão. Para limpar a variável ao terminar a sessão do PowerShell:

```powershell
Remove-Item Env:EMAIL_HOST_PASSWORD
```
