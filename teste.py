from flask import Flask, request, jsonify, flash, redirect, url_for
from datetime import datetime
# Supondo que você tenha o modelo User e o db configurados corretamente
# from sua_aplicacao import User, db

app = Flask(__name__)

@app.route('/buscaCli', methods=['GET'])
@login_required 
def buscar_usuario():
    nome = request.args.get('nome')

    if not nome:
        return jsonify({"error": "Nome não fornecido"}), 400

    usuario = User.query.filter(
        (User.first_name.ilike(f"%{nome}%")) | 
        (User.last_name.ilike(f"%{nome}%"))
    ).first()

    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    return jsonify({
        "first_name": usuario.first_name,
        "last_name": usuario.last_name,
        "endereco": usuario.endereco if usuario.endereco else "Não informado",
        "data_nascimento": usuario.data_nascimento.strftime('%Y-%m-%d') if usuario.data_nascimento else "Não informado",
        "forma_pagamento": usuario.forma_pagamento if usuario.forma_pagamento else "Não informado",
        "dias_treino": usuario.dias_treino if usuario.dias_treino else "Dias de Treino não cadastrados"
    })

@app.route('/alteraCli', methods=['POST'])
@login_required
def atualizar_usuario():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Dados não fornecidos"}), 400

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    endereco = data.get('endereco')
    data_nascimento_str = data.get('data_nascimento')
    forma_pagamento = data.get('forma_pagamento')
    dias_treino = data.get('dias_treino')

    if not first_name or not last_name:
        return jsonify({"error": "Nome e sobrenome são obrigatórios"}), 400

    usuario = User.query.filter_by(first_name=first_name, last_name=last_name).first()

    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    # Validando e convertendo a data de nascimento
    try:
        data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date() if data_nascimento_str else None
    except ValueError:
        return jsonify({"error": "Formato de data inválido para Data de Nascimento."}), 400

    # Atualizando o usuário no banco de dados
    usuario.endereco = endereco
    usuario.data_nascimento = data_nascimento
    usuario.forma_pagamento = forma_pagamento
    usuario.dias_treino = dias_treino

    try:
        db.session.commit()
        return jsonify({"message": "Usuário atualizado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao atualizar usuário: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)