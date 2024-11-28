import time
import usb.core
import usb.util

def find_printer():
    """
    Encontra a impressora USB com base nos IDs de fornecedor e produto.
    """
    dev = usb.core.find(idVendor=0x2D37, idProduct=0xD20B)
    if dev is None:
        raise ValueError('Impressora não encontrada.')

    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)

    dev.set_configuration()
    usb.util.claim_interface(dev, 0)
    return dev

def get_out_endpoint(dev):
    """
    Obtém o endpoint de saída (OUT) da impressora.
    """
    cfg = dev.get_active_configuration()
    intf = cfg[(0,0)]
    endpoint_out = None

    for ep in intf:
        if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
            endpoint_out = ep.bEndpointAddress
            break

    if endpoint_out is None:
        raise ValueError("Endpoint de saída não encontrado.")
    return endpoint_out

def configure_printer(dev, endpoint_out):
    """
    Configurações fixas da impressora.
    """
    try:
        config_command = """
    CLS
    SPEED 5
    SIZE 60 mm,40 mm
    DENSITY 10
    DIRECTION 1
    CODEPAGE 860
"""
        send_tspl_command(dev, endpoint_out, config_command)
        print("Configuração da impressora enviada com sucesso! Codepage: 860")
    except Exception as e:
        print(f"Erro ao configurar a impressora: {e}")

def calibrate_printer(dev, endpoint_out):
    calibrate_command = "GAPDETECT\r\n"
    send_tspl_command(dev, endpoint_out, calibrate_command)
    print("Calibração da impressora realizada.")


def send_tspl_command(dev, endpoint_out, command):
    """
    Envia um comando TSPL para a impressora.
    """
    if dev is None:
        raise ValueError('Impressora não conectada.')

    # Dividir o comando em linhas
    command_lines = command.strip().split('\n')

    for line in command_lines:
        line = line.strip() + '\r\n'  # Adicionar terminador de linha
        command_bytes = line.encode('cp860')  # Usar codepage 860

        for attempt in range(3):
            try:
                dev.write(endpoint_out, command_bytes)
                time.sleep(0.1)  # Pequeno delay entre os comandos
                break
            except usb.core.USBError as e:
                print(f"Erro ao enviar comando '{line}' (tentativa {attempt + 1} de 3): {e}")
                time.sleep(1)
        else:
            print(f"Falha ao enviar comando '{line}' após múltiplas tentativas.")

def print_tspl_label(dev, endpoint_out, name, surname, institution, qr_content, seq_id):
    """
    Envia dados específicos para impressão.
    """
    try:
        # Preparar os dados com codificação correta
        name = name.encode('cp860', errors='ignore').decode('cp860')
        surname = surname.encode('cp860', errors='ignore').decode('cp860')
        institution = institution.encode('cp860', errors='ignore').decode('cp860')

        label_command = f"""
                CLS
                TEXT 50,20,"3",0,2,2,"{name}"
                TEXT 50,80,"3",0,1,1,"{surname}"
                TEXT 50,140,"3",0,1,1,"{institution}"
                TEXT 50,250,"3",0,1,1,"{seq_id}"
                QRCODE 270,110,L,6,A,0,"{qr_content}"
                PRINT 1,1
        """
        send_tspl_command(dev, endpoint_out, label_command)
        print(f"Etiqueta de {name} enviada para impressão!")
    except Exception as e:
        print(f"Erro ao imprimir: {e}")

if __name__ == "__main__":
    dev = None
    try:
        # Inicializar a impressora
        dev = find_printer()

        # Obter o endpoint de saída
        endpoint_out = get_out_endpoint(dev)

        # Configurar a impressora
        configure_printer(dev, endpoint_out)
        # calibrate_printer(dev, endpoint_out)
        # Dados para impressão
        etiquetas = [
            # {"name": "Jádson", "surname": "Abreu", "institution": "UFPE", "qr_content": "aaaaaaaaaaaaaaaaaaaaaaaa"},
            # {"name": "Maria", "surname": "Silva", "institution": "UFPE", "qr_content": "bbbbbbbbbbbbbbbbbbbb"},
            {"name": "João", "surname": "Oliveira", "institution": "UFPE", "qr_content": "cccccccccccccccccccc"},
        ]

        # Imprimir etiquetas
        for i, etiqueta in enumerate(etiquetas):
            print(f"Imprimindo etiqueta {i + 1}...")
            print_tspl_label(dev, endpoint_out,
                             etiqueta["name"], etiqueta["surname"],
                             etiqueta["institution"], etiqueta["qr_content"])
            # time.sleep(5)  # Intervalo entre impressões
    finally:
        if dev:
            usb.util.release_interface(dev, 0)
            dev.attach_kernel_driver(0)
        print("Conexão com a impressora fechada.")
