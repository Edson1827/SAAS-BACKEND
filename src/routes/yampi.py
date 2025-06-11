from flask import Blueprint, request, jsonify
import hashlib
import hmac
import os
import requests
from src.models.user import db
from src.models.ai_growth import Cliente, Plano, Assinatura

yampi_bp = Blueprint('yampi', __name__)

# Configurações da Yampi
YAMPI_API_BASE = "https://api.yampi.com.br/v1"
YAMPI_TOKEN = "VA3EgF8O61Nx4PdWg2ZOw58Zj1UKGYDySPgrVysr"
YAMPI_SECRET = "wh_gztdMhoEddvWyDUFgKWijCcJpCIZFt0vn5xwy"
YAMPI_ALIAS = "ai-growth"

def get_yampi_headers():
    """Retorna headers para requisições à API Yampi"""
    return {
        'Authorization': f'Bearer {YAMPI_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

def verify_yampi_signature(payload, signature, secret):
    """Verifica a assinatura do webhook da Yampi"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

@yampi_bp.route('/checkout/create', methods=['POST'])
def create_checkout():
    """Cria um checkout transparente na Yampi"""
    try:
        data = request.json
        product_id = data.get('product_id')
        customer_data = data.get('customer', {})
        
        # Mapear IDs dos produtos
        product_map = {
            'starter': '40990477',
            'aceleracao': '40990482', 
            'crescimento': '40990485'
        }
        
        yampi_product_id = product_map.get(product_id)
        if not yampi_product_id:
            return jsonify({'error': 'Produto não encontrado'}), 400
        
        # Criar pedido na Yampi
        checkout_data = {
            "customer": {
                "name": customer_data.get('name', ''),
                "email": customer_data.get('email', ''),
                "phone": customer_data.get('phone', ''),
                "document": customer_data.get('document', '')
            },
            "items": [
                {
                    "sku_id": yampi_product_id,
                    "quantity": 1
                }
            ],
            "payment": {
                "method": "credit_card"
            }
        }
        
        response = requests.post(
            f"{YAMPI_API_BASE}/orders",
            json=checkout_data,
            headers=get_yampi_headers()
        )
        
        if response.status_code == 201:
            order_data = response.json()
            return jsonify({
                'status': 'success',
                'order_id': order_data.get('id'),
                'checkout_url': order_data.get('checkout_url'),
                'payment_data': order_data.get('payment')
            })
        else:
            return jsonify({
                'error': 'Erro ao criar checkout',
                'details': response.text
            }), 400
            
    except Exception as e:
        print(f"Erro ao criar checkout: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@yampi_bp.route('/payment/process', methods=['POST'])
def process_payment():
    """Processa pagamento via checkout transparente com upsells"""
    try:
        data = request.json
        customer_data = data.get('customer', {})
        product_id = data.get('product_id')
        upsells = data.get('upsells', [])
        total_monthly = data.get('total_monthly', 0)
        total_onetime = data.get('total_onetime', 0)
        
        # Mapear IDs dos produtos principais
        product_map = {
            'starter': '40990477',
            'aceleracao': '40990482', 
            'crescimento': '40990485'
        }
        
        yampi_product_id = product_map.get(product_id)
        if not yampi_product_id:
            return jsonify({'error': 'Produto não encontrado'}), 400
        
        # Preparar itens do pedido (produto principal + upsells)
        order_items = [
            {
                "sku_id": yampi_product_id,
                "quantity": 1,
                "price": total_monthly * 12  # Valor anual
            }
        ]
        
        # Adicionar upsells como itens separados
        upsell_map = {
            'relatorios_semanais_starter': 'UPSELL_REL_SEM_ST',
            'criativos_adicionais': 'UPSELL_CRIATIVOS',
            'suporte_prioritario_starter': 'UPSELL_SUP_PRIOR_ST',
            'relatorios_semanais_aceleracao': 'UPSELL_REL_SEM_AC',
            'campanha_adicional': 'UPSELL_CAMPANHA',
            'suporte_prioritario_aceleracao': 'UPSELL_SUP_PRIOR_AC',
            'mapeamento_completo': 'UPSELL_MAPEAMENTO',
            'consultoria_mensal': 'UPSELL_CONSULTORIA'
        }
        
        for upsell in upsells:
            upsell_sku = upsell_map.get(upsell.get('id'))
            if upsell_sku:
                price = upsell.get('price', 0)
                if upsell.get('oneTime'):
                    # Pagamento único
                    order_items.append({
                        "sku": upsell_sku,
                        "quantity": 1,
                        "price": price,
                        "name": upsell.get('title', ''),
                        "type": "onetime"
                    })
                else:
                    # Pagamento recorrente (anual)
                    order_items.append({
                        "sku": upsell_sku,
                        "quantity": 1,
                        "price": price * 12,
                        "name": upsell.get('title', ''),
                        "type": "recurring"
                    })
        
        # Criar pedido na Yampi
        order_data = {
            "customer": {
                "name": customer_data.get('name', ''),
                "email": customer_data.get('email', ''),
                "phone": customer_data.get('phone', ''),
                "document": customer_data.get('document', '')
            },
            "items": order_items,
            "payment": {
                "method": "credit_card",
                "card": {
                    "number": data.get('card_number', '').replace(' ', ''),
                    "holder_name": data.get('card_holder', ''),
                    "expiry_month": data.get('card_month', ''),
                    "expiry_year": data.get('card_year', ''),
                    "cvv": data.get('card_cvv', '')
                },
                "installments": data.get('installments', 12)
            },
            "metadata": {
                "upsells_count": len(upsells),
                "total_monthly": total_monthly,
                "total_onetime": total_onetime,
                "source": "ai_growth_mvp"
            }
        }
        
        response = requests.post(
            f"{YAMPI_API_BASE}/orders",
            json=order_data,
            headers=get_yampi_headers()
        )
        
        if response.status_code in [200, 201]:
            order_result = response.json()
            
            # Salvar dados localmente para controle
            try:
                # Criar ou atualizar cliente
                cliente = Cliente.query.filter_by(email=customer_data.get('email')).first()
                if not cliente:
                    cliente = Cliente(
                        nome=customer_data.get('name', ''),
                        email=customer_data.get('email', ''),
                        telefone=customer_data.get('phone', ''),
                        empresa='Não informado'
                    )
                    db.session.add(cliente)
                    db.session.flush()
                
                # Buscar ou criar plano
                plano_names = {
                    'starter': 'Starter',
                    'aceleracao': 'Aceleração',
                    'crescimento': 'Crescimento Exponencial'
                }
                plano_nome = plano_names.get(product_id, 'Starter')
                
                plano = Plano.query.filter_by(nome=plano_nome).first()
                if not plano:
                    valores = {
                        'Starter': 3564,
                        'Aceleração': 7164,
                        'Crescimento Exponencial': 9564
                    }
                    plano = Plano(
                        nome=plano_nome,
                        preco=valores.get(plano_nome, 3564),
                        descricao=f'Plano {plano_nome}'
                    )
                    db.session.add(plano)
                    db.session.flush()
                
                # Criar assinatura
                assinatura = Assinatura(
                    cliente_id=cliente.id,
                    plano_id=plano.id,
                    status='processando',
                    valor_pago=total_monthly * 12 + total_onetime,
                    yampi_order_id=order_result.get('id'),
                    metodo_pagamento='cartao',
                    upsells_data=str(upsells)  # Salvar upsells como string JSON
                )
                db.session.add(assinatura)
                db.session.commit()
                
            except Exception as db_error:
                print(f"Erro ao salvar no banco: {str(db_error)}")
                # Continuar mesmo com erro no banco local
            
            return jsonify({
                'status': 'success',
                'payment_status': order_result.get('status', 'pending'),
                'transaction_id': order_result.get('id'),
                'order_id': order_result.get('id'),
                'total_amount': total_monthly * 12 + total_onetime,
                'upsells_included': len(upsells)
            })
        else:
            error_details = response.text
            print(f"Erro Yampi: {error_details}")
            return jsonify({
                'error': 'Erro ao processar pagamento',
                'details': error_details,
                'status_code': response.status_code
            }), 400
            
    except Exception as e:
        print(f"Erro ao processar pagamento: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500

@yampi_bp.route('/webhook/yampi', methods=['POST'])
def yampi_webhook():
    """Webhook para receber notificações da Yampi"""
    try:
        # Verificar assinatura
        signature = request.headers.get('X-Yampi-Signature')
        
        if signature:
            if not verify_yampi_signature(request.data, signature, YAMPI_SECRET):
                return jsonify({'error': 'Invalid signature'}), 401
        
        data = request.json
        event_type = data.get('event')
        
        if event_type == 'order.paid':
            # Pagamento aprovado
            order = data.get('order', {})
            customer = order.get('customer', {})
            items = order.get('items', [])
            
            if items:
                item = items[0]  # Primeiro item (nosso plano)
                product_id = str(item.get('sku_id', ''))
                
                # Mapear produto para plano (IDs atualizados)
                plano_map = {
                    '40990477': 'Starter',
                    '40990482': 'Aceleração', 
                    '40990485': 'Crescimento Exponencial'
                }
                
                plano_nome = plano_map.get(product_id, 'Starter')
                
                # Criar ou atualizar cliente
                cliente = Cliente.query.filter_by(email=customer.get('email')).first()
                if not cliente:
                    cliente = Cliente(
                        nome=customer.get('name', ''),
                        email=customer.get('email', ''),
                        telefone=customer.get('phone', ''),
                        empresa=customer.get('company', 'Não informado')
                    )
                    db.session.add(cliente)
                    db.session.flush()
                
                # Buscar plano
                plano = Plano.query.filter_by(nome=plano_nome).first()
                if not plano:
                    # Criar plano se não existir
                    valores = {
                        'Starter': 3564,
                        'Aceleração': 7164,
                        'Crescimento Exponencial': 9564
                    }
                    plano = Plano(
                        nome=plano_nome,
                        preco=valores.get(plano_nome, 3564),
                        descricao=f'Plano {plano_nome}'
                    )
                    db.session.add(plano)
                    db.session.flush()
                
                # Criar assinatura
                assinatura = Assinatura(
                    cliente_id=cliente.id,
                    plano_id=plano.id,
                    status='ativa',
                    valor_pago=order.get('total', 0),
                    yampi_order_id=order.get('id'),
                    metodo_pagamento=order.get('payment_method', 'cartao')
                )
                db.session.add(assinatura)
                
                # Salvar tudo
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Cliente criado com sucesso',
                    'cliente_id': cliente.id,
                    'plano': plano_nome
                })
        
        elif event_type == 'order.cancelled':
            # Pagamento cancelado
            order = data.get('order', {})
            yampi_order_id = order.get('id')
            
            # Cancelar assinatura
            assinatura = Assinatura.query.filter_by(yampi_order_id=yampi_order_id).first()
            if assinatura:
                assinatura.status = 'cancelada'
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Assinatura cancelada'
                })
        
        return jsonify({'status': 'success', 'message': 'Event processed'})
        
    except Exception as e:
        print(f"Erro no webhook Yampi: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
