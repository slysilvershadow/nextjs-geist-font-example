import pygame
import base64
import io
from PIL import Image

class WebDisplay:
    """Handles converting Pygame display to web-friendly format"""
    
    @staticmethod
    def surface_to_image_data(surface):
        """Convert a Pygame surface to base64 encoded PNG"""
        # Get the surface data as a string buffer
        string_image = pygame.image.tostring(surface, 'RGB')
        
        # Convert to PIL Image
        pil_image = Image.frombytes('RGB', surface.get_size(), string_image)
        
        # Save to bytes buffer
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Convert to base64
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def update_webpage(image_data):
        """Write the image data to index.html"""
        html_content = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Game Display</title>",
            "<style>",
            "body{margin:0;background:#000;display:flex;justify-content:center;align-items:center;height:100vh}",
            "img{max-width:100vw;max-height:100vh}",
            "</style>",
            "</head>",
            "<body>",
            f'<img src="data:image/png;base64,{image_data}">',
            "</body>",
            "</html>"
        ]
        
        with open('index.html', 'w') as f:
            f.write('\n'.join(html_content))
