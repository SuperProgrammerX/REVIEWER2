<<<<<<< HEAD
# REVIEWER2: Optimizing Review Generation Through Prompt Generation

## Project Description
REVIEWER2 is an innovative system designed to assist authors in improving their academic papers by generating detailed and diverse reviews using large language models (LLMs). By modeling the distribution of possible aspects a review might cover, REVIEWER2 provides more specific and constructive feedback compared to traditional automated review generation methods.

## Prerequisites

Ensure you have the following installed:
- Python 3.x
- Node.js
- npm
- pip
- Java (required for `science-parse-cli`)
- fastapi
- uvicorn
- werkzeug
- transformers
- torch

## Environment Setup

### Backend Setup

#### 1. Clone the Repository
Clone the repository and navigate to the project directory:
```sh
git clone https://github.com/jw2349/REVIEWER2-demo-system.git
cd REVIEWER2-demo-system
```

#### 2. Create and Activate Virtual Environment
Create and activate a virtual environment:
```sh
python -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
Install the required dependencies:
```sh
pip install fastapi uvicorn werkzeug transformers torch
```

### Frontend Setup

#### 1. Navigate to the Frontend Directory
Navigate to the `chat-app` directory:
```sh
cd chat-app
```

#### 2. Install Frontend Dependencies
Install the required frontend dependencies using npm:
```sh
npm install
```

### Configuration

Ensure your environment variables are set up. If you use `.zshrc` for environment configurations, make sure to source it:
```sh
source ~/.zshrc
```

### Directory Structure
Your project directory should look like this:
```
REVIEWER2/
├── .vscode/
├── chat-app/
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   ├── .gitignore
│   ├── package-lock.json
│   ├── package.json
│   └── README.md
├── my-api/
│   ├── json/
│   ├── offloaded_weights_folder/
│   ├── uploads/
│   ├── check_and_restart.sh
│   ├── llama_attn_replace.py
│   ├── rvfastapi.py
│   ├── rvlib.py
│   ├── science-parse-cli-assembly-2.0.3.jar
│   └── start_server.sh
├── logfile.log
└── README.md
```

### Running the Server

#### Start the FastAPI Server
To start the FastAPI server, use the following command:
```sh
cd my-api
uvicorn rvfastapi:app --host 0.0.0.0 --port 3001 --log-level debug
```

### Running the Backend
```sh
cd my-api
python rvfastapi.py
```

### Running the Frontend

#### Start the React App
To start the frontend React application, use the following command:
```sh
cd chat-app
npm start
```

## API Endpoints

### 1. Upload PDF and Generate Prompt
**Endpoint**: `/submit-pdf-text`  
**Method**: `POST`  
**Parameters**:
- `pdfFile`: PDF file to be uploaded.
- `version`: Version of the prompt generator (default is "default").

**Example Request**:
```sh
curl -X POST "http://localhost:3001/submit-pdf-text"   -H "accept: application/json"   -H "Content-Type: multipart/form-data"   -F "pdfFile=@path/to/your/file.pdf"   -F "version=default"
```

**Example Response**:
```json
{
  "state": "success",
  "gen_prompt": "Generated prompt based on the uploaded PDF.",
  "paper_content": "Extracted content from the PDF."
}
```

### 2. Generate Review
**Endpoint**: `/generate-review`  
**Method**: `POST`  
**Parameters**:
- `paper_content`: Content of the paper.
- `prompt`: Generated prompt for the review.
- `version`: Version of the review generator (default is "default").

**Example Request**:
```sh
curl -X POST "http://localhost:3001/generate-review"   -H "Content-Type: application/json"   -d '{
    "paper_content": "Extracted content from the PDF.",
    "prompt": "Generated prompt based on the uploaded PDF.",
    "version": "default"
  }'
```

**Example Response**:
```json
{
  "gen_review": "Generated review based on the provided content and prompt."
}
```

## Automated Scripts

### 1. Start Server Script
Create a script named `start_server.sh` to activate the virtual environment and start the server:
```bash
#!/bin/bash

source /path/to/your/project/venv/bin/activate  # Activate virtual environment
uvicorn rvfastapi:app --host 0.0.0.0 --port 3001 --log-level debug
```

### 2. Check and Restart Server Script
Create a script named `check_and_restart_server.sh` to check if the server is running and restart it if necessary:
```bash
#!/bin/bash

# Check if the server is running
if ! pgrep -f "uvicorn rvfastapi:app" > /dev/null
then
    echo "Server is not running. Restarting..."
    ./start_server.sh
else
    echo "Server is running."
fi
```

Make both scripts executable:
```sh
chmod +x start_server.sh
chmod +x check_and_restart_server.sh
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributors
- Jingtian Wu
- Zhaolin Gao
- Thorsten Joachims

## Contact
For more information, please contact:
- Jingtian Wu: jw2349@cornell.edu
- Zhaolin Gao: zg292@cornell.edu
- Thorsten Joachims: thorsten.joachims@cornell.edu
=======
# REVIEWER2
<<<<<<< HEAD
>>>>>>> 211bcb2 (first commit)
=======
# REVIEWER2
>>>>>>> 1c83d40 (first commit)
