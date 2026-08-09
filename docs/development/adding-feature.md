# Adding a New Feature

This backend follows a modular, Feature-Based approach. To add a new feature (e.g., "products"), follow these steps:

1. **Create the Folder**: Create `src/features/products/`.
2. **Create the Models**: Create `models.py` inside it and define your `SQLModel` database tables.
3. **Create the Schemas**: Create `schemas.py` for your Pydantic input/output validation models.
4. **Create the API Routes**: Create `api.py` and define your FastAPI `@router` endpoints.
5. **Register the Router**: Open `src/app/main.py` and include your new router in the main FastAPI app:
   ```python
   from features.products import api as products
   app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
   ```

Because of this strict isolation, you can safely work on your feature without breaking the rest of the application.
