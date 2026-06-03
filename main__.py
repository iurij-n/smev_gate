import json
import os
# import uuid
import zipfile
from datetime import datetime
import requests

# === НАСТРОЙКИ СВЯЗИ (ЛОКАЛЬНО) ===
# Так как скрипт внутри виртуалки, шлем прямо на localhost
ADAPTER_API_URL = "http://localhost:7590/ws/send"
IT_SYSTEM = "460A01"

# === ПУТЬ К ПАПКЕ ВЛОЖЕНИЙ (ИЗ CONFIG.INI) ===
LINUX_IN_DIR = "/opt/adapter/in"

# Генерируем чистые уникальные ID
# FILE_ID = str(uuid.uuid4())
# ZIP_NAME = f"req_{FILE_ID}.zip"
# XML_NAME = f"req_{FILE_ID}.xml"

# Генерируем чистые уникальные ID
CLIENT_ID = "00000000-0000-0000-0000-000000000018"
ZIP_NAME = f"req_{CLIENT_ID}.zip"
XML_NAME = f"req_{CLIENT_ID}.xml"


# Полные пути для работы с файлами на диске
local_xml_path = os.path.join("/tmp", XML_NAME)  # Временный XML создадим в /tmp
final_zip_path = os.path.join(LINUX_IN_DIR, ZIP_NAME)  # ZIP кладем сразу в 'in' Адаптера

# ==================== ШАГ 1: ГЕНЕРАЦИЯ ВНУТРЕННЕГО XML ====================
xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<fssp:ReferenceInfoRequest xmlns:fssp="http://www.red-soft.biz/schemas/fssp/common/2011/0.5">
    <requestExternalKey>{CLIENT_ID}</requestExternalKey>
    <referenceCode>Departments</referenceCode>
</fssp:ReferenceInfoRequest>"""

with open(local_xml_path, "w", encoding="utf-8") as f:
    f.write(xml_data)

# ==================== ШАГ 2: УПАКОВКА В ZIP НАПРЯМУЮ В ПАПКУ АДАПТЕРА ====================
# Пишем ZIP сразу туда, где его ждет Адаптер

if not os.path.exists(LINUX_IN_DIR):
    os.makedirs(LINUX_IN_DIR, exist_ok=True)

with zipfile.ZipFile(final_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(local_xml_path, arcname=XML_NAME)

# Удаляем временный XML из /tmp
os.remove(local_xml_path)
print(f"1. Архив успешно создан и сохранен в: {final_zip_path}")

# ==================== ШАГ 3: ОТПРАВКА ЛОКАЛЬНОГО POST-ЗАПРОСА ====================
current_date_iso = datetime.now().isoformat(timespec="seconds") + "+03:00"
current_date_short = datetime.now().strftime("%Y-%m-%d")

# Содержимое для тега ANY
any_content = f"<fssp:NsiRequest xmlns:fssp='urn://x-artifacts-fssp-ru/mvv/smev3/nsi/1.0.1' xmlns:c='urn://x-artifacts-fssp-ru/mvv/smev3/container/1.0.1'><c:ID>2345</c:ID><c:Date>{current_date_iso}</c:Date><c:SenderOrganizationCode>БМ</c:SenderOrganizationCode><c:ReceiverOrganizationCode>ФССП</c:ReceiverOrganizationCode><c:Document><c:Organization>БМ</c:Organization><c:ID>2345</c:ID><c:Type>ReferenceInfoRequest</c:Type><c:DocumentDate>{current_date_short}</c:DocumentDate><c:DocumentNumber>2345</c:DocumentNumber><c:Filename>{ZIP_NAME}</c:Filename></c:Document></fssp:NsiRequest>"

# Собираем JSON
json_payload = {
    "itSystem": IT_SYSTEM,
    "requestMessage": {
        "messageType": "RequestMessageType",
        "requestMetadata": {"clientId": CLIENT_ID, "testMessage": True},
        "requestContent": {
            "content": {"messagePrimaryContent": {"any": any_content}},
            "attachmentHeaderList": {
                "attachmentHeader": [
                    {
                        "id": ZIP_NAME,
                        "filePath": ZIP_NAME,  # Указываем только имя, Адаптер сам подставит /opt/adapter/in/
                        "fileName": ZIP_NAME,
                        "transferMethod": "REFERENCE",
                    }
                ]
            },
        },
    },
}

print("2. Отправка JSON-запроса в локальный Адаптер...")
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(
        url=ADAPTER_API_URL, data=json.dumps(json_payload), headers=headers
    )
    print(f"Статус ответа: {response.status_code}")
    print("Ответ Адаптера:")
    print(
        json.dumps(
            response.json()
            if response.headers.get("Content-Type") == "application/json"
            else response.text,
            indent=4,
            ensure_ascii=False,
        )
    )
except Exception as e:
    print(f"Ошибка при отправке запроса: {e}")