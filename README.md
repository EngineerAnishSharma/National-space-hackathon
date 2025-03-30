# National Space Hackathon

Welcome to the **National Space Hackathon** project! 🚀 This repository contains the backend and other components needed to run the application.

## Getting Started

Follow the steps below to set up and run the backend successfully.

### Prerequisites
Ensure you have the following installed:
- Python (3.11 better choice)
- pip (latest version recommended)
- Virtual environment (venv or conda)

### Backend Setup

1. **Navigate to the backend directory:**
   ```sh
   cd backend
   ```

2. **Set up a virtual environment:**
   - Using `venv`:
     ```sh
     python -m venv venv
     ```
   - Using `conda`:
     ```sh
     conda create --name myenv python=3.8
     ```

3. **Activate the virtual environment:**
   - For `venv`:
     - On Windows:
       ```sh
       venv\Scripts\activate
       ```
     - On macOS/Linux:
       ```sh
       source venv/bin/activate
       ```
   - For `conda`:
     ```sh
     conda activate myenv
     ```

4. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

5. **Run the backend:**
   ```sh
   python -m app.main
   ```
   **⚠️ Do not run:**
   ```sh
   cd app
   python main.py  # This won't work ❌
   ```

Now your backend should be running successfully! 🎉

## Contributing
Feel free to contribute by opening issues or submitting pull requests.

## License
This project is licensed under [MIT License](LICENSE).

