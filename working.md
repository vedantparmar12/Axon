# MCP Crawl4AI RAG Testing Guide

This guide provides comprehensive test scenarios and prompts to validate the MCP Crawl4AI RAG system functionality.

## Prerequisites

### 1. Environment Configuration

**⚠️ IMPORTANT: Your .env file needs to be configured before testing!**

Current .env status:
- ❌ OPENAI_API_KEY is empty
- ❌ SUPABASE_URL needs to be set
- ❌ SUPABASE_SERVICE_KEY needs to be set

#### Quick Setup Options:

**Option 1: Local Setup with Ollama (Recommended for testing)**
```bash
# Update your .env with:
EMBEDDING_PROVIDER=ollama
ENABLE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

LLM_PROVIDER=ollama
ENABLE_OLLAMA_LLM=true
OLLAMA_LLM_MODEL=mistral:instruct

# Install Ollama first:
# curl -fsSL https://ollama.com/install.sh | sh
# ollama pull nomic-embed-text
# ollama pull mistral:instruct
```

**Option 2: OpenAI Setup**
```bash
# Update your .env with:
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your-actual-api-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

LLM_PROVIDER=auto  # Will fallback to available options
```

**Option 3: HuggingFace Setup (CPU)**
```bash
EMBEDDING_PROVIDER=huggingface
ENABLE_HUGGINGFACE=true
HUGGINGFACE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
HUGGINGFACE_DEVICE=cpu

LLM_PROVIDER=huggingface
ENABLE_HUGGINGFACE_LLM=true
HUGGINGFACE_LLM_MODEL=microsoft/Phi-3-mini-4k-instruct
HUGGINGFACE_LLM_DEVICE=cpu
```

### 2. Supabase Setup

1. Create a free account at https://supabase.com
2. Create a new project
3. Get your URL and service key from Settings > API
4. Update .env:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-service-key
   ```

### 3. Install Dependencies

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

## Test Scenarios

### 1. Basic Web Crawling Tests

#### Test 1.1: Single URL Crawling
```
# MCP Command
crawl https://docs.anthropic.com/en/docs/intro-to-claude

# Expected Result
- Should successfully crawl the page
- Convert content to markdown
- Store in database with embeddings
- Return crawl statistics
```

#### Test 1.2: Sitemap Crawling
```
# MCP Command
crawl https://docs.anthropic.com/sitemap.xml --max-pages 10

# Expected Result
- Should detect sitemap format
- Extract URLs from sitemap
- Crawl up to 10 pages
- Show progress and statistics
```

#### Test 1.3: Recursive Crawling
```
# MCP Command
crawl https://example.com --max-depth 2 --max-pages 20

# Expected Result
- Should crawl main page
- Follow internal links up to depth 2
- Respect max-pages limit
- Store all content with proper hierarchy
```

### 2. PDF Processing Tests

#### Test 2.1: PDF URL Processing
```
# MCP Command
crawl https://arxiv.org/pdf/2301.00303.pdf

# Expected Result
- Should detect PDF format
- Extract text content
- Create embeddings
- Store in database
```

#### Test 2.2: Visual PDF Processing
```
# MCP Command
process_visual_document https://arxiv.org/pdf/2301.00303.pdf

# Expected Result
- Should process PDF pages as images
- Create ColPali embeddings
- Enable visual search capabilities
```

### 3. Search and Retrieval Tests

#### Test 3.1: Basic Semantic Search
```
# MCP Command
search "what is Claude and how does it work" --limit 5

# Expected Result
- Should return 5 most relevant chunks
- Show similarity scores
- Include source URLs
- Highlight matching content
```

#### Test 3.2: Code Search
```
# MCP Command
search_code_examples "python function to parse JSON"

# Expected Result
- Should return code snippets
- Include language detection
- Show AI-generated summaries
- Provide context
```

#### Test 3.3: Hybrid Search (if enabled)
```
# First enable in .env: USE_HYBRID_SEARCH=true

# MCP Command
search "Model Context Protocol MCP" --hybrid true

# Expected Result
- Should combine vector and keyword search
- Better exact match results
- Balanced relevance scoring
```

#### Test 3.4: Visual Document Search
```
# MCP Command
search_visual_documents "architecture diagram showing API flow"

# Expected Result
- Should search through visual PDF content
- Return relevant page images
- Show ColPali similarity scores
```

### 4. Advanced RAG Features Tests

#### Test 4.1: Contextual Embeddings
```
# Enable in .env: USE_CONTEXTUAL_EMBEDDINGS=true

# MCP Command
crawl https://docs.anthropic.com/en/docs/intro-to-claude
search "Claude capabilities" --limit 3

# Expected Result
- Chunks should have enhanced context
- Better semantic understanding
- More relevant results
```

#### Test 4.2: Agentic RAG (Code Extraction)
```
# Enable in .env: USE_AGENTIC_RAG=true

# MCP Command
crawl https://github.com/anthropics/anthropic-sdk-python

# Expected Result
- Should automatically extract code examples
- Generate summaries for each snippet
- Store in code_examples table
- Enable specialized code search
```

#### Test 4.3: Reranking
```
# Enable in .env: USE_RERANKING=true
# Requires: COHERE_API_KEY in .env

# MCP Command
search "how to implement error handling" --limit 10 --rerank true

# Expected Result
- Initial results from vector search
- Reranked by Cohere for relevance
- Improved result ordering
```

### 5. System Management Tests

#### Test 5.1: List Sources
```
# MCP Command
list_sources

# Expected Result
- Show all crawled domains
- Page counts per source
- Last crawl timestamps
- Total chunks stored
```

#### Test 5.2: Delete Source
```
# MCP Command
delete_source --domain example.com

# Expected Result
- Confirm deletion prompt
- Remove all chunks from domain
- Update source statistics
- Free up vector storage
```

#### Test 5.3: System Health Check
```
# MCP Command
system_health

# Expected Result
- Database connectivity status
- Embedding provider status
- LLM provider status
- Storage statistics
- Performance metrics
```

### 6. Evolution System Tests

#### Test 6.1: Request New Feature
```
# MCP Command
request_feature "Add support for crawling authenticated pages with cookies"

# Expected Result
- Orchestrator analyzes request
- Dependency validator checks requirements
- Code debugger ensures compatibility
- Integration tester validates changes
- New feature branch created
```

#### Test 6.2: Evaluate System Performance
```
# MCP Command
evaluate_system --test-queries 10

# Expected Result
- Run correctness evaluation
- Calculate ROUGE scores
- Measure retrieval accuracy
- Generate performance report
```

### 7. Multi-Modal Tests

#### Test 7.1: Combined Text and Visual Search
```
# MCP Commands
crawl https://example.com/documentation
process_visual_document https://example.com/architecture.pdf
search "system architecture" --multimodal true

# Expected Result
- Search across both text and visual content
- Unified result ranking
- Mixed content types in results
```

## Common Issues and Solutions

### Issue 1: "No embedding provider configured"
**Solution**: Set EMBEDDING_PROVIDER in .env and ensure API keys are provided

### Issue 2: "Supabase connection failed"
**Solution**: Verify SUPABASE_URL and SUPABASE_SERVICE_KEY are correct

### Issue 3: "Ollama not responding"
**Solution**: Ensure Ollama is running: `ollama serve`

### Issue 4: "Out of memory during crawling"
**Solution**: Reduce batch size or max concurrent pages in crawl command

### Issue 5: "PDF processing failed"
**Solution**: Check if PDF is accessible and not password-protected

## Performance Testing

### Load Test
```bash
# Crawl multiple sites concurrently
crawl https://site1.com --async &
crawl https://site2.com --async &
crawl https://site3.com --async &
```

### Embedding Speed Test
```bash
# Time embedding generation
time crawl https://example.com/large-page --chunks 100
```

### Search Performance Test
```bash
# Measure search latency
for i in {1..10}; do
  time search "test query $i" --limit 5
done
```

## Advanced Configuration Testing

### Test Different Embedding Dimensions
```bash
# Update .env for each test:
# OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # 1536 dims
# OPENAI_EMBEDDING_MODEL=text-embedding-3-large  # 3072 dims
# COHERE_EMBEDDING_MODEL=embed-english-v3.0      # 1024 dims
```

### Test Different Chunk Sizes
```bash
crawl https://example.com --chunk-size 1000
crawl https://example.com --chunk-size 5000
crawl https://example.com --chunk-size 10000
```

## Integration Testing

### Test with Claude Desktop
1. Install MCP server
2. Configure Claude Desktop to use this MCP
3. Test commands through Claude interface

### Test with API Endpoints
```bash
# If running as API server
curl -X POST http://localhost:8051/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Monitoring and Debugging

### Enable Debug Logging
```bash
export DEBUG=true
# Run commands to see detailed logs
```

### Check Database State
```sql
-- Connect to Supabase SQL editor
SELECT COUNT(*) FROM crawled_pages;
SELECT COUNT(*) FROM code_examples;
SELECT COUNT(*) FROM sources;
```

### Monitor Resource Usage
```bash
# During crawling
top -p $(pgrep -f crawl4ai)
```

## Success Criteria

✅ Successfully crawl and index web pages
✅ Extract and embed PDF content
✅ Perform accurate semantic search
✅ Handle code examples with summaries
✅ Support multiple embedding providers
✅ Enable advanced RAG strategies
✅ Process visual documents with ColPali
✅ Manage sources and storage efficiently
✅ Self-improve with evolution system
✅ Handle errors gracefully

## Next Steps

1. Start with basic setup (Option 1 with Ollama)
2. Test basic crawling and search
3. Enable advanced features one by one
4. Evaluate performance and accuracy
5. Customize for your specific use case

Happy testing! 🚀