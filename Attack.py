import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

def calculate_risk(probability, impact):
    """Calculate risk score based on probability and impact."""
    try:
        probability = float(probability)
        impact = float(impact)
        if 1 <= probability <= 10 and 1 <= impact <= 10:
            return round(probability * impact, 2)
        else:
            raise ValueError("Probability and impact should be between 1 and 10.")
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
        return None

def get_color_from_risk(risk):
    """Get color and rating text based on the risk score."""
    if risk <= 25:
        return "green", "Negligible"
    elif 26 <= risk <= 50:
        return "yellow", "Low"
    elif 51 <= risk <= 75:
        return "orange", "Medium"
    elif 76 <= risk <= 100:
        return "red", "High"
    return "white", "None"

def get_color_from_impact(impact):
    """Get color based on the impact score."""
    if impact <= 2:
        return "green", "navy"
    elif 2.5 <= impact <= 5:
        return "yellow", "navy"
    elif 5.5 <= impact <= 7.5:
        return "orange", "navy"
    elif 8 <= impact <= 10:
        return "red", "navy"
    return "white", "black"

def update_node_color(node_id):
    """Update the color of a node based on impact and risk score."""
    item = attack_tree.item(node_id)
    impact = float(item["values"][1])
    probability = float(item["values"][2])
    risk = calculate_risk(probability, impact)
    impact_color, impact_font_color = get_color_from_impact(impact)
    risk_color, risk_text = get_color_from_risk(risk)
    attack_tree.item(node_id, tags=(impact_color,))
    attack_tree.tag_configure(impact_color, background=impact_color, foreground=impact_font_color)
    attack_tree.set(node_id, "Risk", risk)
    return risk_color, risk_text

def add_node():
    """Add a new node to the treeview."""
    item_name = item_update_entry.get().strip()
    impact = impact_update_entry.get().strip()
    probability = probability_update_entry.get().strip()
    
    try:
        risk = calculate_risk(probability, impact)
        if item_name and risk is not None:
            selected_item = attack_tree.selection()
            parent_id = selected_item[0] if selected_item else ''
            node_id = attack_tree.insert(parent_id, "end", text=item_name, values=(item_name, impact, probability, risk))
            update_node_color(node_id)
            refresh_calculations()
            item_update_entry.delete(0, "end")
            impact_update_entry.delete(0, "end")
            probability_update_entry.delete(0, "end")
        else:
            messagebox.showerror("Input Error", "Please enter valid item, impact, and probability values.")
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

def update_node():
    """Update an existing node."""
    selected_item = attack_tree.selection()
    if selected_item:
        item_name = item_update_entry.get().strip()
        impact = impact_update_entry.get().strip()
        probability = probability_update_entry.get().strip()
        
        try:
            if item_name:
                risk = calculate_risk(probability, impact)
                if risk is not None:
                    attack_tree.item(selected_item, text=item_name, values=(item_name, impact, probability, risk))
                    update_node_color(selected_item)
                    refresh_calculations()
                else:
                    messagebox.showerror("Input Error", "Please enter valid impact and probability values.")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
    else:
        messagebox.showwarning("Selection Error", "Please select an item to update.")

def delete_node():
    """Delete a selected node."""
    selected_item = attack_tree.selection()
    if selected_item:
        attack_tree.delete(selected_item)
        refresh_calculations()
    else:
        messagebox.showwarning("Selection Error", "Please select an item to delete.")

def refresh_calculations():
    """Refresh the calculations and update the displayed values."""
    total_risk = 0
    num_items = 0
    for item in attack_tree.get_children():
        total_risk += calculate_subtree_risk(item)
        num_items += 1

    if num_items > 0:
        average_risk = total_risk / num_items
        total_risk_value.config(text=f"{total_risk:.2f}")
        average_risk_value.config(text=f"{average_risk:.2f}")
        rating_color, rating_text = get_color_from_risk(average_risk)
        rating_value.config(text=rating_text, background=rating_color, foreground="black")  # Updated font color
    else:
        total_risk_value.config(text="0.00")
        average_risk_value.config(text="0.00")
        rating_value.config(text="Negligible", background="green", foreground="black")  # Updated font color

def calculate_subtree_risk(node_id):
    """Calculate the total risk for a subtree rooted at the given node."""
    risk = 0
    num_items = 0
    for child_id in attack_tree.get_children(node_id):
        risk += calculate_subtree_risk(child_id)
        num_items += 1
    if num_items > 0:
        node_risk = risk / num_items
    else:
        node_risk = float(attack_tree.item(node_id)["values"][3])
    attack_tree.set(node_id, "Risk", node_risk)
    return node_risk

def load_from_json():
    """Load data from a JSON file."""
    file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if not file_path:
        return
    
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        
        # Clear current items in the tree
        attack_tree.delete(*attack_tree.get_children())
        
        def insert_nodes(parent_id, nodes):
            """Recursively insert nodes into the treeview."""
            for node in nodes:
                item_name = node.get("item", "Unknown")
                impact = float(node.get("impact", 0))
                probability = float(node.get("probability", 0))
                risk = calculate_risk(probability, impact)
                
                node_id = attack_tree.insert(parent_id, "end", text=item_name, values=(item_name, impact, probability, risk))
                update_node_color(node_id)
                
                subnodes = node.get("subnodes", [])
                if subnodes:
                    insert_nodes(node_id, subnodes)
        
        insert_nodes("", data.get("nodes", []))
        
    except json.JSONDecodeError:
        messagebox.showerror("File Error", "Error decoding JSON file.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_to_file():
    """Save the current treeview data to a JSON file."""
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if not file_path:
        return
    
    def get_nodes(parent_id):
        """Recursively get nodes from the treeview."""
        nodes = []
        for item in attack_tree.get_children(parent_id):
            node = attack_tree.item(item)
            node_data = {
                "item": node["values"][0],
                "impact": node["values"][1],
                "probability": node["values"][2],
                "risk": node["values"][3]
            }
            subnodes = get_nodes(item)
            if subnodes:
                node_data["subnodes"] = subnodes
            nodes.append(node_data)
        return nodes

    nodes = get_nodes("")
    
    with open(file_path, "w") as file:
        json.dump({"nodes": nodes}, file, indent=4)

def initialize_main_screen():
    """Initialize the main screen of the application."""
    global attack_tree, item_update_entry, impact_update_entry, probability_update_entry
    global total_risk_value, average_risk_value, rating_value

    for widget in root.winfo_children():
        widget.destroy()

    # Header Frame
    header_frame = tk.Frame(root, pady=20, bg="#0033cc")  # Solid blue background
    header_frame.pack(side="top", fill="x")

    # Header Title
    title_label = tk.Label(header_frame, text="Attack Tree Visualizer", font=("Arial", 28, "bold"), bg="#0033cc", fg="white")
    title_label.pack(pady=10, padx=20)

    # Treeview Frame
    tree_frame = tk.Frame(root, padx=10, pady=10)
    tree_frame.pack(side="top", fill="both", expand=True)

    attack_tree = ttk.Treeview(tree_frame, columns=("Item", "Impact", "Probability", "Risk"), show="headings")
    attack_tree.heading("Item", text="Item")
    attack_tree.heading("Impact", text="Impact")
    attack_tree.heading("Probability", text="Probability")
    attack_tree.heading("Risk", text="Risk")

    attack_tree.column("Item", stretch=tk.YES)
    attack_tree.column("Impact", stretch=tk.YES)
    attack_tree.column("Probability", stretch=tk.YES)
    attack_tree.column("Risk", stretch=tk.YES)

    attack_tree.pack(side="left", fill="both", expand=True)

    tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=attack_tree.yview)
    attack_tree.configure(yscroll=tree_scrollbar.set)
    tree_scrollbar.pack(side="right", fill="y")

    # Node Operations Frame
    operations_frame = tk.Frame(root, pady=20)
    operations_frame.pack(side="top", fill="x")

    item_label = tk.Label(operations_frame, text="Item Name:")
    item_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    item_update_entry = tk.Entry(operations_frame)
    item_update_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    impact_label = tk.Label(operations_frame, text="Impact (1-10):")
    impact_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

    impact_update_entry = tk.Entry(operations_frame)
    impact_update_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    probability_label = tk.Label(operations_frame, text="Probability (1-10):")
    probability_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

    probability_update_entry = tk.Entry(operations_frame)
    probability_update_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    add_node_button = ttk.Button(operations_frame, text="Add Node", command=add_node)
    add_node_button.grid(row=0, column=2, padx=5, pady=5)

    update_node_button = ttk.Button(operations_frame, text="Update Node", command=update_node)
    update_node_button.grid(row=1, column=2, padx=5, pady=5)

    delete_node_button = ttk.Button(operations_frame, text="Delete Node", command=delete_node)
    delete_node_button.grid(row=2, column=2, padx=5, pady=5)

    # Risk Calculations Frame
    calculations_frame = tk.Frame(root, pady=20, padx=10)
    calculations_frame.pack(side="top", fill="x")

    total_risk_label = tk.Label(calculations_frame, text="Total Risk:")
    total_risk_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    total_risk_value = tk.Label(calculations_frame, text="0.00")
    total_risk_value.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    average_risk_label = tk.Label(calculations_frame, text="Average Risk:")
    average_risk_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

    average_risk_value = tk.Label(calculations_frame, text="0.00")
    average_risk_value.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    rating_label = tk.Label(calculations_frame, text="Risk Rating:")
    rating_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

    rating_value = tk.Label(calculations_frame, text="Negligible", bg="green", fg="black")
    rating_value.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # File Operations Frame
    file_frame = tk.Frame(root, pady=20)
    file_frame.pack(side="top", fill="x")

    load_button = ttk.Button(file_frame, text="Load from JSON", command=load_from_json)
    load_button.pack(side="left", padx=10)

    save_button = ttk.Button(file_frame, text="Save to JSON", command=save_to_file)
    save_button.pack(side="left", padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Attack Tree Visualizer")
    root.geometry("800x600")
    initialize_main_screen()
    root.mainloop()
