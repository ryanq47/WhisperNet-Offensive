# **WhisperNet Project Setup**  

This guide provides step-by-step instructions for setting up WhisperNet, including environment configuration and required dependencies.  

I promise setup is shorter than it looks :)

| Operating System | Compatibility |
|------------------|--------------|
| Linux           | Yes          |
| Windows        | Probably, not officially supported/tested. If you can get all the Req's, it should work |


---

## **0. Run `./install.sh`**
 - If anything goes wrong with this, follow the below steps for a manual install

## **1. Install Dependencies**  

### **Python Requirements**  

 - **Create a Virtual Environment**  
   A virtual environment isolates project dependencies to avoid conflicts with system packages.  

```bash
python3 -m venv whispernet_venv
```

 - **Activate the Virtual Environment**  

```bash
source whispernet_venv/bin/activate
```


 - **Install Required Python Packages**  
   Install all necessary dependencies from `requirements.txt`.  

```bash
pip install -r requirements.txt
```

---

## **2. Install Additional Dependencies**  

The following system dependencies are required for building and running WhisperNet:  

- **CMake** – Required for building C/C++ components.  
- **MinGW** – Needed for compiling Windows-compatible binaries.  
- **Docker** – Used for containerized environments (AKA the redis server)

### **2.1 Installation Instructions**  

#### **Linux/macOS**  
```bash
sudo apt install cmake
sudo apt install mingw-w64
sudo apt install docker.io
```

---

## **3. Verify Installation**  

Run the following commands to verify the installation of required tools:  

```bash
cmake --version
gcc --version
docker --version
```

If all commands return version numbers, the setup was successful.  

---

## **4. Next Steps**  

Once setup is complete, you can proceed with building and running WhisperNet. Follow the project’s documentation for compiling, configuring, and executing the system.