# Tobi's Restaurant - Local LLM API

A self-hosted AI restaurant ordering system powered by **Llama-3-8B-Instruct** with Docker containerization. Tobi is a chill surfer dude AI that helps customers order food with accurate menu knowledge and a friendly personality.

## 🎯 Features

- **🏄‍♂️ Tobi the Surfer AI**: Friendly surfer dude personality using casual language
- **🧠 Powered by Llama-3-8B**: Smart, accurate responses with no hallucination
- **📋 Swappable Menus**: Easy menu customization via JSON file
- **🚀 GPU Support**: Optional NVIDIA GPU acceleration for blazing-fast responses
- **🐳 Docker Containerized**: One-click deployment with automated scripts
- **💾 Order Tracking**: SQLite database for order management
- **🌐 Share with Others**: ngrok integration for public access

## 🛠️ Tech Stack

- **Language Model**: Meta Llama-3-8B-Instruct (Q4_K_M quantization, ~4.7GB)
- **Backend**: FastAPI + Uvicorn (ASGI server)
- **AI Runtime**: llama-cpp-python (with optional CUDA support)
- **Database**: SQLite
- **Frontend**: HTML/CSS/JavaScript (vanilla)
- **Deployment**: Docker + PowerShell automation
- **Platform**: Windows with Docker Desktop

## 📦 What's New (v2.0)

### ✨ Upgraded from Phi-2 to Llama-3-8B
- **8B parameters** vs 2.7B (3x larger model)
- **Zero hallucination**: Accurately references menu items
- **Better instruction following**: Understands complex questions
- **Larger context window**: 4096 tokens (handles full menu)

### 🔧 Architecture Improvements
- **Menu-agnostic design**: No keyword matching, pure AI inference
- **JSON-based menus**: Swap restaurants by editing `menu.json`
- **Simplified system**: Removed VIP passwords and presidential order numbers
- **GPU-ready**: NVIDIA CUDA support via `Dockerfile.gpu`

## 🚀 Quick Start

### Prerequisites

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
2. **AI Model** - Download Llama-3-8B-Instruct:
   ```bash
   curl -L -o models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf \
   "https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
   ```
3. **(Optional) NVIDIA GPU** - For GPU acceleration, ensure [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) is installed

### One-Click Launch

**CPU Mode** (works on any machine):
```powershell
.\start-tobi.ps1
```

**GPU Mode** (requires NVIDIA GPU):
```powershell
.\start-tobi-gpu.ps1
```

The script will:
- ✅ Build the Docker image
- ✅ Load the Llama-3 model
- ✅ Start the API server
- ✅ Open the chat interface in your browser

## 📁 Project Structure

```
my-llm-api/
├── server.py                   # FastAPI backend
├── restaurant_chat.html        # Frontend chat interface
├── menu.json                   # Restaurant menu (easily swappable!)
├── Dockerfile                  # CPU-only Docker build
├── Dockerfile.gpu              # GPU-accelerated Docker build
├── start-tobi.ps1             # CPU startup script
├── start-tobi-gpu.ps1         # GPU startup script
├── README.md                   # This file
└── models/
    └── Meta-Llama-3-8B-Instruct.Q4_K_M.gguf  # AI model (4.7GB)
```

## 🍽️ Customizing the Menu

Edit `menu.json` to change the restaurant menu:

```json
{
  "restaurant_name": "Your Restaurant Name",
  "starters": [
    {"name": "Item Name", "description": "Details", "price": 12.00}
  ],
  "mains": [...],
  "desserts": [...],
  "drinks": [...]
}
```

Then rebuild:
```bash
docker build -t tobi-restaurant .
docker run -d -p 8000:8000 -v "./models:/app/models" --name tobi tobi-restaurant
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/menu` | Get full menu JSON |
| `POST` | `/chat` | Send message to Tobi |
| `POST` | `/order` | Create new order |
| `GET` | `/order/{id}` | Retrieve order details |

### Example Chat Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the steak frites"}'
```

**Response:**
```json
{
  "response": "Dude! The Steak Frites is a total winner. You get an 8 oz sirloin steak, cooked to perfection, served with some crispy hand-cut fries and a side of chimichurri sauce. It's like, the ultimate comfort food, bro.",
  "session_id": "abc-123",
  "restaurant": "The Common House"
}
```

## 🖥️ System Requirements

### Minimum (CPU-only)
- **CPU**: 4+ cores (Intel i5/AMD Ryzen 5 or better)
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **OS**: Windows 10/11 with Docker Desktop

### Recommended (GPU-accelerated)
- **GPU**: NVIDIA RTX 3060 or better (8GB VRAM)
- **CPU**: 6+ cores
- **RAM**: 16GB
- **Storage**: 15GB free space

### Tested Configuration
- **CPU**: Intel i9-9900K (8 cores, 16 threads)
- **RAM**: 16GB
- **GPU**: NVIDIA RTX 3070 (8GB VRAM)
- **Performance**: ~2-5 second response times (CPU), <1 second (GPU)

## 🌐 Sharing with Others (ngrok)

To let friends/family access Tobi remotely:

1. Install [ngrok](https://ngrok.com/)
2. Run: `ngrok http 8000`
3. Share the public URL (e.g., `https://abc123.ngrok.io`)
4. Update `restaurant_chat.html` to point to the ngrok URL

## 🐛 Troubleshooting

### "Model file not found"
```bash
# Verify model file exists and is named correctly
ls -lh models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf
```

### "Docker is not running"
- Open Docker Desktop and wait for it to start

### "Port 8000 already in use"
```bash
# Stop existing containers
docker stop $(docker ps -q --filter publish=8000)
```

### Slow responses (CPU mode)
- Responses take 2-5 seconds on CPU (normal)
- Use GPU mode for <1 second responses
- Reduce `n_ctx` in server.py if running out of memory

## 🎨 Customization Ideas

- **Change Tobi's personality**: Edit the system prompt in `server.py` (line 127-129)
- **Add more endpoints**: Extend FastAPI routes in `server.py`
- **Custom UI**: Modify `restaurant_chat.html` styling
- **Different models**: Swap Llama-3 for Mistral-7B or other GGUF models
- **Multi-language**: Add language detection and translation

## 📊 Model Comparison

| Model | Size | Speed (CPU) | Accuracy | Recommended For |
|-------|------|-------------|----------|-----------------|
| Phi-2 | 1.7GB | Fast | Low (hallucinates) | ❌ Not recommended |
| Llama-3-8B | 4.7GB | Medium | Excellent | ✅ Current choice |
| Mistral-7B | 4.1GB | Medium | Very Good | ✅ Alternative option |
| Llama-3.1-8B | 5.7GB | Slower | Excellent+ | 🎯 Higher quality option |

## 🤝 Contributing

Feel free to fork, modify, and submit PRs! Some ideas:
- Add user authentication
- Implement payment processing
- Create admin dashboard for order management
- Add menu item images
- Multi-restaurant support

## 📝 License

MIT License - Feel free to use this for personal or commercial projects!

## 🙏 Credits

- **Meta AI** - Llama-3-8B-Instruct model
- **llama.cpp** - Efficient LLM inference
- **FastAPI** - Modern Python web framework
- **Bartowski** - GGUF model quantization

---

**Built with ❤️ by Eric | Powered by Llama-3-8B-Instruct**
