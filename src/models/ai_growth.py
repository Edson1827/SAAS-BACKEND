from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    empresa = db.Column(db.String(100), nullable=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    assinaturas = db.relationship('Assinatura', backref='cliente', lazy=True)
    campanhas = db.relationship('Campanha', backref='cliente', lazy=True)
    leads = db.relationship('Lead', backref='cliente', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'empresa': self.empresa,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ativo': self.ativo
        }

class Plano(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)  # Starter, Aceleração, Crescimento Exponencial
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    beneficios = db.Column(db.JSON, nullable=True)  # Lista de benefícios
    campanhas_ativas = db.Column(db.Integer, default=1)
    criativos_mes = db.Column(db.Integer, default=2)
    relatorios = db.Column(db.String(50), default='mensais')
    suporte = db.Column(db.String(50), default='whatsapp')
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    assinaturas = db.relationship('Assinatura', backref='plano', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'preco': self.preco,
            'descricao': self.descricao,
            'beneficios': self.beneficios,
            'campanhas_ativas': self.campanhas_ativas,
            'criativos_mes': self.criativos_mes,
            'relatorios': self.relatorios,
            'suporte': self.suporte,
            'ativo': self.ativo
        }

class Assinatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    plano_id = db.Column(db.Integer, db.ForeignKey('plano.id'), nullable=False)
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='ativa')  # ativa, cancelada, suspensa
    valor_pago = db.Column(db.Float, nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'plano_id': self.plano_id,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'status': self.status,
            'valor_pago': self.valor_pago,
            'forma_pagamento': self.forma_pagamento
        }

class Campanha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    plataforma = db.Column(db.String(50), nullable=False)  # google, facebook, tiktok, etc
    objetivo = db.Column(db.String(50), nullable=False)  # conversao, trafego, awareness
    orcamento_diario = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='ativa')  # ativa, pausada, finalizada
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime, nullable=True)
    
    # Métricas
    impressoes = db.Column(db.Integer, default=0)
    cliques = db.Column(db.Integer, default=0)
    conversoes = db.Column(db.Integer, default=0)
    gasto_total = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'nome': self.nome,
            'plataforma': self.plataforma,
            'objetivo': self.objetivo,
            'orcamento_diario': self.orcamento_diario,
            'status': self.status,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'impressoes': self.impressoes,
            'cliques': self.cliques,
            'conversoes': self.conversoes,
            'gasto_total': self.gasto_total,
            'ctr': round((self.cliques / self.impressoes * 100), 2) if self.impressoes > 0 else 0,
            'cpc': round((self.gasto_total / self.cliques), 2) if self.cliques > 0 else 0,
            'cpa': round((self.gasto_total / self.conversoes), 2) if self.conversoes > 0 else 0
        }

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    empresa = db.Column(db.String(100), nullable=True)
    plano_interesse = db.Column(db.String(50), nullable=True)
    origem = db.Column(db.String(50), nullable=True)  # landing_page, facebook, google, etc
    status = db.Column(db.String(20), default='novo')  # novo, contatado, qualificado, convertido
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    observacoes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'empresa': self.empresa,
            'plano_interesse': self.plano_interesse,
            'origem': self.origem,
            'status': self.status,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'observacoes': self.observacoes
        }

class ROICalculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    investimento_mensal = db.Column(db.Float, nullable=False)
    ticket_medio = db.Column(db.Float, nullable=False)
    taxa_conversao_atual = db.Column(db.Float, nullable=False)
    receita_atual = db.Column(db.Float, nullable=False)
    receita_com_ai_growth = db.Column(db.Float, nullable=False)
    aumento_receita = db.Column(db.Float, nullable=False)
    economia_anual = db.Column(db.Float, nullable=False)
    data_calculo = db.Column(db.DateTime, default=datetime.utcnow)
    ip_origem = db.Column(db.String(50), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'investimento_mensal': self.investimento_mensal,
            'ticket_medio': self.ticket_medio,
            'taxa_conversao_atual': self.taxa_conversao_atual,
            'receita_atual': self.receita_atual,
            'receita_com_ai_growth': self.receita_com_ai_growth,
            'aumento_receita': self.aumento_receita,
            'economia_anual': self.economia_anual,
            'data_calculo': self.data_calculo.isoformat() if self.data_calculo else None
        }

