# Roadmap de Desenvolvimento - RN Pinturas

Este documento lista as funcionalidades planejadas, em progresso e concluídas para as próximas versões do sistema.

## [v1.1.0] - Security & Identity Update (EM PROGRESSO)

**Objetivo:** Implementar ciclo completo de autenticação, recuperação de conta e blindagem contra ataques de força bruta.

### 📍 Fase 1: Autenticação Essencial (Auth Básica)

- [x] Configuração de URLs de Auth (`django.contrib.auth.urls`).
- [x] View e Template de Login Personalizado.
- [x] Configuração de Logout e Redirecionamento.
- [x] Proteção de Rotas com `@login_required` em todas as views do sistema.
- [x] Ajuste de `LOGIN_REDIRECT_URL` e `LOGOUT_REDIRECT_URL`.

### 📧 Fase 2: Gestão de Senhas e E-mail

- [ ] Configuração SMTP no `.env` (Envio de e-mails).
- [ ] Tela de "Alterar Senha" (para usuário logado).
- [ ] Fluxo de "Esqueci a Senha" (Reset Password):
  - [ ] Formulário de solicitação de e-mail.
  - [ ] Template de e-mail enviado.
  - [ ] Tela de confirmação e nova senha.

### 🛡️ Fase 3: Hardening (Segurança Avançada)

- [x] Proteção contra Brute-Force (Limitar tentativas de login) com `django-axes`.
- [x] Autenticação de Dois Fatores (2FA) com `django-two-factor-auth`.
- [x] Integração com Google Authenticator.

### 🎨 Fase 4: UX e Auditoria

- [x] Navbar Dinâmica (Mostrar nome do usuário / Botão Entrar ou Sair).
- [x] Página de Perfil do Usuário (Meus Dados).
- [ ] Logs de Acesso (Auditoria básica).

---

## [v1.2.0] - (Planejamento Futuro)

- [ ] Dashboard com Gráficos de Vendas.
- [ ] Geração de Relatórios em PDF.
