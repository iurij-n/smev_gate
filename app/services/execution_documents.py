import os
from app.config import settings
import zipfile
from datetime import datetime

def get_any_content(client_ad: str) -> str:
    # ZIP_NAME = f"req_{client_ad}.zip"
    # XML_NAME = f"req_{client_ad}.xml"


    # # Полные пути для работы с файлами на диске
    # local_xml_path = os.path.join("/tmp", XML_NAME)  # Временный XML создадим в /tmp
    # final_zip_path = os.path.join(settings.IN_DIR, ZIP_NAME)  # ZIP кладем сразу в 'in' Адаптера

    # # ==================== ШАГ 1: ГЕНЕРАЦИЯ ВНУТРЕННЕГО XML ====================
    # xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
    # <fssp:ReferenceInfoRequest xmlns:fssp="http://www.red-soft.biz/schemas/fssp/common/2011/0.5">
    #     <requestExternalKey>{client_ad}</requestExternalKey>
    #     <referenceCode>Departments</referenceCode>
    # </fssp:ReferenceInfoRequest>"""

    # with open(local_xml_path, "w", encoding="utf-8") as f:
    #     f.write(xml_data)

    # # ==================== ШАГ 2: УПАКОВКА В ZIP НАПРЯМУЮ В ПАПКУ АДАПТЕРА ====================
    # # Пишем ZIP сразу туда, где его ждет Адаптер

    # if not os.path.exists(settings.IN_DIR):
    #     os.makedirs(settings.IN_DIR, exist_ok=True)

    # with zipfile.ZipFile(final_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    #     zipf.write(local_xml_path, arcname=XML_NAME)

    # # Удаляем временный XML из /tmp
    # os.remove(local_xml_path)
    # print(f"1. Архив успешно создан и сохранен в: {final_zip_path}")

    # # ==================== ШАГ 3: ОТПРАВКА ЛОКАЛЬНОГО POST-ЗАПРОСА ====================
    # current_date_iso = datetime.now().isoformat(timespec="seconds") + "+03:00"
    # current_date_short = datetime.now().strftime("%Y-%m-%d")

    # Содержимое для тега ANY
    # any_content = f"<fssp:NsiRequest xmlns:fssp='urn://x-artifacts-fssp-ru/mvv/smev3/nsi/1.0.1' xmlns:c='urn://x-artifacts-fssp-ru/mvv/smev3/container/1.0.1'><c:ID>2345</c:ID><c:Date>{current_date_iso}</c:Date><c:SenderOrganizationCode>БМ</c:SenderOrganizationCode><c:ReceiverOrganizationCode>ФССП</c:ReceiverOrganizationCode><c:Document><c:Organization>БМ</c:Organization><c:ID>2345</c:ID><c:Type>ReferenceInfoRequest</c:Type><c:DocumentDate>{current_date_short}</c:DocumentDate><c:DocumentNumber>2345</c:DocumentNumber><c:Filename>{ZIP_NAME}</c:Filename></c:Document></fssp:NsiRequest>"
    any_content = "<?xml version='1.0' encoding='UTF-8'?><fssp:ApplicationDocumentsRequest xmlns:fssp='urn://x-artifacts-fssp-ru/mvv/smev3/application-documents/1.1.1' xmlns:c='urn://x-artifacts-fssp-ru/mvv/smev3/container/1.1.0' xmlns:att='urn://x-artifacts-fssp-ru/mvv/smev3/attachments/1.1.0'><c:ID>12f1a3cd-cd5f-48fe-8ed4-f73e3d9f9b2b</c:ID><c:Date>2015-10-12T00:00:00</c:Date><c:SenderID>EPGU01</c:SenderID><c:ReceiverID>FSSP01</c:ReceiverID><c:ReceiverDepartmentCode>33013</c:ReceiverDepartmentCode><c:Document><c:ID>2469</c:ID><c:Type>I_IPSIDE_OSP_COURSEIP</c:Type><c:DocumentDate>2015-10-12</c:DocumentDate><c:DocumentNumber>506559</c:DocumentNumber><c:DocumentCaseNumber>7407/14/33025-ИП</c:DocumentCaseNumber><c:AttachmentsBlock><att:AttachmentDescription><att:AttachmentFormat><att:IsUnstructuredFormat>false</att:IsUnstructuredFormat><att:IsZippedPacket>true</att:IsZippedPacket><att:StructuredFormatType>http://www.fssprus.ru/namespace/IRequestOther/2017/1</att:StructuredFormatType></att:AttachmentFormat><att:AttachmentFilename>piev_4ccb83c6-2888-4561-8b49-49215ca1cfbc.zip</att:AttachmentFilename></att:AttachmentDescription></c:AttachmentsBlock></c:Document></fssp:ApplicationDocumentsRequest>"

    return any_content
