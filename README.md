# 🧥 OVDR: Online Virtual Dressing Room

**Project ID**: [P2024‑16]  
**Project Title**: *Online Virtual Dressing Room with Advanced Try‑On and Clothing Retrieval Features*  
**Team Name**: TEAM2024.07  
**Supervisor**: Dr. Qian Zhang

## 1. Project Overview
**OVDR (Online Virtual Dressing Room)** is a full-stack web application that enables users to virtually try on clothing using advanced computer vision and deep learning techniques. It supports personalized outfit recommendation, description-based search (powered by CLIP), and photorealistic try-on (using StableVITON).

A structured clothing dataset categorized into tops, bottoms, and dresses has also been developed, with each item annotated using descriptive captions. This dataset lays a solid foundation for future integration of semantic search and recommendation systems to enhance accuracy, as well as prompt-based try-on experiences.

---
## 2. Tasks & Deliverables

- [x] A web‑based application with an intuitive user interface.
- [x] A clothing dataset with text captions
- [x] StableVITON virtual try-on integration
- [x] CLIP-based text search system
- [x] User closet, combination and history tracking
- [x] RESTful API endpoints and full documentation
- [x] Efficient browsing and recommendation system integration

---
## 3. Installation Manual

### Prerequisites
- [NVIDIA CUDA](https://developer.nvidia.com/cuda-toolkit-archive)
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/downloads/) (3.8+)
- [Anaconda](https://www.anaconda.com/download) and  Add to Path
> ⚠️ The following tools are **optional or will be installed later in the guide**:
> - [MySQL](https://www.mysql.com/) *(Optional – Only required if you plan to deploy the database locally. See [Step 5](#5---set-up-mysql-optional-for-local-database-only))*
> - [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools) *(Required during Detectron2 setup. See [Step 3](#3---prepare-ai-models-stableviton--clip))* 
From VS Installer, choose Visual Studio Build Tool 2019, click "modify" and download the newest `MSVC` in single component and `Desktop Development using C++` in desktop and mobile applications.


### 1 - Clone the Repository
```bash
git clone https://csprojects.nottingham.edu.cn/grp-team07-gitlab/grp-team07-gitlab-work.git
cd grp-team07-gitlab-work
```
---
### 2 - Set Up Backend Environment
> Each time you run the program, "conda activate OVDR" is required 
```bash
conda create -n OVDR python=3.10 -y
conda activate OVDR
pip install -r requirements.txt

conda create -n StableViton python=3.10 -y
conda activate StableVITON
pip install -r requirements.txt
```

---
### 3 - Prepare AI Models (StableVITON + CLIP)

```bash
conda activate StableVITON
cd backend
mkdir models
cd models

# Install Triton (for Windows)
git clone https://github.com/PrashantSaikia/Triton-for-Windows
cd Triton-for-Windows
pip install triton-2.0.0-cp310-cp310-win_amd64.whl
cd ..

# Download clip-vit-large-patch14
git clone https://huggingface.co/openai/clip-vit-large-patch14

# Download StableVITON (ensure Git LFS is installed)
git lfs install
git clone https://huggingface.co/spaces/rlawjdghek/StableVITON

# Download StavleVITON models
go to https://huggingface.co/spaces/rlawjdghek/StableVITON/tree/main
to download the `checkpoints dir` alone
https://huggingface.co/spaces/rlawjdghek/StableVITON/tree/main
download the checkpoints dir alone
```

# Detectron2 for DensePose
To install `detectron2` and `DensePose` on Windows, make sure **Visual Studio Build Tools** are installed:
1. Download: [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools)  
2. In the installer:
   - Select **Visual Studio Build Tools 2019**
   - Go to **Modify**, check:
     - ✅ **MSVC** (latest version, under “Single Component”)
     - ✅ **Desktop development with C++** workload
3. Install and restart your terminal.
---

Now install `detectron2` and `DensePose`:

> 💡 **Important:** Use **x64 Native Tools Command Prompt for VS 2019**, not regular `cmd` or `PowerShell`

```bash
# Clone detectron2 repository
git clone https://github.com/facebookresearch/detectron2.git

# Activate your environment
conda activate StableViton

# Navigate to Detectron2 repo
cd your_store_project_path/backend/models/detectron2/

# Install detectron2
set DISTUTILS_USE_SDK=1 && pip install .

# Install DensePose
cd ./projects/DensePose
set DISTUTILS_USE_SDK=1 && pip install .
```
---
### 4 - Set Up Frontend
```bash
cd frontend
npm install
npm install concurrently wait-on --save-dev   # Install parallel running dependencies (if not installed)
```
---
### 5 - Set Up MySQL (Optional for Local Try-On Only)
```sql
CREATE DATABASE ovdr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
```bash
mysql -u root -p ovdr < backend/database/ovdr_structure.sql
mysql -u root -p ovdr < backend/database/ovdr_data_only.sql
```
Configure your .env file:
```env
USER_NAME=root
PASSWORD=yourpassword
HOSTNAME=127.0.0.1
PORT=3306
DATABASE=ovdr
```
> For more information about shared team databases and access IPs, please refer to the [Database Notes](#6-database-setup--notes).

### 6 - Run the Application (Ensure you are in `./frontend/`)
```bash
conda activate OVDR
npm run dev
```
If you encounter the error:
```bash
[0] Invalid options object. Dev Server has been initialized using an options object that does not match the API schema.  
[0] - options.allowedHosts[0] should be a non-empty string.
```
Solution:
Please modify the /frontend/node_modules/react-scripts/config/webpackDevServer.config.js file and change the allowedHosts configuration on line 46 to:
```bash
allowedHosts: "all",
```
### 7. Troubleshooting
#### 1 - Error: ModuleNotFoundError
```bash
pip install -r requirements.txt again
```
---
#### 2 - Error: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE
If you see an error like:
```bash
RROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE. torch==2.0.1+cu117 from https://download.pytorch.org/... Expected sha256 ... Got ...
```
This means the downloaded PyTorch package has a different hash than the one recorded in `requirements.txt`. This is usually due to PyTorch officially updating the `.whl` file metadata.

✅ **Solution 1 – Manually download and install the correct PyTorch wheels**:

1. Visit: [https://download.pytorch.org/whl/cu117](https://download.pytorch.org/whl/cu117)
2. Download the matching `.whl` files for your Python version (e.g. `cp310` for Python 3.10):
   - `torch-2.0.1+cu117-cp310-cp310-win_amd64.whl`
   - `torchvision-0.15.2+cu117-cp310-cp310-win_amd64.whl`
   - `torchaudio-2.0.2-cp310-cp310-win_amd64.whl`
3. Run:
```bash
pip install torch-*.whl torchvision-*.whl torchaudio-*.whl
```
---

> The backend runs at `http://localhost:5000`, and the frontend at `http://localhost:3000`.
---


## 4. Project Structure
> Organized by backend, frontend, image data, and documentation.

---
<details>
<summary>📁 OVDR/ (Root Project)</summary>

```bash
OVDR/
├── app.py                          # Project root entrypoint (if needed)
├── README.md                       # Project overview
├── .gitignore                      # Git ignored files
```
</details>

---

<details>
<summary>📁 ./backend/ — Flask backend</summary>

```bash
├── backend/                        # Flask backend
│   ├── __init__.py                 # create_app() and app initialization
│   ├── config.py                   # Config class for DB, mail, etc.
│   ├── exts.py                     # db/mail/cors plugin initialization
│   ├── .env                        # Environment variables for secrets
│
│   ├── database/                   # DB schema, data and documentation
│   │   ├── OVDR.sql
│   │   ├── ovdr_structure.sql
│   │   ├── ovdr_data_only.sql
│   │   ├── backup.sql
│   │   ├── ERD.png                 # Database Entity-Relationship Diagram
│   │   └── database.md             # DB documentation
│
│   ├── migrations/                 # Flask-Migrate migration files
│
│   ├── models/                     # Model directories
│   │   ├── clip-vit-large-patch14  # CLIP model
│   │   └── StableVITON/            # StableVITON try-on model
│
│   ├── routes/                     # Flask route blueprints
│   │   ├── __init__.py
│   │   ├── auth.py                 # Login/Register routes
│   │   ├── closet.py               # Clothing listing & closet management
│   │   ├── combination.py          # Outfit combination logic
│   │   ├── email.py                # Email sending routes
│   │   ├── forms.py                # WTForms for validation
│   │   ├── history.py              # Browsing history
│   │   ├── process.py              # Try-on image generation
│   │   ├── recommend.py            # Recommendation system
│   │   ├── search.py               # CLIP-based text search
│   │   └── user_image.py           # User image upload & fetch
│
│   ├── scripts/                    # One-time utility scripts
│   │   ├── image_embedding.py
│   │   ├── insert_clothes_data.py
│   │   ├── precompute_similarity.py
│   │   ├── qwen_generate_caption.py
│   │   ├── recommend_clicktime.py
│   │   ├── recommend_sim_algorithm.py
│   │   ├── rename_clothes.py
│   │   ├── save_CLIP_model.py
│   │   ├── search_algorithm.py
│   │   ├── search_api.py
│   │   └── similarity_matrix.npy
│
│   ├── utils/                      # Utility modules
│   │   ├── caption_utils.py        # Caption formatting and generation
│   │   ├── download_utils.py       # Download cloth image from URL
│   │   ├── helpers.py              # URL/path formatting utilities
│   │   ├── image_utils.py          # Save/rename/delete user images
│   │   ├── stableviton_runner.py   # Run StableVITON subprocess
│   │   ├── static_serve.py         # Static image serving utilities
│   │   ├── config.py               # Duplicate? (backend/config.py used)
│   │   ├── exts.py                 # Duplicate? (used for plugin setup)
│   │   └── models.py               # SQLAlchemy models (User, Clothing...)
│
│   └── similarity_matrix.npy       # Precomputed similarity matrix
```
</details>

---

<details>
<summary>📁 ./data/ — Static & dynamic image data</summary>

```bash
├── data/                           # Image assets & user uploads
│   ├── clothes/                    # Main clothing image dataset
│   │   ├── tops/
│   │   │   ├── cloth/
│   │   │   │    └── 000001_top.jpg
│   │   │   ├── cloth-mask/
│   │   │   └── model-tryon/
│   │   ├── bottoms/
│   │   ├── dresses/
│   │   └── captions/               # Generated captions JSONs
│
│   ├── users/
│   │   ├── image/                  # Uploaded user full-body images
│   │     └── 1.jpg                 # Named by user_id
│
│   └── combinations/               # Output try-on images
│       └── user_1/
│           └── 000001.jpg
```
</details>

---

<details>
<summary>📁 ./frontend/ — React-based frontend</summary>

```bash
├── frontend/                       # React frontend
│   ├── node_modules/               # Frontend dependencies
│   ├── public/
│   ├── src/                        # Main frontend code
│   │   ├── App.js / App.css
│   │   ├── ClothesDetail.js / .css
│   │   ├── FullCloset.js / .css
│   │   ├── History.js / .css
│   │   ├── Home.js / .css
│   │   ├── Login.js / .css
│   │   ├── Register.js
│   │   ├── SendImage.js / .css
│   │   ├── TryOn.js / .css
│   │   ├── UploadImage.js / .css
│   │   ├── index.js / index.css
│   │   └── setupTests.js / reportWebVitals.js
│   ├── package.json                # React project config
│   ├── package-lock.json
│   └── README.md                   # Frontend description
```
</details>

---

<details>
<summary>📁 ./docs/ — Project documentation</summary>

```bash
├── docs/                           # Project documentation
│   ├── JSdocs/
│   ├── code_report.md              # Final report with structure & logic
│   ├── api_documentation.md        # Full REST API documentation
│   ├── installation_manual.html
│   ├── user_manual.pdf
│   └── Summary_of_quality_assurance.pdf  # Quality testing doc
```
</details>

---

<details>
<summary>📁 ./website/ — Static information site</summary>

```bash
├── website/                        # Static info website
│   ├── css/
│   ├── minutes/
│   ├── src/
│   └── index.html           # Presentation site
```
</details>

---
## 5. Documentation
| Name | Description |
|------|-------------|
| [User Manual](./docs/user_manual.pdf) | Instructions for using the frontend interface |
| [Jsdocs](./docs/JSdocs/) | Detailed technical documentation for all functions |
| [requirements.txt](./requirements.txt) | Python dependency list for backend environment setup |
| [Code Report](./docs/code_report.md) | Architecture, logic explanations, and code structure overview |
| [API Documentation](./docs/api_documentation.md) | Full RESTful API documentation for backend modules |
| [Summary of Quality Assurance](./docs/Summary_of_quality_assurance.pdf) | Final QA report and testing results |

## 6. Database Setup & Notes

This project uses a **MySQL-compatible database running on a designated local server**, typically hosted on the developer machine for team access and testing.

### Common Database IPs

The following IP addresses are commonly used to access the database:

- `10.176.45.0`
- `172.19.108.9`

> These IPs refer to the developer machine that runs the MySQL server.  
> If you are unsure about database access or need permissions, please contact **Zixin Ding (ssyzd4@nottingham.edu.cn)**.

---

### Local Testing (Try-On Demo / Offline Setup)

If you only want to **test the virtual try-on feature locally**, without syncing to the main team database, you can migrate the schema and data to your own machine.

#### MySQL Setup (Local):

1. **Install MySQL**:  
   Official download: [https://www.mysql.com/cn/downloads/](https://www.mysql.com/cn/downloads/)

2. **Create a new database**:
   ```sql
   CREATE DATABASE ovdr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Import the table structure and data**:
   ```bash
   mysql -u root -p ovdr < backend/database/ovdr_structure.sql
   mysql -u root -p ovdr < backend/database/ovdr_data_only.sql
   ```

4. **Edit `.env` file located in `./backend/` with your local config**:
   ```env
   USER_NAME=root
   PASSWORD=yourpassword
   HOSTNAME=127.0.0.1
   PORT=3306
   DATABASE=ovdr
   ```

> This allows you to test try-on, closet, history, and search functions **independently**, without connecting to the shared database.
---

## 7. Team Members & Contact

This project was completed by **TEAM2024.07** as part of the [P2024‑16] Online Virtual Dressing Room capstone.

| Name                      | Role & Responsibilities                                                                                                  | Contact                        |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| **Zhihao Cao**            | StableVITON try-on module, combination saving, bug fixing, Installation Manual, Final Report          | scyzc10@nottingham.edu.cn         |
| **Zixin Ding**            | Backend architecture, dataset and database, caption generation, user auth, upload, closet and history logic, frontend improvement, bug fixing, Code Report, README, Installation Manual, Final Report | ssyzd4@nottingham.edu.cn         |
| **Peini She**             | React frontend development, combination and email routing, bug fixing, User Manual writing      | scyps2@nottingham.edu.cn         |
| **Jinghao Liu** &<br>**Zihan Zhou** | Search and Recommendation module with CLIP, embedding logic, semantic search, Quality Assurance                            | scyjl16@nottingham.edu.cn<br>scyzz15@nottingham.edu.cn |



---

> This project was developed by **Team202407** as part of the **COMP2043 Software Engineering Group Project** at the University of Nottingham, Ningbo, China.
