# Testing Setup

## Database Storage Features Being Tested

### 1. Raw PDF Content Storage
- Model number as unique identifier
- Raw extracted text storage
- Page content with tables
- Section and category organization

### 2. Data Structure Storage
- Structured sections (Features, Electrical, Magnetic)
- Nested categories and subcategories
- Values with units
- Bullet point lists

### 3. Basic Storage Operations
- Single record CRUD
- Batch operations
- Data validation
- Error handling

## Test Data Overview

### Model 100R Data Structure
```json
{
    "model_number": "100R",
    "data": {
        "raw_text": "...",
        "pages": [...],
        "sections": {
            "Features_And_Advantages": {...},
            "Electrical_Specifications": {...},
            "Magnetic_Specifications": {...}
        }
    }
}
```

### Model 200R Data Structure
```json
{
    "model_number": "200R",
    "data": {
        "raw_text": "...",
        "pages": [...],
        "sections": {
            "Features_And_Advantages": {...},
            "Electrical_Specifications": {...},
            "Magnetic_Specifications": {...}
        }
    }
}
```

## Running Tests

1. Set up test database:
```bash
python src/scripts/setup_test_db.py
```

2. Run tests:
```bash
# All tests
pytest src/ai_support_agent/tests/

# Storage tests
pytest src/ai_support_agent/tests/unit/test_storage.py
```

3. Clean up:
```bash
python src/scripts/setup_test_db.py --cleanup
```

## Test Categories

### Storage Tests
- Basic CRUD operations
- Data structure validation
- Error handling
- Type safety

### Database Tests
- Schema validation
- Index usage
- Constraint checking
- Transaction handling

## Environment Setup

Required environment variables in `.env`:
```
SUPABASE_URL=your_test_url
SUPABASE_KEY=your_test_key
```

## Database Purpose

The database is used ONLY for:
1. Storing extracted PDF content
2. Organizing content by model number
3. Maintaining data structure
4. Basic data validation

The database does NOT handle:
1. AI analysis or comparisons
2. Query processing
3. Feature extraction
4. Technical analysis
5. Recommendations

Note: All AI features, comparisons, and analysis are handled by the agents at runtime, not stored in the database. 