from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.ai_growth import Cliente, Plano, Assinatura, Campanha, Lead, ROICalculation
from datetime import datetime

ai_growth_bp = Blueprint('ai_growth', __name__)

# Rotas para Planos
@ai_growth_bp.route('/planos', methods=['GET'])
def get_planos():
    try:
        planos = Plano.query.filter_by(ativo=True).all()
        return jsonify([plano.to_dict() for plano in planos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_growth_bp.route('/planos', methods=['POST'])
def create_plano():
    try:
        data = request.get_json()
        plano = Plano(
            nome=data['nome'],
            preco=data['preco'],
            descricao=data.get('descricao'),
            beneficios=data.get('beneficios', []),
            campanhas_ativas=data.get('campanhas_ativas', 1),
            criativos_mes=data.get('criativos_mes', 2),
            relatorios=data.get('relatorios', 'mensais'),
            suporte=data.get('suporte', 'whatsapp')
        )
        db.session.add(plano)
        db.session.commit()
        return jsonify(plano.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Clientes
@ai_growth_bp.route('/clientes', methods=['GET'])
def get_clientes():
    try:
        clientes = Cliente.query.filter_by(ativo=True).all()
        return jsonify([cliente.to_dict() for cliente in clientes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_growth_bp.route('/clientes', methods=['POST'])
def create_cliente():
    try:
        data = request.get_json()
        
        # Verificar se email já existe
        cliente_existente = Cliente.query.filter_by(email=data['email']).first()
        if cliente_existente:
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        cliente = Cliente(
            nome=data['nome'],
            email=data['email'],
            telefone=data.get('telefone'),
            empresa=data.get('empresa')
        )
        db.session.add(cliente)
        db.session.commit()
        return jsonify(cliente.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_growth_bp.route('/clientes/<int:cliente_id>', methods=['GET'])
def get_cliente(cliente_id):
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        return jsonify(cliente.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rotas para Assinaturas
@ai_growth_bp.route('/assinaturas', methods=['GET'])
def get_assinaturas():
    try:
        assinaturas = Assinatura.query.all()
        return jsonify([assinatura.to_dict() for assinatura in assinaturas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_growth_bp.route('/assinaturas', methods=['POST'])
def create_assinatura():
    try:
        data = request.get_json()
        assinatura = Assinatura(
            cliente_id=data['cliente_id'],
            plano_id=data['plano_id'],
            valor_pago=data['valor_pago'],
            forma_pagamento=data.get('forma_pagamento')
        )
        db.session.add(assinatura)
        db.session.commit()
        return jsonify(assinatura.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Campanhas
@ai_growth_bp.route('/campanhas', methods=['GET'])
def get_campanhas():
    try:
        cliente_id = request.args.get('cliente_id')
        if cliente_id:
            campanhas = Campanha.query.filter_by(cliente_id=cliente_id).all()
        else:
            campanhas = Campanha.query.all()
        return jsonify([campanha.to_dict() for campanha in campanhas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_growth_bp.route('/campanhas', methods=['POST'])
def create_campanha():
    try:
        data = request.get_json()
        campanha = Campanha(
            cliente_id=data['cliente_id'],
            nome=data['nome'],
            plataforma=data['plataforma'],
            objetivo=data['objetivo'],
            orcamento_diario=data['orcamento_diario']
        )
        db.session.add(campanha)
        db.session.commit()
        return jsonify(campanha.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_growth_bp.route('/campanhas/<int:campanha_id>/metricas', methods=['PUT'])
def update_metricas_campanha(campanha_id):
    try:
        data = request.get_json()
        campanha = Campanha.query.get_or_404(campanha_id)
        
        campanha.impressoes = data.get('impressoes', campanha.impressoes)
        campanha.cliques = data.get('cliques', campanha.cliques)
        campanha.conversoes = data.get('conversoes', campanha.conversoes)
        campanha.gasto_total = data.get('gasto_total', campanha.gasto_total)
        
        db.session.commit()
        return jsonify(campanha.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Leads
@ai_growth_bp.route('/leads', methods=['GET'])
def get_leads():
    try:
        leads = Lead.query.order_by(Lead.data_cadastro.desc()).all()
        return jsonify([lead.to_dict() for lead in leads]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_growth_bp.route('/leads', methods=['POST'])
def create_lead():
    try:
        data = request.get_json()
        lead = Lead(
            nome=data['nome'],
            email=data['email'],
            telefone=data.get('telefone'),
            empresa=data.get('empresa'),
            plano_interesse=data.get('plano_interesse'),
            origem=data.get('origem', 'landing_page'),
            observacoes=data.get('observacoes')
        )
        db.session.add(lead)
        db.session.commit()
        return jsonify(lead.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_growth_bp.route('/leads/<int:lead_id>/status', methods=['PUT'])
def update_lead_status(lead_id):
    try:
        data = request.get_json()
        lead = Lead.query.get_or_404(lead_id)
        lead.status = data['status']
        if 'observacoes' in data:
            lead.observacoes = data['observacoes']
        db.session.commit()
        return jsonify(lead.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rota para Calculadora ROI
@ai_growth_bp.route('/calcular-roi', methods=['POST'])
def calcular_roi():
    try:
        data = request.get_json()
        
        investimento_mensal = float(data['investimento_mensal'])
        ticket_medio = float(data['ticket_medio'])
        taxa_conversao_atual = float(data['taxa_conversao_atual'])
        
        # Cálculos baseados na metodologia AI.GROWTH
        # Assumindo melhoria de 40% na taxa de conversão com automação IA
        melhoria_conversao = 1.4
        taxa_conversao_nova = taxa_conversao_atual * melhoria_conversao
        
        # Receita atual
        leads_mes = investimento_mensal / 15  # Assumindo R$ 15 por lead
        conversoes_atuais = leads_mes * (taxa_conversao_atual / 100)
        receita_atual = conversoes_atuais * ticket_medio
        
        # Receita com AI.GROWTH
        conversoes_novas = leads_mes * (taxa_conversao_nova / 100)
        receita_com_ai_growth = conversoes_novas * ticket_medio
        
        # Aumento de receita
        aumento_receita = receita_com_ai_growth - receita_atual
        
        # Economia anual (considerando redução de 30% nos custos operacionais)
        economia_operacional = investimento_mensal * 0.3 * 12
        economia_anual = (aumento_receita * 12) + economia_operacional
        
        # Salvar cálculo no banco
        calculo = ROICalculation(
            investimento_mensal=investimento_mensal,
            ticket_medio=ticket_medio,
            taxa_conversao_atual=taxa_conversao_atual,
            receita_atual=receita_atual,
            receita_com_ai_growth=receita_com_ai_growth,
            aumento_receita=aumento_receita,
            economia_anual=economia_anual,
            ip_origem=request.remote_addr
        )
        db.session.add(calculo)
        db.session.commit()
        
        return jsonify({
            'receita_atual': round(receita_atual, 2),
            'receita_com_ai_growth': round(receita_com_ai_growth, 2),
            'aumento_receita': round(aumento_receita, 2),
            'aumento_percentual': round(((receita_com_ai_growth - receita_atual) / receita_atual * 100), 1),
            'economia_anual': round(economia_anual, 2),
            'roi_anual': round((economia_anual / (investimento_mensal * 12)) * 100, 1),
            'payback_meses': round((investimento_mensal * 12) / (aumento_receita * 12), 1) if aumento_receita > 0 else 0
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rota para Dashboard - Métricas Gerais
@ai_growth_bp.route('/dashboard/metricas', methods=['GET'])
def get_dashboard_metricas():
    try:
        # Contar totais
        total_clientes = Cliente.query.filter_by(ativo=True).count()
        total_campanhas_ativas = Campanha.query.filter_by(status='ativa').count()
        total_leads = Lead.query.count()
        total_assinaturas_ativas = Assinatura.query.filter_by(status='ativa').count()
        
        # Calcular receita total
        assinaturas_ativas = Assinatura.query.filter_by(status='ativa').all()
        receita_mensal = sum([assinatura.valor_pago for assinatura in assinaturas_ativas])
        
        # Métricas de campanhas
        campanhas_ativas = Campanha.query.filter_by(status='ativa').all()
        total_impressoes = sum([campanha.impressoes for campanha in campanhas_ativas])
        total_cliques = sum([campanha.cliques for campanha in campanhas_ativas])
        total_conversoes = sum([campanha.conversoes for campanha in campanhas_ativas])
        total_gasto = sum([campanha.gasto_total for campanha in campanhas_ativas])
        
        # Calcular médias
        ctr_medio = round((total_cliques / total_impressoes * 100), 2) if total_impressoes > 0 else 0
        cpc_medio = round((total_gasto / total_cliques), 2) if total_cliques > 0 else 0
        cpa_medio = round((total_gasto / total_conversoes), 2) if total_conversoes > 0 else 0
        
        return jsonify({
            'total_clientes': total_clientes,
            'total_campanhas_ativas': total_campanhas_ativas,
            'total_leads': total_leads,
            'total_assinaturas_ativas': total_assinaturas_ativas,
            'receita_mensal': round(receita_mensal, 2),
            'total_impressoes': total_impressoes,
            'total_cliques': total_cliques,
            'total_conversoes': total_conversoes,
            'total_gasto': round(total_gasto, 2),
            'ctr_medio': ctr_medio,
            'cpc_medio': cpc_medio,
            'cpa_medio': cpa_medio
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para inicializar dados de exemplo
@ai_growth_bp.route('/init-data', methods=['POST'])
def init_data():
    try:
        # Criar planos padrão se não existirem
        if Plano.query.count() == 0:
            planos = [
                {
                    'nome': 'Starter',
                    'preco': 297.0,
                    'descricao': 'Ideal para PMEs iniciantes',
                    'beneficios': [
                        'Dashboard com KPIs principais',
                        'Gestão básica de campanhas',
                        'Relatórios automáticos mensais',
                        'Tracking de conversão básico',
                        'Suporte via WhatsApp',
                        '1 campanha ativa',
                        '2 criativos por mês'
                    ],
                    'campanhas_ativas': 1,
                    'criativos_mes': 2,
                    'relatorios': 'mensais',
                    'suporte': 'whatsapp'
                },
                {
                    'nome': 'Aceleração',
                    'preco': 597.0,
                    'descricao': 'Para empresas em crescimento',
                    'beneficios': [
                        'Todos os benefícios do Starter',
                        'Gestão multi-plataforma (Google + Facebook)',
                        'Email marketing integrado',
                        'Landing pages builder',
                        'A/B testing automático',
                        'Relatórios semanais',
                        '2 campanhas ativas',
                        '4 criativos por mês',
                        'Consultoria estratégica mensal'
                    ],
                    'campanhas_ativas': 2,
                    'criativos_mes': 4,
                    'relatorios': 'semanais',
                    'suporte': 'prioritario'
                },
                {
                    'nome': 'Crescimento Exponencial',
                    'preco': 797.0,
                    'descricao': 'Para empresas que querem escalar',
                    'beneficios': [
                        'Todos os benefícios anteriores',
                        'CRM integrado completo',
                        'Análise de concorrência',
                        'Automação avançada com IA',
                        'Attribution modeling',
                        'Forecasting e predições',
                        'Suporte prioritário',
                        '4 campanhas ativas',
                        '5 criativos por mês',
                        'Gerente de conta dedicado',
                        'Integrações avançadas (TikTok, LinkedIn)'
                    ],
                    'campanhas_ativas': 4,
                    'criativos_mes': 5,
                    'relatorios': 'quinzenais',
                    'suporte': 'dedicado'
                }
            ]
            
            for plano_data in planos:
                plano = Plano(**plano_data)
                db.session.add(plano)
            
            db.session.commit()
            
        return jsonify({'message': 'Dados inicializados com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

