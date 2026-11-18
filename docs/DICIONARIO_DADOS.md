# Dicionário de dados

## Principais entidades

| Entidade | Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|---|
| Usuário Django | username | string | Sim | Nome usado para entrar no sistema |
| Usuário Django | email | string | Não | E-mail associado à conta |
| Usuário Django | password | hash | Sim | Senha armazenada de forma protegida |
| Usuário Django | is_staff | boolean | Sim | Autoriza acesso às áreas administrativas |
| Usuário Django | is_superuser | boolean | Sim | Concede todas as permissões administrativas |
| PerfilUsuario | usuario | 1:1 com Usuário | Sim | Perfil complementar |
| PerfilUsuario | foto | arquivo | Não | Foto do perfil |
| PerfilUsuario | bio | texto, até 500 caracteres | Não | Biografia exibida no perfil |
| Publicacao | autor | FK Usuário | Sim | Usuário que publicou |
| Publicacao | titulo | string, até 120 caracteres | Não | Título da publicação |
| Publicacao | local_pescaria | string, até 150 caracteres | Não | Local mencionado |
| Publicacao | texto | texto, até 2000 caracteres | Não | Conteúdo da publicação |
| Publicacao | foto | arquivo | Não | Foto anexada |
| Publicacao | status_moderacao | enum | Sim | aprovada, pendente ou rejeitada |
| Comentario | publicacao | FK Publicacao | Sim | Publicação comentada |
| Comentario | autor | FK Usuário | Sim | Autor do comentário |
| Comentario | texto | string, até 500 caracteres | Sim | Conteúdo do comentário |
| Curtida | publicacao | FK Publicacao | Sim | Publicação curtida |
| Curtida | usuario | FK Usuário | Sim | Usuário que realizou a curtida |
| EventoAgenda | nome | string, até 100 caracteres | Sim | Nome do evento |
| EventoAgenda | data_evento | data | Sim | Dia do evento |
| EventoAgenda | hora_evento | hora | Não | Hora do evento |
| EventoAgenda | local | string, até 150 caracteres | Não | Local informado |
| EventoAgenda | mapa_url | URL | Não | Link externo de localização |
| EventoAgenda | descricao | texto, até 5000 caracteres | Não | Detalhes do evento |
| EventoAgenda | tipo | enum | Sim | pessoal, comunidade ou oficial |
| EventoAgenda | organizador | FK Usuário | Sim | Responsável pelo evento |
| LocalPesca | nome | string, até 120 caracteres | Sim | Nome do local |
| LocalPesca | municipio | enum | Não | Município de Rondônia |
| LocalPesca | descricao | texto, até 2000 caracteres | Sim | Informações sobre o local |
| LocalPesca | imagem_url | URL | Não | Endereço externo da imagem |
| LocalPesca | foto | arquivo | Não | Foto principal |
| LocalPesca | cadastrado_por | FK Usuário | Sim | Usuário responsável pelo cadastro |
| FotoLocal | local | FK LocalPesca | Sim | Local que possui a foto |
| FotoLocal | informacao | FK InformacaoLocal | Não | Vincula a foto a uma contribuição |
| FotoLocal | arquivo | arquivo | Sim | Arquivo da imagem |
| InformacaoLocal | local | FK LocalPesca | Sim | Local complementado |
| InformacaoLocal | autor | FK Usuário | Sim | Autor da contribuição |
| InformacaoLocal | descricao | texto, até 2000 caracteres | Sim | Informação adicional |
| Dica | titulo | string, até 120 caracteres | Sim | Título da dica |
| Dica | nivel/categoria | enum | Sim | iniciante, intermediário, avançado ou veterano |
| Dica | descricao | texto | Não | Conteúdo da dica |
| Dica | imagem | arquivo | Não | Ilustração da dica |
| Dica | autor | FK Usuário | Sim | Autor administrativo |
| Equipamento | nome | string, até 120 caracteres | Sim | Nome do equipamento |
| Equipamento | categoria | enum | Sim | Tipo do equipamento |
| Equipamento | foto | arquivo | Não | Foto principal |
| Equipamento | descricao | texto | Sim | Descrição |
| Equipamento | uso | texto | Não | Uso recomendado |
| Equipamento | ativo | boolean | Sim | Indica se está disponível |

## Outras entidades

- **MensagemContato:** nome, e-mail, assunto, mensagem, estado de leitura e data de criação.
- **SolicitacaoRedefinicaoSenha:** usuário, e-mail, senha solicitada, data de criação, data de atendimento e atendente.
- **FotoAdicionalEquipamento:** equipamento associado e arquivo de foto adicional.
- **Grupo Pescador:** grupo de permissões do Django associado a usuários autorizados.
