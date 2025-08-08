import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sqlite3
from database import Database
import json
import hashlib
import pathlib


class PizzaDeliverySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("🍕 Pizza Palace - Delivery Management System")
        self.root.geometry("1400x900")
        self.root.configure(bg="#2C3E50")
        self.session_path = "session.json"
        self.db = Database()
        self.current_user = self.get_logged_in_user()
        if self.current_user:
            self.init_main_app()
        else:
            self.show_login_screen()

    def get_logged_in_user(self):
        try:
            if os.path.exists(self.session_path):
                with open(self.session_path, "r") as f:
                    session = json.load(f)
                mobile = session.get("mobile")
                if mobile:
                    user = self.db.get_user_by_mobile(mobile)
                    if user:
                        return user
        except Exception:
            pass
        return None

    def show_register_screen(self):
        """Show registration screen for new users"""
        self.clear_main_window()
        self.register_frame = tk.Frame(self.root, bg="#ECF0F1")
        self.register_frame.pack(fill="both", expand=True)
        tk.Label(
            self.register_frame,
            text="Register for Pizza Palace!",
            font=("Arial", 24, "bold"),
            fg="#2C3E50",
            bg="#ECF0F1"
        ).pack(pady=(100, 20))
        form = tk.Frame(self.register_frame, bg="#ECF0F1")
        form.pack()
        tk.Label(form, text="Full Name:", font=("Arial", 12), bg="#ECF0F1").pack(anchor="w", pady=(0, 5))
        name_var = tk.StringVar()
        tk.Entry(form, textvariable=name_var, font=("Arial", 14), width=40).pack(pady=(0, 15))
        tk.Label(form, text="Mobile Number:", font=("Arial", 12), bg="#ECF0F1").pack(anchor="w", pady=(0, 5))
        mobile_var = tk.StringVar()
        tk.Entry(form, textvariable=mobile_var, font=("Arial", 14), width=40).pack(pady=(0, 15))
        tk.Label(form, text="Address:", font=("Arial", 12), bg="#ECF0F1").pack(anchor="w", pady=(0, 5))
        address_var = tk.StringVar()
        tk.Entry(form, textvariable=address_var, font=("Arial", 14), width=40).pack(pady=(0, 15))
        tk.Label(form, text="Password:", font=("Arial", 12), bg="#ECF0F1").pack(anchor="w", pady=(0, 5))
        password_var = tk.StringVar()
        tk.Entry(form, textvariable=password_var, font=("Arial", 14), width=40, show="*").pack(pady=(0, 15))
        def save_profile():
            name = name_var.get().strip()
            mobile = mobile_var.get().strip()
            address = address_var.get().strip()
            password = password_var.get().strip()
            if not name or not mobile or not address or not password:
                messagebox.showerror("Error", "Please fill in all fields!", parent=self.root)
                return
            if not all(char.isalpha() or char.isspace() for char in name):
                messagebox.showerror("Error", "Name can only contain alphabetic characters and spaces!", parent=self.root)
                return
            if not mobile.isdigit() or len(mobile) != 10:
                messagebox.showerror("Error", "Mobile number must be exactly 10 digits!", parent=self.root)
                return
            success, error = self.db.register_user(name, mobile, address, password)
            if not success:
                messagebox.showerror("Error", error or "Registration failed!", parent=self.root)
                return
            with open(self.session_path, "w") as f:
                json.dump({"mobile": mobile}, f)
            messagebox.showinfo("Success", "Registration successful! Please login.", parent=self.root)
            self.register_frame.destroy()
            self.show_login_screen()
        tk.Button(
            form,
            text="Register",
            font=("Arial", 14, "bold"),
            bg="#27AE60",
            fg="white",
            relief="flat",
            padx=25,
            pady=10,
            command=save_profile
        ).pack(pady=(20, 0))
        tk.Button(
            form,
            text="Already have an account? Login",
            font=("Arial", 10, "underline"),
            bg="#ECF0F1",
            fg="#3498DB",
            relief="flat",
            command=lambda: [self.register_frame.destroy(), self.show_login_screen()]
        ).pack(pady=(10, 0))

    def show_login_screen(self):
        """Show login screen for existing users"""
        self.clear_main_window()
        self.login_frame = tk.Frame(self.root, bg="#ECF0F1")
        self.login_frame.pack(fill="both", expand=True)
        tk.Label(
            self.login_frame,
            text="Login to Pizza Palace!",
            font=("Arial", 24, "bold"),
            fg="#2C3E50",
            bg="#ECF0F1"
        ).pack(pady=(100, 20))
        form = tk.Frame(self.login_frame, bg="#ECF0F1")
        form.pack()
        tk.Label(form, text="Mobile Number:", font=("Arial", 12), bg="#ECF0F1").pack(anchor="w", pady=(0, 5))
        mobile_var = tk.StringVar()
        tk.Entry(form, textvariable=mobile_var, font=("Arial", 14), width=40).pack(pady=(0, 15))
        tk.Label(form, text="Password:", font=("Arial", 12), bg="#ECF0F1").pack(anchor="w", pady=(0, 5))
        password_var = tk.StringVar()
        tk.Entry(form, textvariable=password_var, font=("Arial", 14), width=40, show="*").pack(pady=(0, 15))
        def login():
            mobile = mobile_var.get().strip()
            password = password_var.get().strip()
            if not mobile or not password:
                messagebox.showerror("Error", "Please enter both mobile and password!", parent=self.root)
                return
            user = self.db.authenticate_user(mobile, password)
            if not user:
                messagebox.showerror("Error", "Invalid mobile number or password!", parent=self.root)
                return
            with open(self.session_path, "w") as f:
                json.dump({"mobile": mobile}, f)
            self.current_user = user
            self.login_frame.destroy()
            self.init_main_app()
        tk.Button(
            form,
            text="Login",
            font=("Arial", 14, "bold"),
            bg="#27AE60",
            fg="white",
            relief="flat",
            padx=25,
            pady=10,
            command=login
        ).pack(pady=(20, 0))
        tk.Button(
            form,
            text="Don't have an account? Register",
            font=("Arial", 10, "underline"),
            bg="#ECF0F1",
            fg="#3498DB",
            relief="flat",
            command=lambda: [self.login_frame.destroy(), self.show_register_screen()]
        ).pack(pady=(10, 0))

    def clear_main_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def get_current_profile(self):
        # Always return a dict with name, mobile, address (from current_user or current entry fields)
        if self.current_user:
            # user tuple: (user_id, name, mobile, address, password)
            return {
                "name": self.current_user[1],
                "mobile": self.current_user[2],
                "address": self.current_user[3]
            }
        return {
            "name": self.customer_name.get() if hasattr(self, 'customer_name') else "",
            "mobile": self.customer_mobile.get() if hasattr(self, 'customer_mobile') else "",
            "address": self.customer_address.get() if hasattr(self, 'customer_address') else ""
        }

    def init_main_app(self):
        # Set window icon and make it resizable
        self.root.resizable(True, True)
        self.root.minsize(1200, 800)
        # Create main container with modern styling
        self.main_container = tk.Frame(self.root, bg="#2C3E50")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        # Create header
        self.create_header()
        # Create main content area with proper layout
        self.content_frame = tk.Frame(self.main_container, bg="#ECF0F1")
        self.content_frame.pack(fill="both", expand=True, pady=(20, 0))
        # Create left and right panels
        self.left_panel = tk.Frame(self.content_frame, bg="#ECF0F1", width=800)
        self.right_panel = tk.Frame(self.content_frame, bg="#ECF0F1", width=400)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.right_panel.pack(side="right", fill="y", padx=(10, 0))
        # Customer details variables (autofill from profile)
        profile = self.get_current_profile()
        self.customer_name = tk.StringVar(value=profile["name"])
        self.customer_address = tk.StringVar(value=profile["address"])
        self.customer_mobile = tk.StringVar(value=profile["mobile"])
        # View management
        self.current_view = "main"  # main, customer_details, bill
        self.view_frames = {}
        self.customer_details_frame = None
        self.bill_frame = None

        # Pizza data with image paths
        self.pizzas = {
            "Margherita": {
                "price": 180,
                "ingredients": "Fresh tomatoes, mozzarella cheese, basil, olive oil",
                "image": "images/1.jpg",
                "description": "Classic Italian pizza with fresh basil"
            },
            "Paneer Tikka Pizza": {
                "price": 280,
                "ingredients": "Marinated paneer, capsicum, onions, Indian spices",
                "image": "images/2.jpg",
                "description": "Spicy Indian twist with grilled paneer"
            },
            "Tandoori Paneer Pizza": {
                "price": 300,
                "ingredients": "Spicy tandoori sauce, grilled paneer, onion",
                "image": "images/3.jpg",
                "description": "Authentic tandoori flavors on pizza"
            },
            "Cheese N Corn Pizza": {
                "price": 320,
                "ingredients": "Mozzarella cheese, sweet corn kernels, tomato sauce",
                "image": "images/4.jpg",
                "description": "Sweet corn with melted cheese"
            },
             "Spicy Schezwan Pizza": {
                "price": 340,
                "ingredients": "Schezwan sauce, bell peppers, onion, mozzarella",
                "image": "images/5.jpg",
                "description": "Indo-Chinese style spicy delight"
            },
            "7 Cheese Pizza": {
                "price": 380,
                "ingredients": "Mozzarella, Cheddar, Parmesan, Gouda, Feta, Provolone, Blue Cheese",
                "image": "images/6.jpg", 
                "description": "A cheesy indulgence with 7 premium cheese blends"
            }
        }

        self.sizes = {
            "Small": {"multiplier": 1.0, "description": "Perfect for 1 person"},
            "Medium": {"multiplier": 1.5, "description": "Great for 2 people"},
            "Large": {"multiplier": 2.0, "description": "Feeds 3-4 people"}
        }

        self.toppings = {
            "Extra Cheese": {"price": 50, "description": "Double the cheesy goodness"},
            "Mushrooms": {"price": 40, "description": "Fresh button mushrooms"},
            "Onions": {"price": 30, "description": "Crispy caramelized onions"},
            "Capsicum": {"price": 30, "description": "Fresh bell peppers"},
            "Olives": {"price": 40, "description": "Black and green olives"}
        }

        self.drinks = {
            "Coca Cola": {"price": 60, "description": "Classic cola"},
            "Sprite": {"price": 60, "description": "Lemon-lime refreshment"},
            "Fanta": {"price": 60, "description": "Orange flavored soda"},
            "Pepsi": {"price": 60, "description": "Pepsi cola"}
        }

        # Selection variables
        self.selected_pizzas = {}
        self.selected_size = tk.StringVar(value="Medium")
        self.selected_toppings = []
        self.selected_drinks = {}
        self.topping_vars = {}
        self.drink_vars = {}
        self.drink_quantity_vars = {}
        self.pizza_images = {}
        self.quantity_vars = {}

        # Create the main interface
        self.create_pizza_selection()
        self.create_customization_panel()
        self.create_order_summary()

    def create_header(self):
        """Create an attractive header with a Profile button and Settings menu"""
        header_frame = tk.Frame(self.main_container, bg="#E74C3C", height=80)
        header_frame.pack(fill="x", pady=(5, 5))
        header_frame.pack_propagate(False)
        # Title with pizza emoji
        title_label = tk.Label(
            header_frame,
            text="🍕 Pizza Palace 🍕",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#E74C3C"
        )
        title_label.pack(side="left", padx=20, pady=20)
        # Settings button with menu
        settings_btn = tk.Menubutton(
            header_frame,
            text="⚙️ Settings",
            font=("Arial", 11, "bold"),
            bg="#2C3E50",
            fg="white",
            relief="flat",
            padx=15,
            pady=5
        )
        settings_menu = tk.Menu(settings_btn, tearoff=0)
        settings_menu.add_command(label="👤 Profile", command=self.show_profile_page)
        settings_menu.add_command(label="🔎 Check My Order Status", command=self.show_my_orders_status)
        settings_menu.add_separator()
        settings_menu.add_command(label="🚪 Logout", command=self.logout)
        settings_btn.config(menu=settings_menu)
        settings_btn.pack(side="right", padx=(0, 20), pady=20)
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Delicious Pizzas Delivered to Your Doorstep",
            font=("Arial", 12),
            fg="white",
            bg="#E74C3C"
        )
        subtitle_label.pack(side="right", padx=20, pady=20)

    def create_pizza_selection(self):
        """Create the pizza selection area in the left panel"""
        # Main pizza selection frame
        pizza_frame = tk.LabelFrame(
            self.left_panel,
            text="🍕 Choose Your Pizza",
            font=("Arial", 14, "bold"),
            bg="#ECF0F1",
            fg="#2C3E50",
            relief="raised",
            bd=2
        )
        pizza_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create scrollable canvas for pizzas (set a fixed height)
        canvas = tk.Canvas(pizza_frame, bg="#ECF0F1", highlightthickness=0, height=500)
        scrollbar = ttk.Scrollbar(pizza_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ECF0F1")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create pizza cards in a grid layout
        for i, (pizza_name, pizza_data) in enumerate(self.pizzas.items()):
            row = i // 2
            col = i % 2
            
            # Create pizza card
            card_frame = tk.Frame(
                scrollable_frame,
                bg="white",
                relief="raised",
                bd=2,
                padx=15,
                pady=15
            )
            card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Load and display pizza image
            image = self.load_pizza_image(pizza_name)
            if image:
                self.pizza_images[pizza_name] = image
                image_label = tk.Label(card_frame, image=image, bg="white")
                image_label.pack(pady=(0, 10))

            # Pizza name and price
            name_frame = tk.Frame(card_frame, bg="white")
            name_frame.pack(fill="x", pady=(0, 10))
            
            tk.Label(
                name_frame,
                text=pizza_name,
                font=("Arial", 12, "bold"),
                fg="#2C3E50",
                bg="white"
            ).pack(side="left")
            
            tk.Label(
                name_frame,
                text=f"₹{pizza_data['price']}",
                font=("Arial", 12, "bold"),
                fg="#E74C3C",
                bg="white"
            ).pack(side="right")

            # Description
            tk.Label(
                card_frame,
                text=pizza_data['description'],
                font=("Arial", 9),
                fg="#7F8C8D",
                bg="white",
                wraplength=200,
                justify="center"
            ).pack(pady=(0, 10))

            # Ingredients
            tk.Label(
                card_frame,
                text="Ingredients:",
                font=("Arial", 9, "bold"),
                fg="#2C3E50",
                bg="white"
            ).pack(anchor="w")
            
            tk.Label(
                card_frame,
                text=pizza_data['ingredients'],
                font=("Arial", 8),
                fg="#7F8C8D",
                bg="white",
                wraplength=200,
                justify="left"
            ).pack(anchor="w", pady=(0, 10))

            # Quantity selector
            quantity_frame = tk.Frame(card_frame, bg="white")
            quantity_frame.pack(fill="x", pady=(0, 10))
            
            tk.Label(
                quantity_frame,
                text="Quantity:",
                font=("Arial", 9, "bold"),
                fg="#2C3E50",
                bg="white"
            ).pack(side="left")
            
            quantity_var = tk.IntVar(value=0)
            self.quantity_vars[pizza_name] = quantity_var
            
            quantity_spinbox = ttk.Spinbox(
                quantity_frame,
                from_=0,
                to=10,
                width=5,
                textvariable=quantity_var,
                command=lambda p=pizza_name: self.update_pizza_quantity(p)
            )
            quantity_spinbox.pack(side="right")

            # Select button
            select_btn = tk.Button(
                card_frame,
                text="Add to Order",
                font=("Arial", 10, "bold"),
                bg="#27AE60",
                fg="white",
                relief="flat",
                padx=20,
                pady=5,
                command=lambda p=pizza_name: self.select_pizza(p)
            )
            select_btn.pack(pady=(10, 0))

        # Configure grid weights
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Unbind when leaving the canvas
        def _on_leave(event):
            canvas.unbind_all("<MouseWheel>")
        def _on_enter(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)

    def create_customization_panel(self):
        """Create the customization panel in the right panel"""
        # Customization frame
        custom_frame = tk.LabelFrame(
            self.right_panel,
            text="⚙️ Customize Your Order",
            font=("Arial", 12, "bold"),
            bg="#ECF0F1",
            fg="#2C3E50",
            relief="raised",
            bd=2
        )
        custom_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Create scrollable canvas for customization options
        canvas = tk.Canvas(custom_frame, bg="#ECF0F1", highlightthickness=0, height=300)
        scrollbar = ttk.Scrollbar(custom_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ECF0F1")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Size selection
        size_frame = tk.LabelFrame(
            scrollable_frame,
            text="📏 Choose Size",
            font=("Arial", 10, "bold"),
            bg="#ECF0F1",
            fg="#2C3E50"
        )
        size_frame.pack(fill="x", padx=10, pady=5)

        for size, data in self.sizes.items():
            size_btn = tk.Radiobutton(
                size_frame,
                text=f"{size} - {data['description']}",
                variable=self.selected_size,
                value=size,
                font=("Arial", 9),
                bg="#ECF0F1",
                fg="#2C3E50",
                command=self.update_price_display
            )
            size_btn.pack(anchor="w", padx=10, pady=2)

        # Toppings selection
        toppings_frame = tk.LabelFrame(
            scrollable_frame,
            text="🥬 Add Toppings",
            font=("Arial", 10, "bold"),
            bg="#ECF0F1",
            fg="#2C3E50"
        )
        toppings_frame.pack(fill="x", padx=10, pady=5)

        for topping, data in self.toppings.items():
            var = tk.BooleanVar()
            self.topping_vars[topping] = var
            
            topping_btn = tk.Checkbutton(
                toppings_frame,
                text=f"{topping} (₹{data['price']}) - {data['description']}",
                variable=var,
                font=("Arial", 8),
                bg="#ECF0F1",
                fg="#2C3E50",
                command=lambda t=topping, v=var: self.update_toppings(t, v)
            )
            topping_btn.pack(anchor="w", padx=10, pady=1)

        # Drinks selection
        drinks_frame = tk.LabelFrame(
            scrollable_frame,
            text="🥤 Select Drinks",
            font=("Arial", 10, "bold"),
            bg="#ECF0F1",
            fg="#2C3E50"
        )
        drinks_frame.pack(fill="x", padx=10, pady=5)

        for drink, data in self.drinks.items():
            drink_item = tk.Frame(drinks_frame, bg="#ECF0F1")
            drink_item.pack(fill="x", padx=10, pady=2)
            
            var = tk.BooleanVar()
            self.drink_vars[drink] = var
            
            tk.Checkbutton(
                drink_item,
                text=f"{drink} (₹{data['price']})",
                variable=var,
                font=("Arial", 8),
                bg="#ECF0F1",
                fg="#2C3E50",
                command=lambda d=drink, v=var: self.update_drinks(d, v)
            ).pack(side="left")
            
            quantity_var = tk.IntVar(value=0)
            self.drink_quantity_vars[drink] = quantity_var
            
            tk.Label(
                drink_item,
                text="Qty:",
                font=("Arial", 8),
                bg="#ECF0F1",
                fg="#2C3E50"
            ).pack(side="left", padx=(10, 0))
            
            ttk.Spinbox(
                drink_item,
                from_=0,
                to=10,
                width=3,
                textvariable=quantity_var,
                command=lambda d=drink: self.update_drink_quantity(d)
            ).pack(side="left", padx=5)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Bind mousewheel to scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Unbind when leaving the canvas
        def _on_leave(event):
            canvas.unbind_all("<MouseWheel>")
        
        def _on_enter(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)

    def create_order_summary(self):
        """Create the order summary and checkout area"""
        # Order summary frame
        summary_frame = tk.LabelFrame(
            self.right_panel,
            text="📋 Order Summary",
            font=("Arial", 12, "bold"),
            bg="#ECF0F1",
            fg="#2C3E50",
            relief="raised",
            bd=2
        )
        summary_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Order details text area
        self.order_text = tk.Text(
            summary_frame,
            height=8,
            width=40,
            font=("Arial", 9),
            bg="white",
            fg="#2C3E50",
            relief="sunken",
            bd=1
        )
        self.order_text.pack(fill="x", padx=10, pady=5)

        # Total amount display
        self.total_label = tk.Label(
            summary_frame,
            text="Total Amount: ₹0",
            font=("Arial", 14, "bold"),
            fg="#000000",
            bg="#ECF0F1"
        )
        self.total_label.pack(pady=10)

        # Action buttons
        buttons_frame = tk.Frame(summary_frame, bg="#ECF0F1")
        buttons_frame.pack(fill="x", padx=10, pady=10)

        # Clear order button
        clear_btn = tk.Button(
            buttons_frame,
            text="🗑️ Clear Order",
            font=("Arial", 10, "bold"),
            bg="#E74C3C",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=self.clear_order
        )
        clear_btn.pack(side="left", padx=(0, 5))

        # Proceed to checkout button
        checkout_btn = tk.Button(
            buttons_frame,
            text="🛒 Proceed to Checkout",
            font=("Arial", 10, "bold"),
            bg="#27AE60",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=self.show_customer_details
        )
        checkout_btn.pack(side="right", padx=(5, 0))

    def load_pizza_image(self, pizza_name):
        """Load and resize pizza image"""
        try:
            image_path = self.pizzas[pizza_name]["image"]
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            return None
        except Exception as e:
            print(f"Error loading image for {pizza_name}: {str(e)}")
            return None

    def update_pizza_quantity(self, pizza_name):
        """Update the quantity of selected pizza"""
        quantity = self.quantity_vars[pizza_name].get()
        if quantity > 0:
            self.selected_pizzas[pizza_name] = quantity
        else:
            self.selected_pizzas.pop(pizza_name, None)
        self.update_order_summary()

    def select_pizza(self, pizza_name):
        """Handle pizza selection"""
        if pizza_name not in self.selected_pizzas:
            self.selected_pizzas[pizza_name] = 1
            self.quantity_vars[pizza_name].set(1)
        self.update_order_summary()

    def update_toppings(self, topping, var):
        """Update toppings selection"""
        if var.get():
            if topping not in self.selected_toppings:
                self.selected_toppings.append(topping)
        else:
            if topping in self.selected_toppings:
                self.selected_toppings.remove(topping)
        self.update_order_summary()

    def update_drinks(self, drink, var):
        """Update drink selection"""
        if var.get():
            if drink not in self.selected_drinks:
                self.selected_drinks[drink] = 1
                self.drink_quantity_vars[drink].set(1)
        else:
            if drink in self.selected_drinks:
                del self.selected_drinks[drink]
                self.drink_quantity_vars[drink].set(0)
        self.update_order_summary()

    def update_drink_quantity(self, drink):
        """Update the quantity of selected drink"""
        quantity = self.drink_quantity_vars[drink].get()
        if quantity > 0:
            self.selected_drinks[drink] = quantity
        else:
            self.selected_drinks.pop(drink, None)
        self.update_order_summary()

    def update_order_summary(self):
        """Update the order summary display"""
        self.order_text.delete(1.0, tk.END)
        
        if not self.selected_pizzas:
            self.order_text.insert(tk.END, "No items selected yet.\n")
            self.total_label.config(text="Total Amount: ₹0")
            return

        total = 0
        summary_text = "=== Your Order ===\n\n"

        # Add pizzas
        for pizza_name, quantity in self.selected_pizzas.items():
            base_price = self.pizzas[pizza_name]["price"]
            size_multiplier = self.sizes[self.selected_size.get()]["multiplier"]
            pizza_cost = round(base_price * size_multiplier * quantity)
            total += pizza_cost
            
            summary_text += f"🍕 {pizza_name} ({self.selected_size.get()}) x{quantity}\n"
            summary_text += f"   ₹{pizza_cost}\n\n"

        # Add toppings
        if self.selected_toppings:
            summary_text += "🥬 Toppings:\n"
            for topping in self.selected_toppings:
                topping_cost = self.toppings[topping]["price"]
                total += topping_cost
                summary_text += f"   • {topping} - ₹{topping_cost}\n"
            summary_text += "\n"

        # Add drinks
        if self.selected_drinks:
            summary_text += "🥤 Drinks:\n"
            for drink, quantity in self.selected_drinks.items():
                drink_cost = self.drinks[drink]["price"] * quantity
                total += drink_cost
                summary_text += f"   • {drink} x{quantity} - ₹{drink_cost}\n"
            summary_text += "\n"

        summary_text += f"💰 Total: ₹{total}"
        s
        self.order_text.insert(tk.END, summary_text)
        self.total_label.config(text=f"Total Amount: ₹{total}")

    def clear_order(self):
        """Clear the entire order"""
        self.selected_pizzas = {}
        self.selected_toppings = [] 
        self.selected_drinks = {}
        
        # Reset all quantity variables
        for pizza_name in self.quantity_vars:
            self.quantity_vars[pizza_name].set(0)
        
        for drink in self.drink_quantity_vars:
            self.drink_quantity_vars[drink].set(0)
        
        # Reset all checkboxes
        for var in self.topping_vars.values():
            var.set(False)
        
        for var in self.drink_vars.values():
            var.set(False)
        
        self.update_order_summary()

    def show_customer_details(self):
        """Show customer details form"""
        if not self.selected_pizzas:
            messagebox.showerror("Error", "Please select at least one pizza!")
            return

        # Switch to customer details view
        self.switch_view("customer_details")

    def place_order(self):
        """Place the order"""
        # Validate customer details
        if not self.customer_name.get() or not self.customer_address.get() or not self.customer_mobile.get():
            messagebox.showerror("Error", "Please fill in all customer details!")
            return

        # Additional validation for mobile number
        mobile = self.customer_mobile.get().strip()
        if not mobile.isdigit() or len(mobile) != 10:
            messagebox.showerror("Error", "Mobile number must be exactly 10 digits!")
            return

        # Additional validation for name (only alphabetic characters and spaces)
        name = self.customer_name.get().strip()
        if not all(char.isalpha() or char.isspace() for char in name):
            messagebox.showerror("Error", "Name can only contain alphabetic characters and spaces!")
            return

        # Calculate total amount
        total = 0
        for pizza_name, quantity in self.selected_pizzas.items():
            base_price = self.pizzas[pizza_name]["price"]
            size_multiplier = self.sizes[self.selected_size.get()]["multiplier"]
            total += round(base_price * size_multiplier * quantity)
        
        for topping in self.selected_toppings:
            total += self.toppings[topping]["price"]
            
        for drink, quantity in self.selected_drinks.items():
            total += self.drinks[drink]["price"] * quantity

        # Save order to database
        try:
            db = Database()
            order_id = db.add_order(
                name,
                self.customer_address.get().strip(),
                mobile,
                total
            )

            # Save order items
            for pizza_name, quantity in self.selected_pizzas.items():
                base_price = self.pizzas[pizza_name]["price"]
                size_multiplier = self.sizes[self.selected_size.get()]["multiplier"]
                price = round(base_price * size_multiplier * quantity)
                db.add_order_item(order_id, "pizza", pizza_name, quantity, price)

            for topping in self.selected_toppings:
                db.add_order_item(order_id, "topping", topping, 1, self.toppings[topping]["price"])

            for drink, quantity in self.selected_drinks.items():
                db.add_order_item(order_id, "drink", drink, quantity, self.drinks[drink]["price"] * quantity)

        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving order: {str(e)}")
            return

        # Show order confirmation
        messagebox.showinfo(
            "🎉 Order Placed Successfully!", 
            f"Thank you for your order!\n\n"
            f"📋 Order ID: {order_id}\n"
            f"💰 Total: ₹{total}\n\n"
            f"🚚 Delivery Details:\n"
            f"👤 Name: {name}\n"
            f"📍 Address: {self.customer_address.get().strip()}\n"
            f"📱 Mobile: {mobile}\n\n"
            f"⏰ Estimated delivery time: 30-45 minutes\n\n"
            f"🍕 Enjoy your delicious pizza!"
        )

        # Switch to bill view
        self.switch_view("bill")

        # Clear the order after showing bill
        self.clear_order()
        self.customer_name.set("")
        self.customer_address.set("")
        self.customer_mobile.set("")

    def generate_bill(self):
        """Generate and display the bill - This method is now deprecated, use show_bill_view instead"""
        # This method is kept for backward compatibility but now redirects to the new system
        self.switch_view("bill")

    def update_price_display(self):
        """Update the price display when size is changed"""
        self.update_order_summary()

    def switch_view(self, view_name):
        """Switch between different views in the main window"""
        self.current_view = view_name
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if view_name == "main":
            # Recreate left and right panels for main order interface
            self.left_panel = tk.Frame(self.content_frame, bg="#ECF0F1", width=800)
            self.right_panel = tk.Frame(self.content_frame, bg="#ECF0F1", width=400)
            
            self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
            self.right_panel.pack(side="right", fill="y", padx=(10, 0))
            
            # Recreate the main interface
            self.create_pizza_selection()
            self.create_customization_panel()
            self.create_order_summary()
            
        elif view_name == "customer_details":
            # Show customer details form
            self.show_customer_details_view()
            
        elif view_name == "bill":
            # Show bill view
            self.show_bill_view()

    def validate_name(self, P):
        """Validate name input - only alphabetic characters and spaces allowed"""
        if P == "":  # Allow empty string for backspace
            return True
        # Allow alphabetic characters and spaces only
        return all(char.isalpha() or char.isspace() for char in P)

    def validate_mobile(self, P):
        """Validate mobile number input - only digits, max 10 characters"""
        if P == "":  # Allow empty string for backspace
            return True
        # Allow only digits and max 10 characters
        return P.isdigit() and len(P) <= 10

    def show_customer_details_view(self):
        """Show customer details form in the main window, editable"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Create customer details frame
        self.customer_details_frame = tk.Frame(self.content_frame, bg="#ECF0F1")
        self.customer_details_frame.pack(fill="both", expand=True, padx=50, pady=50)
        # Title
        tk.Label(
            self.customer_details_frame,
            text="👤 Customer Information",
            font=("Arial", 24, "bold"),
            fg="#2C3E50",
            bg="#ECF0F1"
        ).pack(pady=(75, 10))
        # Form container
        form_frame = tk.Frame(self.customer_details_frame, bg="#ECF0F1")
        form_frame.pack(expand=True)
        # Name field (editable)
        tk.Label(
            form_frame,
            text="Full Name:",
            font=("Arial", 12, "bold"),
            fg="#2C3E50",
            bg="#ECF0F1"
        ).pack(anchor="w", pady=(0, 5))
        name_entry = tk.Entry(
            form_frame,
            textvariable=self.customer_name,
            font=("Arial", 14),
            width=40,
            relief="solid",
            bd=2
        )
        name_entry.pack(fill="x", pady=(0, 20))
        # Address field (editable)
        tk.Label(
            form_frame,
            text="Delivery Address:",
            font=("Arial", 12, "bold"),
            fg="#2C3E50",
            bg="#ECF0F1"
        ).pack(anchor="w", pady=(0, 5))
        address_entry = tk.Entry(
            form_frame,
            textvariable=self.customer_address,
            font=("Arial", 14),
            width=40,
            relief="solid",
            bd=2
        )
        address_entry.pack(fill="x", pady=(0, 20))
        # Mobile field (editable)
        tk.Label(
            form_frame,
            text="Mobile Number:",
            font=("Arial", 12, "bold"),
            fg="#2C3E50",
            bg="#ECF0F1"
        ).pack(anchor="w", pady=(0, 5))
        mobile_entry = tk.Entry(
            form_frame,
            textvariable=self.customer_mobile,
            font=("Arial", 14),
            width=40,
            relief="solid",
            bd=2
        )
        mobile_entry.pack(fill="x", pady=(0, 10))
        # Buttons
        buttons_frame = tk.Frame(form_frame, bg="#ECF0F1")
        buttons_frame.pack(fill="x")
        tk.Button(
            buttons_frame,
            text="❌ Back to Order",
            font=("Arial", 12, "bold"),
            bg="#E74C3C",
            fg="white",
            relief="flat",
            padx=25,
            pady=10,
            command=self.back_to_main_view
        ).pack(side="left", padx=(0, 15))
        tk.Button(
            buttons_frame,
            text="✅ Place Order",
            font=("Arial", 12, "bold"),
            bg="#27AE60",
            fg="white",
            relief="flat",
            padx=25,
            pady=10,
            command=self.place_order
        ).pack(side="right")

    def show_bill_view(self):
        """Show bill in the main window"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create bill frame
        self.bill_frame = tk.Frame(self.content_frame, bg="#ECF0F1")
        self.bill_frame.pack(fill="both", expand=True, padx=50, pady=10)
        
        # Title
        tk.Label(
            self.bill_frame,
            text="🍕 Your Bill",
            font=("Arial", 24, "bold"),
            fg="#2C3E50",
            bg="#ECF0F1"
        ).pack(pady=(0, 20))
        
        # Bill text area with scrollbar
        bill_text_frame = tk.Frame(self.bill_frame, bg="#ECF0F1")
        bill_text_frame.pack(fill="both", expand=True, pady=(0, 20))
        bill_text_area = tk.Text(
            bill_text_frame,
            font=("Courier", 12),
            bg="white",
            fg="#2C3E50",
            relief="sunken",
            bd=2,
            padx=30,
            pady=30,
            wrap=tk.WORD
        )
        bill_text_area.pack(side="left", fill="both", expand=True)
        bill_scrollbar = ttk.Scrollbar(bill_text_frame, orient="vertical", command=bill_text_area.yview)
        bill_scrollbar.pack(side="right", fill="y")
        bill_text_area.config(yscrollcommand=bill_scrollbar.set)
        # Generate bill content
        bill_text = self.generate_bill_text()
        bill_text_area.insert(tk.END, bill_text)
        bill_text_area.config(state="disabled")
        
        # Back button
        tk.Button(
            self.bill_frame,
            text="🏠 Back to Main Menu",
            font=("Arial", 12, "bold"),
            bg="#3498DB",
            fg="white",
            relief="flat",
            padx=25,
            pady=10,
            command=self.back_to_main_view
        ).pack()

    def back_to_main_view(self):
        """Return to the main order view"""
        self.switch_view("main")

    def generate_bill_text(self):
        """Generate bill text content"""
        if not self.selected_pizzas:
            return "No items in order."

        total = 0
        bill_text = "🍕 === PIZZA PALACE BILL === 🍕\n\n"
        
        # Add pizzas to bill
        for pizza_name, quantity in self.selected_pizzas.items():
            base_price = self.pizzas[pizza_name]["price"]
            size_multiplier = self.sizes[self.selected_size.get()]["multiplier"]
            pizza_cost = round(base_price * size_multiplier * quantity)
            total += pizza_cost
            
            bill_text += f"🍕 {pizza_name} ({self.selected_size.get()}) x{quantity}\n"
            bill_text += f"   Base Price: ₹{base_price}\n"
            bill_text += f"   Size Multiplier: {size_multiplier}x\n"
            bill_text += f"   Subtotal: ₹{pizza_cost}\n\n"

        if self.selected_toppings:
            bill_text += "🥬 Toppings:\n"
            for topping in self.selected_toppings:
                topping_cost = self.toppings[topping]["price"]
                total += topping_cost
                bill_text += f"   • {topping}: ₹{topping_cost}\n"
            bill_text += "\n"

        if self.selected_drinks:
            bill_text += "🥤 Drinks:\n"
            for drink, quantity in self.selected_drinks.items():
                drink_cost = self.drinks[drink]["price"] * quantity
                total += drink_cost
                bill_text += f"   • {drink} x{quantity}: ₹{drink_cost}\n"
            bill_text += "\n"

        bill_text += f"💰 Total Amount: ₹{total}\n\n"
        bill_text += "🎉 Thank you for choosing Pizza Palace! 🎉"
        
        return bill_text

    def show_my_orders_status(self):
        """Show all orders for the logged-in user in a new window, with full order history details"""
        db = Database()
        try:
            orders = db.get_orders_by_mobile(self.customer_mobile.get())
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch your orders.\n{str(e)}", parent=self.root)
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("My Orders History")
        dialog.geometry("700x500")
        dialog.configure(bg="#ECF0F1")
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text=f"Order History for {self.customer_name.get()} ({self.customer_mobile.get()})", font=("Arial", 14, "bold"), bg="#ECF0F1").pack(pady=(10, 10))
        if not orders:
            tk.Label(dialog, text="No orders found.", font=("Arial", 12), bg="#ECF0F1").pack(pady=20)
        else:
            frame = tk.Frame(dialog, bg="#ECF0F1")
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            text = tk.Text(frame, font=("Arial", 11), bg="white", fg="#2C3E50", relief="sunken", bd=1)
            text.pack(fill="both", expand=True)
            for order in orders:
                order_id, name, address, mobile, order_date, status, total = order
                text.insert(tk.END, f"Order ID: {order_id}\nDate: {order_date}\nName: {name}\nAddress: {address}\nMobile: {mobile}\nStatus: {status.capitalize()}\nTotal: ₹{total}\n")
                # Fetch and show order items
                try:
                    _, items = db.get_order_details(order_id)
                    text.insert(tk.END, "Items:\n")
                    for item in items:
                        item_type, item_name, quantity, price = item[2], item[3], item[4], item[5]
                        text.insert(tk.END, f"  - {item_name} ({item_type}) x{quantity}: ₹{price}\n")
                except Exception:
                    text.insert(tk.END, "  (Could not fetch items)\n")
                text.insert(tk.END, f"{'-'*50}\n")
            text.config(state="disabled")
        tk.Button(
            dialog,
            text="Close",
            font=("Arial", 10),
            bg="#E74C3C",
            fg="white",
            relief="flat",
            padx=10,
            pady=4,
            command=dialog.destroy
        ).pack(pady=(10, 10))

    def show_profile_page(self):
        """Show a profile/settings page to update user info"""
        profile_win = tk.Toplevel(self.root)
        profile_win.title("Edit Profile")
        profile_win.geometry("400x350")
        profile_win.configure(bg="#ECF0F1")
        profile_win.transient(self.root)
        profile_win.grab_set()
        tk.Label(profile_win, text="Edit Your Profile", font=("Arial", 18, "bold"), bg="#ECF0F1").pack(pady=(20, 10))
        form = tk.Frame(profile_win, bg="#ECF0F1")
        form.pack(pady=10)
        profile = self.get_current_profile()
        tk.Label(form, text="Full Name:", font=("Arial", 12), bg="#ECF0F1").pack(anchor="w", pady=(0, 5))
        name_var = tk.StringVar(value=profile["name"])
        tk.Entry(form, textvariable=name_var, font=("Arial", 14), width=30).pack(pady=(0, 15))
        tk.Label(form, text="Mobile Number:", font=("Arial", 12), bg="#ECF0F1").pack(anchor="w", pady=(0, 5))
        mobile_var = tk.StringVar(value=profile["mobile"])
        tk.Entry(form, textvariable=mobile_var, font=("Arial", 14), width=30).pack(pady=(0, 15))
        tk.Label(form, text="Address:", font=("Arial", 12), bg="#ECF0F1").pack(anchor="w", pady=(0, 5))
        address_var = tk.StringVar(value=profile["address"])
        tk.Entry(form, textvariable=address_var, font=("Arial", 14), width=30).pack(pady=(0, 15))
        def save_profile():
            name = name_var.get().strip()
            mobile = mobile_var.get().strip()
            address = address_var.get().strip()
            if not name or not mobile or not address:
                messagebox.showerror("Error", "Please fill in all fields!", parent=profile_win)
                return
            if not all(char.isalpha() or char.isspace() for char in name):
                messagebox.showerror("Error", "Name can only contain alphabetic characters and spaces!", parent=profile_win)
                return
            if not mobile.isdigit() or len(mobile) != 10:
                messagebox.showerror("Error", "Mobile number must be exactly 10 digits!", parent=profile_win)
                return
            # Update in database
            old_mobile = self.current_user[2] if self.current_user else None
            try:
                self.db.update_user_profile(old_mobile, name, address)
                # If mobile number changed, update it in the users table (not supported by update_user_profile)
                if mobile != old_mobile:
                    # Check if new mobile already exists
                    if self.db.get_user_by_mobile(mobile):
                        messagebox.showerror("Error", "Mobile number already registered!", parent=profile_win)
                        return
                    # Update mobile number directly
                    cursor = self.db.conn.cursor()
                    cursor.execute("UPDATE users SET mobile = ? WHERE mobile = ?", (mobile, old_mobile))
                    self.db.conn.commit()
                # Update session
                with open(self.session_path, "w") as f:
                    json.dump({"mobile": mobile}, f)
                # Update current_user
                self.current_user = self.db.get_user_by_mobile(mobile)
                self.customer_name.set(name)
                self.customer_mobile.set(mobile)
                self.customer_address.set(address)
                messagebox.showinfo("Success", "Profile updated successfully!", parent=profile_win)
                profile_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update profile: {str(e)}", parent=profile_win)
        tk.Button(
            form,
            text="Save",
            font=("Arial", 13, "bold"),
            bg="#27AE60",
            fg="white",
            relief="flat",
            padx=20,
            pady=8,
            command=save_profile
        ).pack(pady=(20, 0))

    def logout(self):
        """Logout the user, clear session, and show login screen"""
        try:
            if os.path.exists(self.session_path):
                os.remove(self.session_path)
        except Exception:
            pass
        self.current_user = None
        self.clear_main_window()
        self.show_login_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = PizzaDeliverySystem(root)
    root.mainloop()