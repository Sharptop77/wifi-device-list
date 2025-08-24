import os
import argparse
import time
import threading
import signal
import sys
from flask import Flask, render_template_string
from routeros_api import RouterOsApiPool

merged = []  # здесь будут храниться актуальные данные
lock = threading.Lock()

def periodic_update(api1, api2, update_interval):
    global merged
    while True:
        try:
            dhcp_data = get_dhcp_leases(api1)
            capsman_data = get_capsman_info(api2)
            with lock:
                merged[:] = merge_data(dhcp_data, capsman_data)  # правильно обновлять весь список
        except Exception as e:
            print(f"Error updating  {e}")
        time.sleep(update_interval)

def update_data_forever(api1, api2, interval):
    global merged
    while True:
        try:
            dhcp_data = get_dhcp_leases(api1)
            capsman_data = get_capsman_info(api2)
            with lock:
                merged[:] = merge_data(dhcp_data, capsman_data)
            print("WiFi list refreshed!")
        except Exception as e:
            print("Error in update_", e)
        time.sleep(interval)

def parse_args():
    parser = argparse.ArgumentParser(description="MikroTik WiFi Info App")
    parser.add_argument('--dhcp-host', default=os.getenv('DHCP_MIKROTIK_HOST'))
    parser.add_argument('--dhcp-user', default=os.getenv('DHCP_MIKROTIK_USER'))
    parser.add_argument('--dhcp-pass', default=os.getenv('DHCP_MIKROTIK_PASS'))

    parser.add_argument('--capsman-host', default=os.getenv('CAPSMAN_MIKROTIK_HOST'))
    parser.add_argument('--capsman-user', default=os.getenv('CAPSMAN_MIKROTIK_USER'))
    parser.add_argument('--capsman-pass', default=os.getenv('CAPSMAN_MIKROTIK_PASS'))
    parser.add_argument('--update-interval', type=int, default=int(os.getenv('UPDATE_INTERVAL', '30')), help='Update interval in seconds')
    args = parser.parse_args()
    # Проверим обязательные параметры
    if not all([args.dhcp_host, args.dhcp_user, args.dhcp_pass,
                args.capsman_host, args.capsman_user, args.capsman_pass]):
        parser.error("Missing MikroTik connection parameters.")
    return args


# Получаем данные с DHCP сервера
def get_dhcp_leases(connection):
    dhcp_resource = connection.get_resource('/ip/dhcp-server/lease')
    leases = dhcp_resource.get()
    # Вернем словарь по mac адресам с инфо
    result = {}
    for lease in leases:
        # В lease есть 'address', 'mac-address', 'host-name'
        mac = lease.get('mac-address')
        result[mac] = {
            'device_name': lease.get('host-name'),
            'ip_address': lease.get('address'),
            'mac': mac
        }
    return result

# Получаем данные с CAPsMAN контроллера (назначение клиентов к точкам доступа)
def get_capsman_info(connection):
    # Получаем клиентов WiFi
    capsman_clients_res = connection.get_resource('/caps-man/registration-table')
    clients = capsman_clients_res.get()
    # Получаем radio info
    capsman_interface_res = connection.get_resource('/caps-man/radio')
    wireless_regs = capsman_interface_res.get()
    # Получаем remote CAP info
    capsman_points_res = connection.get_resource('/caps-man/remote-cap')
    wireless_aps = capsman_points_res.get()

    # Построить словари для быстрого поиска
    radio_info = {ap.get('interface'): ap for ap in wireless_regs if 'interface' in ap}
    ap_info = {ap.get('identity'): ap for ap in wireless_aps if 'identity' in ap}
    
    client_info = {}
    for client in clients:
        mac = client.get('mac-address')
        ap_interface = client.get('interface')
        ssid = client.get('ssid')
        signal = client.get('rx-signal')

        # Безопасный доступ к radio_info
        ap_name = radio_info.get(ap_interface, {}).get('remote-cap-identity', '')
        ap_addr = ap_info.get(ap_name, {}).get('address', '')
        client_info[mac] = {
            'ap_interface': ap_interface or '',
            'ap_name': ap_name or '',
            'ap_address': ap_addr or '',
            'ap_ssid': ssid or '',
            'ap_signal': signal or ''
        }
    return client_info

# Объединение данных
def merge_data(dhcp_data, capsman_data):
    merged_list = []
    for mac, capsman in capsman_data.items():
        dhcp = dhcp_data.get(mac, {})
        merged_list.append({
            'device_name': dhcp.get('device_name', ''),
            'ip_address': dhcp.get('ip_address', ''),
            'mac': mac,
            'ap_interface': capsman.get('ap_interface', ''),
            'ap_ssid': capsman.get('ap_ssid', ''),
            'ap_signal': capsman.get('ap_signal', ''),
            'ap_name': capsman.get('ap_name', ''),
            'ap_address': capsman.get('ap_address', ''),
        })
    return merged_list

# Запуск API и Flask сервера
def main():
    args = parse_args()
    pool1 = RouterOsApiPool(args.dhcp_host, username=args.dhcp_user, password=args.dhcp_pass, plaintext_login=True)
    api1 = pool1.get_api()
    pool2 = RouterOsApiPool(args.capsman_host, username=args.capsman_user, password=args.capsman_pass, plaintext_login=True)
    api2 = pool2.get_api()
   

    # Первый сбор данных до запуска Flask — чтобы была не пустая страница
    update_once = True
    if update_once:
        dhcp_data = get_dhcp_leases(api1)
        capsman_data = get_capsman_info(api2)
        with lock:
            merged[:] = merge_data(dhcp_data, capsman_data)

    # Запускаем цикл автообновления в основном потоке (в фоне)
    update_thread = threading.Thread(target=update_data_forever, args=(api1, api2, args.update_interval), daemon=True)
    update_thread.start()

    @app.route('/')
    def index():
        with lock:  # блокируем на чтение, чтобы не было коллизий
            data = list(merged)
        html = '''
        <html><head><title>WiFi Clients</title></head>
        <body>
        <h2>Подключенные устройства по WiFi</h2>
        <table border="1" cellpadding="5">
            <tr>
                <th>Название устройства</th>
                <th>IP адрес</th>
                <th>MAC адрес</th>
                <th>Интерфейс точки доступа</th>
                <th>SSID</th>
                <th>Уровень приема устройства</th>
                <th>Точка доступа (название)</th>
                <th>Адрес точки доступа</th>
            </tr>
            {% for item in data %}
            <tr>
                <td>{{ item.device_name }}</td>
                <td>{{ item.ip_address }}</td>
                <td>{{ item.mac }}</td>
                <td>{{ item.ap_interface }}</td>
                <td>{{ item.ap_ssid }}</td>
                <td>{{ item.ap_signal }}</td>
                <td>{{ item.ap_name }}</td>
                <td>{{ item.ap_address }}</td>
            </tr>
            {% endfor %}
        </table>
        </body></html>
        '''
        return render_template_string(html, data=data)

    def shutdown(*_):
        print("Disconnecting from routers...")
        pool1.disconnect()
        pool2.disconnect()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    app.run(host='0.0.0.0', port=8080, threaded=False)

if __name__ == '__main__':
    main()
