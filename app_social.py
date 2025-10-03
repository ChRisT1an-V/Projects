import flet as ft
import sqlite3
import hashlib
import json
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors as pdf_colors

class ProgramaSocialApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_user = None
        self.current_view = "login"
        self.inscricoes_data = []
        self.init_database()
        self.setup_page()
        
    def init_database(self):
        """Inicializa o banco de dados SQLite"""
        self.conn = sqlite3.connect('programa_social.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Tabela de usuários (administradores)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                nome TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de inscrições
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inscricoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                idade INTEGER NOT NULL,
                genero TEXT NOT NULL,
                cpf TEXT,
                endereco TEXT NOT NULL,
                telefone TEXT,
                email TEXT,
                renda_familiar REAL NOT NULL,
                membros_familia INTEGER NOT NULL,
                despesas_mensais REAL NOT NULL,
                escolaridade TEXT NOT NULL,
                situacao_moradia TEXT NOT NULL,
                observacoes TEXT,
                status TEXT DEFAULT 'Pendente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar usuário admin padrão se não existir
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE email = ?', ('admin@programa.gov.br',))
        if cursor.fetchone()[0] == 0:
            senha_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO usuarios (email, senha, nome) 
                VALUES (?, ?, ?)
            ''', ('admin@programa.gov.br', senha_hash, 'Administrador'))
        
        self.conn.commit()
    
    def setup_page(self):
        """Configurações iniciais da página"""
        self.page.title = "Programa Social - Cadastro"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        self.show_login()
    
    def show_login(self):
        """Exibe a tela de login"""
        self.page.clean()
        
        # Campos de entrada
        self.email_field = ft.TextField(
            label="Email",
            prefix_icon="email",
            width=300,
            autofocus=True
        )
        
        self.password_field = ft.TextField(
            label="Senha",
            prefix_icon="lock",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        # Botões
        login_btn = ft.ElevatedButton(
            text="Entrar",
            on_click=self.login_click,
            width=300,
            height=50
        )
        
        register_btn = ft.TextButton(
            text="Criar nova conta",
            on_click=self.show_register
        )
        
        # Layout da tela de login
        login_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Programa Social",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color="blue"
                ),
                ft.Text(
                    "Sistema de Cadastro",
                    size=16,
                    color="grey"
                ),
                ft.Divider(height=30),
                self.email_field,
                self.password_field,
                ft.Divider(height=20),
                login_btn,
                register_btn
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
            ),
            alignment=ft.alignment.center,
            padding=40
        )
        
        self.page.add(
            ft.Row([login_container], alignment=ft.MainAxisAlignment.CENTER)
        )
        self.page.update()
    
    def show_register(self, e=None):
        """Exibe a tela de cadastro de usuário"""
        self.page.clean()
        
        # Campos de cadastro
        self.reg_nome = ft.TextField(label="Nome Completo", width=300)
        self.reg_email = ft.TextField(label="Email", width=300)
        self.reg_senha = ft.TextField(label="Senha", password=True, width=300)
        self.reg_confirma_senha = ft.TextField(label="Confirmar Senha", password=True, width=300)
        
        register_container = ft.Container(
            content=ft.Column([
                ft.Text("Criar Nova Conta", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20),
                self.reg_nome,
                self.reg_email,
                self.reg_senha,
                self.reg_confirma_senha,
                ft.Divider(height=20),
                ft.ElevatedButton(
                    text="Cadastrar",
                    on_click=self.register_click,
                    width=300,
                    height=50
                ),
                ft.TextButton(
                    text="Voltar ao Login",
                    on_click=lambda _: self.show_login()
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
            ),
            alignment=ft.alignment.center,
            padding=40
        )
        
        self.page.add(
            ft.Row([register_container], alignment=ft.MainAxisAlignment.CENTER)
        )
        self.page.update()
    
    def login_click(self, e):
        """Processa o login do usuário"""
        email = self.email_field.value
        senha = self.password_field.value
        
        if not email or not senha:
            self.show_snackbar("Por favor, preencha todos os campos", "red")
            return
        
        cursor = self.conn.cursor()
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        cursor.execute('''
            SELECT id, nome FROM usuarios 
            WHERE email = ? AND senha = ?
        ''', (email, senha_hash))
        
        user = cursor.fetchone()
        
        if user:
            self.current_user = {"id": user[0], "nome": user[1], "email": email}
            self.show_dashboard()
        else:
            self.show_snackbar("Email ou senha incorretos", "red")
    
    def register_click(self, e):
        """Processa o cadastro de novo usuário"""
        nome = self.reg_nome.value
        email = self.reg_email.value
        senha = self.reg_senha.value
        confirma = self.reg_confirma_senha.value
        
        if not all([nome, email, senha, confirma]):
            self.show_snackbar("Por favor, preencha todos os campos", "red")
            return
        
        if senha != confirma:
            self.show_snackbar("As senhas não coincidem", "red")
            return
        
        if len(senha) < 6:
            self.show_snackbar("A senha deve ter pelo menos 6 caracteres", "red")
            return
        
        cursor = self.conn.cursor()
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO usuarios (nome, email, senha) 
                VALUES (?, ?, ?)
            ''', (nome, email, senha_hash))
            self.conn.commit()
            self.show_snackbar("Usuário cadastrado com sucesso!", "green")
            self.show_login()
        except sqlite3.IntegrityError:
            self.show_snackbar("Este email já está cadastrado", "red")
    
    def show_dashboard(self):
        """Exibe o dashboard principal"""
        self.page.clean()
        self.current_view = "dashboard"
        
        try:
            # Header
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        f"Bem-vindo, {self.current_user['nome']}",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.IconButton(
                        icon="logout",
                        tooltip="Sair",
                        on_click=self.logout
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=ft.padding.all(20),
                bgcolor="lightblue",
                border_radius=10
            )
            
            # Cards de navegação
            cards = ft.Row([
                self.create_nav_card(
                    "Nova Inscrição",
                    "people",
                    "Cadastrar nova pessoa",
                    self.show_inscricao_form
                ),
                self.create_nav_card(
                    "Gerenciar Inscrições",
                    "list",
                    "Ver e gerenciar inscrições",
                    self.show_inscricoes_list
                ),
                self.create_nav_card(
                    "Relatórios",
                    "assessment",
                    "Gerar relatórios em PDF",
                    self.show_relatorios
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=True,
            spacing=20
            )
            
            # Estatísticas rápidas
            stats = self.get_statistics()
            stats_row = ft.Row([
                self.create_stat_card("Total de Inscrições", stats['total'], "blue"),
                self.create_stat_card("Pendentes", stats['pendentes'], "orange"),
                self.create_stat_card("Aprovadas", stats['aprovadas'], "green"),
                self.create_stat_card("Rejeitadas", stats['rejeitadas'], "red")
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=True,
            spacing=15
            )
            
            self.page.add(
                ft.Column([
                    header,
                    ft.Divider(height=30),
                    ft.Text("Painel de Controle", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20),
                    stats_row,
                    ft.Divider(height=30),
                    cards
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
                )
            )
            self.page.update()
            print("Dashboard carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar dashboard: {e}")
            self.show_snackbar(f"Erro ao carregar dashboard: {e}", "red")
            self.page.update()
    
    def create_nav_card(self, title, icon_name, subtitle, on_click):
        """Cria um card de navegação usando o layout fornecido pelo usuário, com cores em string."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(name=icon_name, size=40, color="blue"), # Alterado de ft.colors.BLUE para "blue"
                    ft.Text(title, weight="bold", size=16, text_align=ft.TextAlign.CENTER),
                    ft.Text(
                        subtitle,
                        size=11,
                        max_lines=2,
                        overflow="ellipsis",
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            on_click=lambda _: on_click(),
            padding=ft.padding.all(16),
            width=200,
            height=160,
            border_radius=10,
            bgcolor="grey100", # Alterado de ft.colors.GREY_100 para "grey100"
        )
    
    def create_stat_card(self, title, value, color):
        """Cria um card de estatística"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(title, size=12, color="grey", text_align=ft.TextAlign.CENTER, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
                ),
                padding=ft.padding.all(15),
                width=100
            )
        )
    
    def get_statistics(self):
        """Obtém estatísticas das inscrições"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM inscricoes')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM inscricoes WHERE status = ?', ('Pendente',))
        pendentes = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM inscricoes WHERE status = ?', ('Aprovada',))
        aprovadas = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM inscricoes WHERE status = ?', ('Rejeitada',))
        rejeitadas = cursor.fetchone()[0]
        
        return {
            'total': total,
            'pendentes': pendentes,
            'aprovadas': aprovadas,
            'rejeitadas': rejeitadas
        }
    
    def show_inscricao_form(self, e=None):
        """Exibe o formulário de inscrição"""
        self.page.clean()
        self.current_view = "inscricao"
        
        # Header com botão voltar
        header = ft.Row([
            ft.IconButton(
                icon="arrow_back",
                tooltip="Voltar",
                on_click=lambda _: self.show_dashboard()
            ),
            ft.Text("Nova Inscrição", size=24, weight=ft.FontWeight.BOLD)
        ])
        
        # Campos do formulário
        self.form_fields = {
            'nome_completo': ft.TextField(label="Nome Completo *", width=400),
            'idade': ft.TextField(label="Idade *", width=200, keyboard_type=ft.KeyboardType.NUMBER),
            'genero': ft.Dropdown(
                label="Gênero *",
                width=200,
                options=[
                    ft.dropdown.Option("Masculino"),
                    ft.dropdown.Option("Feminino"),
                    ft.dropdown.Option("Outro"),
                    ft.dropdown.Option("Prefiro não informar")
                ]
            ),
            'cpf': ft.TextField(label="CPF", width=200),
            'endereco': ft.TextField(label="Endereço Completo *", width=400, multiline=True),
            'telefone': ft.TextField(label="Telefone", width=200),
            'email': ft.TextField(label="Email", width=300),
            'renda_familiar': ft.TextField(
                label="Renda Familiar (R$) *", 
                width=200, 
                keyboard_type=ft.KeyboardType.NUMBER,
                prefix_text="R$ "
            ),
            'membros_familia': ft.TextField(
                label="Membros da Família *", 
                width=200, 
                keyboard_type=ft.KeyboardType.NUMBER
            ),
            'despesas_mensais': ft.TextField(
                label="Despesas Mensais (R$) *", 
                width=200, 
                keyboard_type=ft.KeyboardType.NUMBER,
                prefix_text="R$ "
            ),
            'escolaridade': ft.Dropdown(
                label="Escolaridade *",
                width=250,
                options=[
                    ft.dropdown.Option("Sem escolaridade"),
                    ft.dropdown.Option("Ensino Fundamental Incompleto"),
                    ft.dropdown.Option("Ensino Fundamental Completo"),
                    ft.dropdown.Option("Ensino Médio Incompleto"),
                    ft.dropdown.Option("Ensino Médio Completo"),
                    ft.dropdown.Option("Ensino Superior Incompleto"),
                    ft.dropdown.Option("Ensino Superior Completo"),
                    ft.dropdown.Option("Pós-graduação")
                ]
            ),
            'situacao_moradia': ft.Dropdown(
                label="Situação de Moradia *",
                width=250,
                options=[
                    ft.dropdown.Option("Casa Própria"),
                    ft.dropdown.Option("Casa Alugada"),
                    ft.dropdown.Option("Casa Cedida"),
                    ft.dropdown.Option("Ocupação"),
                    ft.dropdown.Option("Situação de Rua"),
                    ft.dropdown.Option("Outro")
                ]
            ),
            'observacoes': ft.TextField(
                label="Observações Adicionais",
                width=400,
                multiline=True,
                max_lines=3
            )
        }
        
        # Layout do formulário
        form_content = ft.Column([
            header,
            ft.Divider(height=20),
            
            # Seção: Dados Pessoais
            ft.Text("Dados Pessoais", size=18, weight=ft.FontWeight.BOLD, color="blue"),
            ft.Row([
                self.form_fields['nome_completo']
            ]),
            ft.Row([
                self.form_fields['idade'],
                self.form_fields['genero'],
                self.form_fields['cpf']
            ], spacing=20),
            ft.Row([
                self.form_fields['endereco']
            ]),
            ft.Row([
                self.form_fields['telefone'],
                self.form_fields['email']
            ], spacing=20),
            
            ft.Divider(height=20),
            
            # Seção: Dados Socioeconômicos
            ft.Text("Dados Socioeconômicos", size=18, weight=ft.FontWeight.BOLD, color="blue"),
            ft.Row([
                self.form_fields['renda_familiar'],
                self.form_fields['membros_familia'],
                self.form_fields['despesas_mensais']
            ], spacing=20),
            ft.Row([
                self.form_fields['escolaridade'],
                self.form_fields['situacao_moradia']
            ], spacing=20),
            ft.Row([
                self.form_fields['observacoes']
            ]),
            
            ft.Divider(height=30),
            
            # Botões
            ft.Row([
                ft.ElevatedButton(
                    text="Salvar Inscrição",
                    on_click=self.save_inscricao,
                    width=200,
                    height=50,
                    bgcolor="green",
                    color="white"
                ),
                ft.OutlinedButton(
                    text="Limpar Formulário",
                    on_click=self.clear_form,
                    width=200,
                    height=50
                )
            ], spacing=20)
        ],
        spacing=15,
        scroll=ft.ScrollMode.AUTO
        )
        
        self.page.add(form_content)
        self.page.update()
    
    def save_inscricao(self, e):
        """Salva a inscrição no banco de dados"""
        # Validação dos campos obrigatórios
        required_fields = [
            'nome_completo', 'idade', 'genero', 'endereco', 
            'renda_familiar', 'membros_familia', 'despesas_mensais', 
            'escolaridade', 'situacao_moradia'
        ]
        
        for field in required_fields:
            if not self.form_fields[field].value:
                self.show_snackbar(f"Campo '{self.form_fields[field].label}' é obrigatório", "red")
                return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO inscricoes (
                    nome_completo, idade, genero, cpf, endereco, telefone, email,
                    renda_familiar, membros_familia, despesas_mensais, escolaridade,
                    situacao_moradia, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.form_fields['nome_completo'].value,
                int(self.form_fields['idade'].value),
                self.form_fields['genero'].value,
                self.form_fields['cpf'].value,
                self.form_fields['endereco'].value,
                self.form_fields['telefone'].value,
                self.form_fields['email'].value,
                float(self.form_fields['renda_familiar'].value.replace('R$ ', '').replace(',', '.')),
                int(self.form_fields['membros_familia'].value),
                float(self.form_fields['despesas_mensais'].value.replace('R$ ', '').replace(',', '.')),
                self.form_fields['escolaridade'].value,
                self.form_fields['situacao_moradia'].value,
                self.form_fields['observacoes'].value
            ))
            self.conn.commit()
            
            self.show_snackbar("Inscrição salva com sucesso!", "green")
            self.clear_form()
            self.show_dashboard()
            
        except Exception as ex:
            self.show_snackbar(f"Erro ao salvar: {str(ex)}", "red")
    
    def clear_form(self, e=None):
        """Limpa todos os campos do formulário"""
        for field in self.form_fields.values():
            field.value = ""
            if isinstance(field, ft.Dropdown):
                field.value = None
        self.page.update()
    
    def show_inscricoes_list(self, e=None):
        """Exibe a lista de inscrições"""
        self.page.clean()
        self.current_view = "inscricoes"
        
        # Header
        header = ft.Row([
            ft.IconButton(
                icon="arrow_back",
                tooltip="Voltar",
                on_click=lambda _: self.show_dashboard()
            ),
            ft.Text("Gerenciar Inscrições", size=24, weight=ft.FontWeight.BOLD),
            ft.IconButton(
                icon="refresh",
                tooltip="Atualizar",
                on_click=self.refresh_inscricoes
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Filtros
        self.status_filter = ft.Dropdown(
            label="Filtrar por Status",
            width=200,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Pendente"),
                ft.dropdown.Option("Aprovada"),
                ft.dropdown.Option("Rejeitada")
            ],
            value="Todos",
            on_change=self.filter_inscricoes
        )
        
        filters_row = ft.Row([
            self.status_filter,
            ft.ElevatedButton(
                text="Exportar Todas (PDF)",
                on_click=self.export_all_pdf,
                icon="picture_as_pdf"
            )
        ], spacing=20)
        
        # Lista de inscrições
        self.inscricoes_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        
        self.page.add(
            ft.Column([
                header,
                ft.Divider(height=20),
                filters_row,
                ft.Divider(height=20),
                self.inscricoes_column
            ], expand=True)
        )
        
        self.load_inscricoes()
        self.page.update()
    
    def load_inscricoes(self, status_filter="Todos"):
        """Carrega as inscrições do banco de dados"""
        cursor = self.conn.cursor()
        
        if status_filter == "Todos":
            cursor.execute('''
                SELECT * FROM inscricoes 
                ORDER BY created_at DESC
            ''')
        else:
            cursor.execute('''
                SELECT * FROM inscricoes 
                WHERE status = ?
                ORDER BY created_at DESC
            ''', (status_filter,))
        
        inscricoes = cursor.fetchall()
        self.inscricoes_column.controls.clear()
        
        if not inscricoes:
            self.inscricoes_column.controls.append(
                ft.Text("Nenhuma inscrição encontrada", size=16, color="grey")
            )
        else:
            for inscricao in inscricoes:
                self.inscricoes_column.controls.append(
                    self.create_inscricao_card(inscricao)
                )
        
        self.page.update()
        print(f"Inscrições carregadas: {len(inscricoes)}")
    
    def create_inscricao_card(self, inscricao):
        """Cria um card para cada inscrição"""
        id_inscricao, nome, idade, genero, cpf, endereco, telefone, email, renda, membros, despesas, escolaridade, moradia, obs, status, created_at, updated_at = inscricao
        
        # Cor do status
        status_color = {
            'Pendente': "orange",
            'Aprovada': "green",
            'Rejeitada': "red"
        }.get(status, "grey")
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(nome, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Idade: {idade} anos | {genero}", size=12, color="grey"),
                            ft.Text(f"Renda Familiar: R$ {renda:.2f}", size=12),
                            ft.Text(f"Membros da Família: {membros}", size=12)
                        ], expand=True),
                        ft.Column([
                            ft.Container(
                                content=ft.Text(status, color="white", size=12, weight=ft.FontWeight.BOLD),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                border_radius=15
                            ),
                            ft.Text(f"Cadastrado em: {created_at[:10]}", size=10, color="grey")
                        ])
                    ]),
                    ft.Divider(height=10),
                    ft.Row([
                        ft.ElevatedButton(
                            text="Ver Detalhes",
                            on_click=lambda e, id=id_inscricao: self.show_inscricao_details(id),
                            icon="visibility",
                            height=35
                        ),
                        ft.ElevatedButton(
                            text="Gerar PDF",
                            on_click=lambda e, id=id_inscricao: self.generate_pdf(id),
                            icon="picture_as_pdf",
                            height=35,
                            bgcolor="red",
                            color="white"
                        ),
                        ft.Dropdown(
                            width=120,
                            value=status,
                            options=[
                                ft.dropdown.Option("Pendente"),
                                ft.dropdown.Option("Aprovada"),
                                ft.dropdown.Option("Rejeitada")
                            ],
                            on_change=lambda e, id=id_inscricao: self.update_status(id, e.control.value)
                        )
                    ], spacing=10)
                ]),
                padding=20
            )
        )
    
    def show_inscricao_details(self, inscricao_id):
        """Exibe os detalhes completos de uma inscrição"""
        print(f"Tentando mostrar detalhes para inscrição ID: {inscricao_id}")
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT * FROM inscricoes WHERE id = ?', (inscricao_id,))
            inscricao = cursor.fetchone()
            
            if not inscricao:
                self.show_snackbar("Inscrição não encontrada", "red")
                print(f"Inscrição ID {inscricao_id} não encontrada.")
                return
            
            # Criar dialog com detalhes
            details_content = ft.Column([
                ft.Text("Detalhes da Inscrição", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(f"Nome: {inscricao[1]}", size=14),
                ft.Text(f"Idade: {inscricao[2]} anos", size=14),
                ft.Text(f"Gênero: {inscricao[3]}", size=14),
                ft.Text(f"CPF: {inscricao[4] or 'Não informado'}", size=14),
                ft.Text(f"Endereço: {inscricao[5]}", size=14),
                ft.Text(f"Telefone: {inscricao[6] or 'Não informado'}", size=14),
                ft.Text(f"Email: {inscricao[7] or 'Não informado'}", size=14),
                ft.Divider(),
                ft.Text(f"Renda Familiar: R$ {inscricao[8]:.2f}", size=14),
                ft.Text(f"Membros da Família: {inscricao[9]}", size=14),
                ft.Text(f"Despesas Mensais: R$ {inscricao[10]:.2f}", size=14),
                ft.Text(f"Escolaridade: {inscricao[11]}", size=14),
                ft.Text(f"Situação de Moradia: {inscricao[12]}", size=14),
                ft.Divider(),
                ft.Text(f"Observações: {inscricao[13] or 'Nenhuma'}", size=14),
                ft.Text(f"Status: {inscricao[14]}", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"Cadastrado em: {inscricao[15]}", size=12, color="grey")
            ], scroll=ft.ScrollMode.AUTO, height=400)
            
            dialog = ft.AlertDialog(
                title=ft.Text("Detalhes da Inscrição"),
                content=details_content,
                actions=[
                    ft.TextButton("Fechar", on_click=lambda e: self.close_dialog())
                ]
            )
            
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            print(f"Detalhes da inscrição ID {inscricao_id} exibidos com sucesso.")
        except Exception as ex:
            self.show_snackbar(f"Erro ao exibir detalhes: {str(ex)}", "red")
            print(f"Erro ao exibir detalhes da inscrição ID {inscricao_id}: {ex}")
    
    def update_status(self, inscricao_id, new_status):
        """Atualiza o status de uma inscrição"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE inscricoes 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (new_status, inscricao_id))
        self.conn.commit()
        
        self.show_snackbar(f"Status atualizado para: {new_status}", "green")
        self.load_inscricoes(self.status_filter.value if hasattr(self, 'status_filter') else "Todos")
    
    def filter_inscricoes(self, e):
        """Filtra inscrições por status"""
        self.load_inscricoes(e.control.value)
    
    def refresh_inscricoes(self, e):
        """Atualiza a lista de inscrições"""
        self.load_inscricoes(self.status_filter.value if hasattr(self, 'status_filter') else "Todos")
        self.show_snackbar("Lista atualizada", "blue")
    
    def generate_pdf(self, inscricao_id):
        """Gera PDF para uma inscrição específica"""
        print(f"Tentando gerar PDF para inscrição ID: {inscricao_id}")
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT * FROM inscricoes WHERE id = ?', (inscricao_id,))
            inscricao = cursor.fetchone()
            
            if not inscricao:
                self.show_snackbar("Inscrição não encontrada", "red")
                print(f"Inscrição ID {inscricao_id} não encontrada para PDF.")
                return
            
            # Criar diretório se não existir
            os.makedirs('pdfs', exist_ok=True)
            
            filename = f"pdfs/inscricao_{inscricao_id}_{inscricao[1].replace(' ', '_')}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph("PROGRAMA SOCIAL - FICHA DE INSCRIÇÃO", title_style))
            
            # Dados da inscrição
            data = [
                ['Campo', 'Informação'],
                ['Nome Completo', inscricao[1]],
                ['Idade', f"{inscricao[2]} anos"],
                ['Gênero', inscricao[3]],
                ['CPF', inscricao[4] or 'Não informado'],
                ['Endereço', inscricao[5]],
                ['Telefone', inscricao[6] or 'Não informado'],
                ['Email', inscricao[7] or 'Não informado'],
                ['Renda Familiar', f"R$ {inscricao[8]:.2f}"],
                ['Membros da Família', str(inscricao[9])],
                ['Despesas Mensais', f"R$ {inscricao[10]:.2f}"],
                ['Escolaridade', inscricao[11]],
                ['Situacao de Moradia', inscricao[12]],
                ['Observacoes', inscricao[13] or 'Nenhuma'],
                ['Status', inscricao[14]],
                ['Data de Cadastro', inscricao[15]]
            ]
            
            table = Table(data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), pdf_colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, pdf_colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Rodapé
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=1
            )
            story.append(Paragraph(f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", footer_style))
            
            doc.build(story)
            self.show_snackbar(f"PDF gerado: {filename}", "green")
            print(f"PDF gerado com sucesso: {filename}")
            
        except Exception as ex:
            self.show_snackbar(f"Erro ao gerar PDF: {str(ex)}", "red")
            print(f"Erro ao gerar PDF para inscrição ID {inscricao_id}: {ex}")
    
    def export_all_pdf(self, e):
        """Exporta todas as inscrições para PDF"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM inscricoes ORDER BY created_at DESC')
        inscricoes = cursor.fetchall()
        
        if not inscricoes:
            self.show_snackbar("Nenhuma inscrição para exportar", "orange")
            return
        
        try:
            os.makedirs('pdfs', exist_ok=True)
            filename = f"pdfs/relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph("PROGRAMA SOCIAL - RELATÓRIO COMPLETO", title_style))
            story.append(Paragraph(f"Total de Inscrições: {len(inscricoes)}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Tabela resumo
            data = [['ID', 'Nome', 'Idade', 'Renda Familiar', 'Status', 'Data Cadastro']]
            
            for inscricao in inscricoes:
                data.append([
                    str(inscricao[0]),
                    inscricao[1][:25] + '...' if len(inscricao[1]) > 25 else inscricao[1],
                    str(inscricao[2]),
                    f"R$ {inscricao[8]:.2f}",
                    inscricao[14],
                    inscricao[15][:10]
                ])
            
            table = Table(data, colWidths=[0.5*inch, 2*inch, 0.7*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), pdf_colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, pdf_colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Rodapé
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=1
            )
            story.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", footer_style))
            
            doc.build(story)
            self.show_snackbar(f"Relatório exportado: {filename}", "green")
            
        except Exception as ex:
            self.show_snackbar(f"Erro ao exportar relatório: {str(ex)}", "red")
    
    def show_relatorios(self, e=None):
        """Exibe a tela de relatórios"""
        self.page.clean()
        
        header = ft.Row([
            ft.IconButton(
                icon="arrow_back",
                tooltip="Voltar",
                on_click=lambda _: self.show_dashboard()
            ),
            ft.Text("Relatórios", size=24, weight=ft.FontWeight.BOLD)
        ])
        
        # Estatísticas detalhadas
        stats = self.get_detailed_statistics()
        
        stats_cards = ft.Row([
            self.create_stat_card("Total", stats['total'], "blue"),
            self.create_stat_card("Pendentes", stats['pendentes'], "orange"),
            self.create_stat_card("Aprovadas", stats['aprovadas'], "green"),
            self.create_stat_card("Rejeitadas", stats['rejeitadas'], "red")
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        
        # Botões de relatório
        report_buttons = ft.Column([
            ft.ElevatedButton(
                text="Exportar Relatório Completo",
                on_click=self.export_all_pdf,
                icon="picture_as_pdf",
                width=300,
                height=50,
                bgcolor="red",
                color="white"
            ),
            ft.ElevatedButton(
                text="Relatório por Status",
                on_click=self.show_status_report,
                icon="assessment",
                width=300,
                height=50
            ),
            ft.ElevatedButton(
                text="Estatísticas Detalhadas",
                on_click=self.show_detailed_stats,
                icon="analytics",
                width=300,
                height=50
            )
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.add(
            ft.Column([
                header,
                ft.Divider(height=30),
                ft.Text("Estatísticas Gerais", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20),
                stats_cards,
                ft.Divider(height=40),
                ft.Text("Relatórios Disponíveis", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20),
                report_buttons
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        self.page.update()
    
    def get_detailed_statistics(self):
        """Obtém estatísticas detalhadas"""
        cursor = self.conn.cursor()
        
        # Estatísticas básicas
        stats = self.get_statistics()
        
        # Média de renda
        cursor.execute('SELECT AVG(renda_familiar) FROM inscricoes')
        media_renda = cursor.fetchone()[0] or 0
        
        # Média de membros da família
        cursor.execute('SELECT AVG(membros_familia) FROM inscricoes')
        media_membros = cursor.fetchone()[0] or 0
        
        stats.update({
            'media_renda': media_renda,
            'media_membros': media_membros
        })
        
        return stats
    
    def show_status_report(self, e):
        """Mostra relatório por status com gráfico circular."""
        stats = self.get_statistics()
        
        total = stats['total']
        pendentes = stats['pendentes']
        aprovadas = stats['aprovadas']
        rejeitadas = stats['rejeitadas']

        sections = []
        if pendentes > 0:
            sections.append(
                ft.PieChartSection(
                    value=pendentes,
                    title=f"Pendente: {pendentes}",
                    color="orange",
                    radius=60,
                    title_style=ft.TextStyle(size=10, color="white", weight=ft.FontWeight.BOLD),
                )
            )
        if aprovadas > 0:
            sections.append(
                ft.PieChartSection(
                    value=aprovadas,
                    title=f"Aprovada: {aprovadas}",
                    color="green",
                    radius=60,
                    title_style=ft.TextStyle(size=10, color="white", weight=ft.FontWeight.BOLD),
                )
            )
        if rejeitadas > 0:
            sections.append(
                ft.PieChartSection(
                    value=rejeitadas,
                    title=f"Rejeitada: {rejeitadas}",
                    color="red",
                    radius=60,
                    title_style=ft.TextStyle(size=10, color="white", weight=ft.FontWeight.BOLD),
                )
            )
        
        # Adiciona uma seção "vazia" se não houver dados para evitar erro no PieChart
        if not sections and total == 0:
            sections.append(
                ft.PieChartSection(
                    value=1, # Um valor mínimo para o gráfico aparecer
                    title="Sem dados",
                    color="grey",
                    radius=60,
                    title_style=ft.TextStyle(size=10, color="white", weight=ft.FontWeight.BOLD),
                )
            )

        pie_chart = ft.PieChart(
            sections=sections,
            sections_space=0,
            center_space_radius=40,
            width=300,
            height=300,
        )

        content = ft.Column([
            ft.Text("Relatório por Status", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text(f"Total de Inscrições: {total}", size=16),
            ft.Text(f"Pendentes: {pendentes} ({(pendentes/max(total, 1)*100):.1f}%)", size=14),
            ft.Text(f"Aprovadas: {aprovadas} ({(aprovadas/max(total, 1)*100):.1f}%)", size=14),
            ft.Text(f"Rejeitadas: {rejeitadas} ({(rejeitadas/max(total, 1)*100):.1f}%)", size=14),
            ft.Divider(),
            ft.Text("Distribuição por Status (Gráfico Circular)", size=16, weight=ft.FontWeight.BOLD),
            pie_chart
        ])
        
        dialog = ft.AlertDialog(
            title=ft.Text("Relatório por Status"),
            content=content,
            actions=[ft.TextButton("Fechar", on_click=lambda e: self.close_dialog())]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_detailed_stats(self, e):
        """Mostra estatísticas detalhadas com gráfico de colunas."""
        stats = self.get_detailed_statistics()
        
        total = stats['total']
        pendentes = stats['pendentes']
        aprovadas = stats['aprovadas']
        rejeitadas = stats['rejeitadas']

        bar_groups = []
        max_y_value = max(pendentes, aprovadas, rejeitadas, 1) # Garante min_y e max_y para o gráfico

        # Grupo para Pendentes
        bar_groups.append(
            ft.BarChartGroup(
                x=0,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=pendentes,
                        color="orange",
                        width=20,
                        border_radius=5,
                        tooltip=f"Pendente: {pendentes}"
                    )
                ]
            )
        )
        # Grupo para Aprovadas
        bar_groups.append(
            ft.BarChartGroup(
                x=1,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=aprovadas,
                        color="green",
                        width=20,
                        border_radius=5,
                        tooltip=f"Aprovada: {aprovadas}"
                    )
                ]
            )
        )
        # Grupo para Rejeitadas
        bar_groups.append(
            ft.BarChartGroup(
                x=2,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=rejeitadas,
                        color="red",
                        width=20,
                        border_radius=5,
                        tooltip=f"Rejeitada: {rejeitadas}"
                    )
                ]
            )
        )

        bar_chart = ft.BarChart(
            bar_groups=bar_groups,
            # border_color="grey", # Removido
            # border_width=1,     # Removido
            left_axis=ft.ChartAxis(
                labels_size=30,
                title="Número de Inscrições",
                title_size=16,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=0, label=ft.Container(ft.Text("Pendente"), padding=5)),
                    ft.ChartAxisLabel(value=1, label=ft.Container(ft.Text("Aprovada"), padding=5)),
                    ft.ChartAxisLabel(value=2, label=ft.Container(ft.Text("Rejeitada"), padding=5)),
                ],
                labels_size=30,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=max_y_value / 5 if max_y_value > 0 else 1, # Ajusta o intervalo da grade
                color="grey",
                width=0.5,
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=1,
                color="grey",
                width=0.5,
            ),
            min_y=0,
            max_y=max_y_value * 1.2, # Adiciona um pouco de margem no topo
            height=300,
            width=400,
            animate=500,
        )
        
        content = ft.Column([
            ft.Text("Estatísticas Detalhadas", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text(f"Total de Inscrições: {total}", size=16),
            ft.Text(f"Renda Familiar Média: R$ {stats['media_renda']:.2f}", size=14),
            ft.Text(f"Média de Membros por Família: {stats['media_membros']:.1f}", size=14),
            ft.Divider(),
            ft.Text("Distribuição por Status (Gráfico de Colunas)", size=16, weight=ft.FontWeight.BOLD),
            bar_chart
        ])
        
        dialog = ft.AlertDialog(
            title=ft.Text("Estatísticas Detalhadas"),
            content=content,
            actions=[ft.TextButton("Fechar", on_click=lambda e: self.close_dialog())]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self):
        """Fecha o dialog atual"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def logout(self, e):
        """Faz logout do usuário"""
        self.current_user = None
        self.show_login()
    
    def show_snackbar(self, message, color):
        """Exibe uma mensagem de feedback"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=color
        )
        self.page.snack_bar.open = True
        self.page.update()

def main(page: ft.Page):
    """Função principal do aplicativo"""
    app = ProgramaSocialApp(page)

if __name__ == "__main__":
    ft.app(target=main)
