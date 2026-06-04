from fastapi import FastAPI, HTTPException, status
import requests
from app.config import settings
from app.services import execution_documents
import json

# import uuid


app = FastAPI(title=settings.PROJECT_NAME)

@app.post(
    "/api/v1/smev/execution-documents/send",
    summary="Исполнительные документы (метод send)"
)
async def execution_documents_send(payload: dict):
    # #################################################################################################################
    test_payload = {
        "pack_id": "12f1a3cd-cd5f-48fe-8ed4-f73e3d9f9b2b",  # c:ID пакета
        "date": "2015-10-12T00:00:00",  # c:Date
        "sender_id": "EPGU01",  # c:SenderID (например Мнемоника ЕПГУ)
        "receiver_id": "FSSP01",  # c:ReceiverID (Мнемоника ФССП)
        "receiver_department": "33013",  # c:ReceiverDepartmentCode (Код ОСП)
        "documents": [
            {
                "doc_id": "2469",  # c:ID документа
                "type": "I_IPSIDE_OSP_COURSEIP",  # c:Type (Код типа)
                "document_date": "2015-10-12",  # c:DocumentDate
                "document_number": "506559",  # c:DocumentNumber
                "case_number": "7407/14/33025-ИП",  # c:DocumentCaseNumber
                "is_unstructured": False,  # att:IsUnstructuredFormat
                "structured_format_type": "http://www.fssprus.ru/namespace/IRequestOther/2017/1",  # att:StructuredFormatType
                "attachment_filename": "piev_4ccb83c6-2888-4561-8b49-49215ca1cfbc.zip",  # att:AttachmentFilename
            }
        ],
    }

    # #################################################################################################################

    ADAPTER_API_URL = f"{settings.ADAPTER_URL}/send"
    CLIENT_ID = payload.get("client_id", "00000000-0000-0000-0000-000000000024")
    
    json_payload = {
        "itSystem": settings.IS_MNEMONIC,
        "requestMessage": {
            "messageType": "RequestMessageType",
            "requestMetadata": {
                "clientId": CLIENT_ID,
                "testMessage": True
            },
            "requestContent": {
                "content": {
                    "messagePrimaryContent": {
                        # "any": execution_documents.get_any_content(CLIENT_ID)
                        "any": execution_documents.generate_smev3_application_any_content(test_payload)
                    }
                }
            }
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            url=ADAPTER_API_URL,
            data=json.dumps(json_payload),
            headers=headers
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке запроса: {str(e)}"
        )
    else:
        return {
            "adapter_http_code": response.status_code,
            "adapter_raw_response": response.text,
            "client_id": CLIENT_ID
        }
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
