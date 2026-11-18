# Manual do usuário - RondoPesca

Este manual explica como usar o sistema RondoPesca sem conhecimentos técnicos.

## Como ler este manual

Cada seção indica a tela, o caminho no menu e os principais campos. Para ilustrar as instruções durante uma demonstração, utilize as capturas das telas reais obtidas no navegador; mantenha os exemplos sem dados pessoais.

```text
Tela ilustrada esperada
+--------------------------------------------------+
| RondoPesca  |  Menu lateral  |  Usuário          |
|--------------------------------------------------|
| Conteúdo da página selecionada                   |
| Botão principal da tarefa                        |
+--------------------------------------------------+
```

## 1. Acessar o sistema

1. Abra o navegador e acesse `http://127.0.0.1:8000/`.
2. Na página inicial pública, escolha **Entrar**.
3. Informe o usuário e a senha.
4. Após entrar, use o menu lateral para acessar as áreas do sistema.

O servidor local pode ser iniciado pelo comando `python manage.py runserver`.

## 2. Criar uma conta

1. Acesse a página inicial.
2. Escolha a opção de cadastro.
3. Preencha os dados solicitados.
4. Confirme o cadastro e faça login.

Uma conta nova tem acesso comum. Recursos de publicação podem exigir aprovação no grupo **Pescador**.

## 3. Usar o perfil

1. Clique no nome do usuário no canto superior direito.
2. Escolha **Ver perfil**.
3. Na edição do perfil, altere foto e informações permitidas.
4. Salve as alterações.

## 4. Consultar e publicar na comunidade

1. Clique em **Comunidade** no menu lateral.
2. Leia as publicações existentes.
3. Usuários do grupo Pescador podem criar uma publicação.
4. Ao criar uma publicação, informe título, local e texto.
5. O autor pode editar ou remover suas próprias publicações e comentários.

Também é possível comentar e curtir publicações aprovadas.

## 5. Consultar dicas

1. Clique em **Dicas**.
2. Escolha uma dica para consultar o conteúdo.
3. As dicas são organizadas pelos níveis iniciantes, intermediários e avançados.

Somente contas administrativas podem adicionar ou administrar dicas.

## 6. Consultar locais de pesca

1. Clique em **Locais de pesca**.
2. Use a lista para consultar nome, município, descrição e fotos.
3. Quando permitido, Pescadores podem cadastrar locais ou adicionar informações.
4. Use o link de mapa, quando disponível, para abrir a localização no Google Maps.

## 7. Consultar e criar eventos

1. Clique em **Eventos**.
2. Consulte eventos públicos e seus dados.
3. Usuários conectados podem confirmar ou cancelar participação.
4. A opção de criação permite informar nome, data, hora, local, mapa e descrição.
5. O organizador pode editar ou excluir seus próprios eventos.

Eventos pessoais são exibidos apenas para quem os criou.

## 8. Consultar equipamentos

1. Clique em **Equipamentos**.
2. Consulte os equipamentos disponíveis e suas descrições.
3. Contas autorizadas podem cadastrar novos equipamentos.

## 9. Fale conosco

1. Clique em **Fale conosco** no rodapé lateral.
2. Preencha nome, assunto, e-mail e mensagem.
3. Envie o formulário.
4. A mensagem fica registrada para consulta por uma conta administrativa.

## 10. Funções administrativas

Contas com acesso administrativo podem usar o Django Admin e as áreas internas para:

- gerenciar pescadores;
- consultar mensagens de contato;
- cadastrar dicas;
- atender solicitações de redefinição de senha;
- acessar os registros cadastrados no sistema.

## 11. Conta de demonstração

Durante o desenvolvimento, o comando `python manage.py runserver` cria dados locais idempotentes.
A conta criada para demonstração é `demo`, com senha padrão `rondopesca123`.

Para iniciar com outra senha, configure antes do servidor:

```powershell
$env:DEMO_PASSWORD = "uma-senha-nova"
python manage.py runserver
```

Essa conta deve ser removida ou protegida antes de uma publicação pública.

## 12. Checklist visual da demonstração

Use estas telas nesta ordem durante a apresentação:

1. Página inicial: domínio do problema e opções públicas.
2. Cadastro e login: criação da conta e acesso autenticado.
3. Comunidade: publicação, comentário e curtida.
4. Locais de pesca: consulta e cadastro autorizado.
5. Eventos: consulta, participação e edição pelo organizador.
6. Perfil: alteração de foto e informações.
7. Área administrativa: gestão de pescadores, dicas e mensagens.
8. Página 404: endereço inexistente com navegação de retorno.
