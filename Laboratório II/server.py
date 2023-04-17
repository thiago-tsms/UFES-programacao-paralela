import sys
import flwr as fl

num_rounds=int(sys.argv[1])

def weighted_average(metrics):
    # Multiply accuracy of each client by number of examples used
    acc = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    results = {"accuracy": sum(acc) / sum(examples)}
    return results

strategy = fl.server.strategy.FedAvg(
    fraction_fit=0.9,           # Escolher aleatoriamento 90% dos clientes
    fraction_evaluate=1,        # Usar todos os clientes para avaliação do modelo
    min_fit_clients=5,          # Minimo de 5 clientes para o treinamento
    min_evaluate_clients=5,    # Mínimo de 5 clientes para avaliação
    min_available_clients=5,    # Mínimo de 5 clientes para comessar o treinamento
    evaluate_metrics_aggregation_fn=weighted_average,   # Usar esta função como função de agregação da métricas
)

# Start Flower server
result = fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=num_rounds),
    strategy=strategy,
    #config=fl.server.serverConfigserverConfig(num_rounds=5),
)

with open(f'results/result_{num_rounds}.csv', "w") as arquivo:
    for dt in result.metrics_distributed['accuracy']:
	    arquivo.write(f'{dt[0]};{dt[1]}\n')