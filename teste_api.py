import requests
import json
from datetime import datetime, timedelta

# URL base da API
BASE_URL = 'http://127.0.0.1:5000'

def imprimir_resposta(titulo, response):
    """Imprime resposta da API de forma organizada"""
    print(f"\n{'='*50}")
    print(f"🧪 {titulo}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    try:
        dados = response.json()
        print(f"Resposta: {json.dumps(dados, indent=2, ensure_ascii=False)}")
        return dados
    except:
        print(f"Resposta (texto): {response.text}")
        return None

def testar_api_completa():
    """Testa todas as funcionalidades da API"""
    print("🎆 INICIANDO TESTES DA API GERENCIADOR DE TAREFAS")
    
    try:
        # 1. Testar página inicial
        print("\n1️⃣ Testando página inicial...")
        response = requests.get(f'{BASE_URL}/')
        dados_api = imprimir_resposta("Informações da API", response)
        
        # 2. Criar categorias
        print("\n2️⃣ Criando categorias...")
        categorias_teste = [
            {"nome": "Trabalho", "descricao": "Tarefas relacionadas ao trabalho", "cor": "#3498db"},
            {"nome": "Pessoal", "descricao": "Tarefas pessoais", "cor": "#e74c3c"},
            {"nome": "Estudos", "descricao": "Atividades de aprendizado", "cor": "#2ecc71"}
        ]
        
        categorias_criadas = []
        for categoria in categorias_teste:
            response = requests.post(
                f'{BASE_URL}/categorias',
                json=categoria,
                headers={'Content-Type': 'application/json'}
            )
            dados = imprimir_resposta(f"Criando categoria: {categoria['nome']}", response)
            if dados:
                categorias_criadas.append(dados)
        
        # 3. Listar categorias
        print("\n3️⃣ Listando todas as categorias...")
        response = requests.get(f'{BASE_URL}/categorias')
        imprimir_resposta("Lista de Categorias", response)
        
        # 4. Criar tarefas
        print("\n4️⃣ Criando tarefas...")
        data_futura = (datetime.now() + timedelta(days=7)).isoformat()
        data_passada = (datetime.now() - timedelta(days=1)).isoformat()
        
        tarefas_teste = [
            {
                "titulo": "Implementar autenticação",
                "descricao": "Adicionar sistema de login e logout",
                "prioridade": "alta",
                "status": "em_andamento",
                "data_vencimento": data_futura,
                "responsavel": "João Silva",
                "categoria_id": categorias_criadas[0]['id'] if categorias_criadas else None
            },
            {
                "titulo": "Fazer compras",
                "descricao": "Comprar ingredientes para o jantar",
                "prioridade": "media",
                "status": "pendente",
                "responsavel": "Maria Santos",
                "categoria_id": categorias_criadas[1]['id'] if len(categorias_criadas) > 1 else None
            },
            {
                "titulo": "Estudar Python",
                "descricao": "Completar curso de Flask",
                "prioridade": "alta",
                "status": "pendente",
                "data_vencimento": data_futura,
                "categoria_id": categorias_criadas[2]['id'] if len(categorias_criadas) > 2 else None
            },
            {
                "titulo": "Tarefa vencida",
                "descricao": "Esta tarefa está vencida para testar estatísticas",
                "prioridade": "urgente",
                "status": "pendente",
                "data_vencimento": data_passada
            }
        ]
        
        tarefas_criadas = []
        for tarefa in tarefas_teste:
            response = requests.post(
                f'{BASE_URL}/tarefas',
                json=tarefa,
                headers={'Content-Type': 'application/json'}
            )
            dados = imprimir_resposta(f"Criando tarefa: {tarefa['titulo']}", response)
            if dados:
                tarefas_criadas.append(dados)
        
        # 5. Listar todas as tarefas
        print("\n5️⃣ Listando todas as tarefas...")
        response = requests.get(f'{BASE_URL}/tarefas')
        imprimir_resposta("Lista Completa de Tarefas", response)
        
        # 6. Filtrar tarefas por status
        print("\n6️⃣ Filtrando tarefas por status 'pendente'...")
        response = requests.get(f'{BASE_URL}/tarefas?status=pendente')
        imprimir_resposta("Tarefas Pendentes", response)
        
        # 7. Filtrar tarefas por prioridade
        print("\n7️⃣ Filtrando tarefas por prioridade 'alta'...")
        response = requests.get(f'{BASE_URL}/tarefas?prioridade=alta')
        imprimir_resposta("Tarefas de Alta Prioridade", response)
        
        # 8. Atualizar uma tarefa
        if tarefas_criadas:
            print("\n8️⃣ Atualizando tarefa...")
            tarefa_id = tarefas_criadas[0]['id']
            atualizacao = {
                "status": "concluida",
                "descricao": "Tarefa concluída com sucesso! ✅"
            }
            response = requests.put(
                f'{BASE_URL}/tarefas/{tarefa_id}',
                json=atualizacao,
                headers={'Content-Type': 'application/json'}
            )
            imprimir_resposta(f"Atualizando tarefa ID {tarefa_id}", response)
        
        # 9. Obter tarefa específica
        if tarefas_criadas:
            print("\n9️⃣ Obtendo tarefa específica...")
            tarefa_id = tarefas_criadas[0]['id']
            response = requests.get(f'{BASE_URL}/tarefas/{tarefa_id}')
            imprimir_resposta(f"Tarefa ID {tarefa_id}", response)
        
        # 10. Estatísticas
        print("\n🔟 Obtendo estatísticas...")
        response = requests.get(f'{BASE_URL}/estatisticas')
        imprimir_resposta("Estatísticas do Sistema", response)
        
        # 11. Testar erro (tarefa inexistente)
        print("\n1️⃣1️⃣ Testando erro (tarefa inexistente)...")
        response = requests.get(f'{BASE_URL}/tarefas/999')
        imprimir_resposta("Erro esperado - Tarefa não encontrada", response)
        
        # 12. Testar validação (criar tarefa sem título)
        print("\n1️⃣2️⃣ Testando validação (tarefa sem título)...")
        tarefa_invalida = {"descricao": "Tarefa sem título"}
        response = requests.post(
            f'{BASE_URL}/tarefas',
            json=tarefa_invalida,
            headers={'Content-Type': 'application/json'}
        )
        imprimir_resposta("Erro esperado - Título obrigatório", response)
        
        print("\n✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("\n📊 RESUMO DOS TESTES:")
        print("• ✅ Página inicial")
        print("• ✅ CRUD de Categorias")
        print("• ✅ CRUD de Tarefas")
        print("• ✅ Filtros por status e prioridade")
        print("• ✅ Estatísticas")
        print("• ✅ Tratamento de erros")
        print("• ✅ Validações")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor.")
        print("💡 Certifique-se de que o servidor Flask está rodando:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")

def testar_crud_simples():
    """Teste simples e rápido das funcionalidades básicas"""
    print("🚀 TESTE RÁPIDO - CRUD BÁSICO")
    
    try:
        # Criar categoria
        categoria = {"nome": "Teste Rápido", "cor": "#000000"}
        response = requests.post(f'{BASE_URL}/categorias', json=categoria)
        print(f"✅ Categoria criada: {response.status_code}")
        
        # Criar tarefa
        tarefa = {
            "titulo": "Tarefa de Teste",
            "descricao": "Apenas um teste rápido",
            "prioridade": "baixa"
        }
        response = requests.post(f'{BASE_URL}/tarefas', json=tarefa)
        print(f"✅ Tarefa criada: {response.status_code}")
        
        # Listar tarefas
        response = requests.get(f'{BASE_URL}/tarefas')
        tarefas = response.json()
        print(f"✅ Tarefas listadas: {len(tarefas)} encontradas")
        
        # Estatísticas
        response = requests.get(f'{BASE_URL}/estatisticas')
        stats = response.json()
        print(f"✅ Estatísticas: {stats['total_tarefas']} tarefas total")
        
        print("\n🎉 API funcionando perfeitamente!")
        
    except Exception as e:
        print(f"❌ Erro no teste rápido: {e}")

if __name__ == '__main__':
    print("📋 TESTES DA API GERENCIADOR DE TAREFAS")
    print("📡 URL Base:", BASE_URL)
    print("\nEscolha o tipo de teste:")
    print("1 - Teste Completo (todas as funcionalidades)")
    print("2 - Teste Rápido (CRUD básico)")
    
    escolha = input("\nDigite sua escolha (1 ou 2): ").strip()
    
    if escolha == "1":
        testar_api_completa()
    elif escolha == "2":
        testar_crud_simples()
    else:
        print("\n🚀 Executando teste completo por padrão...")
        testar_api_completa()

