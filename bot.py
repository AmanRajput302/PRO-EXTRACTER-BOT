import os
import re
import base64
import random
import string
from pyrogram import Client, filters
from pyrogram.types import Message
from config import CHANNEL_ID

thumb_path = "Extractor/thumbs/html-5.png"

def extract_names_and_urls(file_content):
    """Extract names and URLs from the text content."""
    lines = file_content.strip().split("\n")
    data = []
    
    for line in lines:
        if not line.strip():
            continue
            
        separators = [':', ' - ', '|', '=>', '->']
        for separator in separators:
            if separator in line:
                parts = line.split(separator, 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    url = parts[1].strip()
                    url = url.strip('"').strip("'").strip()
                    
                    # Handle classplusapp URLs
                    if "media-cdn.classplusapp.com" in url:
                        url = f"https://api.extractor.workers.dev/player?url={url}"
                    
                    data.append((name, url))
                    break
                    
    return data

def categorize_urls(urls):
    """Categorize URLs into videos, PDFs, and others."""
    videos = []
    pdfs = []
    others = []

    video_patterns = [
        r'\.m3u8',
        r'\.mp4',
        r'media-cdn\.classplusapp\.com',
        r'api\.extractor\.workers\.dev',
        r'cpvod\.testbook',
        r'/master\.mpd',
        r'youtube\.com',
        r'youtu\.be',
        r'player\.vimeo\.com',
        r'dailymotion\.com',
        r'jwplayer',
        r'brightcove'
    ]
    
    pdf_patterns = [
        r'\.pdf',
        r'/pdf/',
        r'drive\.google\.com.*pdf',
        r'docs\.google\.com.*pdf'
    ]
    
    image_patterns = [
        r'\.jpg', r'\.jpeg', r'\.png', r'\.gif', r'\.webp',
        r'imgur\.com', r'\.svg', r'\.bmp'
    ]

    for name, url in urls:
        url = url.strip()
        
        # Check for video patterns
        is_video = any(re.search(pattern, url, re.IGNORECASE) for pattern in video_patterns)
        if is_video:
            videos.append((name, url))
            continue
            
        # Check for PDF patterns
        is_pdf = any(re.search(pattern, url, re.IGNORECASE) for pattern in pdf_patterns)
        if is_pdf:
            pdfs.append((name, url))
            continue
            
        # Add to others with type info
        link_type = 'default'
        link_icon = 'fas fa-link'
        
        # Check for image
        if any(re.search(pattern, url, re.IGNORECASE) for pattern in image_patterns):
            link_type = 'image'
            link_icon = 'fas fa-image'
        # Check for YouTube
        elif 'youtube.com' in url or 'youtu.be' in url:
            link_type = 'youtube'
            link_icon = 'fab fa-youtube'
        # Check for social media
        elif 'twitter.com' in url or 'x.com' in url:
            link_type = 'twitter'
            link_icon = 'fab fa-twitter'
        elif 'facebook.com' in url:
            link_type = 'facebook'
            link_icon = 'fab fa-facebook'
        elif 'instagram.com' in url:
            link_type = 'instagram'
            link_icon = 'fab fa-instagram'
        elif 'linkedin.com' in url:
            link_type = 'linkedin'
            link_icon = 'fab fa-linkedin'
        elif 'github.com' in url:
            link_type = 'github'
            link_icon = 'fab fa-github'
        elif 'drive.google.com' in url:
            link_type = 'gdrive'
            link_icon = 'fab fa-google-drive'
        elif 'docs.google.com' in url:
            link_type = 'gdocs'
            link_icon = 'fas fa-file-alt'
        
        others.append((name, url, link_type, link_icon))

    return videos, pdfs, others

def obfuscate_url(url):
    """Obfuscate URL to make it unreadable but decodable."""
    # Add some salt to make it more complex
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    salted = salt + url
    # Double encode to make it more obscure
    encoded = base64.b64encode(salted.encode()).decode()
    encoded = base64.b64encode(encoded.encode()).decode()
    return encoded

def generate_html(file_name, videos, pdfs, others):
    """Generate modern HTML content programmatically."""
    file_name_without_extension = os.path.splitext(file_name)[0]
    
    # Helper function to determine video action
    def get_video_action(url):
        if 'utkarshapp.com' in url:
            return f"window.open('{url}', '_blank')"
        return f"playVideo('{obfuscate_url(url)}')"
    
    head = f"""
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
        <title>{file_name_without_extension}</title>
        <link href="https://cdn.plyr.io/3.7.8/plyr.css" rel="stylesheet" />
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/js-base64@3.7.5/base64.min.js"></script>
        <style>
            :root {{
                --font-family: 'Inter', sans-serif;
                --heading-color: #2d3748;
                --text-color: #4a5568;
                --accent-color: #4299e1;
                --border-color: #e2e8f0;
                --bg-color: #f7fafc;
            }}

            body {{
                font-family: var(--font-family);
                line-height: 1.6;
                color: var(--text-color);
                background-color: var(--bg-color);
            }}

            .brand-title {{
                font-weight: 700;
                letter-spacing: -0.025em;
                color: var(--heading-color);
                font-variant: small-caps;
                margin-bottom: 1.5rem;
            }}

            .header-title {{
                font-size: 1.875rem;
                font-weight: 600;
                color: var(--heading-color);
                margin-bottom: 1rem;
                font-variant: small-caps;
            }}

            .stats-container {{
                display: flex;
                justify-content: center;
                gap: 1.5rem;
                margin-bottom: 2rem;
                flex-wrap: wrap;
            }}

            .stat-item {{
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                padding: 1rem 1.5rem;
                border-radius: 12px;
                border: 1px solid var(--border-color);
                text-align: center;
                min-width: 150px;
            }}

            .stat-number {{
                font-size: 2rem;
                font-weight: 700;
                color: var(--accent-color);
                margin-bottom: 0.25rem;
                font-variant: small-caps;
            }}

            .stat-label {{
                font-size: 0.875rem;
                color: var(--text-color);
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}

            .content-section {{
                margin-top: 2rem;
            }}

            .section-title {{
                font-size: 1.25rem;
                font-weight: 600;
                color: var(--heading-color);
                margin-bottom: 1rem;
                font-variant: small-caps;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}

            .link-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}

            .link-item {{
                background: white;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.75rem;
                transition: all 0.2s ease;
            }}

            .link-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }}

            .link-item a {{
                color: var(--accent-color);
                text-decoration: none;
                font-weight: 500;
            }}

            pre {{
                background: #1a202c;
                color: #e2e8f0;
                padding: 1rem;
                border-radius: 8px;
                overflow-x: auto;
                font-family: 'Monaco', 'Consolas', monospace;
                font-size: 0.875rem;
                margin: 1rem 0;
            }}

            blockquote {{
                border-left: 4px solid var(--accent-color);
                margin: 1rem 0;
                padding: 0.5rem 1rem;
                background: rgba(66, 153, 225, 0.1);
                border-radius: 4px;
            }}

            .extracted-by {{
                margin-top: 3rem;
                text-align: center;
                font-size: 0.875rem;
                color: var(--text-color);
                font-variant: small-caps;
            }}

            .extracted-by a {{
                color: var(--accent-color);
                text-decoration: none;
                font-weight: 500;
            }}

            @media (max-width: 768px) {{
                .stats-container {{
                    gap: 1rem;
                }}

                .stat-item {{
                    min-width: 120px;
                    padding: 0.75rem 1rem;
                }}

                .stat-number {{
                    font-size: 1.5rem;
                }}
            }}

            :root[data-theme="light"] {{
                --bs-body-bg: #f8fafc;
                --bs-body-color: #1e293b;
                --card-bg: rgba(255, 255, 255, 0.9);
                --card-border: rgba(0, 0, 0, 0.1);
                --hover-bg: rgba(59, 130, 246, 0.1);
                --icon-color: #3b82f6;
                --input-color: #1e293b;
                --input-placeholder: #64748b;
                --tab-active: #3b82f6;
                --tab-inactive: #64748b;
            }}
            :root[data-theme="dark"] {{
                --bs-body-bg: #0f172a;
                --bs-body-color: #e2e8f0;
                --card-bg: rgba(255, 255, 255, 0.1);
                --card-border: rgba(255, 255, 255, 0.2);
                --hover-bg: rgba(59, 130, 246, 0.2);
                --icon-color: #60a5fa;
                --input-color: #e2e8f0;
                --input-placeholder: rgba(226, 232, 240, 0.5);
                --tab-active: #ffffff;
                --tab-inactive: #94a3b8;
            }}
            body {{ 
                background: var(--bs-body-bg); 
                color: var(--bs-body-color);
                overflow-x: hidden;
                width: 100%;
                min-height: 100vh;
                -webkit-text-size-adjust: 100%;
                transition: all 0.3s ease;
            }}
            .container-fluid {{
                padding-left: max(15px, env(safe-area-inset-left));
                padding-right: max(15px, env(safe-area-inset-right));
            }}
            .brand-title {{ 
                font-size: min(2.5rem, 8vw);
                font-weight: 900;
                background: linear-gradient(45deg, #3b82f6, #10b981);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 2rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                animation: gradientText 3s ease infinite;
                padding: 0 10px;
                text-align: center;
                width: 100%;
            }}
            .header-title {{ 
                font-size: min(1.8rem, 6vw);
                font-weight: 700;
                overflow-wrap: break-word;
                word-wrap: break-word;
                hyphens: auto;
                max-width: 100%;
                padding: 0 15px;
                margin: 0 auto;
            }}
            @media (max-width: 768px) {{
                .nav-tabs .nav-link {{ 
                    padding: 10px 15px;
                    font-size: 0.9rem;
                }}
                .list-group-item {{
                    padding: 12px 15px;
                    flex-direction: column;
                    gap: 10px;
                }}
                .list-group-item .item-title {{
                    font-size: 0.9rem;
                    text-align: center;
                    justify-content: center;
                }}
                .list-group-item .item-actions {{
                    width: 100%;
                    justify-content: center;
                }}
                .floating-controls {{
                    bottom: max(20px, env(safe-area-inset-bottom));
                    right: max(20px, env(safe-area-inset-right));
                }}
                .toast-container {{
                    bottom: max(70px, calc(env(safe-area-inset-bottom) + 70px));
                    width: 90%;
                }}
                .btn-action {{
                    padding: 10px;
                }}
                .search-input {{
                    font-size: 16px; /* Prevents zoom on iOS */
                }}
            }}
            @supports not (padding: max(0px)) {{
                .container-fluid {{
                    padding-left: 15px;
                    padding-right: 15px;
                }}
                .floating-controls {{
                    bottom: 20px;
                    right: 20px;
                }}
                .toast-container {{
                    bottom: 70px;
                }}
            }}
            /* Video player container styles */
            .video-container {{
                position: relative;
                width: 100%;
                max-width: 1000px;
                margin: 0 auto;
                aspect-ratio: 16/9;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }}
            
            .video-container video {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            
            .plyr {{
                width: 100%;
                height: 100%;
            }}
            
            /* Make player controls bigger */
            :root {{
                --plyr-control-icon-size: 20px;
                --plyr-font-size-base: 15px;
                --plyr-control-spacing: 10px;
            }}
            
            /* Center the player in container */
            .container.mb-5 {{
                max-width: 1200px;
                padding: 0;
                margin-bottom: 0 !important;
            }}
            
            .glass-card {{
                padding: 12px !important;
                background: var(--card-bg);
                backdrop-filter: blur(16px);
                border-radius: 12px;
                border: 1px solid var(--card-border);
                transition: all 0.3s ease;
                margin: 10px;
            }}
            
            .glass-card:hover {{
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.47);
                transform: translateY(-5px);
            }}
            .nav-tabs {{ 
                display: flex;
                flex-wrap: nowrap;
                overflow-x: auto;
                scrollbar-width: none;
                -ms-overflow-style: none;
                border-bottom-color: rgba(255, 255, 255, 0.2);
            }}
            .nav-tabs::-webkit-scrollbar {{ display: none; }}
            .nav-tabs .nav-item {{ flex: 1; min-width: max-content; }}
            .list-group-item {{ 
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                color: var(--bs-body-color);
                transition: all 0.3s ease;
                margin-bottom: 8px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                padding: 12px 20px;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }}
            .list-group-item::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                width: 4px;
                height: 100%;
                background: var(--icon-color);
                opacity: 0;
                transition: all 0.3s ease;
            }}
            .list-group-item:hover {{ 
                background: var(--hover-bg);
                transform: translateX(10px);
            }}
            .list-group-item:hover::before {{
                opacity: 1;
            }}
            .list-group-item .item-title {{
                display: flex;
                align-items: center;
                gap: 12px;
                flex: 1;
            }}
            .list-group-item .item-title i {{
                font-size: 1.2rem;
                color: var(--icon-color);
                transition: all 0.3s ease;
            }}
            .list-group-item:hover .item-title i {{
                transform: scale(1.2);
            }}
            .list-group-item .item-title span {{
                font-weight: 500;
            }}
            .list-group-item .item-actions {{
                display: flex;
                align-items: center;
                gap: 10px;
                opacity: 0;
                transition: opacity 0.3s ease;
            }}
            .list-group-item:hover .item-actions {{
                opacity: 1;
            }}
            .btn-action {{
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 8px;
                width: 36px;
                height: 36px;
                color: #e2e8f0;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .btn-action:hover {{
                transform: scale(1.1);
            }}
            .btn-action.download {{
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
            }}
            .btn-action.play {{
                background: rgba(59, 130, 246, 0.2);
                color: #3b82f6;
            }}
            .btn-action.view {{
                background: rgba(245, 158, 11, 0.2);
                color: #f59e0b;
            }}
            .nav-tabs .nav-link {{ 
                color: var(--tab-inactive);
                border: none;
                position: relative;
                transition: all 0.3s ease;
                padding: 15px 25px;
                font-weight: 600;
            }}
            .nav-tabs .nav-link:hover {{ 
                color: var(--tab-active);
                border: none;
                background: transparent;
            }}
            .nav-tabs .nav-link.active {{ 
                color: var(--tab-active);
                background: transparent;
                border: none;
            }}
            .nav-tabs .nav-link.active::after {{
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 2px;
                background: var(--tab-active);
                animation: tabSlide 0.3s ease;
            }}
            @keyframes tabSlide {{
                from {{ width: 0; }}
                to {{ width: 100%; }}
            }}
            .search-input {{
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                color: var(--input-color);
                border-radius: 10px;
                padding: 12px 20px;
                width: 100%;
                transition: all 0.3s ease;
            }}
            .search-input:focus {{
                background: var(--card-bg);
                border-color: var(--icon-color);
                box-shadow: 0 0 0 0.25rem rgba(59, 130, 246, 0.25);
                color: var(--input-color);
            }}
            .search-input::placeholder {{ 
                color: var(--input-placeholder);
            }}
            .video-js {{ border-radius: 15px; overflow: hidden; }}
            .vjs-theme-forest {{ --vjs-theme-forest--primary: #3b82f6; }}
            .vjs-theme-forest .vjs-control-bar {{ background-color: rgba(15, 23, 42, 0.7); }}
            .pulse {{ animation: pulse 2s infinite; }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
            .floating-controls {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                display: flex;
                gap: 10px;
                z-index: 1000;
            }}
            .floating-btn {{
                background: rgba(59, 130, 246, 0.9);
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }}
            .floating-btn:hover {{
                transform: scale(1.1);
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
            }}
            .toast-container {{
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 1050;
            }}
            .theme-toggle {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 50px;
                padding: 8px 16px;
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
            .theme-toggle:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
            }}
            .theme-toggle i {{
                font-size: 1.2rem;
                color: var(--icon-color);
            }}
            /* Plyr customization */
            :root {{
                --plyr-color-main: #3b82f6;
                --plyr-video-background: var(--card-bg);
                --plyr-menu-background: var(--card-bg);
                --plyr-menu-color: var(--bs-body-color);
            }}
            .plyr {{
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }}
            /* Custom URL Input */
            .url-input-wrapper {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-top: 15px;
                padding: 8px;
                background: var(--card-bg);
                border-radius: 10px;
                border: 1px solid var(--card-border);
            }}
            
            .custom-url-input {{
                flex: 1;
                padding: 10px 15px;
                border-radius: 8px;
                border: 1px solid var(--card-border);
                background: var(--bs-body-bg);
                color: var(--bs-body-color);
                font-size: 15px;
                transition: all 0.3s ease;
            }}
            
            .custom-url-input:focus {{
                outline: none;
                border-color: var(--plyr-color-main);
                box-shadow: 0 0 8px rgba(59, 130, 246, 0.2);
            }}
            
            .custom-url-btn {{
                padding: 10px 20px;
                border-radius: 8px;
                background: var(--plyr-color-main);
                color: white;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
                white-space: nowrap;
                min-height: 42px;
            }}
            
            .custom-url-btn:hover {{
                opacity: 0.9;
                transform: scale(1.02);
            }}

            @media (max-width: 768px) {{
                .container.mb-5 {{
                    padding: 0;
                }}
                
                .glass-card {{
                    margin: 8px;
                    padding: 8px !important;
                }}
                
                .url-input-wrapper {{
                    flex-direction: column;
                    gap: 10px;
                    margin-top: 10px;
                    padding: 8px;
                }}
                
                .custom-url-input {{
                    width: 100%;
                    padding: 12px;
                }}
                
                .custom-url-btn {{
                    width: 100%;
                    justify-content: center;
                    padding: 12px;
                }}
            }}

            /* Fullscreen styles */
            .plyr--fullscreen-active {{
                width: 100% !important;
                height: 100% !important;
            }}

            @media screen and (orientation: portrait) {{
                .plyr--fullscreen-active {{
                    transform: rotate(-90deg);
                    transform-origin: center;
                }}
            }}
        </style>
    </head>
    """
    
    header = f"""
    <div class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">
        <i class="fas fa-sun"></i>
        <i class="fas fa-moon" style="display: none;"></i>
    </div>
    <div class="container-fluid py-5 text-center">
        <h1 class="brand-title mb-4">
<a href="https://t.me/zhonsnow" style="text-decoration: none; color: inherit;">
  <i class="fas fa-bolt"></i> 𓍯𝙎𝙪𝙟𝙖𝙡⚝ <i class="fas fa-bolt"></i>
</a>

                </h1>
        <h2 class="header-title mb-4">{file_name_without_extension}</h2>
        <p class="lead">
<a href="https://t.me/zhonsnow" style="text-decoration: none; color: inherit;">
  <span class="badge bg-primary me-2">
    <i class="fas fa-robot"></i> Join @zhonsnowchatbbot
  </span>
</a>

            <a href="http://t.me/GodxBOts" class="text-decoration-none">
                <span class="badge bg-warning">
                    <i class="fas fa-bolt"></i>𓍯𝙎𝙪𝙟𝙖𝙡⚝ 
                </span>
            </a>
        </p>
    </div>
    """
    
    video_player = """
    <div class="container mb-5">
        <div class="row justify-content-center">
            <div class="col-12">
                <div class="glass-card">
                    <div class="video-container">
                        <video id="player" playsinline controls>
                            <p>Please enable JavaScript to view videos.</p>
                        </video>
                    </div>
                    <div class="url-input-wrapper">
                        <input type="text" class="custom-url-input" id="customUrl" placeholder="Enter video URL to play...">
                        <button class="custom-url-btn" onclick="playCustomUrl()">
                            <i class="fas fa-play"></i>
                            <span>Play Video</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    search_bar = """
    <div class="container mb-4">
        <div class="row justify-content-center">
            <div class="col-12 col-md-8">
                <div class="input-group">
                    <span class="input-group-text bg-transparent border-0">
                        <i class="fas fa-search" style="color: var(--icon-color);"></i>
                    </span>
                    <input type="text" class="form-control search-input" id="searchInput" 
                           placeholder="Search content..." oninput="filterContent()">
                </div>
            </div>
        </div>
    </div>
    """
    
    # Build content sections with modern styling
    video_links = "".join(
        f'<div class="list-group-item" onclick="{get_video_action(url)}">'
        f'<div class="item-title">'
        f'<i class="fas fa-play-circle"></i>'
        f'<span>{name}</span>'
        f'</div>'
        f'</div>' 
        for name, url in videos
    )
    
    pdf_links = "".join(
        f'<div class="list-group-item">'
        f'<div class="item-title">'
        f'<i class="fas fa-file-pdf text-danger"></i>'
        f'<span>{name}</span>'
        f'</div>'
        f'<div class="item-actions">'
        f'<button class="btn-action view" onclick="viewPDF(\'{obfuscate_url(url)}\')" title="View PDF">'
        f'<i class="fas fa-eye"></i></button>'
        f'<button class="btn-action download" onclick="downloadFile(\'{obfuscate_url(url)}\', \'{name} - @zhonsnowchatbbot.pdf\')" title="Download PDF">'
        f'<i class="fas fa-download"></i></button>'
        f'</div>'
        f'</div>'
        for name, url in pdfs
    )
    
    other_links = "".join(
        f'<div class="list-group-item">'
        f'<div class="item-title">'
        f'<i class="{link_icon} text-{get_icon_color(link_type)}"></i>'
        f'<span>{name}</span>'
        f'</div>'
        f'<div class="item-actions">'
        f'<a href="javascript:void(0)" onclick="window.open(deobfuscateUrl(\'{obfuscate_url(url)}\'), \'_blank\')" class="btn-action" title="Open Link">'
        f'<i class="fas fa-external-link-alt"></i></a>'
        f'</div>'
        f'</div>'
        for name, url, link_type, link_icon in others
    )
    
    content = f"""
    <div class="container">
        <div class="row">
            <div class="col-12">
                <div class="glass-card p-4">
                    <ul class="nav nav-tabs mb-4" role="tablist">
                        <li class="nav-item">
                            <a class="nav-link active" data-bs-toggle="tab" href="#videos">
                                <i class="fas fa-video"></i>Videos
                                <span class="tab-indicator">{len(videos)}</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" data-bs-toggle="tab" href="#pdfs">
                                <i class="fas fa-file-pdf"></i>PDFs
                                <span class="tab-indicator">{len(pdfs)}</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" data-bs-toggle="tab" href="#others">
                                <i class="fas fa-link"></i>Others
                                <span class="tab-indicator">{len(others)}</span>
                            </a>
                        </li>
                    </ul>
                    
                    <div class="tab-content">
                        <div id="videos" class="tab-pane active">
                            <div class="list-group">{video_links}</div>
                        </div>
                        <div id="pdfs" class="tab-pane">
                            <div class="list-group">{pdf_links}</div>
                        </div>
                        <div id="others" class="tab-pane">
                            <div class="list-group">{other_links}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="floating-controls">
        <button class="floating-btn" onclick="scrollToTop()" title="Scroll to Top">
            <i class="fas fa-arrow-up"></i>
        </button>
    </div>
    
    <div class="toast-container"></div>
    """
    
    scripts = """
    <script src="https://cdn.plyr.io/3.7.8/plyr.polyfilled.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <script>
        // Initialize theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeToggle();
        
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeToggle();
        }
        
        function updateThemeToggle() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const sunIcon = document.querySelector('.theme-toggle .fa-sun');
            const moonIcon = document.querySelector('.theme-toggle .fa-moon');
            if (currentTheme === 'dark') {
                sunIcon.style.display = '';
                moonIcon.style.display = 'none';
            } else {
                sunIcon.style.display = 'none';
                moonIcon.style.display = '';
            }
        }
        
        function deobfuscateUrl(encoded) {
            try {
                let decoded = atob(encoded);
                decoded = atob(decoded);
                return decoded.slice(8);
            } catch (e) {
                console.error('Error decoding URL:', e);
                return encoded;
            }
        }
        
        // Initialize Plyr with more features
        const player = new Plyr('#player', {
            controls: [
                'play-large',
                'restart',
                'rewind',
                'play',
                'fast-forward',
                'progress',
                'current-time',
                'duration',
                'mute',
                'volume',
                'settings',
                'pip',
                'airplay',
                'fullscreen'
            ],
            settings: ['captions', 'quality', 'speed', 'loop'],
            speed: { selected: 1, options: [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 3, 4] },
            tooltips: { controls: true, seek: true },
            keyboard: { focused: true, global: true },
            resetOnEnd: true,
            fullscreen: { enabled: true, fallback: true, iosNative: true }
        });
        
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
        
        function playCustomUrl() {
            const url = document.getElementById('customUrl').value.trim();
            if (url) {
                if (url.includes('utkarshapp.com')) {
                    window.open(url, '_blank');
                } else {
                    loadVideo(url);
                    document.getElementById('customUrl').value = '';
                }
            }
        }

        // Add Enter key support for custom URL
        document.getElementById('customUrl').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                playCustomUrl();
            }
        });
        
        function playVideo(encodedUrl) {
            const url = deobfuscateUrl(encodedUrl);
            if (url.includes('utkarshapp.com')) {
                window.open(url, '_blank');
                return;
            }
            
            if (url.includes('api.extractor.workers.dev')) {
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        if (data.url) {
                            loadVideo(data.url);
                        }
                    })
                    .catch(() => {
                        window.open(url, '_blank');
                        showToast('Opening video in new tab', 'info');
                    });
            } else {
                loadVideo(url);
            }
            
            document.getElementById('player').scrollIntoView({ 
                behavior: 'smooth',
                block: 'center'
            });
        }
        
        function loadVideo(url) {
            const source = { type: 'video' };
            
            if (url.includes('.m3u8')) {
                if (Hls.isSupported()) {
                    const hls = new Hls();
                    hls.loadSource(url);
                    hls.attachMedia(player.media);
                    hls.on(Hls.Events.MANIFEST_PARSED, () => {
                        player.play();
                    });
                } else if (player.media.canPlayType('application/vnd.apple.mpegurl')) {
                    source.src = url;
                    source.type = 'application/x-mpegURL';
                    player.source = source;
                    player.play();
                }
            } else {
                source.src = url;
                source.type = 'video/mp4';
                player.source = source;
                player.play();
            }
        }
        
        function viewPDF(encodedUrl) {
            const url = deobfuscateUrl(encodedUrl);
            const viewerUrl = `https://tempnewwebsite.classx.co.in/pdfjs/web/viewer.html?file=${encodeURIComponent(url)}&embedded=true`;
            window.open(viewerUrl, '_blank');
        }
        
        function downloadFile(encodedUrl, filename) {
            const url = deobfuscateUrl(encodedUrl);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
        
        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
        
        function filterContent() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            document.querySelectorAll('.list-group-item').forEach(item => {
                const text = item.querySelector('.item-title').textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.opacity = '0';
                    setTimeout(() => {
                        item.style.display = '';
                        item.style.opacity = '1';
                    }, 150);
                } else {
                    item.style.display = 'none';
                }
            });
        }
        
        // Initialize tooltips
        document.addEventListener('DOMContentLoaded', () => {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        });

        // Handle fullscreen change
        player.on('enterfullscreen', () => {
            if (screen.orientation && screen.orientation.lock) {
                screen.orientation.lock('landscape').catch(() => {});
            }
        });

        player.on('exitfullscreen', () => {
            if (screen.orientation && screen.orientation.unlock) {
                screen.orientation.unlock();
            }
        });
    </script>
    """
    
    # Combine all parts with theme support
    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
{head}
<body>
{header}
{video_player}
{search_bar}
{content}
{scripts}
</body>
</html>"""
    
    return html

def get_icon_color(link_type):
    """Get Bootstrap color class based on link type."""
    color_map = {
        'image': 'info',
        'youtube': 'danger',
        'twitter': 'info',
        'facebook': 'primary',
        'instagram': 'danger',
        'linkedin': 'primary',
        'github': 'dark',
        'gdrive': 'success',
        'gdocs': 'primary',
        'default': 'success'
    }
    return color_map.get(link_type, 'success')

async def handle_txt2html(client: Client, message: Message):
    """Handle text file to HTML conversion."""
    if not message.document or not message.document.file_name.endswith('.txt'):
        await message.reply_text("Please upload a .txt file.")
        return
        
    try:
        # Download the file
        file_path = await message.download()
        file_name = message.document.file_name
        
        # Read the file content
        with open(file_path, "r", encoding='utf-8') as f:
            file_content = f.read()
            
        # Extract names and URLs
        urls = extract_names_and_urls(file_content)
        if not urls:
            await message.reply_text("❌ No valid content found in the text file.\n\nFormat should be:\nName: URL\nName2: URL2")
            return
            
        # Categorize URLs
        videos, pdfs, others = categorize_urls(urls)
        
        # Generate HTML
        html_content = generate_html(file_name, videos, pdfs, others)
        
        # Save HTML file with @GodxBots suffix
        base_name = os.path.splitext(file_name)[0]
        html_file_name = f"{base_name}_@zhonsnowchatbbot.html"
        html_file_path = os.path.join(os.path.dirname(file_path), html_file_name)
        
        with open(html_file_path, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        # Send the HTML file
        await message.reply_document(
            document=html_file_path,
            thumb=thumb_path if thumb_path else None,
            caption="<blockquote>✨ ʜᴛᴍʟ ꜰɪʟᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜰᴜʟʟʏ!</blockquote>\n\n"
            "• 🖤 ᴜʟᴛʀᴀ ᴍᴏᴅᴇʀɴ ᴅᴀʀᴋ ᴜɪ\n"
            "• 🎬 ꜱᴍᴀʀᴛ ᴠɪᴅᴇᴏ ᴘʟᴀʏᴇʀ\n"
            "• 📄 ᴘᴅꜰ ᴅᴏᴡɴʟᴏᴀᴅ ꜱᴜᴘᴘᴏʀᴛ\n"
            "• ✨ ʙᴇᴀᴜᴛɪꜰᴜʟ ᴀɴɪᴍᴀᴛɪᴏɴꜱ\n"
            "• 🧭 ꜰʟᴏᴀᴛɪɴɢ ᴄᴏɴᴛʀᴏʟꜱ",
    file_name=html_file_name
)

        
        # Forward to channel if configured
        if CHANNEL_ID:
            await client.send_document(chat_id=CHANNEL_ID, document=html_file_path)
        
        # Cleanup
        try:
            os.remove(file_path)
            os.remove(html_file_path)
        except:
            pass
            
    except Exception as e:
        await message.reply_text(f"❌ Error processing file: {str(e)}")
async def show_txt2html_help(client: Client, message: Message):
    await message.reply_text(
        "<b>📝 ᴛxᴛ ➜ ʜᴛᴍʟ ᴄᴏɴᴠᴇʀᴛᴇʀ</b>\n"
        "<blockquote>• ᴍᴏᴅᴇʀɴ ᴅᴀʀᴋ ᴛʜᴇᴍᴇ ᴜɪ 🖤</blockquote>\n"
        "<blockquote>• ᴠɪᴅᴇᴏ ᴘʟᴀʏᴇʀ ɪɴᴛᴇɢʀᴀᴛɪᴏɴ 🎬</blockquote>\n"
        "<blockquote>• ᴘᴅꜰ ᴅᴏᴄᴜᴍᴇɴᴛ ꜱᴇᴄᴛɪᴏɴ 📄</blockquote>\n"
        "<blockquote>• ꜱᴍᴀʀᴛ ꜱᴇᴀʀᴄʜ ꜰᴜɴᴄᴛɪᴏɴᴀʟɪᴛʏ 🔎</blockquote>\n"
        "<blockquote>• ʀᴇꜱᴘᴏɴꜱɪᴠᴇ ᴅᴇꜱɪɢɴ 📱</blockquote>\n"
        "<b>📩 ꜱᴇɴᴅ ᴀ .ᴛxᴛ ꜰɪʟᴇ ᴛᴏ ɢᴇᴛ ꜱᴛᴀʀᴛᴇᴅ!</b>"
    )

