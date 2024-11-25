# Email Link Extractor and Unsubscriber

A Python-based application with a **Tkinter GUI** for extracting and managing **unsubscribe links** from your email inbox. This application allows you to log in to your email, extract up to 100 unsubscribe links, and optionally visit those links directly.

---

## Features

### 1. Extract Unsubscribe Links
- Logs into your email inbox using your credentials.
- Searches for emails containing "unsubscribe" links.
- Extracts and displays up to 100 unsubscribe links in a scrollable interface.

### 2. Click Links
- Allows you to "click" the extracted links by sending HTTP GET requests.
- Displays the results of each request (success, failure, or error) in a detailed, scrollable interface.

### 3. User-Friendly Interface
- Simple **Tkinter-based GUI**:
  - Input page for entering email credentials.
  - Display page for extracted links.
  - Results page for link-clicking operations.

---

## Installation

### Prerequisites
Ensure you have Python installed (version 3.7 or later). Install the required libraries by running:

```bash
pip install beautifulsoup4 requests

