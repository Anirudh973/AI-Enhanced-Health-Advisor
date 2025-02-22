def get_nhs_urls():
    """
    Fetches URLs from the NHS website sitemap.
    Returns:
        List[str]: List of URLs
    """            
    sitemap_url = "https://www.nhs.uk/sitemap.xml"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nhs.uk/'
        }
        
        response = requests.get(sitemap_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Filter for relevant sections (conditions, symptoms, medicines)
        relevant_paths = ['/conditions/', '/symptoms/', '/medicines/']
        urls = [
            loc.text for loc in root.findall('.//ns:loc', namespace)
            if any(path in loc.text for path in relevant_paths)
        ]
        
        return urls
        
    except Exception as e:
        print(f"Error fetching NHS sitemap: {e}")
        return []

async def process_chunk(chunk: str, chunk_number: int, url: str) -> ProcessedChunk:
    """Process a single chunk of text."""
    # Get title and summary
    extracted = await get_title_and_summary(chunk, url)
    
    # Get embedding
    embedding = await get_embedding(chunk)
    
    # Determine page type based on URL
    page_type = 'general'
    if '/conditions/' in url:
        page_type = 'condition'
    elif '/symptoms/' in url:
        page_type = 'symptom'
    elif '/medicines/' in url:
        page_type = 'treatment'
    
    # Create metadata
    metadata = {
        "source": "nhs_uk",
        "chunk_size": len(chunk),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "url_path": urlparse(url).path,
        "page_type": page_type
    }
    
    return ProcessedChunk(
        url=url,
        chunk_number=chunk_number,
        title=extracted['title'],
        summary=extracted['summary'],
        content=chunk,
        metadata=metadata,
        embedding=embedding
    ) 