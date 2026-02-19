from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llama_cpp import Llama
import json
import sqlite3
import uuid
import os

MODEL_PATH = "/app/models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"

# Enable GPU acceleration with n_gpu_layers (set to -1 to use all layers on GPU)
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,  # Llama-3 supports larger context
    n_gpu_layers=-1,  # Use GPU for all layers
    verbose=False
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Simple order number counter
ORDER_COUNTER_START = 1000

# Load menu from JSON file (allows easy menu swapping!)
MENU_FILE = os.getenv("MENU_FILE", "/app/menu.json")
try:
    with open(MENU_FILE, 'r') as f:
        MENU_DATA = json.load(f)
    print(f"Loaded menu from {MENU_FILE}")
except FileNotFoundError:
    print(f"Menu file not found at {MENU_FILE}, using fallback hardcoded menu")
    # Fallback to hardcoded menu if file doesn't exist
    MENU_DATA = {
    "restaurant_name": "The Common House",
    "starters": [
        {"name": "Truffle Fries", "description": "Parmesan, rosemary, truffle oil", "price": 12.00},
        {"name": "Spicy Tuna Tartare", "description": "Ahi tuna, avocado, sesame-soy dressing", "price": 16.00},
        {"name": "Crispy Brussels", "description": "Balsamic glaze, chili flakes, lemon zest", "price": 11.00},
        {"name": "Burrata & Tomato", "description": "Heirloom tomato, basil oil, sea salt", "price": 14.00},
        {"name": "Smoked Chicken Flatbread", "description": "Arugula, goat cheese, roasted red pepper", "price": 13.00}
    ],
    "mains": [
        {"name": "Seared Salmon Bowl", "description": "Brown rice, avocado, miso vinaigrette", "price": 24.00},
        {"name": "Short Rib Pappardelle", "description": "Red wine braise, parmesan, gremolata", "price": 26.00},
        {"name": "Buttermilk Fried Chicken Sandwich", "description": "Pickles, garlic aioli, brioche bun", "price": 18.00},
        {"name": "Miso Glazed Cod", "description": "Snap peas, jasmine rice, sesame", "price": 28.00},
        {"name": "Steak Frites", "description": "8 oz sirloin, chimichurri, hand-cut fries", "price": 32.00},
        {"name": "House Smash Burger", "description": "Double patty, cheddar, caramelized onion", "price": 16.00},
        {"name": "Roasted Mushroom Risotto", "description": "Truffle oil, parmesan, thyme", "price": 22.00},
        {"name": "Grilled Chicken Cobb", "description": "Bacon, egg, blue cheese, avocado ranch", "price": 19.00},
        {"name": "Lobster Mac & Cheese", "description": "Cavatappi, gruyère, breadcrumbs", "price": 29.00},
        {"name": "Spaghetti Pomodoro", "description": "San Marzano tomato, basil, pecorino", "price": 17.00}
    ],
    "desserts": [
        {"name": "Warm Chocolate Torte", "description": "Sea salt, vanilla cream", "price": 9.00},
        {"name": "Olive Oil Cake", "description": "Lemon glaze, whipped mascarpone", "price": 8.00},
        {"name": "Salted Caramel Pudding", "description": "Toasted pecans, chantilly", "price": 7.00}
    ],
    "drinks": [
        {"name": "Old Fashioned", "description": "Bourbon, bitters, sugar, orange peel", "price": 12.00},
        {"name": "Espresso Martini", "description": "Vodka, espresso, coffee liqueur", "price": 14.00},
        {"name": "Negroni", "description": "Gin, Campari, sweet vermouth", "price": 13.00},
        {"name": "Margarita", "description": "Tequila, lime, orange liqueur", "price": 11.00},
        {"name": "Whiskey Sour", "description": "Bourbon, lemon, egg white", "price": 12.00}
    ]
    }

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('/app/orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            order_number INTEGER UNIQUE,
            session_id TEXT,
            items TEXT,
            total REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def get_next_order_number():
    conn = sqlite3.connect('/app/orders.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM orders')
    count = cursor.fetchone()[0]
    conn.close()
    return ORDER_COUNTER_START + count

@app.get("/")
def root():
    return {"status": "The Common House AI Assistant is running", "restaurant": "The Common House"}

@app.get("/menu")
def get_menu():
    return MENU_DATA

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt") or data.get("message", "")
        session_id = data.get("session_id", str(uuid.uuid4()))
        
        if not prompt:
            return {"error": "No prompt or message provided"}

        # Build full menu context with descriptions - let the model infer what the customer wants
        menu_text = ""
        for category in ["starters", "mains", "desserts", "drinks"]:
            if category in MENU_DATA and isinstance(MENU_DATA[category], list):
                menu_text += f"\n{category.title()}: "
                items_list = [f"{item['name']} ({item['description']}, ${item['price']})" for item in MENU_DATA[category]]
                menu_text += "; ".join(items_list)

        system_context = f"Full menu:{menu_text}"

        # Llama-3 instruction format with system message
        simple_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are Tobi, a chill surfer who works at {MENU_DATA['restaurant_name']} restaurant. {system_context} Answer questions about our menu in 1-2 short sentences. Use casual surfer language. Only mention items actually on our menu with accurate descriptions. Everything is available.<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

        output = llm(simple_prompt, max_tokens=70, temperature=0.5, stop=["<|eot_id|>", "<|end_of_text|>"])
        ai_response = output["choices"][0]["text"].strip()
        
        return {
            "response": ai_response,
            "session_id": session_id,
            "restaurant": MENU_DATA.get("restaurant_name", "Restaurant")
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/order")
async def create_order(request: Request):
    try:
        data = await request.json()
        session_id = data.get("session_id", str(uuid.uuid4()))
        items = data.get("items", [])
        
        if not items:
            return {"error": "No items provided"}
        
        total = sum(float(item.get('price', 0)) for item in items)
        order_number = get_next_order_number()
        
        conn = sqlite3.connect('/app/orders.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (order_number, session_id, items, total, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_number, session_id, json.dumps(items), total, 'confirmed'))
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "order_number": order_number,
            "items": items,
            "total": total,
            "message": f"Order #{order_number} confirmed! Your food will be ready shortly."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/order/{order_number}")
def get_order(order_number: int):
    try:
        conn = sqlite3.connect('/app/orders.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
        order = cursor.fetchone()
        conn.close()
        
        if not order:
            return {"error": "Order not found"}
        
        return {
            "order_number": order[1],
            "items": json.loads(order[3]),
            "total": order[4],
            "status": order[5],
            "created_at": order[6]
        }
    except Exception as e:
        return {"error": f"Error retrieving order: {str(e)}"}