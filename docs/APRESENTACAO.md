# Roteiro da apresentação — RondoPesca

Use este roteiro como apoio à apresentação oral. A avaliação deve priorizar o sistema em funcionamento, não uma leitura de slides.

## 1. Problema e público

O RondoPesca reúne pescadores e facilita o acesso a informações sobre pesca em Rondônia. O público-alvo inclui iniciantes, pescadores experientes, organizadores de eventos e administradores da plataforma.

Explique que a dor resolvida é a falta de um ambiente centralizado para encontrar locais, dicas, pessoas da comunidade e eventos.

## 2. Demonstração ao vivo

Siga esta sequência:

1. Abra a página inicial e apresente as áreas públicas.
2. Faça login com a conta `demo`.
3. Mostre o perfil e a edição dos dados permitidos.
4. Na comunidade, abra uma publicação e realize um comentário ou curtida.
5. Em Locais de pesca, consulte um local e o link de mapa.
6. Em Eventos, consulte um evento e confirme participação.
7. Acesse o Django Admin ou o painel administrativo.
8. Acesse uma URL inexistente para demonstrar a página 404.

Prepare antes da apresentação dados novos e não use informações pessoais reais.

## 3. Decisões técnicas

- Django para organização em aplicativos e autenticação.
- SQLite para desenvolvimento local e entrega simples.
- Templates e arquivos estáticos separados por área.
- Grupos de permissões para distinguir usuários comuns, pescadores e equipe administrativa.
- Migrações automáticas e dados de demonstração idempotentes ao iniciar `runserver`.
- Separação das documentações de usuário e técnica.

## 4. Aprendizados e melhorias futuras

O grupo deve dizer:

- qual dificuldade técnica foi mais importante;
- qual decisão seria mantida;
- qual decisão seria mudada;
- quais melhorias seriam implementadas em uma próxima versão.
