# MikroTik WiFi Clients Dashboard

## Описание

Это приложение предназначено для централизованного отображения всех устройств, подключённых по WiFi в инфраструктуре MikroTik с использованием CAPsMAN-контроллера и DHCP-сервера.  
Расширенная таблица клиентов WiFi формируется на основе данных двух роутеров MikroTik (один — DHCP сервер, второй — CAPsMAN контроллер), и выдаётся через веб-интерфейс (Flask).

Приложение поддерживает периодическое обновление информации с настраиваемым интервалом, параметры подключения и интервал обновления можно указывать через переменные окружения или аргументы командной строки.

---

## Возможности

- Получение актуального списка WiFi-клиентов, их IP адресов, MAC адресов, привязки к точкам доступа (AP) - SSID, интерфейс, уровень сигнала
- Корректное сопоставление данных по MAC-адресу между DHCP и CAPsMAN
- Отображение информации в виде html-таблицы на веб-странице
- Настраиваемый интервал обновления данных (по умолчанию 30 секунд)
- Простая интеграция и запуск в Docker-контейнере

---

## Требования

- Python 3.8+
- Два MikroTik-устройства с включённым API (DHCP сервер и CAPsMAN контроллер)
- Доступность портов MikroTik API (8728 по умолчанию)
- Docker (для контейнеризации, опционально)

---

## Установка и запуск

### 1. Клонируйте репозиторий и перейдите в его директорию
```
git clone https://github.com/Sharptop77/wifi-device-list.git
cd wifi-device-list
```
---

### 2. Подготовьте переменные окружения (или воспользуйтесь аргументами):

- `DHCP_MIKROTIK_HOST` — IP DHCP MikroTik
- `DHCP_MIKROTIK_USER` — Логин DHCP MikroTik
- `DHCP_MIKROTIK_PASS` — Пароль DHCP MikroTik
- `CAPSMAN_MIKROTIK_HOST` — IP CAPsMAN MikroTik
- `CAPSMAN_MIKROTIK_USER` — Логин CAPsMAN MikroTik
- `CAPSMAN_MIKROTIK_PASS` — Пароль CAPsMAN MikroTik
- `UPDATE_INTERVAL` — Интервал обновления (секунды, по умолчанию 30)

---

### 3. Запуск через Docker

Соберите и запустите контейнер:
``` bash
docker build -t mikrotik_wifi_app .

docker run -d -p 8080:8080 
-e DHCP_MIKROTIK_HOST=192.168.88.1 
-e DHCP_MIKROTIK_USER=admin 
-e DHCP_MIKROTIK_PASS=adminpass 
-e CAPSMAN_MIKROTIK_HOST=192.168.88.2 
-e CAPSMAN_MIKROTIK_USER=admin 
-e CAPSMAN_MIKROTIK_PASS=adminpass 
-e UPDATE_INTERVAL=30 
–name mikrotik_wifi_container mikrotik_wifi_app
```

После запуска интерфейс будет доступен по адресу:  

http://localhost:8080

---

### 4. Запуск локально (без Docker)

Создайте виртуальное окружение, установите зависимости:
``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Запуск приложения (пример с аргументами):
``` bash
python app.py \
–dhcp-host 192.168.88.1 –dhcp-user admin –dhcp-pass adminpass \
–capsman-host 192.168.88.2 –capsman-user admin –capsman-pass adminpass \
–update-interval 30 \

```
---

## Пример таблицы (что отображается)


| Название устройства | IP адрес | MAC адрес | Интерфейс AP | SSID | Уровень сигнала устройства | Точка доступа (Имя) | Адрес точки доступа/Порт |
|--------------------|----------|-----------|--------------|-------|----------------------------|------------------------------------------------|
| laptop-A           | ...      | ...       | cap1         | Mikrotik |   -75 | ... (Remote CAP identity) | ...                                 |
| ...                | ...      | ...       | ...          | ... | ... | ....                     | ...                                 |


---

## FAQ

**Q: Как изменить период обновления?**  
A: Используйте переменную окружения `UPDATE_INTERVAL` или параметр `--update-interval`.

**Q: Как узнать правильные значения для переменных окружения?**  
A: Это нужные IP/логин/пароль ваших MikroTik устройств с включённым доступом по API.

**Q: Почему соединение не устанавливается?**  
A: Проверьте firewall, корректность API портов, доступность пользователя и пароля, и что выбранные пользователи имеют разрешение на работу с API.

---

## Лицензия

MIT (или ваша лицензия)

---

## Контакты

Для вопросов и предложений — создавайте issue или отправьте email.


