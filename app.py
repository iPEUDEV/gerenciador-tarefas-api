from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

# Criar a aplicação Flask
app = Flask(__name__)

# Configurar o banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gerenciador_tarefas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Enum para status da tarefa
class StatusTarefa(enum.Enum):
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"

# Enum para prioridade
class PrioridadeTarefa(enum.Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"

# Modelo de Tarefa
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    status = db.Column(db.Enum(StatusTarefa), default=StatusTarefa.PENDENTE, nullable=False)
    prioridade = db.Column(db.Enum(PrioridadeTarefa), default=PrioridadeTarefa.MEDIA, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_vencimento = db.Column(db.DateTime)
    data_conclusao = db.Column(db.DateTime)
    responsavel = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Tarefa {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'status': self.status.value if self.status else None,
            'prioridade': self.prioridade.value if self.prioridade else None,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'responsavel': self.responsavel
        }

# Modelo de Categoria
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    cor = db.Column(db.String(7))  # Código hex da cor #FFFFFF
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com tarefas
    tarefas = db.relationship('Tarefa', backref='categoria', lazy=True)
    
    def __repr__(self):
        return f'<Categoria {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'cor': self.cor,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'total_tarefas': len(self.tarefas)
        }

# Adicionar coluna categoria_id na tabela Tarefa
Tarefa.categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))

# ===== ROTAS DA API =====

@app.route('/')
def index():
    return jsonify({
        'message': 'API Gerenciador de Tarefas',
        'version': '1.0',
        'endpoints': {
            'tarefas': '/tarefas',
            'categorias': '/categorias',
            'estatisticas': '/estatisticas'
        }
    })

# ===== ROTAS DE TAREFAS =====

@app.route('/tarefas', methods=['GET'])
def listar_tarefas():
    # Filtros opcionais
    status = request.args.get('status')
    prioridade = request.args.get('prioridade')
    categoria_id = request.args.get('categoria_id')
    
    query = Tarefa.query
    
    if status:
        try:
            status_enum = StatusTarefa(status)
            query = query.filter(Tarefa.status == status_enum)
        except ValueError:
            return jsonify({'erro': f'Status inválido: {status}'}), 400
    
    if prioridade:
        try:
            prioridade_enum = PrioridadeTarefa(prioridade)
            query = query.filter(Tarefa.prioridade == prioridade_enum)
        except ValueError:
            return jsonify({'erro': f'Prioridade inválida: {prioridade}'}), 400
    
    if categoria_id:
        query = query.filter(Tarefa.categoria_id == categoria_id)
    
    tarefas = query.all()
    return jsonify([tarefa.to_dict() for tarefa in tarefas])

@app.route('/tarefas', methods=['POST'])
def criar_tarefa():
    dados = request.get_json()
    
    if not dados or 'titulo' not in dados:
        return jsonify({'erro': 'Título é obrigatório'}), 400
    
    # Validar status se fornecido
    status = StatusTarefa.PENDENTE
    if 'status' in dados:
        try:
            status = StatusTarefa(dados['status'])
        except ValueError:
            return jsonify({'erro': f'Status inválido: {dados["status"]}'}), 400
    
    # Validar prioridade se fornecida
    prioridade = PrioridadeTarefa.MEDIA
    if 'prioridade' in dados:
        try:
            prioridade = PrioridadeTarefa(dados['prioridade'])
        except ValueError:
            return jsonify({'erro': f'Prioridade inválida: {dados["prioridade"]}'}), 400
    
    # Validar data de vencimento se fornecida
    data_vencimento = None
    if 'data_vencimento' in dados:
        try:
            data_vencimento = datetime.fromisoformat(dados['data_vencimento'])
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use ISO format: YYYY-MM-DDTHH:MM:SS'}), 400
    
    tarefa = Tarefa(
        titulo=dados['titulo'],
        descricao=dados.get('descricao'),
        status=status,
        prioridade=prioridade,
        data_vencimento=data_vencimento,
        responsavel=dados.get('responsavel'),
        categoria_id=dados.get('categoria_id')
    )
    
    try:
        db.session.add(tarefa)
        db.session.commit()
        return jsonify(tarefa.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao criar tarefa', 'detalhes': str(e)}), 500

@app.route('/tarefas/<int:id>', methods=['GET'])
def obter_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    return jsonify(tarefa.to_dict())

@app.route('/tarefas/<int:id>', methods=['PUT'])
def atualizar_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    dados = request.get_json()
    
    if not dados:
        return jsonify({'erro': 'Dados não fornecidos'}), 400
    
    # Atualizar campos
    if 'titulo' in dados:
        tarefa.titulo = dados['titulo']
    
    if 'descricao' in dados:
        tarefa.descricao = dados['descricao']
    
    if 'status' in dados:
        try:
            tarefa.status = StatusTarefa(dados['status'])
            # Se marcou como concluída, adicionar data de conclusão
            if tarefa.status == StatusTarefa.CONCLUIDA and not tarefa.data_conclusao:
                tarefa.data_conclusao = datetime.utcnow()
        except ValueError:
            return jsonify({'erro': f'Status inválido: {dados["status"]}'}), 400
    
    if 'prioridade' in dados:
        try:
            tarefa.prioridade = PrioridadeTarefa(dados['prioridade'])
        except ValueError:
            return jsonify({'erro': f'Prioridade inválida: {dados["prioridade"]}'}), 400
    
    if 'data_vencimento' in dados:
        if dados['data_vencimento']:
            try:
                tarefa.data_vencimento = datetime.fromisoformat(dados['data_vencimento'])
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido'}), 400
        else:
            tarefa.data_vencimento = None
    
    if 'responsavel' in dados:
        tarefa.responsavel = dados['responsavel']
    
    if 'categoria_id' in dados:
        tarefa.categoria_id = dados['categoria_id']
    
    try:
        db.session.commit()
        return jsonify(tarefa.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao atualizar tarefa', 'detalhes': str(e)}), 500

@app.route('/tarefas/<int:id>', methods=['DELETE'])
def deletar_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    
    try:
        db.session.delete(tarefa)
        db.session.commit()
        return jsonify({'message': 'Tarefa deletada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao deletar tarefa', 'detalhes': str(e)}), 500

# ===== ROTAS DE CATEGORIAS =====

@app.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = Categoria.query.all()
    return jsonify([categoria.to_dict() for categoria in categorias])

@app.route('/categorias', methods=['POST'])
def criar_categoria():
    dados = request.get_json()
    
    if not dados or 'nome' not in dados:
        return jsonify({'erro': 'Nome é obrigatório'}), 400
    
    categoria = Categoria(
        nome=dados['nome'],
        descricao=dados.get('descricao'),
        cor=dados.get('cor')
    )
    
    try:
        db.session.add(categoria)
        db.session.commit()
        return jsonify(categoria.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao criar categoria (nome já existe?)', 'detalhes': str(e)}), 500

@app.route('/categorias/<int:id>', methods=['GET'])
def obter_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    return jsonify(categoria.to_dict())

@app.route('/categorias/<int:id>', methods=['PUT'])
def atualizar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    dados = request.get_json()
    
    if not dados:
        return jsonify({'erro': 'Dados não fornecidos'}), 400
    
    if 'nome' in dados:
        categoria.nome = dados['nome']
    
    if 'descricao' in dados:
        categoria.descricao = dados['descricao']
    
    if 'cor' in dados:
        categoria.cor = dados['cor']
    
    try:
        db.session.commit()
        return jsonify(categoria.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao atualizar categoria', 'detalhes': str(e)}), 500

@app.route('/categorias/<int:id>', methods=['DELETE'])
def deletar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    
    # Verificar se há tarefas associadas
    if categoria.tarefas:
        return jsonify({
            'erro': 'Não é possível deletar categoria com tarefas associadas',
            'tarefas_associadas': len(categoria.tarefas)
        }), 400
    
    try:
        db.session.delete(categoria)
        db.session.commit()
        return jsonify({'message': 'Categoria deletada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao deletar categoria', 'detalhes': str(e)}), 500

# ===== ROTA DE ESTATÍSTICAS =====

@app.route('/estatisticas', methods=['GET'])
def obter_estatisticas():
    total_tarefas = Tarefa.query.count()
    
    # Estatísticas por status
    stats_status = {}
    for status in StatusTarefa:
        count = Tarefa.query.filter(Tarefa.status == status).count()
        stats_status[status.value] = count
    
    # Estatísticas por prioridade
    stats_prioridade = {}
    for prioridade in PrioridadeTarefa:
        count = Tarefa.query.filter(Tarefa.prioridade == prioridade).count()
        stats_prioridade[prioridade.value] = count
    
    # Tarefas vencidas
    tarefas_vencidas = Tarefa.query.filter(
        Tarefa.data_vencimento < datetime.utcnow(),
        Tarefa.status != StatusTarefa.CONCLUIDA
    ).count()
    
    # Total de categorias
    total_categorias = Categoria.query.count()
    
    return jsonify({
        'total_tarefas': total_tarefas,
        'total_categorias': total_categorias,
        'tarefas_vencidas': tarefas_vencidas,
        'por_status': stats_status,
        'por_prioridade': stats_prioridade
    })

# ===== INICIALIZAÇÃO =====

# Criar as tabelas do banco de dados
with app.app_context():
    db.create_all()
    print("🗄️  Banco de dados criado com sucesso!")
    print("📋 Modelos criados: Tarefa, Categoria")

if __name__ == '__main__':
    print("🚀 Iniciando API Gerenciador de Tarefas...")
    print("📡 Servidor rodando em: http://127.0.0.1:5000")
    print("📖 Documentação: GET /")
    app.run(debug=True)

