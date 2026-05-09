# Search Engine Tool — Video Demonstration Script

**Duration:** 5 minutes (strict maximum)  
**Target:** 75-85+ grade band  
**Structure:** Live Demo → Code Walkthrough → Testing → Git → GenAI Evaluation

---

## 0. Opening (10 sec)

**[Screen: Title slide with your name, student ID, project name]**

> "Hi, this is [Name] demonstrating my Search Engine Tool for XJCO3011 Coursework 2. The tool crawls quotes.toscrape.com, builds an inverted index, and supports intelligent search with TF-IDF ranking."

**Transition:** Switch to terminal.

---

## (a) Live Demonstration — 1 min 50 sec

**[Screen: Terminal running `python src/main.py`]**

### Command 1: `build` (20 sec)

> "First, the build command crawls the target website, respects the 6-second politeness window between requests, and constructs the inverted index."

**Type:**
```
> build
```

**Narrate while it runs:**
> "You can see it crawling each page with a 6-second delay, then building the index with word frequencies and positions. The index is saved to data/index.json."

*(Wait for it to finish, or say "For the demo, I've pre-built the index to save time" and skip to load)*

### Command 2: `load` (10 sec)

> "The load command restores the index from disk so we can query it without re-crawling."

**Type:**
```
> load
```

### Command 3: `print` — single word lookup (20 sec)

> "The print command shows the inverted index entry for a specific word. Here I'll look up 'love'."

**Type:**
```
> print love
```

**Point out:**
> "Notice it displays the frequency, the exact positions in the document, and the page title. This is the raw index data."

### Command 4: `find` — multi-word query with TF-IDF (40 sec) ⭐ KEY FEATURE

> "Now for the most important feature: the find command. I'll search for 'good friends'. This uses two advanced features beyond the basic requirements."

**Type:**
```
> find good friends
```

**Point to the Score line:**
> "First, TF-IDF ranking. Instead of just counting words, we compute term frequency divided by document length, multiplied by the inverse document frequency. This means rare words like 'friends' contribute more than common words like 'good'."

**Point to the Proximity line:**
> "Second, phrase proximity scoring. Pages where 'good' and 'friends' appear close together get a bonus. You can see this page at the top has a high proximity score because the words are adjacent in the text."

### Edge Cases (20 sec)

> "The tool also handles edge cases gracefully."

**Type:**
```
> find nonexistentword12345
```

> "Non-existent words return an empty result without crashing."

**Type:**
```
> find
```

> "An empty query shows usage instructions."

**Type:**
```
> exit
```

---

## (b) Code Walkthrough & Design Decisions — 1 min 30 sec

**[Screen: VS Code / IDE showing the project]**

### Project Structure (20 sec)

**[Screen: Show the src/ directory]**

> "The project is split into four modules. Crawler handles HTTP requests and HTML parsing. Indexer builds the inverted index. Search implements the ranking algorithms. Main provides the CLI interface."

### Inverted Index Data Structure (30 sec)

**[Screen: Open `src/indexer.py`, scroll to the index structure comment]**

> "The core data structure is the inverted index. Instead of storing page-to-words, we store word-to-pages. Each word maps to a dictionary of URLs, and each URL stores frequency, positions, document length, and title."

**[Screen: Show a snippet of the actual index JSON]**

> "We also store metadata at the top level: total document count and average document length. This is essential for the TF-IDF calculation."

### Why TF-IDF? (25 sec)

**[Screen: Open `src/search.py`, show `compute_tf_idf` function]**

> "For ranking, I chose TF-IDF over raw frequency for two reasons. First, raw frequency biases toward long documents. TF normalises by document length. Second, IDF rewards rare query terms. If you search for 'algorithm', pages containing this rare word should outrank pages with common words like 'the'."

### Why Proximity Scoring? (15 sec)

**[Screen: Show `compute_proximity_score` function]**

> "For multi-word queries, I added proximity scoring. The minimum distance between any two word positions is found using a two-pointer scan in O(n) time. Closer words get a higher bonus."

---

## (c) Testing Demonstration — 30 sec

**[Screen: Terminal running pytest]**

**Type:**
```bash
pytest tests/ -v -m "not slow" --cov=src --cov-report=term-missing
```

> "The test suite contains 45 tests covering unit tests, integration tests, and performance benchmarks. We use mocks for network calls so tests run in milliseconds. The coverage report shows 81% line coverage."

**Point to the output:**
> "Key tests include TF-IDF calculation verification, proximity scoring for adjacent words, parametrised tokenisation edge cases, and performance benchmarks ensuring 100-page index builds in under one second."

---

## (d) Version Control — 30 sec

**[Screen: Terminal showing git log]**

**Type:**
```bash
git log --oneline
```

> "The Git history shows incremental development using semantic commits. 'feat:' for new features like TF-IDF, 'test:' for test additions, and 'docs:' for README updates. This demonstrates a professional development workflow."

**[Screen: Briefly show git diff or file changes]**

---

## (e) GenAI Critical Evaluation — 30 sec

**[Screen: Back to yourself speaking to camera, or show a slide with bullet points]**

> "I used Claude as a primary development assistant. Three specific examples:
>
> **First, where it helped.** Claude suggested the overall project structure — crawler, indexer, search, main — which matched the coursework requirements exactly. It also helped me derive the TF-IDF formula correctly, which I then verified against lecture materials.
>
> **Second, where it misled.** Claude initially suggested using a list to store the inverted index entries, which would have made URL lookups O(n). I debugged this and refactored to nested dictionaries for O(1) lookups.
>
> **Third, the learning impact.** Using AI accelerated my understanding of BeautifulSoup and pytest parametrisation. However, I made sure to manually test every edge case — empty queries, non-existent words, network failures — because AI-generated tests missed several of these."

---

## Closing (10 sec)

> "Thank you for watching. The full source code, test suite, and compiled index are available in the GitHub repository linked in the submission."

**[Screen: End slide with GitHub URL]**

---

## Recording Tips

1. **Script the live demo** — practise the typing so there are no typos
2. **Zoom in** — terminal and code should be readable at 720p
3. **Use OBS or PowerPoint** — record screen + narration in one go
4. **Keep pacing tight** — if you run over 5 minutes, cut content from the code walkthrough, not the live demo
5. **Upload unlisted to YouTube** — test the link in an incognito window before submitting
