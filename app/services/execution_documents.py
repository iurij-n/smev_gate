import os
from app.config import settings
import zipfile
from datetime import datetime
import xml.etree.ElementTree as ET


def generate_smev3_application_any_content(payload: dict) -> str:
    """Генерирует первичный XML-контент (any_content) для вида сведений ФССП

    'Обращения, подаваемые в ФССП России, и результаты их рассмотрения' v1.1.1
    """
    # Регистрируем пространства имен, чтобы они красиво записывались в префиксы
    ns_fssp = (
        "urn://x-artifacts-fssp-ru/mvv/smev3/application-documents/1.1.1"
    )
    ns_container = "urn://x-artifacts-fssp-ru/mvv/smev3/container/1.1.0"
    ns_attachments = "urn://x-artifacts-fssp-ru/mvv/smev3/attachments/1.1.0"

    ET.register_namespace("fssp", ns_fssp)
    ET.register_namespace("c", ns_container)
    ET.register_namespace("att", ns_attachments)

    # 1. Создаем корневой элемент ApplicationDocumentsRequest
    root = ET.Element(f"{{{ns_fssp}}}ApplicationDocumentsRequest")

    # 2. Заполняем метаданные пакета (Smev3PackType)
    # Идентификатор пакета в ИС контрагента
    c_id = ET.SubElement(root, f"{{{ns_container}}}ID")
    c_id.text = str(payload.get("pack_id"))

    # Дата формирования пакета в формате YYYY-MM-DDTHH:MM:SS
    c_date = ET.SubElement(root, f"{{{ns_container}}}Date")
    c_date.text = payload.get("date", datetime.now().isoformat()[:19])

    # Мнемоника отправителя и получателя в СМЭВ 3
    c_sender = ET.SubElement(root, f"{{{ns_container}}}SenderID")
    c_sender.text = str(payload.get("sender_id"))

    if payload.get("sender_department"):
        c_send_dep = ET.SubElement(
            root, f"{{{ns_container}}}SenderDepartmentCode"
        )
        c_send_dep.text = str(payload.get("sender_department"))

    c_receiver = ET.SubElement(root, f"{{{ns_container}}}ReceiverID")
    c_receiver.text = str(payload.get("receiver_id"))

    # Код территориального органа/подразделения ФССП (обязателен по регламенту)
    if payload.get("receiver_department"):
        c_recv_dep = ET.SubElement(
            root, f"{{{ns_container}}}ReceiverDepartmentCode"
        )
        c_recv_dep.text = str(payload.get("receiver_department"))

    # 3. Перебираем и добавляем документы (может быть 1...n штук)
    for doc in payload.get("documents", []):
        c_doc = ET.SubElement(root, f"{{{ns_container}}}Document")

        # Идентификатор самого документа (ExternalKey заявления/обращения)
        d_id = ET.SubElement(c_doc, f"{{{ns_container}}}ID")
        d_id.text = str(doc.get("doc_id"))

        # Для результатов рассмотрения/ответов передается ID исходного заявления
        if doc.get("incoming_doc_key"):
            d_inkey = ET.SubElement(c_doc, f"{{{ns_container}}}IncomingDocKey")
            d_inkey.text = str(doc.get("incoming_doc_key"))

        # Код типа документа (например: I_IPSIDE_OSP_COURSEIP или REFERENCE_PAYMENT_REQUEST)
        d_type = ET.SubElement(c_doc, f"{{{ns_container}}}Type")
        d_type.text = str(doc.get("type"))

        # Регистрационная дата документа (YYYY-MM-DD)
        d_date = ET.SubElement(c_doc, f"{{{ns_container}}}DocumentDate")
        d_date.text = str(doc.get("document_date"))

        # Регистрационный номер документа
        d_num = ET.SubElement(c_doc, f"{{{ns_container}}}DocumentNumber")
        d_num.text = str(doc.get("document_number"))

        # Номер исполнительного производства или дела (если применимо)
        if doc.get("case_number"):
            d_case = ET.SubElement(
                c_doc, f"{{{ns_container}}}DocumentCaseNumber"
            )
            d_case.text = str(doc.get("case_number"))

        # 4. Блок описания связанного СМЭВ-вложения (УКЭП + XML внутри ZIP)
        d_attach_block = ET.SubElement(
            c_doc, f"{{{ns_container}}}AttachmentsBlock"
        )
        att_desc = ET.SubElement(
            d_attach_block, f"{{{ns_attachments}}}AttachmentDescription"
        )

        att_format = ET.SubElement(
            att_desc, f"{{{ns_attachments}}}AttachmentFormat"
        )

        # Флаг структурированности (обычно false, так как основной документ внутри zip)
        is_unstructured = ET.SubElement(
            att_format, f"{{{ns_attachments}}}IsUnstructuredFormat"
        )
        is_unstructured.text = "true" if doc.get("is_unstructured") else "false"

        # Флаг архивации (всегда true для этого ВС)
        is_zipped = ET.SubElement(
            att_format, f"{{{ns_attachments}}}IsZippedPacket"
        )
        is_zipped.text = "true"

        # Namespace внутренней схемы самого бизнес-документа (например, схемы заявления)
        struct_type = ET.SubElement(
            att_format, f"{{{ns_attachments}}}StructuredFormatType"
        )
        struct_type.text = str(doc.get("structured_format_type"))

        # Имя файла архива (должно строго соответствовать маске piev_<UUID>.zip)
        att_filename = ET.SubElement(
            att_desc, f"{{{ns_attachments}}}AttachmentFilename"
        )
        att_filename.text = str(doc.get("attachment_filename"))

    # Преобразуем дерево элементов в байтовую XML строку с кодировкой UTF-8
    xml_bytes = ET.tostring(root, encoding="utf-8", method="xml")

    # Возвращаем декодированную строку, добавляя XML-декларацию
    return '<?xml version="1.0" encoding="UTF-8"?>' + xml_bytes.decode(
        "utf-8"
    )


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
