# Diary App with Flet

## Overview
A modern, cross-platform diary application built using Flet and Python, allowing users to create, update, and manage personal diary entries with file attachments.

## Features
- User Authentication
- Create, Read, Update, Delete (CRUD) Diary Entries
- File Attachment Support (Images, Documents, Audio)
- Responsive UI with Flet
- Backend API Integration

## Prerequisites
- Python 3.8+
- Flet
- Requests library
- Backend API (Django/DRF recommended)

## Installation

### Clone the Repository
```bash
git clone https://github.com/yourusername/diary-app.git
cd diary-app
```

### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration
1. Set up your backend API URL in `main.py`
2. Configure any environment variables if needed

## Running the Application
```bash
python mobile/main.py
```

## Project Structure
```
diary-app-with-flet/
│
├── mobile/
│   └── main.py         # Main Flet application
│
├── backend/            # Backend API (if included)
│   └── ...
│
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore file
└── README.md           # Project documentation
```

## Technologies Used
- Frontend: Flet (Python UI Framework)
- Backend: Django/DRF (Recommended)
- Authentication: Token-based
- File Handling: Multipart form uploads

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Your Name - your.email@example.com

Project Link: [https://github.com/ikhwanand/diary-app](https://github.com/yourusername/diary-app)
