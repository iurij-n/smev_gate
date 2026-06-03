from fastapi import FastAPI, HTTPException, status
import requests
from app.config import settings
import json
import os
# import uuid
import zipfile
from datetime import datetime

app = FastAPI(title=settings.PROJECT_NAME)

@app.post(
    "/api/v1/smev/execution-documents",
    summary="Прямая трансляция запроса в Адаптер СМЭВ (метод send)"
)
async def execution_documents_send(payload: dict):
    ADAPTER_API_URL = f"{settings.ADAPTER_URL}/send"

    # Генерируем чистые уникальные ID
    CLIENT_ID = "00000000-0000-0000-0000-000000000021"
    ZIP_NAME = f"req_{CLIENT_ID}.zip"
    XML_NAME = f"req_{CLIENT_ID}.xml"


    # Полные пути для работы с файлами на диске
    local_xml_path = os.path.join("/tmp", XML_NAME)  # Временный XML создадим в /tmp
    final_zip_path = os.path.join(settings.IN_DIR, ZIP_NAME)  # ZIP кладем сразу в 'in' Адаптера

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

    if not os.path.exists(settings.IN_DIR):
        os.makedirs(settings.IN_DIR, exist_ok=True)

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
    # json_payload = {
    #     "itSystem": settings.IS_MNEMONIC,
    #     "requestMessage": {
    #         "messageType": "RequestMessageType",
    #         "requestMetadata": {"clientId": CLIENT_ID, "testMessage": True},
    #         "requestContent": {
    #             "content": {"messagePrimaryContent": {"any": any_content}},
    #             "attachmentHeaderList": {
    #                 "attachmentHeader": [
    #                     {
    #                         "id": ZIP_NAME,
    #                         "filePath": ZIP_NAME,
    #                         "fileName": ZIP_NAME,
    #                         "transferMethod": "REFERENCE",
    #                     }
    #                 ]
    #             },
    #         },
    #     },
    # }
    json_payload = {
        "itSystem": "460A01",
        "requestMessage": {
            "messageType": "RequestMessageType",
            "requestMetadata": {
                "clientId": CLIENT_ID,
                "testMessage": True
            },
            "requestContent": {
                "content": {
                    "messagePrimaryContent": {
                        # "any": "<?xml version='1.0' encoding='UTF-8'?><fssp:NsiRequest xmlns:fssp='urn://x-artifacts-fssp-ru/mvv/smev3/nsi/1.0.1' xmlns:c='urn://x-artifacts-fssp-ru/mvv/smev3/container/1.0.1'><c:ID>2345</c:ID><c:Date>2015-10-12T00:00:00</c:Date><c:SenderOrganizationCode>БМ</c:SenderOrganizationCode><c:ReceiverOrganizationCode>ФССП</c:ReceiverOrganizationCode><c:Document><c:Organization>БМ</c:Organization><c:ID>2345</c:ID><c:Type>ReferenceInfoRequest</c:Type><c:DocumentDate>2015-10-12</c:DocumentDate><c:DocumentNumber>2345</c:DocumentNumber><c:Filename>req_4xzb12c8-2194-4401-8b49-49215ca1cfbc.zip</c:Filename></c:Document></fssp:NsiRequest>"
                        "any": "<?xml version='1.0' encoding='UTF-8'?><fssp:ApplicationDocumentsRequest xmlns:fssp='urn://x-artifacts-fssp-ru/mvv/smev3/application-documents/1.1.1' xmlns:c='urn://x-artifacts-fssp-ru/mvv/smev3/container/1.1.0' xmlns:att='urn://x-artifacts-fssp-ru/mvv/smev3/attachments/1.1.0'><c:ID>12f1a3cd-cd5f-48fe-8ed4-f73e3d9f9b2b</c:ID><c:Date>2015-10-12T00:00:00</c:Date><c:SenderID>EPGU01</c:SenderID><c:ReceiverID>FSSP01</c:ReceiverID><c:ReceiverDepartmentCode>33013</c:ReceiverDepartmentCode><c:Document><c:ID>2469</c:ID><c:Type>I_IPSIDE_OSP_COURSEIP</c:Type><c:DocumentDate>2015-10-12</c:DocumentDate><c:DocumentNumber>506559</c:DocumentNumber><c:DocumentCaseNumber>7407/14/33025-ИП</c:DocumentCaseNumber><c:AttachmentsBlock><att:AttachmentDescription><att:AttachmentFormat><att:IsUnstructuredFormat>false</att:IsUnstructuredFormat><att:IsZippedPacket>true</att:IsZippedPacket><att:StructuredFormatType>http://www.fssprus.ru/namespace/IRequestOther/2017/1</att:StructuredFormatType></att:AttachmentFormat><att:AttachmentFilename>piev_4ccb83c6-2888-4561-8b49-49215ca1cfbc.zip</att:AttachmentFilename></att:AttachmentDescription></c:AttachmentsBlock></c:Document></fssp:ApplicationDocumentsRequest>"
                    }
                }
            }
        }
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
    else:
        return {
            "adapter_http_code": response.status_code,
            "adapter_raw_response": response.text
        }



    # """
    # Принимает любой JSON от 1С и отправляет его на http://<adapter_ip>:8080/ws/send
    # Возвращает сырой текстовый ответ Адаптера (обычно XML).
    # """
    # Формируем прямой URL к методу send Адаптера
    # target_url = f"{settings.ADAPTER_URL}/send"
    
    # try:
    #     # Так как мы пока не знаем, в каком формате Адаптер ждет данные на этот эндпоинт
    #     # (в виде JSON, сырого XML или Multipart), отправляем payload как JSON.
    #     # В заголовках явно передаем тип контента.
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Accept": "*/*"
    #     }
        
    #     # Делаем синхронный запрос к виртуалке
    #     response = requests.post(
    #         target_url,
    #         json=payload,
    #         headers=headers,
    #         timeout=10.0  # Таймаут 10 секунд, чтобы 1С не зависала вечно
    #     )
        
    #     # Возвращаем структуру ответа
    #     return {
    #         "gateway_status": "forwarded",
    #         "adapter_http_code": response.status_code,
    #         "adapter_raw_response": response.text
    #     }
        
    # except requests.exceptions.ConnectTimeout:
    #     raise HTTPException(
    #         status_code=status.HTTP_504_GATEWAY_TIMEOUT,
    #         detail=f"Не удалось подключиться к Адаптеру по адресу {target_url}. Превышено время ожидания (Timeout)."
    #     )
    # except requests.exceptions.ConnectionError:
    #     raise HTTPException(
    #         status_code=status.HTTP_502_BAD_GATEWAY,
    #         detail=f"Сеть доступна, но Адаптер отверг подключение по адресу {target_url}. Проверьте, запущен ли сервис Адаптера на виртуалке."
    #     )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Внутренняя ошибка шлюза: {str(e)}"
    #     )