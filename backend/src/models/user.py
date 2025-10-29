from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable=False)  # admin, profissional_saude, gestor_educacional, estudante
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.nome}>'

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'tipo_usuario': self.tipo_usuario,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ativo': self.ativo
        }

class Escola(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.Text)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'endereco': self.endereco,
            'telefone': self.telefone,
            'email': self.email,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

class Estudante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date)
    genero = db.Column(db.String(20))
    escola_id = db.Column(db.Integer, db.ForeignKey('escola.id'))
    responsavel_nome = db.Column(db.String(100))
    responsavel_telefone = db.Column(db.String(20))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('User', backref=db.backref('estudante', uselist=False))
    escola = db.relationship('Escola', backref=db.backref('estudantes', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'genero': self.genero,
            'escola_id': self.escola_id,
            'responsavel_nome': self.responsavel_nome,
            'responsavel_telefone': self.responsavel_telefone,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

class AvaliacaoPostural(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_estudante = db.Column(db.Integer, db.ForeignKey('estudante.id'), nullable=False)
    data_avaliacao = db.Column(db.DateTime, default=datetime.utcnow)
    imagem_frontal_url = db.Column(db.String(255))
    imagem_lateral_url = db.Column(db.String(255))
    imagem_posterior_url = db.Column(db.String(255))
    dados_alinhamento_json = db.Column(db.Text)  # JSON com dados da análise
    relatorio_pdf_url = db.Column(db.String(255))
    audio_exercicio_path = db.Column(db.String(255))
    observacoes = db.Column(db.Text)
    profissional_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    estudante = db.relationship('Estudante', backref=db.backref('avaliacoes', lazy=True))
    profissional = db.relationship('User', backref=db.backref('avaliacoes_realizadas', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'id_estudante': self.id_estudante,
            'data_avaliacao': self.data_avaliacao.isoformat() if self.data_avaliacao else None,
            'imagem_frontal_url': self.imagem_frontal_url,
            'imagem_lateral_url': self.imagem_lateral_url,
            'imagem_posterior_url': self.imagem_posterior_url,
            'dados_alinhamento_json': self.dados_alinhamento_json,
            'relatorio_pdf_url': self.relatorio_pdf_url,
            'audio_exercicio_path': self.audio_exercicio_path,
            'observacoes': self.observacoes,
            'profissional_id': self.profissional_id
        }

class SessaoRV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_estudante = db.Column(db.Integer, db.ForeignKey('estudante.id'), nullable=False)
    data_sessao = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_sessao = db.Column(db.String(50), nullable=False)  # jogo, alongamento
    duracao_minutos = db.Column(db.Integer)
    progresso_json = db.Column(db.Text)  # JSON com dados do progresso
    pontuacao = db.Column(db.Integer)

    estudante = db.relationship('Estudante', backref=db.backref('sessoes_rv', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'id_estudante': self.id_estudante,
            'data_sessao': self.data_sessao.isoformat() if self.data_sessao else None,
            'tipo_sessao': self.tipo_sessao,
            'duracao_minutos': self.duracao_minutos,
            'progresso_json': self.progresso_json,
            'pontuacao': self.pontuacao
        }
