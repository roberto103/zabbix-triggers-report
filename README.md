
# 📊 Zabbix Trigger Report

Este script em Python conecta-se à API do Zabbix para coletar e exportar triggers com problemas ocorridos em um intervalo de tempo definido. Os dados são exportados em um arquivo `.csv`, ordenados pela quantidade de eventos em ordem decrescente.

## ✅ Pré-requisitos

- Zabbix **versão 7.0 ou superior**
- Python 3.10+
- Dependências listadas no `requirements.txt`

## 🔧 Funcionalidades

- Consulta a API do Zabbix usando `event.get` e `trigger.get`
- Agrupa e contabiliza eventos de problema por trigger
- Recupera detalhes dos hosts e das triggers
- Exporta para CSV com colunas:
  - `Host`
  - `Trigger`
  - `Severidade`
  - `Quantidade de incidentes`
- Ordenação automática por quantidade de problemas (decrescente)
- Suporte a datas personalizadas

---

## 🚀 Como usar

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Configure o ambiente

Crie um arquivo `.env` com base no modelo `.env.example`:

```python
url = 'http://SEU_ZABBIX/api_jsonrpc.php'
token = 'SEU_TOKEN_DE_AUTENTICAÇÃO'
```

### 3. Execute o script

```bash
python3 trigger_report.py
```

Por padrão, o script irá gerar um CSV com o nome baseado na data/hora atual, por exemplo:

```
17-06-2025-180402.csv
```

---

## 📌 Exemplo de uso

No final do arquivo `trigger_report.py`:

```python
run_trigger_report(
    time_from="01/06/2025",
    time_till="17/06/2025",
    limit=1000
)
```

Altere os valores de `time_from` e `time_till` para o intervalo desejado.

---

## 📁 Estrutura esperada do CSV

| Host         | Trigger                           | Severidade | Quantidade de incidentes |
|--------------|-----------------------------------|------------|--------------------------|
| WebServer01  | CPU usage is too high             | High       | 18                       |
| DBServer02   | Free disk space is low on /var    | Warning    | 12                       |

---

## ✨ Contribuições

Pull requests são bem-vindos! Para mudanças maiores, por favor abra uma issue primeiro para discutir o que você gostaria de modificar.