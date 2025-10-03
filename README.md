# Programa Social - Sistema de Cadastro

Sistema completo para cadastro e gerenciamento de pessoas carentes em programas sociais, desenvolvido em Python com Flet.

## Funcionalidades

### 🔐 Autenticação
- Sistema de login seguro com hash SHA-256
- Cadastro de novos usuários administradores
- Sessão persistente durante o uso

### 📝 Cadastro de Inscrições
- Formulário completo com dados pessoais e socioeconômicos
- Validação de campos obrigatórios
- Interface intuitiva e responsiva

### 📊 Gerenciamento
- Lista todas as inscrições com filtros por status
- Visualização detalhada de cada inscrição
- Atualização de status (Pendente/Aprovada/Rejeitada)
- Estatísticas em tempo real

### 📄 Relatórios PDF
- Geração de PDF individual para cada inscrição
- Relatório completo com todas as inscrições
- Formatação profissional com tabelas e estatísticas

### 💾 Armazenamento
- Banco de dados SQLite local
- Backup automático dos dados
- Funcionalidade offline completa

## Como Usar

### Instalação
\`\`\`bash
pip install -r requirements.txt
python main.py
\`\`\`

### Login Padrão
- **Email:** admin@programa.gov.br
- **Senha:** admin123

### Estrutura do Banco
- **usuarios:** Administradores do sistema
- **inscricoes:** Dados dos inscritos no programa

## Campos do Formulário

### Dados Pessoais
- Nome completo (obrigatório)
- Idade (obrigatório)
- Gênero (obrigatório)
- CPF (opcional)
- Endereço completo (obrigatório)
- Telefone (opcional)
- Email (opcional)

### Dados Socioeconômicos
- Renda familiar (obrigatório)
- Número de membros da família (obrigatório)
- Despesas mensais (obrigatório)
- Escolaridade (obrigatório)
- Situação de moradia (obrigatório)
- Observações (opcional)

## Recursos Técnicos

- **Framework:** Flet (Python)
- **Banco de Dados:** SQLite
- **PDF:** ReportLab
- **Segurança:** Hash SHA-256 para senhas
- **Interface:** Material Design
- **Compatibilidade:** Web e Mobile

## Arquivos Gerados

- `programa_social.db` - Banco de dados
- `pdfs/` - Diretório com relatórios PDF gerados
- `inscricao_[ID]_[NOME].pdf` - PDF individual
- `relatorio_completo_[DATA].pdf` - Relatório geral

## Status das Inscrições

- **Pendente:** Aguardando análise (padrão)
- **Aprovada:** Inscrito aprovado no programa
- **Rejeitada:** Inscrito não atende aos critérios
