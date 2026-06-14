# Receituário Digital

Aplicação web em Python com Flask e MySQL para gerenciamento de receituário digital, atendimentos, pacientes, médicos/funcionários e medicamentos.

## Funcionalidades

- Login com perfis de acesso:
  - Consultório: cadastra médicos, pacientes, medicamentos e vincula pacientes ao médico responsável.
  - Funcionário/médico: registra atendimentos, emite receitas e consulta relatórios.
  - Paciente: visualiza receitas emitidas e atendimentos anteriores.
- CRUD de médicos com nome, CRM, especialidade, UF do CRM e certificado digital.
- CRUD de pacientes com CPF, data de nascimento, sexo, endereço, histórico médico e vínculo de atendimento.
- CRUD de medicamentos com princípio ativo, dosagem, forma farmacêutica, categoria de controle e emissão da receita.
- Registro de receitas com paciente, médico, data/hora do atendimento, consultório, medicamento, dosagem, frequência, duração e observações.

## Requisitos

- Python 3.10 ou superior
- MySQL 8 ou superior

## Instalação

1. Crie o banco no MySQL:

```sql
CREATE DATABASE receituario_digital CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instale as dependências:

```powershell
pip install -r requirements.txt
```

4. Copie o arquivo de ambiente:

```powershell
copy .env.example .env
```

5. Edite o `.env` com usuário, senha, host e porta do MySQL:

```env
DATABASE_URL=mysql+pymysql://root:sua_senha@localhost:3306/receituario_digital
SECRET_KEY=uma-chave-segura
```

6. Inicialize as tabelas e crie o usuário do consultório:

```powershell
$env:FLASK_APP="run.py"
flask init-db
flask seed-admin
```

O login inicial criado por padrão é:

- E-mail: `admin@consultorio.local`
- Senha: `admin123`

Você pode alterar antes de rodar o comando:

```powershell
$env:ADMIN_EMAIL="seu-email@clinica.com"
$env:ADMIN_PASSWORD="uma-senha-forte"
flask seed-admin
```

7. Execute o sistema:

```powershell
python run.py
```

Acesse `http://127.0.0.1:5000`.

## Fluxo sugerido de uso

1. Entre como consultório.
2. Cadastre um médico e informe e-mail/senha para criar o login de funcionário.
3. Cadastre um paciente, informe e-mail/senha para criar o login de paciente e vincule-o ao médico responsável.
4. Cadastre medicamentos.
5. Entre como médico/funcionário e registre atendimentos ou emita receitas.
6. Entre como paciente para visualizar receitas e atendimentos.

## Observações

Este projeto implementa a parte operacional do receituário. Para uso real em produção, revise requisitos legais, assinatura ICP-Brasil, auditoria, trilhas de acesso, criptografia de dados sensíveis, LGPD e integração com certificados digitais.
