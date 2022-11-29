import os
from secure_json import Settings
import requests
import imaplib
from datetime import datetime
import time
import email


settings = Settings('Settings.json').data


def send_document(text, path_to_doc, chat_id, TOKEN, remove_after=True):
    url = "https://api.telegram.org/bot"
    url += TOKEN
    method = url + "/sendDocument"

    with open(path_to_doc, "rb") as file_doc:
        files = {"document": file_doc}

        r = requests.post(method, data={
            "chat_id": chat_id,
            "caption": text
        }, files=files)

    if remove_after:
        os.remove(path_to_doc)


def mkdir_image():
    if not os.path.exists('image'):
        os.mkdir('image')


if __name__ == '__main__':

    mail = imaplib.IMAP4_SSL('imap.yandex.ru')
    mail.login(settings.email.mail, settings.email.password)

    while True:

        try:

            mail.list()
            mail.select('inbox')

            unseen_ids = mail.search(None, 'UNSEEN')[1][0]
            id_list = unseen_ids.split()

            for id in id_list:
                try:
                    result, data = mail.fetch(id, "(RFC822)")
                    raw_email = data[0][1]
                    raw_email_string = raw_email.decode('utf-8')

                    email_message = email.message_from_string(raw_email_string)

                    payloads = email_message.get_payload()

                    message = ''

                    file_name = ''

                    for payload in payloads:
                        if payload.get_content_type() == "image/jpeg" or payload.get_content_type() == "image/png":
                            file_name = payload.get_filename()
                            mkdir_image()
                            file = open(file_name, 'wb')
                            file.write(payload.get_payload(decode=True))
                            file.close()
                        else:
                            message += payload.get_payload(decode=True).decode('utf-8')

                    if file_name > '':
                        send_document('Детекция', file_name, settings.telegram.chat_id, settings.telegram.bot_token)

                    mail.store(id, '+FLAGS', '\\Deleted')
                    mail.expunge()
                except:
                    pass

            time.sleep(10)
        except:
            time.sleep(30)