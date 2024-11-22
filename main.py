import imaplib
import email
import os

username = ""
password = ""

def emailConnect():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")
        return mail
    except imaplib.IMAP4.error as e:
        print(f"Error connecting to email server: {e}")
        return None

def search_for_email():
    mail = emailConnect()
    if not mail:
        return

    try:
        _, search_data = mail.search(None, '(TEXT "unsubscribe")')
        email_ids = search_data[0].split()

        print(f"Found {len(email_ids)} emails containing 'unsubscribe'.")

        for num in email_ids:
            _, data = mail.fetch(num, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        html_content = part.get_payload(decode=True).decode()
                        print("Email HTML Content:\n", html_content)
            else:
                content_type = msg.get_content_type()
                content = msg.get_payload(decode=True).decode()
                if content_type == "text/html":
                    print("Email HTML Content:\n", content)
    except Exception as e:
        print(f"Error during email processing: {e}")
    finally:
        mail.logout()

search_for_email()
