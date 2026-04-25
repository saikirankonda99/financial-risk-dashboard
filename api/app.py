from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Financial Risk API is running"}

@app.get("/risk/var")
def get_var():
    return {
        "portfolio_value": 12458320,
        "var_99": 342117,
        "expected_shortfall": 418093
    }