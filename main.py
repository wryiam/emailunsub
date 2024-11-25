import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import imaplib
import email
from bs4 import BeautifulSoup

def emailConnect(username, password):
    """Connect to the email server."""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")
        return mail
    except imaplib.IMAP4.error as e:
        raise ValueError(f"Error connecting to email server: {e}")


def linkextract(html_content):
    """Extract unsubscribe links from HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    links = [link['href'] for link in soup.find_all("a", href=True) if "unsubscribe" in link["href"].lower()]
    return links


def decode_content(payload):
    """Decode email content with a fallback for encoding issues."""
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return payload.decode("latin-1")
        except UnicodeDecodeError:
            return ""


def search_for_email(username, password, limit=100):
    """Search emails containing 'unsubscribe' and extract links."""
    mail = emailConnect(username, password)
    try:
        _, search_data = mail.search(None, '(TEXT "unsubscribe")')
        email_ids = search_data[0].split()
        links = []

        for num in email_ids:
            if len(links) >= limit:
                break

            _, data = mail.fetch(num, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        payload = part.get_payload(decode=True)
                        html_content = decode_content(payload)
                        links.extend(linkextract(html_content))
                        if len(links) >= limit:
                            break
            else:
                content_type = msg.get_content_type()
                payload = msg.get_payload(decode=True)
                if content_type == "text/html":
                    html_content = decode_content(payload)
                    links.extend(linkextract(html_content))
                    if len(links) >= limit:
                        break

        return links[:limit]
    finally:
        mail.logout()


def click_link(link):
    """Attempt to visit the given link."""
    try:
        response = requests.get(link)
        if response.status_code == 200:
            return f"Successfully visited: {link}"
        else:
            return f"Failed to visit {link} - Status Code: {response.status_code}"
    except Exception as e:
        return f"Error visiting {link} - {str(e)}"

class EmailLinkExtractorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Email Unsubscriber")
        self.geometry("600x500")
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.links = []

        self.create_input_page()

    def create_input_page(self):
        """Create the input page for email and password."""
        self.clear_frame()

        ttk.Label(self, text="Email Link Extractor", font=("Arial", 18)).pack(pady=10)

        ttk.Label(self, text="Email:").pack(pady=(20, 5))
        ttk.Entry(self, textvariable=self.username, width=40).pack()

        ttk.Label(self, text="Password:").pack(pady=5)
        ttk.Entry(self, textvariable=self.password, width=40, show="*").pack()

        ttk.Button(self, text="Extract Links", command=self.extract_links).pack(pady=20)

    def create_links_page(self):
        """Create the page to display extracted links and enable clicking."""
        self.clear_frame()

        ttk.Label(self, text="Extracted Links", font=("Arial", 18)).pack(pady=10)

        text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=15)
        text_area.pack(pady=10)
        for link in self.links:
            text_area.insert(tk.END, link + "\n")
        text_area.configure(state="disabled")

        ttk.Button(self, text="Unsubscribe", command=self.click_all_links).pack(pady=10)
        ttk.Button(self, text="Back to Input Page", command=self.create_input_page).pack(pady=10)

    def extract_links(self):
        """Handle link extraction."""
        email = self.username.get().strip()
        password = self.password.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "Email and Password fields cannot be empty.")
            return

        try:
            self.links = search_for_email(email, password, limit=100)
            if self.links:
                self.create_links_page()
            else:
                messagebox.showinfo("No Links Found", "No unsubscribe links were found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def click_all_links(self):
        """Attempt to click all extracted links and show results."""
        results = []
        for link in self.links:
            result = click_link(link)
            results.append(result)

        results_window = tk.Toplevel(self)
        results_window.title("Click Results")
        results_window.geometry("600x400")

        text_area = scrolledtext.ScrolledText(results_window, wrap=tk.WORD, width=70, height=20)
        text_area.pack(pady=10)
        for result in results:
            text_area.insert(tk.END, result + "\n")
        text_area.configure(state="disabled")

        ttk.Button(results_window, text="Close", command=results_window.destroy).pack(pady=10)

    def clear_frame(self):
        """Clear all widgets from the current frame."""
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = EmailLinkExtractorApp()
    app.mainloop()

