import json
import boto3
import logging
from consumer import consume_sqs
from printer import find_printer, get_out_endpoint, configure_printer, print_tspl_label

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_printer():
    """
    Get printer information and connection.
    """
    dev = find_printer()
    endpoint_out = get_out_endpoint(dev)
    configure_printer(dev, endpoint_out)
    return dev, endpoint_out

def print_data(dev, endpoint_out, body):
    """
    Print queue data.
    """
    data = json.loads(body)
    print(f"Imprimindo etiqueta para o email {data['name']} {data['surname']}...")

    print_tspl_label(dev, endpoint_out,
                    data["name"], data["surname"],
                    data["institution"], data["qr_content"], data["seq_id"])


if __name__ == "__main__":
    dev, endpoint_out = get_printer()
    consume_sqs("secomp.fifo", 10, 1, print_data, dev, endpoint_out)