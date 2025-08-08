import tkinter as tk 
from tkinter import ttk, messagebox
from database import Database
from datetime import datetime

class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Pizza Delivery Admin Panel")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        # Configure style
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=30, font=('Arial', 10))
        self.style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        self.style.configure("TLabelframe.Label", font=('Arial', 12, 'bold'))
        
        # Configure custom button styles
        self.style.configure("Accept.TButton", 
                           font=('Arial', 12, 'bold'),
                           padding=10,
                           background='#4CAF50',
                           foreground  ='white')
        
        self.style.configure("Reject.TButton", 
                           font=('Arial', 12, 'bold'),
                           padding=10,
                           background='#f44336',
                           foreground='white')
        
        self.style.configure("Complete.TButton", 
                           font=('Arial', 12, 'bold'),
                           padding=10,
                           background='#2196F3',
                           foreground='white')

        self.db = Database()
        self.create_widgets()
        self.load_orders()

    def create_widgets(self):
        # Create main container with padding
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill="both", expand=True)

        # Create tabs with custom style
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # Create all tabs
        self.pending_tab = ttk.Frame(self.tab_control)
        self.accepted_tab = ttk.Frame(self.tab_control)
        self.rejected_tab = ttk.Frame(self.tab_control)
        self.completed_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.pending_tab, text="Pending Orders")
        self.tab_control.add(self.accepted_tab, text="Accepted Orders")
        self.tab_control.add(self.rejected_tab, text="Rejected Orders")

        self.tab_control.add(self.completed_tab, text="Completed Orders")
        
        self.tab_control.pack(fill="both", expand=True)

        # Create order list frames for each tab
        self.create_order_list(self.pending_tab, "pending")
        self.create_order_list(self.accepted_tab, "accepted")
        self.create_order_list(self.rejected_tab, "rejected")
        self.create_order_list(self.completed_tab, "completed") 

        # Create order details frame with improved styling
        self.details_frame = ttk.LabelFrame(self.main_frame, text="Order Details", padding="15")
        self.details_frame.pack(fill="both", expand=True, pady=15)

        # Create a grid layout for details
        details_grid = ttk.Frame(self.details_frame)
        details_grid.pack(fill="both", expand=True, pady=10)

        # Left side - Order details   
        left_frame = ttk.Frame(details_grid)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.details_text = tk.Text(left_frame, height=10, width=60, font=('Arial', 11))
        self.details_text.pack(fill="both", expand=True)

        # Right side - Action buttons
        right_frame = ttk.Frame(details_grid)
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        # Status and amount display
        self.status_frame = ttk.LabelFrame(right_frame, text="Order Status", padding="10")
        self.status_frame.pack(fill="x", pady=(0, 10))

        self.status_label = ttk.Label(self.status_frame, text="Status: ", font=('Arial', 11))
        self.status_label.pack(anchor="w", pady=5)

        self.amount_label = ttk.Label(self.status_frame, text="Amount: ", font=('Arial', 11))
        self.amount_label.pack(anchor="w", pady=5)

        # Action buttons with improved styling
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill="x", pady=10)

        # Accept Order Button
        self.accept_button = tk.Button(
            button_frame,
            text="✓ Accept Order",
            command=lambda: self.update_order_status("accepted"),
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            width=25,
            height=2,
            relief=tk.RAISED,
            borderwidth=3
        )
        self.accept_button.pack(fill="x", pady=(0, 10))

        # Reject Order Button
        self.reject_button = tk.Button(
            button_frame,
            text="✕ Reject Order",
            command=lambda: self.update_order_status("rejected"),
            font=('Arial', 12, 'bold'),
            bg='#f44336',
            fg='white',
            width=25,
            height=2,
            relief=tk.RAISED,
            borderwidth=3
        )
        self.reject_button.pack(fill="x", pady=(0, 10))

        # Complete Order Button
        self.complete_button = tk.Button(
            button_frame,
            text="✓ Mark as Completed",
            command=lambda: self.update_order_status("completed"),
            font=('Arial', 12, 'bold'),
            bg='#2196F3',
            fg='white',
            width=25,
            height=2,
            relief=tk.RAISED,
            borderwidth=3
        )
        self.complete_button.pack(fill="x", pady=(0, 10))

        # Initially disable buttons
        self.accept_button.configure(state="disabled")
        self.reject_button.configure(state="disabled")
        self.complete_button.configure(state="disabled")

    def create_order_list(self, parent, status):
        # Create frame for the list
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create Treeview with improved columns
        if status == "pending":
            columns = ("Order ID", "Customer", "Date", "Amount", "Status", "Actions")
        elif status == "accepted":
            columns = ("Order ID", "Customer", "Date", "Amount", "Status", "Actions")
        else:
            columns = ("Order ID", "Customer", "Date", "Amount", "Status")
        
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

        # Set column headings and widths
        tree.heading("Order ID", text="Order ID")
        tree.heading("Customer", text="Customer")
        tree.heading("Date", text="Date")
        tree.heading("Amount", text="Amount")
        tree.heading("Status", text="Status")
        
        if status in ["pending", "accepted"]:
            tree.heading("Actions", text="Actions")

        tree.column("Order ID", width=100)
        tree.column("Customer", width=200)
        tree.column("Date", width=150)
        tree.column("Amount", width=150)
        tree.column("Status", width=100)
        
        if status in ["pending", "accepted"]:
            tree.column("Actions", width=200)

        # Configure tags for styling
        if status == "pending":
            tree.tag_configure("action_buttons", background="#e3f2fd", foreground="#1565c0")
        elif status == "accepted":
            tree.tag_configure("complete_button", background="#e8f5e8", foreground="#2e7d32")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind selection event
        tree.bind("<<TreeviewSelect>>", lambda e: self.show_order_details(e, tree))

        # Store tree reference
        setattr(self, f"{status}_tree", tree)

    def load_orders(self):
        # Clear existing items
        for status in ["pending", "accepted", "rejected", "completed"]:
            tree = getattr(self, f"{status}_tree")
            for item in tree.get_children():
                tree.delete(item)

        # Load orders from database
        pending_orders = self.db.get_orders_by_status("pending")
        accepted_orders = self.db.get_orders_by_status("accepted")
        rejected_orders = self.db.get_orders_by_status("rejected")
        completed_orders = self.db.get_orders_by_status("completed")

        # Populate trees
        self.populate_tree(self.pending_tree, pending_orders)
        self.populate_tree(self.accepted_tree, accepted_orders)
        self.populate_tree(self.rejected_tree, rejected_orders)
        self.populate_tree(self.completed_tree, completed_orders)

    def populate_tree(self, tree, orders):
        for order in orders:
            order_id, customer_name, _, _, order_date, status, total_amount = order
            
            if status == "pending":
                # For pending orders, include accept and reject buttons
                item = tree.insert("", "end", values=(
                    order_id,
                    customer_name,
                    order_date,
                    f"₹{total_amount:.2f}",
                    status,
                    "Click to Accept/Reject"
                ), tags=("action_buttons",))
                
                # Store order_id in the item for later reference
                tree.set(item, "Order ID", order_id)
            elif status == "accepted":
                # For accepted orders, include complete button
                item = tree.insert("", "end", values=(
                    order_id,
                    customer_name,
                    order_date,
                    f"₹{total_amount:.2f}",
                    status,
                    "Click to Complete"
                ), tags=("complete_button",))
                
                # Store order_id in the item for later reference
                tree.set(item, "Order ID", order_id)
            else:
                # For other statuses, no actions column
                tree.insert("", "end", values=(
                    order_id,
                    customer_name,
                    order_date,
                    f"₹{total_amount:.2f}",
                    status
                ))
        
        # Bind click events for trees with actions
        if tree == self.pending_tree:
            tree.bind("<Button-1>", self.handle_pending_tree_click)
        elif tree == self.accepted_tree:
            tree.bind("<Button-1>", self.handle_accepted_tree_click)

    def handle_pending_tree_click(self, event):
        """Handle clicks in the pending orders tree"""
        region = self.pending_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.pending_tree.identify_column(event.x)
            if column == "#6":  # Actions column
                item = self.pending_tree.identify_row(event.y)
                if item:
                    order_id = self.pending_tree.item(item)["values"][0]
                    # Show a simple confirmation dialog for action selection
                    self.show_action_dialog(order_id)

    def show_action_dialog(self, order_id):
        """Show a dialog to select Accept or Reject action"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Action")
        dialog.geometry("300x150")
        dialog.configure(bg="#f0f0f0")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Create frame
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill="both", expand=True)
        
        # Label
        label = ttk.Label(frame, text=f"Select action for Order {order_id}:", font=('Arial', 12))
        label.pack(pady=(0, 20))
        
        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x")
        
        # Accept button
        accept_btn = tk.Button(
            button_frame,
            text="Accept Order",
            command=lambda: [self.accept_order_from_list(order_id), dialog.destroy()],
            font=('Arial', 11, 'bold'),
            bg='#4CAF50',
            fg='white',
            width=15,
            height=2,
            relief=tk.RAISED,
            borderwidth=2
        )
        accept_btn.pack(side="left", padx=(0, 10))
        
        # Reject button
        reject_btn = tk.Button(
            button_frame,
            text="Reject Order",
            command=lambda: [self.reject_order_from_list(order_id), dialog.destroy()],
            font=('Arial', 11, 'bold'),
            bg='#f44336',
            fg='white',
            width=15,
            height=2,
            relief=tk.RAISED,
            borderwidth=2
        )
        reject_btn.pack(side="right", padx=(10, 0))
        
        # Cancel button
        cancel_btn = tk.Button(
            frame,
            text="Cancel",
            command=dialog.destroy,
            font=('Arial', 10),
            bg='#9e9e9e',
            fg='white',
            width=10,
            relief=tk.RAISED,
            borderwidth=2
        )
        cancel_btn.pack(pady=(20, 0))
        
        # Focus on dialog
        dialog.focus_set()
        dialog.wait_window()

    def accept_order_from_list(self, order_id):
        """Accept order directly from the pending orders list"""
        # Update status in database
        self.db.update_order_status(order_id, "accepted")
        
        # Reload orders
        self.load_orders()
        
        # Clear details if this was the selected order
        if hasattr(self, 'current_order_id') and self.current_order_id == order_id:
            self.details_text.delete(1.0, tk.END)
            self.accept_button.configure(state="disabled")
            self.reject_button.configure(state="disabled")
            self.complete_button.configure(state="disabled")
        
        # Show confirmation
        messagebox.showinfo("Success", f"Order {order_id} has been accepted!")

    def reject_order_from_list(self, order_id):
        """Reject order directly from the pending orders list"""
        # Update status in database
        self.db.update_order_status(order_id, "rejected")
        
        # Reload orders
        self.load_orders()
        
        # Clear details if this was the selected order
        if hasattr(self, 'current_order_id') and self.current_order_id == order_id:
            self.details_text.delete(1.0, tk.END)
            self.accept_button.configure(state="disabled")
            self.reject_button.configure(state="disabled")
            self.complete_button.configure(state="disabled")
        
        # Show confirmation
        messagebox.showinfo("Success", f"Order {order_id} has been rejected!")

    def show_order_details(self, event, tree):
        # Get selected item
        selection = tree.selection()
        if not selection:
            return

        # Get order ID from selected item
        order_id = tree.item(selection[0])["values"][0]

        # Get order details from database
        order, items = self.db.get_order_details(order_id)

        # Clear previous details
        self.details_text.delete(1.0, tk.END)

        # Display order details with improved formatting
        self.details_text.insert(tk.END, f"Order ID: {order[0]}\n", "bold")
        self.details_text.insert(tk.END, f"Customer: {order[1]}\n")
        self.details_text.insert(tk.END, f"Address: {order[2]}\n")
        self.details_text.insert(tk.END, f"Mobile: {order[3]}\n")
        self.details_text.insert(tk.END, f"Date: {order[4]}\n")
        self.details_text.insert(tk.END, f"Status: {order[5]}\n")
        self.details_text.insert(tk.END, f"Total Amount: ₹{order[6]:.2f}\n\n")

        self.details_text.insert(tk.END, "Order Items:\n", "bold")
        for item in items:
            self.details_text.insert(tk.END, 
                f"- {item[3]} ({item[2]}) x {item[4]}: ₹{item[5]:.2f}\n")

        # Update status and amount labels
        self.status_label.configure(text=f"Status: {order[5]}")
        self.amount_label.configure(text=f"Amount: ₹{order[6]:.2f}")

        # Enable/disable buttons based on order status
        status = order[5]
        self.accept_button.configure(state="normal" if status == "pending" else "disabled")
        self.reject_button.configure(state="normal" if status == "pending" else "disabled")
        self.complete_button.configure(state="normal" if status == "accepted" else "disabled")

        # Store current order ID
        self.current_order_id = order_id

    def update_order_status(self, new_status):
        if not hasattr(self, 'current_order_id'):
            return

        # Update status in database
        self.db.update_order_status(self.current_order_id, new_status)

        # Reload orders
        self.load_orders()

        # Clear details
        self.details_text.delete(1.0, tk.END)
        self.accept_button.configure(state="disabled")
        self.reject_button.configure(state="disabled")
        self.complete_button.configure(state="disabled")

        # Show confirmation
        messagebox.showinfo("Success", f"Order status updated to {new_status}")

    def handle_accepted_tree_click(self, event):
        """Handle clicks in the accepted orders tree"""
        region = self.accepted_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.accepted_tree.identify_column(event.x) 
            if column == "#6":  # Actions column
                item = self.accepted_tree.identify_row(event.y)
                if item:
                    order_id = self.accepted_tree.item(item)["values"][0]
                    # Show confirmation dialog for complete action
                    self.show_complete_dialog(order_id)

    def show_complete_dialog(self, order_id):
        """Show a dialog to confirm completing the order"""
        result = messagebox.askyesno(
            "Complete Order",
            f"Do you want to mark Order {order_id} as completed?",
            icon='question'
        )
        if result:
            self.complete_order_from_list(order_id)

    def complete_order_from_list(self, order_id):
        """Complete order directly from the accepted orders list"""
        # Update status in database
        self.db.update_order_status(order_id, "completed")
        
        # Reload orders
        self.load_orders()
        
        # Clear details if this was the selected order
        if hasattr(self, 'current_order_id') and self.current_order_id == order_id:
            self.details_text.delete(1.0, tk.END)
            self.accept_button.configure(state="disabled")
            self.reject_button.configure(state="disabled")
            self.complete_button.configure(state="disabled")
        
        # Show confirmation
        messagebox.showinfo("Success", f"Order {order_id} has been completed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminPanel(root)
    root.mainloop() 