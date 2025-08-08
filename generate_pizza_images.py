from PIL import Image, ImageDraw
import os

def create_pizza_image(name, color, toppings_color):
    # Create a new image with a white background
    img = Image.new('RGB', (400, 400), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw the pizza base (circle)
    draw.ellipse([50, 50, 350, 350], fill=color)
    
    # Draw some toppings (circles)
    for _ in range(20):
        x = 100 + 200 * (0.2 + 0.6 * (_ % 5) / 5)
        y = 100 + 200 * (0.2 + 0.6 * (_ // 5) / 5)
        draw.ellipse([x-10, y-10, x+10, y+10], fill=toppings_color)
    
    # Save the image
    if not os.path.exists('images'):
        os.makedirs('images')
    img.save(f'images/{name.lower()}.png')

# Create images for different pizza types
create_pizza_image('margherita', '#FFD700', '#FF0000')  # Gold base with red toppings
create_pizza_image('pepperoni', '#FFD700', '#8B0000')   # Gold base with dark red toppings
create_pizza_image('vegetarian', '#FFD700', '#228B22')  # Gold base with green toppings
create_pizza_image('supreme', '#FFD700', '#FF4500')     # Gold base with orange-red toppings 