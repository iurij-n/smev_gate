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

    ADAPTER_API_URL = f"{settings.ADAPTER_URL}/send"
    CLIENT_ID = payload.get("client_id", "00000000-0000-0000-0000-000000000022")
    
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
                        "any": execution_documents.get_any_content(CLIENT_ID)
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
        # print(f"Статус ответа: {response.status_code}")
        # print("Ответ Адаптера:")
        # print(
        #     json.dumps(
        #         response.json()
        #         if response.headers.get("Content-Type") == "application/json"
        #         else response.text,
        #         indent=4,
        #         ensure_ascii=False,
        #     )
        # )
    except Exception as e:
        # print(f"Ошибка при отправке запроса: {e}")
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