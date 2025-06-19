import requests
import csv
import time
from datetime import datetime
import logging
import os


# === CONFIGURAÇÕES DE LOG ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)

# === CONFIGURAÇÕES GERAIS ===
url = os.getenv('ZABBIX_URL')
token = os.getenv('ZABBIX_TOKEN')

priority_map = {
    '0': 'Not classified',
    '1': 'Information',
    '2': 'Warning',
    '3': 'Average',
    '4': 'High',
    '5': 'Disaster',
}


def get_problem_event_counts(time_from: int, time_till: int, limit: int = 5) -> dict:
    """
    Coleta eventos de problema agrupados por triggerid.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "event.get",
        "params": {
            "countOutput": True,
            "groupBy": "objectid",
            "value": 1,
            "time_from": time_from,
            "time_till": time_till,
            "sortfield": ["rowscount"],
            "sortorder": "DESC",
            "limit": limit
        },
        "auth": token,
        "id": 1
    }

    try:
        logging.debug("Enviando requisição para event.get")
        response = requests.post(url, json=payload)
        result = response.json()['result']
        logging.info(f"{len(result)} triggers com problemas encontradas.")
        # print(result)
        return {entry['objectid']: int(entry['rowscount']) for entry in result}
    except Exception as e:
        logging.error("Erro ao buscar eventos com problemas: %s", e)
        return {}


def get_trigger_details(trigger_ids: list) -> list:
    """
    Coleta detalhes das triggers com base em seus IDs.
    """
    if not trigger_ids:
        logging.warning("Lista de trigger_ids vazia. Nenhuma trigger será consultada.")
        return []

    payload = {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "output": ["triggerid", "description", "priority"],
            "triggerids": trigger_ids,
            "expandDescription": True,
            "selectHosts": ["hostid", "name"]
        },
        "auth": token,
        "id": 2
    }

    try:
        logging.debug("Enviando requisição para trigger.get")
        response = requests.post(url, json=payload)
        result = response.json()['result']
        logging.info(f"{len(result)} detalhes de triggers recuperados.")
        return result
    except Exception as e:
        logging.error("Erro ao buscar detalhes das triggers: %s", e)
        return []

def export_triggers_to_csv(triggers: list, trigger_counts: dict, file_name: str):
    """
    Exporta os dados para CSV, ordenando por quantidade de problemas (Quantidade de incidentes) de forma decrescente.
    """
    try:
        # Ordena os triggers com base em Quantidade de incidentes
        sorted_triggers = sorted(
            triggers,
            key=lambda t: trigger_counts.get(t['triggerid'], 0),
            reverse=True
        )

        with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Host', 'Trigger', 'Severidade', 'Quantidade de incidentes'])

            for trigger in sorted_triggers:
                host_name = trigger['hosts'][0]['name'] if trigger['hosts'] else 'N/A'
                description = trigger['description']
                severity = priority_map.get(str(trigger['priority']), 'Unknown')
                count = trigger_counts.get(trigger['triggerid'], 0)
                writer.writerow([host_name, description, severity, count])

        logging.info(f"Arquivo CSV exportado com sucesso: {file_name}")
    except Exception as e:
        logging.critical("Erro ao exportar para CSV: %s", e)

def run_trigger_report(time_from: int, time_till: int, limit: int = 5):
    """
    Orquestra a coleta e exportação de triggers com problemas.
    """
    # Converte as datas de string para datetime
    time_from_dt = datetime.strptime(time_from, "%d/%m/%Y")
    time_till_dt = datetime.strptime(time_till, "%d/%m/%Y")

    # Converte as datas para timestamp
    time_from_ts = int(time_from_dt.timestamp())
    time_till_ts = int(time_till_dt.timestamp())

    logging.info("Iniciando coleta de dados do Zabbix...")

    trigger_counts = get_problem_event_counts(time_from_ts, time_till_ts, limit)
    trigger_ids = list(trigger_counts.keys())

    if not trigger_ids:
        logging.warning("Nenhuma trigger com eventos de problema encontrada.")
        return

    trigger_details = get_trigger_details(trigger_ids)
    logging.info("Fim da coleta de dados do Zabbix.")

    csv_name = f'{datetime.now().strftime("%d-%m-%Y-%H%M%S")}.csv'
    export_triggers_to_csv(trigger_details, trigger_counts, csv_name)

# === EXECUÇÃO ===
if __name__ == '__main__':
    ti = time.time()
    run_trigger_report(
        time_from="01/06/2025",
        time_till="17/06/2025",
        limit=1000
    )
    tf = time.time()
    logging.info("Tempo total de execução: %.2fs", tf - ti)